#!/usr/bin/env python3
"""Assemble GitHub-supported HTML with descriptive alt text and mobile artwork."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def picture(name, alt, folder='sg', mobile=True):
    src=f'assets/{folder}/{name}'
    source=f'    <source media="(max-width: 600px)" srcset="{src}-mobile.svg"/>\n' if mobile else ''
    return f'  <picture>\n{source}    <img src="{src}.svg" alt="{alt}" width="100%"/>\n  </picture>'


def centered(content):
    return f'<div align="center">\n{content}\n</div>\n'


parts=['<!-- Native SVG artwork. Rebuild with python3 scripts/build_assets.py and scripts/build_readme.py. -->\n']
parts.append(centered(picture('hero','Shrawani Gawade — Developer, with a curious mind. The sentence ending types and erases curious mind, sweet heart, creative spark, cute side and love for little things. A little code. A lot of curiosity.')))
sections=[
    ('dossier', 'About Shrawani', 'dossier', 'I’m Shrawani, an engineering student exploring web development, AI tools and automation. I learn by building interfaces and working demos.'),
    ('equipment', 'My toolkit', 'equipment', 'TypeScript, JavaScript, Java, React, Next.js, Tailwind CSS, HTML, CSS, Node.js and Git.'),
]
for section, title, asset, alt in sections:
    parts.append('<br/>\n'+picture('section-'+section,title)+'\n'+centered(picture(asset,alt)))
parts.append('<br/>\n'+picture('section-contracts','Selected work'))
for i,url,alt in [
    (1,'https://github.com/shrawaniGawade/deepattend','DeepAttend — A webcam attendance demo with face enrollment, student records and an admin dashboard. Next.js, React and TypeScript. Explore repository.'),
    (2,'https://github.com/shrawaniGawade/CodeGuardian','CodeGuardian — A security dashboard prototype and findings API for tracking web application issues. In progress. Next.js, NestJS and TypeScript. Explore repository.'),
]:
    parts.append(centered(f'  <a href="{url}">\n'+picture(f'contract-{i}',alt)+'\n  </a>'))
parts.append('<br/>\n'+picture('section-statistics','The building journal')+'\n'+centered(picture('stats','GitHub public activity: contributions in the last year, public repository count, stars on original public repositories, and primary languages ranked by number of original public repositories. Updated daily; snapshot date is displayed in the graphic.','generated')))
parts.append('<br/>\n'+picture('section-surveillance','A year in bloom — my contribution garden')+'\n'+centered('  <a href="https://github.com/shrawaniGawade?tab=overview">\n'+picture('contribution-garden','A chronological GitHub contribution calendar for the last year. Rose intensity indicates daily contribution activity. A small decorative snake moves across the grid; reduced motion shows the still calendar.','generated')+'\n  </a>'))
parts.append('<br/>\n'+picture('section-contact','Say hello')+'\n'+centered('  <a href="https://github.com/shrawaniGawade">\n'+picture('contact','Explore my work, share an idea, or follow along. Find Shrawani Gawade on GitHub.')+'\n  </a>'))
parts.append('<br/>\n'+centered(picture('divider','',mobile=False)+'\n'+picture('complete','Still learning. Still blooming. Thanks for stopping by my little corner of GitHub. — Shrawani Gawade')))

(ROOT/'README.md').write_text('\n'.join(parts))
print('Built README.md.')
