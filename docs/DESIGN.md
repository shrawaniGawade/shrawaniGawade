# Shrawani’s illustrated GitHub profile

The profile uses the supplied portrait as its visual starting point: the bright blue sky, ivory sari, rose border, antique gate and leafy garden. The hero’s arched frame follows the gate’s curves; small outlined flowers echo the sari embroidery. The original portrait is embedded unchanged inside the hero SVGs, so they have no external image dependency.

## Palette and type

| Role | Color |
| --- | --- |
| Ivory paper | `#FFF9EF` |
| Deep blue text | `#243F52` |
| Sari rose | `#B65F76` |
| Sky blue | `#DCEFF6` |
| Antique gold | `#B98941` |
| Leaf green | `#52755F` |

Georgia gives headings a personal, storybook feel. Trebuchet MS, with Arial as fallback, keeps body text clear. No remote fonts, scripts, foreignObject, or external image services are required. Light artwork deliberately retains its own palette in both GitHub themes. Mobile artwork is selected with standard picture/source markup.

## Editing

- `scripts/build_assets.py`: artwork, intro, toolkit and project-card text.
- `scripts/build_readme.py`: GitHub links, image alt text and accessible text version.
- `assets/sg/portrait.png`: the user-supplied portrait. Replace only with an image you want public.
- `scripts/update_activity.py`: public GitHub statistics and contribution garden.
- `.github/workflows/refresh-profile.yml`: automatic activity refresh.

Rebuild from the repository root with Python 3:

```sh
python3 scripts/build_assets.py
python3 scripts/build_readme.py
python3 scripts/update_activity.py
```

The activity script uses GitHub CLI authentication. The scheduled workflow uses the repository’s built-in token. No personal access token or additional secret is needed.

## Content and inspiration

The illustrated layout and all SVG drawing code are original. The section-by-section profile format was inspired by [Abdullah Mohamed’s profile](https://github.com/AbdullahM07/AbdullahM07); none of his personal details, artwork, projects, branding, or contact links are reused.

Shrawani’s name and engineering/web/AI/automation interests were checked against her public portfolio. Selected projects link to her original repositories. CodeGuardian is explicitly described as a prototype in progress. The profile has no verified email or LinkedIn address, so its contact card links only to her canonical GitHub account.
