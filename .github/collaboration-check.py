"""One-time public-page browser checks. No visitor tracking or email sending."""
from pathlib import Path
import concurrent.futures, functools, hashlib, http.server, json, re, shutil, subprocess, threading, time, urllib.request, urllib.error
from urllib.parse import urlsplit, parse_qs
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
BASE='https://jordanmccarthy.com/'
BASE_COMMIT='da4bb08c39225440c1481150211a417cbd3d88e6'
MAIN='8643b7d7ddde026a0bed302ab4a97c3722852b64'
EMAIL='jordan.mccarthy@bc.biol.ethz.ch'
qa=Path('_qa');qa.mkdir(exist_ok=True)
files=['index.html','robots.txt','sitemap.xml','CNAME','.nojekyll','release-checksums.json']
protected=['assets/portrait-editorial-lake.jpg','assets/portrait-editorial-lake.webp','assets/portrait-editorial-lake-400.webp','assets/aging-chip.jpg','assets/mad-setup.jpg','assets/mad-controls.jpg','CNAME','.nojekyll','robots.txt','sitemap.xml']
original_hashes={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in protected}
original_meta=BeautifulSoup(Path('index.html').read_text(),'html.parser')
changed=subprocess.check_output(['git','diff','--name-only',BASE_COMMIT,'HEAD'],text=True).splitlines()
allowed_staging={'.github/collaboration-update.py','.github/collaboration-update.css','.github/collaboration-check.py','.github/workflows/collaboration-refinement.yml'}
assert set(changed)<=allowed_staging,('Concurrent repository changes',changed)
main_sha=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]
assert main_sha==MAIN,'Course branch changed; review before proceeding.'
def snapshot(name):
 target=qa/(name+'-site');target.mkdir(exist_ok=True)
 for path in files:shutil.copy2(path,target/path)
 shutil.copytree('assets',target/'assets',dirs_exist_ok=True)
 return target
before=snapshot('before')
origin={'url':BASE,'checks':{},'performance_measurement':False}
for name in ['index.html','assets/attention-layout.css']+protected:
 if name in origin['checks'] or name in ['CNAME','.nojekyll']:continue
 req=urllib.request.Request(BASE+name+'?audit=collaboration-before',headers={'Cache-Control':'no-cache','User-Agent':'Website-release-verification/1.0'})
 with urllib.request.urlopen(req,timeout=20) as response:data=response.read(6000000);status=response.status
 same=hashlib.sha256(data).hexdigest()==hashlib.sha256(Path(name).read_bytes()).hexdigest()
 origin['checks'][name]={'http_status':status,'matches_checkout':same}
 assert status==200 and same,('Live baseline differs',name)
(qa/'before-origin.json').write_text(json.dumps(origin,indent=2))
script=Path('.github/collaboration-update.py')
script.write_text(script.read_text().replace("css.write_text(css.read_text()+'\\n'+delta)","css.write_text(css.read_text()+delta)"))
subprocess.run(['python','.github/collaboration-update.py','.'],check=True)
after=snapshot('after')
assert original_hashes=={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in protected}
soup=BeautifulSoup(Path('index.html').read_text(),'html.parser')
for selector in ['link[rel="canonical"]','script[type="application/ld+json"]','.hero figure','.authors','.method-attribution']:
 assert str(original_meta.select_one(selector))==str(soup.select_one(selector)),('Protected element changed',selector)
assert len(soup.select('h1'))==1
ids=[x['id'] for x in soup.select('[id]')];assert len(ids)==len(set(ids))
assert all(a['href'][1:] in ids for a in soup.select('a[href^="#"]'))
for a in soup.select('a[href^="mailto:"]'):
 uri=urlsplit(a['href']);assert uri.path==EMAIL
 if 'collaboration' in a.get_text().lower():
  q=parse_qs(uri.query);assert q['subject']==['Research collaboration | jordanmccarthy.com']
  assert all(x in q['body'][0] for x in ['Biological question:','Model/system:','Measurement difficulty','we could contribute'])
  assert '\r\n' in q['body'][0]
server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(http.server.SimpleHTTPRequestHandler,directory='.'))
threading.Thread(target=server.serve_forever,daemon=True).start()
report={'source_commit':BASE_COMMIT,'course_branch':MAIN,'viewports':{},'checks':{},'measured_eye_tracking':False,'conversion_results':None,'render_source':'Exact checkout files served over local HTTP on GitHub Actions; separate live-origin checks and screenshots.'}
widths=[(320,812),(390,844),(760,1024),(1024,768),(1440,1000)]
with sync_playwright() as p:
 browser=p.chromium.launch()
 for phase in ['before','after']:
  folder=qa/phase;folder.mkdir(exist_ok=True);rows=[]
  for width,height in widths:
   context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1)
   page=context.new_page();errors=[];external=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('request',lambda req:external.append(req.url) if not req.url.startswith(('http://127.0.0.1:8765/','data:')) else None)
   page.goto('http://127.0.0.1:8765/_qa/'+phase+'-site/',wait_until='networkidle')
   page.evaluate("document.querySelectorAll('img').forEach(im=>im.loading='eager')")
   page.wait_for_function("Array.from(document.images).every(im=>im.complete && im.naturalWidth>0)")
   metrics=page.evaluate('''()=>({document_height:document.documentElement.scrollHeight,viewport_width:innerWidth,scroll_width:document.documentElement.scrollWidth,positions:Object.fromEntries(['work','research','methods','contact','about'].map(id=>[id,Math.round(document.getElementById(id).getBoundingClientRect().top+scrollY)]))})''')
   assert metrics['scroll_width']<=width+1,('Overflow',phase,width,metrics)
   button=page.locator('.hero .action-primary');box=button.bounding_box()
   metrics.update({'width':width,'height':height,'primary_action_bottom':round(box['y']+box['height'],2),'primary_action_height':round(box['height'],2),'primary_action_font':button.evaluate('(el)=>getComputedStyle(el).fontSize')})
   page.screenshot(path=str(folder/(str(width)+'-first.png')))
   page.screenshot(path=str(folder/(str(width)+'-full.png')),full_page=True)
   if width<761:
    page.locator('.menu-toggle').click();assert page.locator('.menu-toggle').get_attribute('aria-expanded')=='true'
    page.keyboard.press('Escape');assert page.locator('.menu-toggle').get_attribute('aria-expanded')=='false'
    page.locator('.menu-toggle').click();page.locator('#navigation a[href="#methods"]').click();page.wait_for_timeout(1600)
    assert page.locator('.menu-toggle').get_attribute('aria-expanded')=='false'
   if phase=='after':
    assert box['height']>=44 and metrics['primary_action_font']=='16px'
    if width==390:assert metrics['primary_action_bottom']<844
    for selector in ['.hero-copy','.method-readouts dd','.contribution-visible','.analysis-note p']:
     assert page.locator(selector).first.evaluate('(el)=>parseFloat(getComputedStyle(el).fontSize)')>=16,(selector,width)
    page.locator('.hero .action-primary').click();page.wait_for_timeout(1600)
    assert page.url.endswith('#contact')
    landing=page.locator('#contact').bounding_box();assert 0<=landing['y']<240,('contact anchor',width,landing)
    compose=page.locator('.compose-block .action-primary');cb=compose.bounding_box()
    metrics['compose_button_bottom_after_anchor']=round(cb['y']+cb['height'],2)
    assert compose.get_attribute('href').startswith('mailto:'+EMAIL+'?subject=Research%20collaboration')
    page.locator('#contact').focus();page.keyboard.press('Tab')
    assert page.evaluate("document.activeElement.matches('.compose-block .action-primary')"),'Keyboard path to compose'
    assert compose.evaluate('(el)=>getComputedStyle(el).outlineStyle')!='none'
    for sel in ['.research-directions','.science-primer','.contribution','.method-attribution details','.speaking']:
     d=page.locator(sel);summary=d.locator('summary').first;summary.focus();page.keyboard.press('Enter');assert d.get_attribute('open') is not None
     page.keyboard.press('Enter');assert d.get_attribute('open') is None
    for target in ['work','methods','about','contact']:
     if width<761:page.locator('.menu-toggle').click()
     page.locator('#navigation a[href="#'+target+'"]').click();page.wait_for_timeout(1600)
     y=page.locator('#'+target).bounding_box()['y'];assert 0<=y<240,(width,target,y)
    page.emulate_media(reduced_motion='reduce');assert page.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=='auto'
   assert not errors,errors
   assert not external,external
   metrics.update({'javascript_errors':errors,'external_requests':external,'all_images_loaded':True})
   rows.append(metrics);context.close()
  report['viewports'][phase]=rows
 for mode in ['granted','denied','unavailable']:
  c=browser.new_context(viewport={'width':390,'height':844},permissions=['clipboard-read','clipboard-write'] if mode=='granted' else [])
  if mode=='denied':c.add_init_script("Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>Promise.reject(new Error('denied'))}})")
  if mode=='unavailable':c.add_init_script("Object.defineProperty(navigator,'clipboard',{value:undefined})")
  page=c.new_page();page.goto('http://127.0.0.1:8765/_qa/after-site/',wait_until='networkidle')
  page.locator('.copy-email').click()
  if mode=='granted':
   page.wait_for_function("document.getElementById('email-copy-status').textContent==='Email address copied.'")
   assert page.evaluate('navigator.clipboard.readText()')==EMAIL
  else:
   page.wait_for_function("document.getElementById('email-copy-status').textContent.startsWith('Automatic copy is unavailable.')")
   assert page.evaluate('window.getSelection().toString()')==EMAIL
  assert page.locator('#email-copy-status').get_attribute('role')=='status'
  assert not page.locator('.copy-email').is_disabled()
  report['checks']['copy_email_'+mode]=True;c.close()
 for width,height in [(320,812),(390,844),(1440,1000)]:
  c=browser.new_context(viewport={'width':width,'height':height},java_script_enabled=False)
  page=c.new_page();page.goto('http://127.0.0.1:8765/_qa/after-site/',wait_until='networkidle')
  assert page.locator('#navigation a[href="#contact"]').is_visible()
  assert page.locator('.copy-email').is_hidden()
  assert page.locator('#contact-email').inner_text()==EMAIL
  page.locator('.hero .action-primary').click();page.wait_for_timeout(1600);assert page.url.endswith('#contact')
  assert page.locator('.compose-block .action-primary').is_visible()
  page.locator('.speaking summary').click();assert page.locator('.speaking a').is_visible()
  report['checks']['no_javascript_'+str(width)]=True;c.close()
 c=browser.new_context(viewport={'width':1024,'height':768});page=c.new_page();page.goto('http://127.0.0.1:8765/_qa/after-site/',wait_until='networkidle')
 page.evaluate("document.querySelectorAll('p,dd,dt,li,a,summary,button').forEach(el=>el.style.fontSize=(parseFloat(getComputedStyle(el).fontSize)*2)+'px')")
 report['checks']['text_resize_200_percent_no_horizontal_overflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 c.close()
 c=browser.new_context(viewport={'width':390,'height':844});page=c.new_page()
 try:
  page.goto(BASE+'?audit=collaboration-before-browser',wait_until='networkidle',timeout=30000)
  page.screenshot(path=str(qa/'before-live-mobile.png'))
  report['checks']['live_origin_baseline_browser']=True
 except Exception as e:report['checks']['live_origin_baseline_browser']={'unverified':str(e)[:240]}
 c.close();browser.close()
server.shutdown()
def luminance(rgb):
 vals=[v/255 for v in rgb];vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals]
 return sum(a*b for a,b in zip(vals,[.2126,.7152,.0722]))
def contrast(a,b):
 x,y=sorted([luminance(a),luminance(b)]);return (y+.05)/(x+.05)
report['checks']['primary_button_contrast']=round(contrast((244,241,233),(32,51,43)),2)
report['checks']['muted_body_contrast']=round(contrast((244,241,233),(89,99,91)),2)
assert report['checks']['primary_button_contrast']>=4.5 and report['checks']['muted_body_contrast']>=4.5
report['checks']['protected_images_and_metadata_unchanged']=True
report['checks']['email_uri_encoding_and_recipient']=True
report['checks']['two_activations_from_hero_to_compose']=True
urls=sorted(set(a['href'] for a in soup.select('a[href^="http"]')))
def check_url(url):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 WebsiteLinkCheck'}),timeout=15) as r:
   r.read(1024)
   return {'url':url,'http_status':r.status,'final_url':r.url,'status':'reachable'}
 except urllib.error.HTTPError as e:
  return {'url':url,'http_status':e.code,'status':'access_restricted_or_unverified' if e.code in [401,403,429] else 'http_error_needs_review'}
 except Exception as e:return {'url':url,'status':'tool_or_network_unverified','detail':str(e)[:160]}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:report['external_links']=list(pool.map(check_url,urls))
(qa/'browser-tests.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
