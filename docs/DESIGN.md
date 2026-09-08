# Shrawani’s illustrated GitHub profile

The profile uses the supplied portrait as its visual starting point: the bright blue sky, ivory sari, rose border, antique gate and leafy garden. The hero’s arched frame follows the gate’s curves; small outlined flowers echo the sari embroidery. The portrait is converted into colored vector paths and inlined inside both hero SVGs. Every displayed asset is native SVG, with no embedded PNG or external image dependency. Vector tracing gives the portrait a slightly more graphic, illustrated finish.

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

## A little movement

Self-contained CSS animations add a slow sunlight glint along the portrait arch, a few drifting gold specks and a swaying botanical sprig. Animated flowers grow from a small bud, hold a full bloom, and shrink again in an eight-second loop. The two desktop banner flowers bloom at different points in that cycle.

DeepAttend uses one coordinated eight-second sequence: the scan line travels over the face and fades out, then the corners turn green, a success badge appears, and its checkmark draws on. The confirmation holds briefly before fading and resetting for the next scan. A soft ring accents the confirmation. CodeGuardian uses the supplied angled shield and lock, recolored in deep blue, rose, gold and green. A sky-blue scan travels down and back over seven seconds, briefly highlighting the contours. The same shield appears as a small accent on the hero portrait. The project sequences also appear in the mobile cards.

The hero name fades into place once. The user-supplied interests — Curious Mind, Explainer and Automation Recorder — then reveal in sequence with a matching icon and a drawn gold underline. Each phrase has five seconds within a fifteen-second loop. Portrait geometry and contribution data remain stationary. All motion follows `prefers-reduced-motion`: with that preference enabled, all three interests appear together, flowers remain open, the shield and lock stay visible, and DeepAttend shows its completed checkmark. The README’s links provide interaction through the clickable project and contact cards. There are no JavaScript or hover-dependent controls inside the SVG images.

The contribution garden has a small, muted green snake inspired by the classic grid game. Its eight segments advance one cell every 140 milliseconds, with a fading tail. V and S shapes are hidden in the route; neither letter nor the route is drawn as a separate graphic. The snake visits each 18-week band in sequence, with enough time for its tail to leave before the next band begins. Contribution cells keep their real dates, counts and colors throughout. The daily refresh generates this animation alongside the calendar, using only native SVG shapes and CSS. Reduced motion hides the decorative snake and leaves the complete calendar visible.

## Editing

- `scripts/build_assets.py`: artwork, intro, toolkit and project-card text.
- `scripts/build_readme.py`: GitHub links and descriptive image alt text.
- `assets/security scan.svg`: the user-supplied shield source, retained unchanged.
- `scripts/shield_art.py`: extracts the supplied shield and lock paths, removes export-specific IDs and animations, and adds the profile palette and scan sequence.
- `assets/sg/security-shield.svg`: the standalone adapted native shield; the same artwork is inlined into the hero and CodeGuardian cards.
- `assets/sg/portrait.svg`: standalone native vector portrait, inlined by the banner generator.
- `assets/sg/portrait.png`: the original source, retained for future conversion; never embedded in the profile artwork.
- `scripts/vectorize_portrait.py`: optional conversion utility using VTracer 1.0.0a4; normal SVG builds do not require VTracer.
- `scripts/update_activity.py`: public GitHub statistics and contribution garden.
- `.github/workflows/refresh-profile.yml`: automatic activity refresh.

Rebuild from the repository root with Python 3:

```sh
python3 scripts/build_assets.py
python3 scripts/build_readme.py
python3 scripts/update_activity.py
```

The activity script uses GitHub CLI authentication. The scheduled workflow uses the repository’s built-in token. No personal access token or additional secret is needed.

To regenerate the vector portrait after changing the source image, install `vtracer==1.0.0a4` in a virtual environment and run `python3 scripts/vectorize_portrait.py`, followed by the normal asset build. [VTracer](https://github.com/visioncortex/vtracer) performs the local raster-to-path conversion; it is not required by viewers or the daily activity workflow.

## Content and inspiration

The illustrated layout and decorative drawing code are original; the portrait and angled shield geometry come from the user's supplied artwork. The section-by-section profile format was inspired by [Abdullah Mohamed’s profile](https://github.com/AbdullahM07/AbdullahM07); none of his personal details, artwork, projects, branding, or contact links are reused.

Shrawani’s name and engineering/web/AI/automation interests were checked against her public portfolio. Selected projects link to her original repositories. CodeGuardian is explicitly described as a prototype in progress. The profile has no verified email or LinkedIn address, so its contact card links only to her canonical GitHub account.
