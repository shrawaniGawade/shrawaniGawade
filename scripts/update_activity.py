#!/usr/bin/env python3
"""Build profile SVGs from GitHub's API using Python's standard library and gh.

Run: python3 scripts/update_activity.py
The workflow uses its repository-scoped GITHUB_TOKEN; local runs use existing gh
authentication. Only public repositories and aggregate calendar data are queried.
No credentials, email addresses, private repository names or API payloads are saved.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
from math import hypot
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PAPER, INK, ROSE = "#FFF9EF", "#243F52", "#B65F76"
MUTED, SKY, GOLD, GREEN = "#596A70", "#DCEFF6", "#B98941", "#52755F"
LEVELS = {
    "NONE": "#EDE9DF",
    "FIRST_QUARTILE": "#E5B6C0",
    "SECOND_QUARTILE": "#CE879B",
    "THIRD_QUARTILE": "#A55370",
    "FOURTH_QUARTILE": "#73394F",
}
QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          firstDay
          contributionDays { date weekday contributionCount contributionLevel }
        }
      }
    }
  }
}
"""


def gh_json(*arguments: str):
    """Fail visibly on API/CLI errors; a failed refresh never fabricates zeros."""
    result = subprocess.run(
        ["gh", "api", *arguments], check=True, capture_output=True, text=True,
        timeout=90,
    )
    payload = json.loads(result.stdout)
    if isinstance(payload, dict) and payload.get("errors"):
        raise ValueError(f"GitHub GraphQL error: {payload['errors']}")
    return payload


def fetch_data(username: str, now: datetime) -> dict:
    start = now.date() - timedelta(days=364)
    response = gh_json(
        "graphql", "-f", f"query={QUERY}", "-f", f"login={username}",
        "-f", f"from={start.isoformat()}T00:00:00Z",
        "-f", f"to={now.isoformat().replace('+00:00', 'Z')}",
    )
    user = response["data"]["user"]
    if user is None:
        raise ValueError(f"GitHub user {username!r} does not exist")
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = calendar_days(calendar)
    if days[0]["date"] != start.isoformat() or days[-1]["date"] != now.date().isoformat():
        raise ValueError("GitHub returned an unexpected contribution date range")
    pages = gh_json(
        f"users/{username}/repos?per_page=100&type=owner", "--paginate", "--slurp",
        "-H", "Accept: application/vnd.github+json",
    )
    repositories = [repo for page in pages for repo in page if not repo["private"]]
    originals = [repo for repo in repositories if not repo["fork"]]
    languages = Counter(repo["language"] for repo in originals if repo["language"])
    return {
        "username": user["login"], "date": now.date().isoformat(),
        "calendar": calendar, "repositories": len(repositories),
        "stars": sum(repo["stargazers_count"] for repo in originals),
        "languages": sorted(languages.items(), key=lambda item: (-item[1], item[0]))[:3],
    }


def calendar_days(calendar: dict) -> list[dict]:
    """Validate chronological cells, weekdays, counts and the reported total."""
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    if not days:
        raise ValueError("Contribution calendar is empty")
    previous = None
    total = 0
    for day in days:
        current = date.fromisoformat(day["date"])
        if previous is not None and current != previous + timedelta(days=1):
            raise ValueError("Contribution dates are duplicated, missing or unordered")
        if day["weekday"] != current.isoweekday() % 7:
            raise ValueError("Contribution weekday does not match its date")
        count = day["contributionCount"]
        if type(count) is not int or count < 0:
            raise ValueError("Contribution count is not a nonnegative integer")
        if day["contributionLevel"] not in LEVELS:
            raise ValueError("Unknown contribution level")
        if (count == 0) != (day["contributionLevel"] == "NONE"):
            raise ValueError("Contribution color level contradicts its count")
        previous = current
        total += count
    if total != calendar["totalContributions"]:
        raise ValueError("Calendar total does not match its daily contributions")
    return days


def text(x, y, content, size=22, color=INK, font="Trebuchet MS, Arial, sans-serif", **attrs):
    attributes = " ".join(f'{key.replace("_", "-")}="{escape(str(value), quote=True)}"' for key, value in attrs.items())
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-family="{font}" {attributes}>{escape(str(content))}</text>'


def svg(width, height, title, description, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="24" fill="{PAPER}" stroke="#E5D9C8"/>
{''.join(body)}
</svg>
'''


def stats_svg(data: dict, mobile=False) -> str:
    width, height = (600, 550) if mobile else (1000, 310)
    total = data["calendar"]["totalContributions"]
    body = [text(36, 51, "Small steps. Real progress.", 32 if mobile else 34, font="Georgia, serif")]
    stamp = f"Updated {data['date']} · UTC"
    body.append(text(36 if mobile else 964, 87 if mobile else 50, stamp, 20, MUTED, text_anchor="start" if mobile else "end"))
    metrics = [(total, "Contributions", "last 365 days"), (data["repositories"], "Public repos", "owned repositories"), (data["stars"], "Stars earned", "original public repos")]
    for index, (number, label, note) in enumerate(metrics):
        if mobile:
            x, y = 38, 151 + index * 92
            body.extend([
                text(x, y + 14, f"{number:,}", 48, ROSE, font="Georgia, serif"),
                text(190, y - 2, label, 25),
                text(190, y + 28, note, 22, MUTED),
            ])
        else:
            x, y = 40 + index * 330, 129
            body.extend([
                text(x, y, f"{number:,}", 52, ROSE, font="Georgia, serif"),
                text(x, y + 33, label, 24),
                text(x, y + 62, note, 20, MUTED),
            ])
            if index < 2:
                body.append(f'<path d="M{x+293} 91V188" stroke="#E5D9C8"/>')
    rule_y = 395 if mobile else 216
    body.append(f'<path d="M36 {rule_y}H{width-36}" stroke="#E5D9C8"/>')
    body.append(text(36, rule_y + 34, "Primary languages · original public repos", 22 if mobile else 21, MUTED))
    language_text = "  ·  ".join(f"{name} ({count})" for name, count in data["languages"])
    if not language_text:
        language_text = "No language data available yet"
    if mobile and len(language_text) > 38:
        first = "  ·  ".join(f"{name} ({count})" for name, count in data["languages"][:2])
        body.append(text(36, rule_y + 72, first, 24, GREEN))
        body.append(text(36, rule_y + 109, "  ·  ".join(f"{name} ({count})" for name, count in data["languages"][2:]), 24, GREEN))
    else:
        body.append(text(36, rule_y + 71, language_text, 24, GREEN))
    description = (
        f"GitHub snapshot for {data['username']}, updated {data['date']} UTC. "
        f"{total} contributions over the last 365 days; {data['repositories']} owned public repositories; "
        f"{data['stars']} stars across original public repositories. "
        f"Primary languages ranked by number of original public repositories: {language_text}."
    )
    return svg(width, height, "Shrawani Gawade — GitHub progress", description, body)


def snake_route(columns: int) -> list[tuple[int, int] | None]:
    """An orthogonal route; V/S turns are hidden in its movement.

    Empty entries separate the 18-week bands for the renderer's fade transitions.
    The same logical route works on the wide calendar and its mobile bands.
    """
    route = []
    for offset in range(0, columns, 18):
        width = min(18, columns - offset)
        local = []

        def go(x, y):
            if not local:
                local.append((x, y))
                return
            last_x, last_y = local[-1]
            if x != last_x and y != last_y:
                raise ValueError("Snake turns must follow calendar cells")
            while (last_x, last_y) != (x, y):
                last_x += (x > last_x) - (x < last_x)
                last_y += (y > last_y) - (y < last_y)
                local.append((last_x, last_y))

        if width >= 17:
            # A pixel V, a connecting lane, then an S traversed from its foot.
            for point in [(0, 3), (0, 1), (1, 1), (1, 2), (2, 2),
                          (2, 4), (3, 4), (3, 5), (4, 5), (4, 4),
                          (5, 4), (5, 2), (6, 2), (6, 1), (8, 1),
                          (8, 5), (14, 5), (14, 3), (10, 3),
                          (10, 1), (width - 2, 1), (width - 2, 6),
                          (0, 6), (0, 0), (width - 1, 0), (width - 1, 6)]:
                go(*point)
        else:
            # Short date ranges and a narrow final band still move safely.
            go(0, 0)
            for row in range(7):
                go(width - 1 if row % 2 == 0 else 0, row)
                if row < 6:
                    go(local[-1][0], row + 1)
        route.extend((x + offset, y) for x, y in local)
        route.extend([None] * 10)
    return route


def rounded_snake_path(points: list[tuple[float, float]], radius: float) -> tuple[str, float]:
    """Round grid corners and measure the path for a consistent travel speed."""
    vertices = [points[0]]
    for before, point, after in zip(points, points[1:], points[2:]):
        if ((point[0] - before[0]) * (after[1] - point[1]) !=
                (point[1] - before[1]) * (after[0] - point[0])):
            vertices.append(point)
    vertices.append(points[-1])
    path = [f'M{vertices[0][0]:.3f} {vertices[0][1]:.3f}']
    length = 0.0
    last = vertices[0]

    def line(point):
        nonlocal length, last
        point = tuple(round(value, 3) for value in point)
        length += hypot(point[0] - last[0], point[1] - last[1])
        path.append(f'L{point[0]:.3f} {point[1]:.3f}')
        last = point

    for before, corner, after in zip(vertices, vertices[1:], vertices[2:]):
        incoming = hypot(corner[0] - before[0], corner[1] - before[1])
        outgoing = hypot(after[0] - corner[0], after[1] - corner[1])
        r = min(radius, incoming / 2, outgoing / 2)
        enter = (corner[0] + (before[0] - corner[0]) * r / incoming,
                 corner[1] + (before[1] - corner[1]) * r / incoming)
        leave = (corner[0] + (after[0] - corner[0]) * r / outgoing,
                 corner[1] + (after[1] - corner[1]) * r / outgoing)
        line(enter)
        # Subpixel chords keep SVG stroke and motion-path distance calculations
        # aligned; browsers otherwise flatten quadratic curves differently.
        for step in range(1, 13):
            t = step / 12
            line(tuple((1 - t)**2 * enter[axis] + 2 * (1 - t) * t * corner[axis]
                       + t**2 * leave[axis] for axis in (0, 1)))
    line(vertices[-1])
    return ''.join(path), length


def garden_snake(columns: int, mobile=False) -> str:
    """A short tapered stroke and native motion-path head, with no drawn route."""
    gap, size = (26, 21) if mobile else (min(16.4, 864 / columns), 12.6)
    logical_bands, band = [], []
    for point in snake_route(columns):
        if point is not None:
            band.append(point)
        elif band:
            logical_bands.append(band)
            band = []
    plans, cursor = [], 0.0
    for logical in logical_bands:
        points = []
        for column, row in logical:
            if mobile:
                points.append((88 + (column % 18) * gap + size / 2,
                               145 + (column // 18) * 241 + row * gap + size / 2))
            else:
                points.append((87 + column * gap + size / 2, 140 + row * gap + size / 2))
        path, length = rounded_snake_path(points, gap * .34)
        tail = min(gap * 6.5, length * .3)
        travel = length / gap * .19
        clear = tail / gap * .19
        plans.append(dict(path=path, tail=tail / length * 1000,
                          start=cursor, end=cursor + travel, clear=cursor + travel + clear))
        cursor += travel + clear + .45
    duration = cursor
    styles = [f'.garden-snake{{pointer-events:none}}',
              f'.garden-snake-band,.garden-snake-head,.garden-snake-trail{{animation-duration:{duration:.4f}s;animation-timing-function:linear;animation-iteration-count:infinite}}',
              '.garden-snake-band,.garden-snake-head{opacity:0}',
              '@media(prefers-reduced-motion:reduce){.garden-snake{display:none}.garden-snake-band,.garden-snake-head,.garden-snake-trail{animation:none!important}}']
    paths, body = [], []

    def keyframes(name, values):
        # Merge coincident start/end entries; CSS and SMIL share one timeline.
        ordered = dict(sorted(values))
        return '@keyframes ' + name + '{' + ''.join(
            f'{time / duration * 100:.6f}%{{{value}}}' for time, value in ordered.items()) + '}'

    for index, plan in enumerate(plans):
        start, end, clear = plan['start'], plan['end'], plan['clear']
        path_id = f'garden-snake-path-{index}'
        paths.append(f'<path id="{path_id}" d="{plan["path"]}" pathLength="1000"/>')
        styles.append(keyframes(f'snake-band-{index}', [
            (0, 'opacity:0'), (start, 'opacity:0'), (start + .18, 'opacity:1'),
            (clear - .18, 'opacity:1'), (clear, 'opacity:0'), (duration, 'opacity:0')]))
        styles.append(keyframes(f'snake-head-{index}', [
            (0, 'opacity:0'), (start, 'opacity:0'), (start + .18, 'opacity:1'),
            (end - .16, 'opacity:1'), (end, 'opacity:0'), (duration, 'opacity:0')]))
        body.append(f'<g class="garden-snake-band" style="animation-name:snake-band-{index}">')
        # Overlapping rounded strokes create a narrow tail and a fuller neck.
        for layer in range(8):
            fraction = 1 - layer / 9
            tail = plan['tail'] * fraction
            name = f'snake-trail-{index}-{layer}'
            styles.append(keyframes(name, [
                (0, f'stroke-dashoffset:{tail:.4f}'),
                (start, f'stroke-dashoffset:{tail:.4f}'),
                (end, f'stroke-dashoffset:{tail - 1000:.4f}'),
                (clear, f'stroke-dashoffset:{tail - 1000 - plan["tail"]:.4f}'),
                (duration, f'stroke-dashoffset:{tail - 1000 - plan["tail"]:.4f}')]))
            body.append(f'<use href="#{path_id}" class="garden-snake-trail" style="animation-name:{name}" fill="none" stroke="{GREEN}" stroke-width="{size * (.14 + layer * .046):.2f}" stroke-opacity=".26" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{tail:.4f} 2200" stroke-dashoffset="{tail:.4f}"/>')
        times = {0: 0, start: 0, end: 1, duration: 1}
        key_times = ';'.join(f'{time / duration:.8f}' for time in sorted(times))
        key_points = ';'.join(str(times[time]) for time in sorted(times))
        body.append(f'<g class="garden-snake-head" style="animation-name:snake-head-{index}"><g data-snake="head">')
        body.append(f'<ellipse rx="{size*.38:.2f}" ry="{size*.28:.2f}" fill="{GREEN}"/>')
        for eye_y in (-size * .14, size * .14):
            body.append(f'<circle cx="{size*.16:.2f}" cy="{eye_y:.2f}" r="{size*.052:.2f}" fill="{PAPER}"/>')
        body.append(f'<animateMotion dur="{duration:.4f}s" rotate="auto" calcMode="linear" keyTimes="{key_times}" keyPoints="{key_points}" repeatCount="indefinite"><mpath href="#{path_id}"/></animateMotion>')
        body.append('</g></g></g>')
    return '<defs>' + ''.join(paths) + '<style>' + ''.join(styles) + '</style></defs><g class="garden-snake" aria-hidden="true">' + ''.join(body) + '</g>'


def garden_svg(data: dict) -> str:
    days = calendar_days(data["calendar"])
    start = date.fromisoformat(days[0]["date"])
    anchor = start - timedelta(days=start.isoweekday() % 7)
    end = date.fromisoformat(days[-1]["date"])
    columns = ((end - anchor).days // 7) + 1
    gap, size = min(16.4, 864 / columns), 12.6
    grid_x, grid_y = 87, 140
    total = data["calendar"]["totalContributions"]
    body = [
        text(36, 51, "A garden of little beginnings", 32, font="Georgia, serif"),
        text(36, 82, f"{start:%d %b %Y} — {end:%d %b %Y}", 18, MUTED),
        text(962, 49, f"{total:,}", 34, ROSE, font="Georgia, serif", text_anchor="end"),
        text(962, 77, "contributions", 17, MUTED, text_anchor="end"),
    ]
    for weekday, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        body.append(text(36, grid_y + weekday * gap + 11, label, 15, MUTED))
    previous_month = None
    last_label_column = -99
    for day in days:
        current = date.fromisoformat(day["date"])
        column = (current - anchor).days // 7
        weekday = current.isoweekday() % 7
        x, y = grid_x + column * gap, grid_y + weekday * gap
        month_key = (current.year, current.month)
        if month_key != previous_month:
            # Omit a label when a short leading month would collide with the next.
            if column - last_label_column >= 3:
                body.append(text(f"{x:.1f}", 121, current.strftime("%b"), 17, MUTED))
                last_label_column = column
            previous_month = month_key
        count = day["contributionCount"]
        title = f"{day['date']}: {count} contribution{'s' if count != 1 else ''}"
        body.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" rx="3.1" '
            f'fill="{LEVELS[day["contributionLevel"]]}" data-date="{day["date"]}" '
            f'data-count="{count}"><title>{escape(title)}</title></rect>'
        )
    body.append(garden_snake(columns))
    body.append(text(36, 301, f"Updated {date.fromisoformat(data['date']):%d %b %Y} · UTC", 17, MUTED))
    body.append(text(751, 301, "Less", 16, MUTED))
    for index, color in enumerate(LEVELS.values()):
        body.append(f'<rect x="{789+index*19}" y="286" width="14" height="14" rx="3" fill="{color}"/>')
    body.append(text(895, 301, "More", 16, MUTED))
    description = (
        f"{data['username']}'s contribution calendar from {start.isoformat()} to {end.isoformat()}. "
        f"{total} total contributions. Weeks run from left to right, Sunday through Saturday top to bottom. "
        "Cream squares indicate no contributions; progressively deeper rose shades indicate more contributions, "
        "using GitHub's relative contribution levels. Every square includes its date and exact count. "
        "A small decorative snake moves across the grid; reduced motion shows the still calendar. "
        f"Refreshed {data['date']} UTC."
    )
    return svg(1000, 326, "Shrawani Gawade — contribution garden", description, body)


def garden_mobile_svg(data: dict) -> str:
    """Wrap complete chronological weeks into readable mobile calendar bands."""
    days = calendar_days(data["calendar"])
    start = date.fromisoformat(days[0]["date"])
    end = date.fromisoformat(days[-1]["date"])
    anchor = start - timedelta(days=start.isoweekday() % 7)
    total = data["calendar"]["totalContributions"]
    columns = ((end - anchor).days // 7) + 1
    bands = (columns + 17) // 18
    height = 155 + bands * 241
    gap, size, grid_x = 26, 21, 88
    body = [
        text(32, 49, "A garden of little beginnings", 30, font="Georgia, serif"),
        text(32, 84, f"{start:%d %b %Y} — {end:%d %b %Y}", 18, MUTED),
        text(568, 84, f"{total:,} contributions", 19, ROSE, text_anchor="end"),
    ]
    for band in range(bands):
        band_start = anchor + timedelta(weeks=band * 18)
        band_end = min(end, band_start + timedelta(weeks=18, days=-1))
        band_first = max(start, band_start)
        top = 125 + band * 241
        body.append(text(32, top, f"{band_first:%d %b %Y} — {band_end:%d %b %Y}", 20, INK))
        grid_y = top + 20
        for weekday, label in ((1, "M"), (3, "W"), (5, "F")):
            body.append(text(46, grid_y + weekday * gap + 17, label, 18, MUTED))
        for day in days:
            current = date.fromisoformat(day["date"])
            column = (current - anchor).days // 7
            if column // 18 != band:
                continue
            local_column = column % 18
            weekday = current.isoweekday() % 7
            x, y = grid_x + local_column * gap, grid_y + weekday * gap
            count = day["contributionCount"]
            title = f"{day['date']}: {count} contribution{'s' if count != 1 else ''}"
            body.append(
                f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="4" '
                f'fill="{LEVELS[day["contributionLevel"]]}" data-date="{day["date"]}" '
                f'data-count="{count}"><title>{escape(title)}</title></rect>'
            )
    body.append(garden_snake(columns, mobile=True))
    footer_y = 125 + bands * 241
    body.append(text(32, footer_y, f"Updated {date.fromisoformat(data['date']):%d %b %Y} · UTC", 18, MUTED))
    body.append(text(362, footer_y, "Less", 18, MUTED))
    for index, color in enumerate(LEVELS.values()):
        body.append(f'<rect x="{409+index*24}" y="{footer_y-19}" width="19" height="19" rx="4" fill="{color}"/>')
    body.append(text(536, footer_y, "More", 18, MUTED))
    description = (
        f"{data['username']}'s contribution calendar from {start.isoformat()} to {end.isoformat()}. "
        f"{total} total contributions. Weeks run left to right in each band, then continue in the band below. "
        "Each band contains at most 18 weeks. Rows run Sunday through Saturday. "
        "Cream indicates no contributions; deeper rose indicates more contributions using GitHub's relative levels. "
        "Every square includes its exact date and count. "
        "A small decorative snake visits each band; reduced motion shows the still calendar. "
        f"Refreshed {data['date']} UTC."
    )
    return svg(600, height, "Shrawani Gawade — contribution garden", description, body)


def write_outputs(output_dir: Path, outputs: dict[str, str]) -> None:
    """Validate and stage every output before replacing any existing artifact."""
    for content in outputs.values():
        ET.fromstring(content)
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".activity-", dir=output_dir.parent) as directory:
        staging = Path(directory)
        for filename, content in outputs.items():
            (staging / filename).write_text(content, encoding="utf-8")
        for filename in outputs:
            os.replace(staging / filename, output_dir / filename)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="shrawaniGawade")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets/generated")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", args.username):
        parser.error("username must be a valid GitHub login")
    data = fetch_data(args.username, datetime.now(timezone.utc).replace(microsecond=0))
    outputs = {
        "stats.svg": stats_svg(data),
        "stats-mobile.svg": stats_svg(data, mobile=True),
        "contribution-garden.svg": garden_svg(data),
        "contribution-garden-mobile.svg": garden_mobile_svg(data),
    }
    write_outputs(args.output_dir, outputs)
    print(f"Refreshed {len(outputs)} SVGs for {data['username']} at {data['date']} UTC: "
          f"{data['calendar']['totalContributions']} contributions, "
          f"{data['repositories']} public repositories, {data['stars']} stars.")


if __name__ == "__main__":
    main()
