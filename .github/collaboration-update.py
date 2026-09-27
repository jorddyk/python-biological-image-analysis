"""Targeted public website update preserving the current portrait and visual design."""
from pathlib import Path
import re, hashlib, json, sys
from urllib.parse import quote
from bs4 import BeautifulSoup
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
p=root/'index.html'
original=p.read_text()
assert hashlib.sha256(p.read_bytes()).hexdigest()=='9edc265c553d2c5f3505338955ee29dab4da45bafcc111640a5896e51330e240','Concurrent homepage change'
h=original
old='<p class="hero-copy" data-attention-region="research-question">I study <strong>how cells keep unfinished RNA inside the nucleus</strong>, and how that quality control changes with age. At ETH Zürich, I connect single-cell microscopy with molecular measurements in aging yeast.</p>'
new='<p class="hero-copy" data-attention-region="research-question">I study RNA quality control in aging yeast, combining <strong>individual cell histories</strong>, molecular measurements of age-enriched populations and human-reviewed image analysis.</p>'
assert old in h;h=h.replace(old,new,1)
old='<div class="hero-actions" data-attention-region="primary-action"><a class="action-primary" href="#work">Explore the research <span aria-hidden="true">↓</span></a><a class="text-link" href="#contact">Get in touch <span aria-hidden="true">↗</span></a></div>'
new='<div class="hero-actions" data-attention-region="primary-action"><a class="action-primary" href="#contact">Explore a research collaboration <span aria-hidden="true">↓</span></a><a class="text-link" href="#work">See the published research <span aria-hidden="true">↗</span></a></div>'
assert old in h;h=h.replace(old,new,1)
h=h.replace('How cells age. Why RNA matters. Biochemistry and cellular aging research at ETH Zürich.','RNA quality control in aging yeast. Single-cell histories, age-enriched molecular measurements and focused research collaborations.',1)
old='<p class="work-description">Our 2025 study connects displacement of the nuclear basket to pre-mRNA leakage and chromosome loss in aging yeast. Removing introns from three chromosome-segregation genes suppressed that chromosome-loss phenotype.<br><br>The finding connects a structural change at the nuclear pore to a specific, intron-dependent failure of cell function.</p>'
new='<div class="research-case"><p><strong>Question.</strong> How does nuclear-pore remodeling contribute to chromosome loss in aging yeast?</p><p><strong>Result.</strong> Our 2025 study linked nuclear-basket displacement to pre-mRNA leakage and chromosome loss. Removing introns from three chromosome-segregation genes suppressed the chromosome-loss phenotype.</p><p><strong>Why it matters.</strong> A structural change at the nuclear pore is connected to an intron-dependent failure of cell function.</p></div>'
assert old in h;h=h.replace(old,new,1)
needle='<details class="contribution"><summary>My contribution to this study</summary>'
assert needle in h
h=h.replace(needle,'<p class="contribution-visible"><strong>My contribution:</strong> formal analysis, validation and experimental investigation, plus manuscript review and editing.</p>\n<details class="contribution"><summary>Published contribution statement</summary>',1)
h=h.replace('Working on RNA quality control or cellular aging? Tell me the question you are trying to answer.','Have a complementary question, assay or set of strains? Let’s explore a focused research collaboration.',1)
h=h.replace('href="#contact">Discuss a research question <span aria-hidden="true">↗</span>','href="#contact">Explore a research collaboration <span aria-hidden="true">↗</span>',1)
old='<p>Microfluidic traps keep mother cells in view while fresh medium flows through the chip. Repeated imaging lets us follow divisions and changes within cells, instead of comparing isolated snapshots.</p><p class="method-purpose"><strong>The question:</strong> How does a cell change as it produces successive daughters, and what changes its replicative lifespan?</p>'
new='<dl class="method-readouts"><div><dt>Question</dt><dd>When does a cell’s behavior change during its replicative life?</dd></div><div><dt>Approach</dt><dd>Microfluidic traps and repeated imaging follow individual yeast mothers as they produce daughters.</dd></div><div><dt>Readout</dt><dd>Division histories and replicative lifespan; fluorescence trajectories where a suitable reporter is used.</dd></div></dl>'
assert old in h;h=h.replace(old,new,1)
old='<p>The Miniature-chemostat Aging Device, or MAD, retains magnetically labelled yeast cells while their daughters are washed away. This provides aging cell populations for RNA measurements and other molecular analyses.</p><p class="method-purpose"><strong>The question:</strong> Which molecular features differ between younger and older cell populations?</p>'
new='<dl class="method-readouts"><div><dt>Question</dt><dd>Which molecular features differ between younger and age-enriched yeast populations?</dd></div><div><dt>Approach</dt><dd>The Miniature-chemostat Aging Device (MAD) retains magnetically labelled mothers while daughters wash out.</dd></div><div><dt>Readout</dt><dd>Age-enriched populations for RNA and other molecular measurements, rather than perfectly age-pure samples.</dd></div></dl>'
assert old in h;h=h.replace(old,new,1)
needle='<div class="method-attribution">'
assert h.count(needle)==1
h=h.replace(needle,'''<p class="scale-note">These approaches address complementary scales: the bulk samples are not the same cells followed in the movies.</p>
<div class="analysis-note"><h3>From movies to reviewed cell histories.</h3><p>I develop image-analysis workflows to organize trap-level images, support annotation, and extract division and lifespan summaries. Automated calls remain subject to human review; the workflow is still being developed and validated.</p></div>
'''+needle,1)
h=h.replace('My PhD research in the Barral laboratory at ETH Zürich asks how nuclear RNA quality control changes during aging and stress. A mother yeast cell produces successive daughters. The number it produces over its lifetime is its replicative lifespan. This gives us a way to connect molecular changes to a cell’s life history, and to test mechanisms in a well-understood organism.','My current PhD research asks how nuclear RNA quality control changes during aging and stress. A mother yeast cell produces successive daughters; the number produced over its lifetime is its replicative lifespan.',1)
email='jordan.mccarthy@bc.biol.ethz.ch'
subject='Research collaboration | jordanmccarthy.com'
body='Hello Jordan,\r\n\r\nI would like to explore a focused research collaboration.\r\n\r\nOptional prompts:\r\nBiological question: \r\nModel/system: \r\nMeasurement difficulty (and any relevant strains, data, assay or expertise we could contribute): \r\n\r\nBest,\r\n'
collab='mailto:'+email+'?subject='+quote(subject,safe='')+'&amp;body='+quote(body,safe='')
seminar='mailto:'+email+'?subject='+quote('Seminar invitation | jordanmccarthy.com',safe='')+'&amp;body='+quote('Hello Jordan,\r\n\r\nAudience and institution: \r\nProposed date or window: \r\nTopic of interest: \r\n\r\nBest,\r\n',safe='')
contact='''<section class="contact" id="contact" aria-labelledby="contact-title" data-attention-region="contact" tabindex="-1">
<p class="section-label"><span class="section-number">04</span> Working together</p>
<div><h2 id="contact-title">A focused question.<br>A complementary collaboration.</h2>
<p>I’m interested in research collaborations connecting cell histories with molecular measurements. A good fit brings a specific cellular-aging question and complementary strains, data, an assay, expertise or research resources.</p>
<div class="collaboration-fit"><h3>Possible starting questions</h3><ul><li>Does a yeast perturbation change when divisions slow or when a fluorescent reporter changes during replicative aging?</li><li>Could a molecular difference in your age-enriched yeast samples motivate a test in individual cell histories?</li></ul></div>
<p class="collaboration-next"><strong>First, a short research-fit discussion.</strong> We would agree a bounded question, each partner’s contribution, scope, resources and any laboratory access individually.</p>
<div class="compose-block"><a class="action-primary" href="COLLAB_URI">Compose a collaboration email <span aria-hidden="true">↗</span></a><p>A brief, non-confidential outline is enough. The link opens an editable email; nothing is sent automatically.</p></div>
<div class="email-fallback"><a id="contact-email" href="mailto:EMAIL">EMAIL</a><button type="button" class="copy-email" hidden aria-describedby="email-copy-status">Copy email</button></div><p class="email-copy-status" id="email-copy-status" role="status" aria-live="polite"></p>
</div></section>'''.replace('COLLAB_URI',collab).replace('EMAIL',email)
old_contact=re.search(r'<section class="contact".*?</section>',h,re.S).group()
h=h.replace(old_contact,'',1)
anchor='<section class="about" id="about"'
assert h.count(anchor)==1
h=h.replace(anchor,contact+'\n'+anchor,1)
h=h.replace('<span class="section-number">04</span> About','<span class="section-number">05</span> About',1)
about=re.search(r'<section class="about".*?</section>',h,re.S).group()
speaking='''<details class="speaking"><summary>Seminar invitations</summary><p>Topics include RNA quality control, nuclear-pore remodeling and cellular aging in budding yeast. Include the audience, institution and proposed date.</p><a class="text-link" href="SEMINAR_URI">Compose a seminar invitation <span aria-hidden="true">↗</span></a></details>'''.replace('SEMINAR_URI',seminar)
assert about.endswith('</div></section>')
new_about=about[:-len('</div></section>')]+speaking+'\n</div></section>'
h=h.replace(about,new_about,1)
copyjs='''
(function(){
'use strict';
const button=document.querySelector('.copy-email');
const address=document.getElementById('contact-email');
const status=document.getElementById('email-copy-status');
if(!button||!address||!status)return;
button.hidden=false;
button.addEventListener('click',async function(){
 const text=address.textContent.trim();
 button.disabled=true;
 try{
  if(!navigator.clipboard||!window.isSecureContext)throw new Error('Clipboard unavailable');
  await navigator.clipboard.writeText(text);
  status.textContent='Email address copied.';
 }catch(error){
  const selection=window.getSelection();
  if(selection){const range=document.createRange();range.selectNodeContents(address);selection.removeAllRanges();selection.addRange(range);selection.addRange(range);}
  status.textContent='Automatic copy is unavailable. Select the email address and use your device’s Copy command, or open the email link.';
 }finally{button.disabled=false;}
});
})();
'''
# The selection contains exactly one range.
copyjs=copyjs.replace('selection.addRange(range);selection.addRange(range);','selection.addRange(range);')
h=h.replace('</body>','<script>'+copyjs+'</script>\n</body>',1)
h=h.replace('assets/attention-layout.css?v=20260927-1','assets/attention-layout.css?v=20260927-2',1)
s0=BeautifulSoup(original,'html.parser');s=BeautifulSoup(h,'html.parser')
assert str(s0.select_one('.hero figure'))==str(s.select_one('.hero figure')),'Portrait changed'
assert str(s0.select_one('.authors'))==str(s.select_one('.authors')),'Authors changed'
for sel in ['.method-card figure','.method-attribution','.education','.profile-links','script[type="application/ld+json"]']:
 assert [str(x) for x in s0.select(sel)]==[str(x) for x in s.select(sel)],'Protected content changed: '+sel
ids=[x['id'] for x in s.select('[id]')];assert len(ids)==len(set(ids))
assert all(a['href'][1:] in ids for a in s.select('a[href^="#"]'))
assert s.select_one('.hero .action-primary')['href']=='#contact'
assert len(s.select('.hero .action-primary'))==1
assert s.select_one('.contribution-visible')
p.write_text(h)
h=p.read_text()
research=re.search(r'<section class="research".*?</section>',h,re.S).group()
research2=research.replace('<div class="questions">','<details class="research-directions"><summary>Explore my current research questions</summary><div class="questions">',1)
assert research2.endswith('</section>')
research2=research2[:-len('</section>')]+'</details></section>'
h=h.replace(research,research2,1)
fit=re.search(r'<div class="collaboration-fit">.*?</div>',h,re.S).group()
h=h.replace(fit,'',1)
anchor='<p class="email-copy-status" id="email-copy-status" role="status" aria-live="polite"></p>'
assert anchor in h
h=h.replace(anchor,anchor+'\n'+fit,1)
p.write_text(h)
assert hashlib.sha256(p.read_bytes()).hexdigest()=='14e68974f5db00a3f525cb2108749c6fabbeeb1a1e3a4ea4a0c4566c79b8d3fb','HTML differs from rendered review'
css=root/'assets/attention-layout.css'
assert hashlib.sha256(css.read_bytes()).hexdigest()=='eddbb348069516dcfbf17419f217d97e5eafd52a0a50ab7787e67ea8b91baa0d','Concurrent stylesheet change'
delta=(root/'.github/collaboration-update.css').read_text()
css.write_text(css.read_text()+'\n'+delta)
assert hashlib.sha256(css.read_bytes()).hexdigest()=='8f3ed714ff2d70719177a457bbac26b97f0c07e9aeed6e0f50906d8c9e39a633','CSS differs from rendered review'
manifest=json.loads((root/'release-checksums.json').read_text())
for name in ['index.html','assets/attention-layout.css']:
 manifest[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
(root/'release-checksums.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'html_sha256':manifest['index.html'],'css_sha256':manifest['assets/attention-layout.css'],'portrait_and_science_images_unchanged':True},indent=2))
