"""Bounded homepage update: publish an existing owner-selected portrait, not a new generation."""
from pathlib import Path
import hashlib, io, json, os, re, subprocess, urllib.request
from urllib.parse import quote
from PIL import Image
from bs4 import BeautifulSoup

root=Path('.')
original=Path('index.html').read_text()
expected='e474afd4df5476dfdd9146c46ae1619974f9732b'
if subprocess.check_output(['git','hash-object','index.html'],text=True).strip()!=expected:
    raise SystemExit('Homepage changed since review; stopping before overwriting concurrent work.')
if Path('CNAME').read_text().strip()!='jordanmccarthy.com':
    raise SystemExit('Unexpected publication destination.')

with urllib.request.urlopen(os.environ['PORTRAIT_SOURCE'],timeout=45) as response:
    raw=response.read(15000000)
im=Image.open(io.BytesIO(raw)).convert('RGB')
if im.width<1000 or im.height<1250 or not 0.78<im.width/im.height<0.82:
    raise SystemExit('Unexpected source dimensions; refusing a substitute image.')
# Crop only; facial expression, anatomy, lighting and background are the existing approved edit.
margin=round(im.width*.12)
w=im.width-2*margin
crop_h=round(w*1.25)
top=round(im.height*.12)
if top+crop_h>im.height:
    raise SystemExit('Invalid crop bounds.')
portrait=im.crop((margin,top,margin+w,top+crop_h)).resize((800,1000),Image.Resampling.LANCZOS)
portrait.save('assets/portrait-editorial-lake.jpg',quality=93,optimize=True)
portrait.save('assets/portrait-editorial-lake.webp',quality=91,method=6)
portrait.resize((400,500),Image.Resampling.LANCZOS).save('assets/portrait-editorial-lake-400.webp',quality=90,method=6)

email_match=re.search(r'mailto:([^?"<>]+)',original)
if not email_match:
    raise SystemExit('No existing contact destination to preserve.')
email=email_match.group(1)
research_mail='mailto:'+email+'?subject='+quote('Research conversation | jordanmccarthy.com')+'&amp;body='+quote('Hello Jordan,\n\nMy research question is: \nOrganism or system: \nThe measurement or collaboration I have in mind: \n\nBest,\n')
seminar_mail='mailto:'+email+'?subject='+quote('Seminar invitation | jordanmccarthy.com')+'&amp;body='+quote('Hello Jordan,\n\nWe would like to invite you to speak.\nAudience and institution: \nProposed date or window: \nTopic of interest: \n\nBest,\n')
hero='''<section class="hero" aria-labelledby="hero-title">
<div class="hero-identity" data-attention-region="identity">
<p class="hero-name">Jordan McCarthy</p><p class="eyebrow">PhD researcher · Barral laboratory · ETH Zürich</p>
<h1 id="hero-title"><span>How cells age.</span><span>Why RNA <em>matters.</em></span></h1>
</div>
<figure class="portrait-mount" data-attention-region="portrait">
<div class="portrait-paper"><div class="portrait-frame"><picture><source type="image/webp" srcset="assets/portrait-editorial-lake-400.webp 400w, assets/portrait-editorial-lake.webp 800w" sizes="(max-width:760px) 43vw, (max-width:1050px) 38vw, 405px"><img src="assets/portrait-editorial-lake.jpg" alt="Digitally edited portrait of Jordan McCarthy beside a lake at sunset" width="800" height="1000" fetchpriority="high" decoding="async"></picture></div></div>
<figcaption class="portrait-caption"><span class="portrait-caption-name">Jordan McCarthy</span><span>Digitally edited portrait</span></figcaption>
</figure>
<p class="hero-copy" data-attention-region="research-question">I study <strong>how cells keep unfinished RNA inside the nucleus</strong>, and how that quality control changes with age. At ETH Zürich, I connect single-cell microscopy with molecular measurements in aging yeast.</p>
<div class="hero-actions" data-attention-region="primary-action"><a class="action-primary" href="#work">Explore the research <span aria-hidden="true">↓</span></a><a class="text-link" href="#contact">Get in touch <span aria-hidden="true">↗</span></a></div>
<a class="hero-proof" href="#work" data-attention-region="published-proof"><span class="hero-proof-label">eLife · 2025</span><span><span class="proof-title">Nuclear basket, RNA leakage &amp; chromosome loss</span>Co-author · View the published study and my contribution.</span></a>
</section>'''
h,n=re.subn(r'<section class="hero"[^>]*>.*?</section>',lambda m:hero,original,count=1,flags=re.S)
if n!=1: raise SystemExit('Hero anchor not found.')
h=h.replace('https://jordanmccarthy.com/assets/portrait-lake-sunset.jpg','https://jordanmccarthy.com/assets/portrait-editorial-lake.jpg')
h=h.replace('content="Portrait of Jordan McCarthy"','content="Digitally edited portrait of Jordan McCarthy"')
h=h.replace('</head>','<link rel="stylesheet" href="assets/attention-layout.css?v=20260927-1">\n</head>',1)
nav='''<nav class="navlinks" id="navigation" aria-label="Main navigation"><a href="#work">Research</a><a href="#methods">Methods</a><a href="#about">About</a><a class="nav-contact" href="#contact">Contact <span aria-hidden="true">↗</span></a></nav>'''
h,n=re.subn(r'<nav class="navlinks"[^>]*>.*?</nav>',lambda m:nav,h,count=1,flags=re.S)
if n!=1: raise SystemExit('Navigation anchor not found.')
h=h.replace('<button class="menu-toggle"','<a class="header-contact" href="#contact">Contact <span aria-hidden="true">↗</span></a>\n<button class="menu-toggle"',1)

work_match=re.search(r'<section class="work" id="work".*?</section>',h,re.S)
if not work_match: raise SystemExit('Published work section missing.')
work=work_match.group()
h=h[:work_match.start()]+h[work_match.end():]
work=work.replace('<span class="section-number">03</span>','<span class="section-number">01</span>',1)
next_step='''<div class="evidence-next"><p>Working on RNA quality control or cellular aging? Tell me the question you are trying to answer.</p><a class="text-link" href="#contact">Discuss a research question <span aria-hidden="true">↗</span></a></div>'''
if not work.endswith('</div></section>'): raise SystemExit('Unexpected work wrapper.')
work=work[:-len('</div></section>')]+next_step+'\n</div></section>'
anchor='<section class="research" id="research"'
if h.count(anchor)!=1: raise SystemExit('Research insertion point missing.')
h=h.replace(anchor,'</div>\n'+work+'\n<div class="wrap">\n'+anchor,1)
h=h.replace('<span class="section-number">01</span> The questions','<span class="section-number">02</span> The questions',1)
h=h.replace('<span class="section-number">02</span> How I do the work','<span class="section-number">03</span> How I do the work',1)

contact='''<section class="contact" id="contact" aria-labelledby="contact-title" data-attention-region="contact">
<p class="section-label"><span class="section-number">05</span> In conversation</p>
<div><h2 id="contact-title">Have a question worth<br>working on together?</h2><p>For research collaborations, methods discussions and seminar invitations, start with the question you have in mind.</p>
<div class="contact-options">
<article class="contact-option"><h3>Research &amp; methods</h3><p>Tell me your biological question, the organism you work on, and the measurement that is difficult today.</p><a class="action-primary" href="RESEARCH_MAIL">Discuss a research question <span aria-hidden="true">↗</span></a></article>
<article class="contact-option"><h3>Talks &amp; seminars</h3><p>Tell me about the audience, the proposed date and the scientific questions they would like to explore.</p><a class="text-link" href="SEMINAR_MAIL">Invite me to speak <span aria-hidden="true">↗</span></a></article>
</div><p class="contact-direct">Prefer a blank email? <a href="mailto:EMAIL">EMAIL</a></p>
</div></section>'''.replace('RESEARCH_MAIL',research_mail).replace('SEMINAR_MAIL',seminar_mail).replace('EMAIL',email)
h,n=re.subn(r'<section class="contact"[^>]*>.*?</section>',lambda m:contact,h,count=1,flags=re.S)
if n!=1: raise SystemExit('Contact section anchor missing.')
old='The portrait is a personal photograph provided by Jordan McCarthy, cropped for this page. No generated likenesses are used.'
new='The homepage portrait was digitally edited using owner-provided photographs, including changes to expression, clothing silhouette and background. It is not an unaltered documentary photograph.'
if old not in h: raise SystemExit('Portrait attribution differs from reviewed source.')
h=h.replace(old,new,1)

# The scientific content and existing research media are not part of this edit.
for section in ['research','methods','about']:
    p=r'<section[^>]*id="'+section+r'"[^>]*>.*?</section>'
    before=re.search(p,original,re.S).group()
    after=re.search(p,h,re.S).group()
    strip=lambda s:re.sub(r'<span class="section-number">\d+</span>','',s)
    if strip(before)!=strip(after): raise SystemExit('Protected content changed: '+section)
for p in [r'<article class="paper">.*?</article>',r'<p class="work-description">.*?</p>']:
    if re.search(p,original,re.S).group()!=re.search(p,h,re.S).group():
        raise SystemExit('Published study text changed unexpectedly.')
soup=BeautifulSoup(h,'html.parser')
ids=[x['id'] for x in soup.select('[id]')]
if len(ids)!=len(set(ids)): raise SystemExit('Duplicate HTML IDs.')
for a in soup.select('a[href^="#"]'):
    if a['href'][1:] not in ids: raise SystemExit('Broken anchor '+a['href'])
if len(soup.select('.hero .action-primary'))!=1: raise SystemExit('Expected one primary hero action.')
if soup.select('.about-photo') or 'No generated likenesses' in h: raise SystemExit('Stale portrait content.')
if any(x in h for x in ['getUserMedia','webgazer','sessionReplay','honey trap','HEARTH']):
    raise SystemExit('Unexpected tracking or private strategy content.')
Path('index.html').write_text(h)
notes=Path('WEBSITE-NOTES.md')
notes.write_text(notes.read_text()+'''\n\n## Editorial portrait and attention layout\nThe owner requested publication of the existing digitally edited lake portrait. No new likeness was generated in this release. The crop and web encoding are derived from that existing edit. The current attribution replaces the earlier unedited-photograph statement.\nThe opening groups identity, portrait, research question, one primary research action, and a compact publication link. Published evidence now precedes the longer research and methods sections. Contact offers a research/methods route and a seminar route.\nThis is research-informed visual hierarchy, not measured eye tracking. No camera access, visitor gaze collection, sexual profiling, session replay, remote analytics, or automatic scrolling is added. data-attention-region attributes are labels for possible future consent-based usability studies, not tracking code.\nSources: Hutton & Nolte (2011), DOI 10.1002/acp.1763; Simola et al. (2014), DOI 10.3389/fpsyg.2014.00166; Jones et al. (2006), DOI 10.1111/j.1467-9280.2006.01749.x; Bolmont et al. (2014), DOI 10.1177/0956797614539706; W3C WCAG 2.2. These findings do not validate this site's conversion performance.\n''')
manifest=json.loads(Path('release-checksums.json').read_text())
for name in ['index.html','WEBSITE-NOTES.md','assets/attention-layout.css','assets/portrait-editorial-lake.jpg','assets/portrait-editorial-lake.webp','assets/portrait-editorial-lake-400.webp']:
    manifest[name]=hashlib.sha256(Path(name).read_bytes()).hexdigest()
Path('release-checksums.json').write_text(json.dumps(manifest,indent=2))
Path('_review').mkdir(exist_ok=True)
Path('_review/implementation.json').write_text(json.dumps({'source_image_pixels':im.size,'web_portrait_pixels':[800,1000],'html_sha256':manifest['index.html'],'research_text_unchanged':True,'camera_or_remote_analytics_added':False,'eye_tracking_observations':0,'contact_destination_preserved':email,'intended_path':['portrait and identity','research question','published evidence','contact']},indent=2))
print(Path('_review/implementation.json').read_text())
