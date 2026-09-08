"""Adapt the user's native shield geometry to the profile palette and motion."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
STYLE = '''
.cg-travel{transform:translateY(28px);animation:cg-travel 7s ease-in-out infinite}
.cg-beam{opacity:0;animation:cg-beam 7s ease-in-out infinite}
.cg-highlight{opacity:.9}
@keyframes cg-travel{0%,8%{transform:translateY(28px)}46%,54%{transform:translateY(164px)}92%,100%{transform:translateY(28px)}}
@keyframes cg-beam{0%,8%,48%,52%,94%,100%{opacity:0}17%,39%,63%,85%{opacity:.7}}
@media(prefers-reduced-motion:reduce){.cg-travel,.cg-beam{animation:none!important}.cg-beam,.cg-highlight{display:none}}
'''


def adapted_shield(source: Path) -> str:
    root = ET.parse(source).getroot()
    # Extract the supplied front, side and lock shapes, not its duplicate IDs,
    # oversized masks or exported animation timing.
    def layer(identifier, color, opacity=None):
        found = next(e for e in root if e.get('id') == identifier)
        group = deepcopy(found)
        for parent in list(group.iter()):
            for child in list(parent):
                if child.tag.rsplit('}', 1)[-1] in {'animate', 'animateTransform'}:
                    parent.remove(child)
            for key in ('id', 'mask', 'filter', 'display', 'opacity'):
                parent.attrib.pop(key, None)
            if parent.tag.rsplit('}', 1)[-1] == 'path':
                parent.set('fill', color)
        if opacity is not None:
            group.set('opacity', str(opacity))
        return group

    front = layer('i17', '#243F52')
    # The second contour is the inset outline from the original drawing.
    front_paths = list(front.iter(f'{{{SVG}}}path'))
    front_paths[1].set('fill', '#B98941')
    side = layer('i18', '#B65F76', .7)
    lock = layer('i10', '#52755F')
    for path in lock.iter(f'{{{SVG}}}path'):
        path.set('stroke', '#52755F')
        path.set('stroke-width', '.3')
        path.set('stroke-linejoin', 'round')
    highlights = [layer('i17', '#4C9DB8'), layer('i18', '#E2B66D'), layer('i10', '#B98941')]
    ET.register_namespace('', SVG)
    def xml(element):
        return ET.tostring(element, encoding='unicode').replace(f' xmlns="{SVG}"', '')
    geometry = ''.join(xml(e) for e in (side, front, lock))
    glow = ''.join(xml(e) for e in highlights)
    return f'''<svg xmlns="{SVG}" width="160" height="184" viewBox="0 0 160 184" role="img" aria-labelledby="cg-title cg-desc">
<title id="cg-title">CodeGuardian — animated security shield</title>
<desc id="cg-desc">An angled shield and lock with a slow scanning light, adapted from the supplied native SVG. Motion stops when reduced motion is requested.</desc>
<defs><style>{STYLE}</style>
<linearGradient id="cg-scan-light" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4C9DB8" stop-opacity="0"/><stop offset="1" stop-color="#4C9DB8" stop-opacity=".32"/></linearGradient>
<mask id="cg-scan-mask" x="0" y="0" width="160" height="184" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse"><g class="cg-travel"><rect x="0" y="-26" width="160" height="28" fill="white"/></g></mask>
</defs>
{geometry}
<g class="cg-highlight" mask="url(#cg-scan-mask)">{glow}</g>
<g class="cg-beam"><g class="cg-travel"><rect x="24" y="-24" width="112" height="24" rx="2" fill="url(#cg-scan-light)"/><path d="M24 0H136" stroke="#4C9DB8" stroke-width="1.1" stroke-linecap="round"/></g></g>
</svg>'''


def shield_art(source: Path, x, y, width, height) -> str:
    root = ET.fromstring(adapted_shield(source))
    for key in ('role', 'aria-labelledby'):
        root.attrib.pop(key, None)
    root.set('x', str(x)); root.set('y', str(y))
    root.set('width', str(width)); root.set('height', str(height))
    root.set('viewBox', '24 20 120 145')
    root.set('overflow', 'hidden')
    root.set('aria-hidden', 'true')
    return ET.tostring(root, encoding='unicode')
