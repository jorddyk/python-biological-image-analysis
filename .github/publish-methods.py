"""One-time content migration for the owner-approved public methods page.
No private records, scientific results, strategy documents or credentials belong here.
"""
from pathlib import Path
import hashlib, json, subprocess

base = Path('index.html')
if subprocess.check_output(['git', 'hash-object', 'index.html'], text=True).strip() != '7c86cbfc614341fa457482a8dd6232338aa29834':
    raise SystemExit('Site changed since review; refusing to overwrite concurrent edits.')
if Path('CNAME').read_text().strip() != 'jordanmccarthy.com':
    raise SystemExit('Unexpected domain; stopping.')
for name in ['aging-chip.jpg', 'mad-setup.jpg', 'mad-controls.jpg']:
    if not Path('assets', name).is_file():
        raise SystemExit('Approved image missing: ' + name)
h = base.read_text()
h = h.replace('https://jorddyk.github.io/python-biological-image-analysis/', 'https://jordanmccarthy.com/')
h = h.replace('<a href="#research">Research</a><a href="#work">Selected work</a>', '<a href="#research">Research</a><a href="#methods">Methods</a><a href="#work">Selected work</a>', 1)
h = h.replace('<div><p class="eyebrow">ETH Zürich / Barral Laboratory</p>', '<div><p class="eyebrow">Jordan McCarthy · PhD researcher · ETH Zürich</p>', 1)
h = h.replace('I’m Jordan, a biochemist studying <strong>how cells keep unfinished RNA in the nucleus</strong>, and what changes when that quality-control system fails with age.', 'I study <strong>how RNA quality control changes as yeast cells age</strong>. In the Barral laboratory at ETH Zürich, I combine single-cell microscopy with experiments that collect aging cells for molecular analysis.', 1)
h = h.replace('href="#research">The questions', 'href="#methods">See the experiments', 1)
h = h.replace('Budding yeast provides a way to connect molecular mechanisms to the life of an individual cell.', 'A mother yeast cell produces successive daughters. The number it produces over its lifetime is its replicative lifespan. This gives us a way to connect molecular changes to a cell’s life history, and to test mechanisms in a well-understood organism.', 1)
primer = '''<details class="science-primer"><summary>New to RNA biology? Start here.</summary><p>RNA carries genetic instructions from DNA toward the machinery that makes proteins. Many newly made RNA messages contain segments called introns, which are normally removed by a process called splicing. Cells also control which messages can leave the nucleus.</p><p>I study how this processing and quality control change with age. The immediate aim is to understand mechanisms of aging in budding yeast. Whether a finding applies to human aging is a separate experimental question.</p></details>'''
h = h.replace('<div class="questions">', primer + '\n<div class="questions">', 1)
h = h.replace('When does a molecular change become a phenotype?', 'When does a molecular change affect the cell?', 1)
methods = '''
<section class="methods" id="methods" aria-labelledby="methods-title">
<div class="section-heading"><p class="section-label"><span class="section-number">02</span> How I do the work</p><div><h2 id="methods-title">Two views of the same problem.<br>A cell’s life. Its molecular state.</h2><p class="section-description">One approach follows the life of an individual cell. The other collects aging cells in sufficient numbers to measure their molecules. Together, they let us study aging at two different scales.</p></div></div>
<div class="methods-grid">
<article class="method-card"><figure><div class="method-image"><img src="assets/aging-chip.jpg" width="1024" height="1024" alt="Yeast cells held in an array of curved microfluidic traps" loading="lazy" decoding="async"></div><figcaption>Microscopy inside an aging chip. The curved structures hold yeast cells in place so they can be followed over time.</figcaption></figure><p class="method-eyebrow">The life of one cell</p><h3>Watch a cell grow old.</h3><p>Microfluidic traps keep mother cells in view while fresh medium flows through the chip. Repeated imaging lets us follow divisions and changes within cells, instead of comparing isolated snapshots.</p><p class="method-purpose"><strong>The question:</strong> How does a cell change as it produces successive daughters, and what changes its replicative lifespan?</p></article>
<article class="method-card"><figure><div class="method-image"><img src="assets/mad-setup.jpg" width="1200" height="1600" alt="MAD bioreactor setup with a glass culture tube inside a magnet rack, connected to media and pumps" loading="lazy" decoding="async"></div><figcaption>MAD bioreactor setup in the Barral laboratory. The tube, magnetic rack and pumps allow aging mother cells to be retained in flowing culture.</figcaption></figure><p class="method-eyebrow">The molecules of a population</p><h3>Collect aging cells.<br>Measure what changes.</h3><p>The Miniature-chemostat Aging Device, or MAD, retains magnetically labelled yeast cells while their daughters are washed away. This provides aging cell populations for RNA measurements and other molecular analyses.</p><p class="method-purpose"><strong>The question:</strong> Which molecular features differ between younger and older cell populations?</p></article>
</div>
<div class="method-attribution"><p>I learned the MAD approach with the Caudron laboratory in Montpellier and worked with the ETH workshop on our laboratory implementation. With thanks to <strong>Remo Zangger and Daniel Smith</strong> for the setup, and to <strong>Sung Sik Lee</strong> for the aging-chip platform. MAD was introduced by <a href="https://doi.org/10.7554/eLife.39911">Hendrickson and colleagues, eLife (2018)</a>.</p><details><summary>Inside the setup: pumps, controls and image sources</summary><figure class="controls-photo"><img src="assets/mad-controls.jpg" width="1200" height="1600" alt="Close-up of the MAD pump and its control equipment" loading="lazy" decoding="async"><figcaption>Pump and control equipment used in the MAD setup.</figcaption></figure><p>The microscopy frame and apparatus photographs are from slides 39, 48 and 49 of my 26 September 2025 lab presentation. The presentation date is not the acquisition date. These images illustrate the methods rather than a quantitative experimental comparison.</p></details></div>
</section>
'''
needle = '</div>\n<section class="work" id="work"'
if needle not in h:
    raise SystemExit('Expected insertion anchor missing.')
h = h.replace(needle, methods + '\n' + needle, 1)
h = h.replace('<span class="section-number">02</span> Selected work', '<span class="section-number">03</span> Selected work', 1)
h = h.replace('<span class="section-number">03</span> About', '<span class="section-number">04</span> About', 1)
h = h.replace('<span class="section-number">04</span> In conversation', '<span class="section-number">05</span> In conversation', 1)
h = h.replace('Good science begins<br>with a good question.', 'Studying RNA or yeast aging?<br>Let’s compare questions.', 1)
h = h.replace('For research conversations, collaborations and speaking enquiries, you can reach me through my ETH profile.', 'For a research or methods conversation, tell me your biological question, the organism you work on, and the measurement that is difficult today. For a seminar invitation, include the audience and proposed date.', 1)
h = h.replace('<a class="text-link" href="https://bc.biol.ethz.ch/research/barral/members-barral/jordan-mccarthy.html">Get in touch at ETH', '<a class="text-link" href="mailto:jordan.mccarthy@bc.biol.ethz.ch?subject=Research%20conversation%20%7C%20jordanmccarthy.com">Discuss a research question', 1)
h = h.replace('<a class="text-link" href="https://orcid.org/0000-0002-2824-4248">Research record', '<a class="text-link" href="mailto:jordan.mccarthy@bc.biol.ethz.ch?subject=Seminar%20invitation%20%7C%20jordanmccarthy.com">Invite me to speak', 1)
h = h.replace('This website describes public research and does not disclose unpublished laboratory results.', 'The methods images are from my September 2025 presentation and illustrate the experimental approaches, not a quantitative lifespan comparison.', 1)
css = '''
.methods{padding:0 0 86px}.methods-grid{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:40px}.method-image{height:390px;background:#e3e4dc;overflow:hidden;display:flex;align-items:center;justify-content:center;border:1px solid var(--line)}.method-image img{width:100%;height:100%;object-fit:contain}.method-card figcaption{font:11px/1.65 var(--sans);color:var(--muted);margin-top:12px;min-height:54px}.method-eyebrow{font:10px/1.7 var(--mono);letter-spacing:.08em;text-transform:uppercase;margin:24px 0 12px;color:var(--accent)}.method-card h3{font:30px/1.2 var(--serif);letter-spacing:-.03em;max-width:420px}.method-card>p:not(.method-eyebrow){font-size:15px;line-height:1.8;color:var(--muted);margin-top:16px}.method-purpose{padding-top:16px;border-top:1px solid var(--line)}.method-attribution{margin-top:38px;padding-top:23px;border-top:1px solid var(--line);font-size:12px;color:var(--muted);line-height:1.8;max-width:1000px}.method-attribution p{max-width:950px}.method-attribution details{margin-top:18px}.method-attribution details p{max-width:740px}.method-attribution summary{cursor:pointer;min-height:38px}.method-attribution a{text-underline-offset:3px}.controls-photo{max-width:340px;margin:15px 0}.controls-photo figcaption{font-size:11px;margin-top:8px}.hero .eyebrow{line-height:1.9}.science-primer{margin:27px 0 0 33%;padding:14px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:14px;color:var(--muted)}.science-primer summary{cursor:pointer;min-height:35px;color:var(--ink)}.science-primer p{margin:15px 0;line-height:1.85}
@media(max-width:760px){.methods{padding:0 0 55px}.methods-grid{grid-template-columns:1fr;gap:35px;margin-top:28px}.method-image{height:355px}.method-card figcaption{min-height:0}.method-card h3{font-size:28px}.method-card>p:not(.method-eyebrow){font-size:14px}.method-attribution{font-size:11px}.science-primer{margin:25px 0 0;font-size:13px}.methods .section-heading h2{font-size:33px}.controls-photo{max-width:300px}}
'''
h = h.replace('</style>', css + '\n</style>', 1)
for prohibited in ['PRIVATE REVIEW', 'noindex,nofollow', 'NOT cleared', 'conditional-website-model', 'North Star', 'HEARTH']:
    if prohibited in h:
        raise SystemExit('Non-public review text found.')
base.write_text(h)
Path('robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://jordanmccarthy.com/sitemap.xml\n')
Path('sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://jordanmccarthy.com/</loc><lastmod>2026-09-27</lastmod></url></urlset>\n')
Path('WEBSITE-NOTES.md').write_text('''# Jordan McCarthy personal research website

Canonical site: https://jordanmccarthy.com/ . Publish branch: gh-pages.
Static HTML/CSS/JavaScript and locally hosted images. No added analytics.

The methods images were explicitly approved for publication by Jordan McCarthy.
Source: Lab Meeting 26 September 2025, slides 39 (chip-movie still), 48 (MAD overview), 49 (MAD controls).
The original presentation and notes, research results and private records are not included.
Apparatus photographs were rotated to match the slide, resized and re-encoded without EXIF or generated changes.
The source media's acquisition date is not established by the deck date.

MAD method: Hendrickson et al., eLife 2018, DOI 10.7554/eLife.39911.
Implementation acknowledgements: Caudron laboratory, Remo Zangger, Daniel Smith.
Aging-chip platform: Sung Sik Lee.
Credits do not claim sole invention or ownership of the underlying methods.

Personal research publication is separate from any future commercial service site.
''')
files=['index.html','robots.txt','sitemap.xml','WEBSITE-NOTES.md','assets/aging-chip.jpg','assets/mad-setup.jpg','assets/mad-controls.jpg']
manifest={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files}
Path('release-checksums.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'html_sha256':manifest['index.html'],'public_files':files},indent=2))
