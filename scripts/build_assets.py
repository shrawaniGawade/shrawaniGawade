#!/usr/bin/env python3
"""Rebuild the original, self-contained profile artwork. Python standard library only."""
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'sg'
P = dict(paper='#FFF9EF', ink='#243F52', rose='#B65F76', muted='#596A70', sky='#DCEFF6', gold='#B98941', green='#52755F', blush='#F4E2DF', line='#DDCDBB')

# Animate decorative layers only. The portrait, typography and data stay still.
MOTION = '''
.breeze{transform-origin:0 150px;animation:breeze 9s ease-in-out infinite}
.petals{transform-origin:0 0;animation:petals 8s cubic-bezier(.45,0,.25,1) infinite}
.flower-core{transform-origin:0 0;animation:flower-core 8s ease-in-out infinite}
.arch-glint{opacity:0;animation:arch-glint 16s ease-in-out infinite}
.sun-dust{opacity:.35;animation:sun-dust 10s ease-in-out infinite}
.sun-dust.late{animation-delay:-4s}
.sun-dust.later{animation-delay:-7s}
.scan-light{opacity:0;animation:scan-light 8s ease-in-out infinite}
.scan-frame{stroke:#B98941;animation:scan-frame 8s ease-in-out infinite}
.scan-success{transform-origin:0 0;animation:scan-success 8s ease-in-out infinite}
.check-stroke{stroke-dasharray:100;stroke-dashoffset:0;animation:check-stroke 8s ease-in-out infinite}
.success-halo{transform-origin:0 0;opacity:0;animation:success-halo 8s ease-out infinite}
.shield-light{opacity:0;animation:shield-light 11s ease-in-out infinite}
@keyframes breeze{0%,100%{transform:rotate(-2deg)}50%{transform:rotate(2deg)}}
@keyframes petals{0%,12%,100%{transform:rotate(-14deg) scale(.24);opacity:.65}40%{transform:rotate(2deg) scale(1.04);opacity:1}48%,64%{transform:rotate(0deg) scale(1);opacity:1}90%{transform:rotate(-14deg) scale(.24);opacity:.65}}
@keyframes flower-core{0%,12%,90%,100%{transform:scale(.72)}40%,64%{transform:scale(1)}}
@keyframes arch-glint{0%,8%{stroke-dashoffset:100;opacity:0}16%{opacity:.8}64%{stroke-dashoffset:0;opacity:.8}72%,100%{stroke-dashoffset:0;opacity:0}}
@keyframes sun-dust{0%,100%{transform:translateY(0);opacity:.2}50%{transform:translateY(-12px);opacity:.7}}
@keyframes scan-light{0%,8%{transform:translateY(0);opacity:0}12%{opacity:.7}40%{transform:translateY(60px);opacity:.7}46%,100%{transform:translateY(60px);opacity:0}}
@keyframes scan-frame{0%,46%,100%{stroke:#B98941}56%,84%{stroke:#52755F}}
@keyframes scan-success{0%,48%,90%,100%{transform:scale(.65);opacity:0}56%{transform:scale(1.08);opacity:1}62%,83%{transform:scale(1);opacity:1}}
@keyframes check-stroke{0%,55%,94%,100%{stroke-dashoffset:100}66%,92%{stroke-dashoffset:0}}
@keyframes success-halo{0%,51%{transform:scale(.9);opacity:0}55%{transform:scale(1);opacity:.35}73%,100%{transform:scale(1.65);opacity:0}}
@keyframes shield-light{0%,15%{stroke-dashoffset:100;opacity:0}24%{opacity:.65}70%{stroke-dashoffset:0;opacity:.65}80%,100%{stroke-dashoffset:0;opacity:0}}
@media(prefers-reduced-motion:reduce){.breeze,.petals,.flower-core,.arch-glint,.sun-dust,.scan-light,.scan-frame,.scan-success,.check-stroke,.success-halo,.shield-light{animation:none!important}}
'''


def text(x, y, value, size=24, color='ink', font='body', extra=''):
    return f'<text x="{x}" y="{y}" class="{font}" font-size="{size}" fill="{P.get(color, color)}" {extra}>{escape(value)}</text>'


def flower(x, y, scale=1, color='rose', motion=False, delay=0):
    petals = ''.join(f'<ellipse cx="0" cy="-16" rx="7" ry="13" transform="rotate({a})"/>' for a in range(0, 360, 60))
    core = f'<circle r="5" fill="{P["gold"]}" stroke="none"/>'
    if motion:
        petals = f'<g class="petals" style="animation-delay:{delay}s">{petals}</g>'
        core = f'<g class="flower-core" style="animation-delay:{delay}s">{core}</g>'
    return f'<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="{P[color]}" stroke-width="1.5">{petals}{core}</g>'


def sprig(x, y, scale=1, motion=False):
    return f'''<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="{P['green']}" stroke-width="2.5" stroke-linecap="round">
    <g{(' class="breeze"' if motion else '')}>
    <path d="M0 150 Q12 80 64 0"/><path d="M20 92 Q-19 72 -8 47 Q28 53 20 92Z" fill="{P['green']}" opacity=".22"/>
    <path d="M32 63 Q70 66 79 34 Q47 26 32 63Z" fill="{P['green']}" opacity=".22"/>
    <path d="M46 33 Q26 4 42 -14 Q67 2 46 33Z" fill="{P['green']}" opacity=".22"/></g></g>'''


def arch_glint(path):
    return f'<path d="{path}" class="arch-glint" pathLength="100" stroke-dasharray="9 91" fill="none" stroke="#FFE1A2" stroke-width="3" stroke-linecap="round"/>'


def dust(x, y, delay=''):
    return f'<g transform="translate({x} {y})"><g class="sun-dust {delay}" fill="#B98941"><path d="M0 -6Q1 -1 6 0Q1 1 0 6Q-1 1 -6 0Q-1 -1 0 -6Z"/><circle cx="12" cy="-16" r="1.6"/></g></g>'


def portrait_art(x, y, width, height):
    """Inline real vector geometry; no SVG image element or bitmap payload."""
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    root = ET.parse(OUT / 'portrait.svg').getroot()
    for element in root.iter():
        if element.tag.rsplit('}', 1)[-1] in {'image', 'foreignObject', 'script'}:
            raise ValueError('The portrait must contain native SVG geometry only.')
    viewbox = escape(root.attrib['viewBox'], quote=True)
    markup = ET.tostring(root, encoding='unicode')
    geometry = markup.partition('>')[2].rsplit('</svg>', 1)[0]
    return f'<g clip-path="url(#portrait)"><svg x="{x}" y="{y}" width="{width}" height="{height}" viewBox="{viewbox}" preserveAspectRatio="xMidYMid slice" overflow="hidden" aria-hidden="true">{geometry}</svg></g>'


def svg(name, w, h, body, title, desc='', bg='paper', defs=''):
    OUT.mkdir(parents=True, exist_ok=True)
    style = '.body{font-family:Trebuchet MS,Arial,sans-serif}.display{font-family:Georgia,Times New Roman,serif}.mono{font-family:Courier New,monospace}'
    if any(f'class="{name}' in body for name in ('breeze','petals','arch-glint','sun-dust','scan-light','shield-light')):
        style += MOTION
    source = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc or title)}</desc>
<defs><style>{style}</style>{defs}</defs>
<rect width="{w}" height="{h}" rx="24" fill="{P[bg]}"/>
{body}
</svg>\n'''
    (OUT / name).write_text(source)


def pill(x, y, value, w, color='ink', bg='paper', size=22):
    return f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="22" fill="{P[bg]}"/>' + text(x+w/2,y+29,value,size,color,extra='text-anchor="middle"')


def hero(mobile=False):
    if mobile:
        w,h=600,930
        clip='<clipPath id="portrait"><path d="M310 905V571A128 128 0 0 1 566 571V905Z"/></clipPath>'
        body = text(38,60,'Hello, I’m',27,'muted') + text(34,147,'Shrawani',78,font='display') + text(35,233,'Gawade.',78,font='display')
        body += text(38,291,'Developer, with a curious mind.',25)
        body += text(38,347,'Exploring web, AI & automation.',24,'muted')
        body += '<path d="M38 390H560" stroke="#DDCDBB"/>'
        body += portrait_art(276,438,315,510)
        arch='M301 905V571A137 137 0 0 1 575 571V905'
        body += f'<path d="{arch}" fill="none" stroke="#B98941" stroke-width="1.2"/>'+arch_glint(arch)
        body += text(38,476,'A little code.',30,font='display')+text(38,518,'A lot of',30,font='display')+text(38,560,'curiosity.',30,font='display')
        body += sprig(63,677,1,True)+flower(128,660,.75,motion=True)+flower(64,720,.5)
        body += dust(266,657,'late')
        body += text(38,870,'@shrawaniGawade',21,'muted')
        svg('hero-mobile.svg',w,h,body,'Shrawani Gawade — developer exploring web, AI and automation',defs=clip)
        return
    clip='<clipPath id="portrait"><path d="M575 555V228A182 182 0 0 1 939 228V555Z"/></clipPath>'
    body = '<path d="M554 0H976Q1000 0 1000 24V615H554Z" fill="#DCEFF6"/>'
    body += portrait_art(560,40,395,530)
    body += '<path d="M564 555V228A193 193 0 0 1 950 228V555" fill="none" stroke="#B98941" stroke-width="1.5"/>'
    body += arch_glint('M564 555V228A193 193 0 0 1 950 228V555')
    body += text(48,66,'Hello, I’m',23,'muted')+text(44,165,'Shrawani',84,font='display')+text(46,261,'Gawade.',84,font='display')
    body += text(50,326,'Developer, with a curious mind.',25)
    body += text(50,372,'Exploring web, AI & automation.',23,'muted')
    body += '<path d="M50 411H477" stroke="#DDCDBB"/>'
    body += text(50,457,'A little code. A lot of curiosity.',24,font='display')+text(50,520,'@shrawaniGawade',21,'muted')
    body += flower(499,69,.60,motion=True)+flower(964,492,.6,motion=True,delay=-3)
    body += dust(973,188)+dust(568,382,'late')+dust(962,365,'later')
    body += '<path d="M0 591H1000V616Q1000 640 976 640H24Q0 640 0 616Z" fill="#243F52"/>'
    for x,label in [(48,'Thoughtful interfaces'),(365,'Creative experiments'),(695,'Learning by making')]:
        body+=text(x,622,label,21,'paper')
    svg('hero.svg',1000,640,body,'Shrawani Gawade — developer exploring web, AI and automation','An illustrated portrait of Shrawani, framed by sky blue, sari rose and antique gold.',defs=clip)


def section(name, heading, note):
    body = flower(30,43,.52) + text(60,54,heading,34,font='display')
    body += text(962,53,note,19,'muted',extra='text-anchor="end"')
    svg(f'section-{name}.svg',1000,86,body,heading)
    svg(f'section-{name}-mobile.svg',600,82,flower(27,41,.48)+text(57,53,heading,34,font='display'),heading)


def about(mobile=False):
    if mobile:
        body=text(32,57,'A little about me',34,font='display')
        for y,line in [(110,'I’m Shrawani, an engineering student'),(144,'exploring web development, AI tools'),(178,'and automation.')]:body+=text(32,y,line,24)
        for y,line in [(240,'I learn by building: turning ideas into'),(274,'interfaces, testing what works, and'),(308,'improving one detail at a time.')]:body+=text(32,y,line,24,'muted')
        body+='<path d="M32 345H568" stroke="#DDCDBB"/>'
        body+=text(32,394,'Currently exploring',24,'rose')
        body+=text(32,436,'Web apps · AI tools · Automation',23)
        svg('dossier-mobile.svg',600,479,body,'About Shrawani Gawade')
        return
    body=text(44,64,'Curiosity is where it starts.',36,font='display')
    for y,line in [(116,'I’m Shrawani, an engineering student exploring'),(150,'web development, AI tools and automation.'),(207,'I learn by building: turning ideas into interfaces,'),(241,'testing what works, and improving as I go.')]:body+=text(44,y,line,23,'muted')
    body+='<path d="M646 44V275" stroke="#DDCDBB"/>'
    body+=text(681,82,'My creative corner',26,font='display')
    for y,v in [(132,'Thoughtful web experiences'),(178,'AI & automation experiments'),(224,'Small ideas, working demos')]:
        body+=f'<circle cx="688" cy="{y-7}" r="4" fill="#B65F76"/>'+text(706,y,v,20)
    svg('dossier.svg',1000,310,body,'About Shrawani Gawade','Engineering student exploring web development, AI tools and automation. Learning by building interfaces and demos.')


def equipment(mobile=False):
    w=600 if mobile else 1000
    if mobile:
        body=text(32,56,'Tools I build with',34,font='display')
        rows=[('Languages',['TypeScript','JavaScript','Java']),('Interface',['React','Next.js','Tailwind CSS']),('Foundations',['HTML & CSS','Node.js','Git'])]
        for i,(label,items) in enumerate(rows):
            y=94+i*130
            body+=text(32,y+18,label,23,'muted')
            x=32
            for item in items:
                pw=len(item)*12+30
                body+=pill(x,y+38,item,pw,bg='sky',size=22);x+=pw+10
        svg('equipment-mobile.svg',w,486,body,'Toolkit: TypeScript, JavaScript, Java, React, Next.js, Tailwind CSS, HTML, CSS, Node.js and Git')
        return
    body=text(44,62,'From a first idea to a working interface.',32,font='display')
    rows=[('Languages',['TypeScript','JavaScript','Java']),('Interface',['React','Next.js','Tailwind CSS','HTML & CSS']),('Foundations',['Node.js','Git'])]
    for i,(label,items) in enumerate(rows):
        y=95+i*67
        body+=text(44,y+29,label,23,'muted')
        x=243
        for item in items:
            pw=len(item)*12+32
            body+=pill(x,y,item,pw,bg='sky' if i!=1 else 'blush');x+=pw+12
    svg('equipment.svg',w,323,body,'Toolkit: TypeScript, JavaScript, Java, React, Next.js, Tailwind CSS, HTML, CSS, Node.js and Git')


def project_illustration(which,x,y,scale=1):
    body = f'<g transform="translate({x} {y}) scale({scale}) translate(-735 -34)">'
    if which==1:
        body+='<rect x="735" y="34" width="223" height="166" rx="16" fill="#DCEFF6"/><rect x="754" y="53" width="185" height="126" rx="10" fill="#FFF9EF"/>'
        body+='<g class="scan-frame" stroke="#B98941" stroke-width="2.5" fill="none"><path d="M775 88V74H790M918 88V74H903M775 142V157H790M918 142V157H903"/></g><circle cx="846" cy="105" r="18" fill="#B65F76" opacity=".7"/><path d="M816 147Q846 112 876 147" fill="#B65F76" opacity=".7"/>'
        body+='<path class="scan-light" d="M789 84H903" stroke="#52755F" stroke-width="2" stroke-linecap="round"/>'
        body+='<g transform="translate(902 153)"><circle class="success-halo" r="17" fill="none" stroke="#52755F" stroke-width="1.5"/><g class="scan-success"><circle r="17" fill="#52755F"/><path class="check-stroke" d="M-8 0L-2 6L9 -7" pathLength="100" fill="none" stroke="#FFF9EF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g></g>'
    else:
        shield='M846 60L895 78V117Q892 147 846 173Q800 147 797 117V78Z'
        body+='<rect x="735" y="34" width="223" height="166" rx="16" fill="#F4E2DF"/>'
        body+=f'<path d="{shield}" fill="#FFF9EF" stroke="#B98941" stroke-width="2"/><path class="shield-light" d="{shield}" pathLength="100" stroke-dasharray="26 74" fill="none" stroke="#B65F76" stroke-width="3" stroke-linecap="round"/>'
        body+='<g stroke="#243F52" stroke-width="3" stroke-linecap="round" fill="none"><path d="M838 101L825 115L838 129M855 101L868 115L855 129"/></g>'
    return body+'</g>'


def project(which,mobile=False):
    first=which==1
    title='DeepAttend' if first else 'CodeGuardian'
    category='Attendance demo' if first else 'Security dashboard prototype'
    lines=['A webcam attendance demo with face enrollment,','student records and an admin dashboard.'] if first else ['A dashboard and findings API for tracking','web application issues. A work in progress.']
    tech='Next.js / React / TypeScript' if first else 'Next.js / NestJS / TypeScript'
    if mobile:
        body=text(32,54,category,23,'rose')+text(30,112,title,48,font='display')
        ml=['A webcam attendance demo with face','enrollment, student records and an','admin dashboard.'] if first else ['A dashboard and findings API for','tracking web application issues.','A work in progress.']
        for i,l in enumerate(ml):body+=text(32,172+i*35,l,24,'muted')
        body+=text(32,302,tech,22)+pill(32,337,'Explore repository',234,bg='ink',color='paper',size=22)
        body+=project_illustration(which,468,330,.4)
        svg(f'contract-{which}-mobile.svg',600,416,body,title+' — '+category)
        return
    body=text(42,56,category,22,'rose')+text(40,117,title,48,font='display')
    for i,l in enumerate(lines):body+=text(42,164+i*34,l,23,'muted')
    body+=text(42,248,tech,21)+pill(735,229,'Explore repository',223,bg='ink',color='paper',size=21)
    body+=project_illustration(which,735,34)
    svg(f'contract-{which}.svg',1000,301,body,title+' — '+category,' '.join(lines)+' Built with '+tech+'. Select this card to explore the repository.')


def finishing():
    body=text(44,63,'Good things start with a conversation.',35,font='display')+text(44,113,'Explore my work, share an idea, or follow along on GitHub.',23,'muted')
    body+=pill(44,148,'Find me on GitHub',247,bg='ink',color='paper',size=22)+sprig(850,55,.8,True)+flower(901,51,.65,motion=True)
    svg('contact.svg',1000,238,body,'Connect with Shrawani Gawade on GitHub')
    body=text(32,58,'Let’s connect.',37,font='display')+text(32,108,'Explore my work, share an idea,',24,'muted')+text(32,143,'or follow along on GitHub.',24,'muted')+pill(32,179,'Find me on GitHub',247,bg='ink',color='paper',size=22)
    svg('contact-mobile.svg',600,260,body,'Connect with Shrawani Gawade on GitHub')
    body='<path d="M40 38H454M546 38H960" stroke="#DDCDBB"/>'+flower(500,38,.8,motion=True)
    svg('divider.svg',1000,76,body,'A rose flower divider')
    body=text(500,61,'Still learning. Still blooming.',40,font='display',extra='text-anchor="middle"')+text(500,111,'Thanks for stopping by my little corner of GitHub.',22,'muted',extra='text-anchor="middle"')+text(500,158,'Shrawani Gawade',24,'rose',font='display',extra='text-anchor="middle"')
    svg('complete.svg',1000,198,body,'Still learning. Still blooming. Thanks for visiting Shrawani Gawade’s GitHub.')
    body=text(300,55,'Still learning. Still blooming.',32,font='display',extra='text-anchor="middle"')+text(300,102,'Thanks for stopping by.',23,'muted',extra='text-anchor="middle"')+text(300,146,'Shrawani Gawade',24,'rose',font='display',extra='text-anchor="middle"')
    svg('complete-mobile.svg',600,188,body,'Still learning. Still blooming. Thanks for visiting Shrawani Gawade’s GitHub.')


def main():
    for m in [False,True]:
        hero(m); about(m); equipment(m); project(1,m); project(2,m)
    for args in [('dossier','The person behind the pixels','A little about me'),('equipment','My toolkit','Things I build with'),('contracts','Selected work','Ideas taking shape'),('statistics','The building journal','Progress, one commit at a time'),('surveillance','A year in bloom','My contribution garden'),('contact','Say hello','Let’s connect')]:section(*args)
    finishing()
    print(f'Built {len(list(OUT.glob("*.svg")))} SVG assets.')


if __name__ == '__main__':main()
