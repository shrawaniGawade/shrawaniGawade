#!/usr/bin/env python3
"""Optional source conversion: pip install vtracer==1.0.0a4, then run this script.

Normal profile builds use the committed portrait.svg and need only Python itself.
"""
from pathlib import Path
from hashlib import sha256
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG = 'http://www.w3.org/2000/svg'


def main():
    import vtracer

    assets = ROOT / 'assets/sg'
    config = vtracer.Config(
        mode='spline', filter_speckle=6, color_precision=6,
        layer_difference=24, path_precision=2, optimize=2, simplify=0.6,
    )
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / 'portrait.svg'
        config.convert_file(str(assets / 'portrait.png'), str(output))
        root = ET.parse(output).getroot()
        if any(element.tag.rsplit('}', 1)[-1] != 'path' for element in root):
            raise ValueError('Expected only native vector paths from the converter.')
        root.set('viewBox', f"0 0 {root.attrib['width']} {root.attrib['height']}")
        root.set('role', 'img')
        root.set('aria-labelledby', 'portrait-title portrait-desc')
        title = ET.Element(f'{{{SVG}}}title', id='portrait-title')
        title.text = 'Shrawani Gawade — native vector portrait'
        description = ET.Element(f'{{{SVG}}}desc', id='portrait-desc')
        description.text = 'A vector interpretation of the supplied illustrated portrait: Shrawani in an ivory and rose sari beside an ornate gate under a blue sky. Drawn entirely with colored SVG paths.'
        root.insert(0, title)
        root.insert(1, description)
        # Preserve the original portrait's tiny bindi, below the trace's speckle threshold.
        # Do not apply this image-specific detail if the source is replaced later.
        if sha256((assets / 'portrait.png').read_bytes()).hexdigest() == '11582df9b251bef27c9f13970962fe97782741db01232d112d8af4228e1bdb72':
            ET.SubElement(root, f'{{{SVG}}}ellipse', cx='474.7', cy='508.4', rx='1.9', ry='3.1', fill='#9c2233')
            ET.SubElement(root, f'{{{SVG}}}ellipse', cx='474.7', cy='509', rx='1.3', ry='2', fill='#721e2d')
        ET.register_namespace('', SVG)
        ET.ElementTree(root).write(assets / 'portrait.svg', encoding='unicode')
        paths = sum(element.tag == f'{{{SVG}}}path' for element in root)
        print(f'Wrote native portrait with {paths:,} SVG paths.')


if __name__ == '__main__':
    main()
