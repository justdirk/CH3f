#!/usr/bin/env python3
import json, os, html, re, hashlib, shutil
from urllib.parse import quote
from pathlib import Path
from content import LANGS, SLUGS
from refined import REFINED
for lang,values in REFINED.items(): LANGS[lang].update(values)
from conversion import COPY
for lang,values in COPY.items(): LANGS[lang].update(values)
from product_depth import DEPTH
from guide_depth import GUIDE_DEPTH
ROOT=Path(__file__).parent
OUT=ROOT/'dist'
ORIGIN=os.environ.get('SITE_ORIGIN',os.environ.get('CF_PAGES_URL','http://localhost:4173')).rstrip('/')
PUBLIC=os.environ.get('SITE_INDEXABLE')=='true' and os.environ.get('CF_PAGES_BRANCH','main')=='main'
if PUBLIC and not os.environ.get('SITE_ORIGIN','').startswith('https://'):
 raise ValueError('Set SITE_ORIGIN to the verified production HTTPS origin before enabling indexing.')
if not re.fullmatch(r'https?://[a-zA-Z0-9.-]+(?::[0-9]+)?',ORIGIN):
 raise ValueError('SITE_ORIGIN must be a site origin without a path, query or trailing slash.')
CONTACT=json.loads((ROOT/'contact.json').read_text())
WHATSAPP=re.sub(r'[\s()+-]', '', CONTACT.get('whatsapp',''))
if WHATSAPP and not re.fullmatch(r'[1-9][0-9]{7,14}', WHATSAPP):
 raise ValueError('WhatsApp requires the full international phone number')
E=html.escape
if OUT.exists(): shutil.rmtree(OUT)
(OUT/'assets').mkdir(parents=True)
ASSETS={}
for source in sorted((ROOT/'assets').iterdir(),key=lambda p:p.suffix=='.css'):
 if not source.is_file():continue
 data=source.read_bytes()
 if source.suffix=='.css':
  css=data.decode()
  for original,hashed in ASSETS.items():css=css.replace('/assets/'+original,hashed)
  data=css.encode()
 filename=source.stem+'.'+hashlib.sha256(data).hexdigest()[:12]+source.suffix
 (OUT/'assets'/filename).write_bytes(data)
 ASSETS[source.name]='/assets/'+filename
def asset(name):return ASSETS[name]
ORDER=['it','de','en','tr','fr','es','pt']
PRODUCTS=['electric','gas','knife80','knife120']
SOURCES={'electric':'https://toros-italia.com/product/elektrikli-ust-motorlu-dner-makina-xzb4o','gas':'https://toros-italia.com/product/gazli-ust-motorlu-dner-makina-oj6ab','knife80':'https://toros-italia.com/product/80-mm-dner-bak-r8mop','knife120':'https://toros-italia.com/product/deneme-f33qf'}
def url(l,i):return '/'+l+'/'+(SLUGS[l][i]+'/' if SLUGS[l][i] else '')
def nl(s):return E(s).replace('\n','<br>')
def btn(href,label,outline=False):return f'<a class="button{ " outline" if outline else ""}" href="{E(href)}">{E(label)}<span aria-hidden="true">↗</span></a>'
def brand(l):return f'<a class="brand" href="{url(l,0)}" aria-label="CH3F — {E(LANGS[l]["home"])}"><img src="{asset("ch3f-logo-signature-348.webp")}" srcset="{asset("ch3f-logo-signature-348.webp")} 348w, {asset("ch3f-logo-signature-522.webp")} 522w" sizes="(max-width:1150px) 150px, 174px" width="174" height="58" alt="CH3F"></a>'
def photograph(d,k,cls='',lazy=True):
 w,h={'electric':(598,800),'gas':(534,800),'knife80':(1500,1000),'knife120':(390,200)}[k]
 widths={'electric':[320,598],'gas':[320,534],'knife80':[600,1000],'knife120':[390]}[k]
 srcset=', '.join(asset(k+'-'+str(width)+'.webp')+' '+str(width)+'w' for width in widths)
 return f'<img class="{cls}" src="{asset(k+"-"+str(widths[-1])+".webp")}" srcset="{srcset}" sizes="(max-width:600px) 86vw, 42vw" alt="{E(d[k])} — TOROS" width="{w}" height="{h}" decoding="async"'+(' loading="lazy"' if lazy else ' fetchpriority="high"')+'>'
def specification(d,k):
 specs=[(d['manufacturer'],'TOROS')]
 if k=='electric':specs += [(d['supply'],d['electricPower']),(d['motor'],d['top']),(d['radiants'],'4'),(d['voltage'],'380 V'),(d['dimensions'],'470 × 540 × 1050 mm'),(d['weight'],'33 kg')]
 elif k=='gas':specs += [(d['supply'],d['gasPower']),(d['motor'],d['top'])]
 else:specs += [(d['supply'],d['electricPower']),(d['diameter'],'80 mm' if k=='knife80' else '120 mm')]
 return specs
def product_guidance(l,d,k):
 if l not in DEPTH:return ''
 c=DEPTH[l];p=c[k]
 checklist=''.join('<li>'+E(t)+'</li>' for t in p['checks'])
 questions=''.join('<details><summary>'+E(q)+'</summary><p>'+E(a)+'</p></details>' for q,a in p['faqs'])
 links=''.join(btn(url(l,n),d[PRODUCTS[n-5]],True) for n in p['related'])
 return f'<section class="section product-guidance"><div><p class="eyebrow">CH3F / {E(d["guide"])}</p><h2>{E(c["choiceTitle"])}</h2><p>{E(p["body"])}</p><a class="text-link" href="{url(l,3)}">{E(d["guide"])} ↗</a></div><aside><h2>{E(c["checkTitle"])}</h2><ul>{checklist}</ul>{btn(url(l,4)+"?product="+k,d["quote"])}</aside></section><section class="section product-questions"><h2>{E(c["questionsTitle"])}</h2>{questions}</section><section class="section related-products"><h2>{E(c["relatedTitle"])}</h2><div class="guide-links">{links}</div></section>'
def chat(l,d,i):
 product=d[PRODUCTS[i-5]] if i>=5 else d['machines']+' / '+d['knives']
 link='https://wa.me/'+WHATSAPP+'?text='+quote(d['whatsappDraft'].format(product=product)) if WHATSAPP else ''
 icon='<svg width="23" height="23" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M20.5 11.8a8.7 8.7 0 0 1-12.9 7.6L3 21l1.5-4.7A8.7 8.7 0 1 1 20.5 11.8Z" stroke="currentColor" stroke-width="1.6"/><path d="M8 7.5c-.8 1 .2 3.2 1.8 4.8 1.6 1.7 4 2.8 5.1 1.9l.9-1-2.4-1.4-.8.7c-1.2-.5-2.2-1.5-2.8-2.7l.7-.8-1.4-2.3Z" fill="currentColor"/></svg>'
 if link:return f'<a class="whatsapp-float" href="{E(link)}" target="_blank" rel="noopener noreferrer" aria-label="{E(d["chatLabel"])}">{icon}<span>WhatsApp</span></a>'
 return f'<details class="whatsapp-widget"><summary aria-label="{E(d["chatLabel"])}">{icon}<span>WhatsApp</span></summary><div class="whatsapp-panel"><p class="eyebrow">CH3F / WhatsApp</p><p>{E(d["whatsappUnavailable"])}</p>{btn(url(l,4),d["quote"])}</div></details>'
def comparison(l,d,i):
 keys=['electric','gas'] if i==1 else ['knife80','knife120']
 cards=''
 for k in keys:
  detail=d['top']+' · '+d['radiants']+': 4 · 380 V' if k=='electric' else d['top'] if k=='gas' else d['diameter']+': '+('80' if k=='knife80' else '120')+' mm'
  note=d[k+'Check'] if i==1 else d['knifeCheck']
  cards+=f'<article><h3>{E(d[k])}</h3><p class="compare-spec">{E(detail)}</p><h4>{E(d["checkBefore"])}</h4><p>{E(note)}</p>{btn(url(l,4)+"?product="+k,d["quote"],True)}</article>'
 return f'<section class="section comparison"><p class="eyebrow">{E(d["guide"])}</p><h2>{E(d["compareMachine" if i==1 else "compareKnife"])}</h2><p>{E(d["compareIntro"])}</p><div class="comparison-grid">{cards}</div><a class="text-link" href="{url(l,3)}">{E(d["guide"])} ↗</a></section>'
def faq(d):return '<section class="section faq"><p class="eyebrow">CH3F / FAQ</p><h2>'+E(d['faqTitle'])+'</h2><div>'+''.join('<details><summary>'+E(q)+'</summary><p>'+E(a)+'</p></details>' for q,a in d['faqs'])+'</div></section>'
def cta(l,d):return '<section class="section cta"><div><p class="eyebrow">'+E(d['next'])+'</p><h2>'+nl(d['ctaTitle'])+'</h2><p>'+E(d['ctaText'])+'</p></div>'+btn(url(l,4),d['quote'])+'</section>'
def product_card(l,d,k,index):
    marks={'electric':'4','gas':'GAS','knife80':'Ø80','knife120':'Ø120'}
    labels={'electric':d['radiants'],'gas':d['gasPower'],'knife80':'mm','knife120':'mm'}
    return f'<article class="product-card"><a class="product-panel {k}" href="{url(l,index)}" aria-label="{E(d[k])}"><span class="eyebrow">TOROS / CH3F</span>{photograph(d,k,"product-photograph")}<span class="panel-foot">{E(labels[k])}<span aria-hidden="true">↗</span></span></a><h2><a href="{url(l,index)}">{E(d[k])}</a></h2><p>{E(d[k+"Desc"])}</p><a class="text-link" href="{url(l,index)}">{E(d["view"])} <span aria-hidden="true">↗</span></a></article>'
def page(l,i):
 d=LANGS[l].copy()
 if l in DEPTH:
  for product in PRODUCTS:d[product+'Desc']=DEPTH[l][product]['intro']
 titles=[d['machines']+' & '+d['knives'],d['machineTitle'],d['knifeTitle'],d['guide'],d['quote']]+[d[k] for k in PRODUCTS]
 desc=[d['intro'],d['machineIntro'],d['knifeIntro'],d['guideIntro'],d['quoteIntro']]+[d[k+'Desc'] for k in PRODUCTS]
 title=d['homeTitle'] if i==0 else titles[i]+' | CH3F'
 desc=desc[i]
 if i>=5 and l in DEPTH:
  detail=DEPTH[l][PRODUCTS[i-5]]
  title=detail['title'];desc=detail['description']
 base=url(l,i)
 alternates=''.join(f'<link rel="alternate" hreflang="{j}" href="{ORIGIN+url(j,i)}">' for j in ORDER)+f'<link rel="alternate" hreflang="x-default" href="{ORIGIN+url("en",i)}">'
 schema=[{'@context':'https://schema.org','@type':'WebSite','name':'CH3F','url':ORIGIN,'inLanguage':ORDER},{'@context':'https://schema.org','@type':'Organization','@id':ORIGIN+'/#organization','name':'CH3F','url':ORIGIN,'logo':ORIGIN+asset('ch3f-logo-signature-522.webp')}]
 if i:
  schema=[{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':d['home'],'item':ORIGIN+url(l,0)},{'@type':'ListItem','position':2,'name':titles[i],'item':ORIGIN+base}]}]
 if i>=5:
  k=PRODUCTS[i-5]
  category=1 if i<7 else 2
  schema[0]['itemListElement'].insert(1,{'@type':'ListItem','position':2,'name':d['machines' if category==1 else 'knives'],'item':ORIGIN+url(l,category)})
  schema[0]['itemListElement'][-1]['position']=3
  schema.append({'@context':'https://schema.org','@type':'Product','name':d[k],'description':d[k+'Desc'],'manufacturer':{'@type':'Organization','name':'TOROS'},'brand':{'@type':'Brand','name':'TOROS'},'url':ORIGIN+base,'image':ORIGIN+asset({'electric':'electric-598.webp','gas':'gas-534.webp','knife80':'knife80-1000.webp','knife120':'knife120-390.webp'}[k]),'additionalProperty':[{'@type':'PropertyValue','name':label,'value':value} for label,value in specification(d,k)[1:]]})
 if i==3 and l in GUIDE_DEPTH:
  schema.append({'@context':'https://schema.org','@type':'Article','headline':d['guideTitle'],'inLanguage':l,'dateModified':'2026-09-16','author':{'@type':'Organization','name':'CH3F','url':ORIGIN},'mainEntityOfPage':ORIGIN+base})
 if i in [1,2]:
  indices=[5,6] if i==1 else [7,8]
  schema.append({'@context':'https://schema.org','@type':'ItemList','name':titles[i],'itemListElement':[{'@type':'ListItem','position':n+1,'url':ORIGIN+url(l,p),'name':d[PRODUCTS[p-5]]} for n,p in enumerate(indices)]})
 schema_json=json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')
 head=f'''<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title><meta name="description" content="{E(desc)}"><meta name="robots" content="{'index,follow' if PUBLIC and i!=4 else 'noindex,follow'}"><meta name="theme-color" content="#171918"><link rel="canonical" href="{ORIGIN+base}">{alternates}<meta property="og:type" content="website"><meta property="og:site_name" content="CH3F"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{ORIGIN+base}"><link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='3' fill='%2359665f'/%3E%3Ctext x='8' y='25' font-family='Arial' font-weight='900' font-size='27' fill='white'%3E3%3C/text%3E%3C/svg%3E"><link rel="stylesheet" href="{asset("style.css")}"><link rel="preload" href="{asset("manrope-light.woff2")}" as="font" type="font/woff2" crossorigin><script type="application/ld+json">{schema_json}</script><script defer src="{asset("app.js")}"></script></head><body><a class="skip" href="#main">{E(d['skip'])}</a>'''
 langs=''.join(f'<option value="{url(j,i)}" {"selected" if j==l else ""}>{LANGS[j]["name"]}</option>' for j in ORDER)
 head+=f'<header>{brand(l)}<nav aria-label="{E(d["menu"])}">'+''.join(f'<a href="{url(l,n)}" {"aria-current=page" if i==n else ""}>{E(d[k])}</a>' for n,k in [(1,'machines'),(2,'knives'),(3,'guide')])+f'</nav><label class="sr-only" for="language">{E(d["language"])}</label><select id="language" class="lang-switch">{langs}</select><a class="button small" href="{url(l,4)}">{E(d["quote"])} ↗</a></header><main id="main">'
 if i:
  trail=f'<a href="{url(l,0)}">{E(d["home"])}</a>'
  if i>=5:
   cat=1 if i<7 else 2
   trail+=f'<span aria-hidden="true">/</span><a href="{url(l,cat)}">{E(d["machines" if cat==1 else "knives"])}</a>'
  head+=f'<nav class="breadcrumbs" aria-label="{E(d["menu"])}">{trail}<span aria-hidden="true">/</span><span aria-current="page">{E(titles[i])}</span></nav>'
 if i==0:
  hero_srcset=', '.join(asset('machine-hero-'+str(w)+'.webp')+' '+str(w)+'w' for w in [960,1440,1774])
  body=f'<section class="hero studio"><img class="hero-photograph" src="{asset("machine-hero-1774.webp")}" srcset="{hero_srcset}" sizes="(max-width:760px) 180vw, 93vw" alt="{E(d["electric"])} — TOROS" width="1774" height="887" fetchpriority="high" decoding="async"><div class="hero-copy"><p class="eyebrow">CH3F / {E(d["heroEyebrow"])} </p><h1>{E(d["hero1"])}<br><span>{E(d["hero2"])}</span></h1><p>{E(d["intro"])}</p><div class="hero-actions">{btn(url(l,4),d["quote"])}<a class="text-link" href="#range">{E(d["explore"])}</a></div><p class="hero-preview">{E(d["previewShort"])}</p></div><div class="hero-rule"><span>DÖNER / GYROS / SHAWARMA</span><span>CH3F — COLLECTION 01</span></div></section>'

  body+=f'<section class="section" id="range"><div class="section-heading"><div><p class="eyebrow">{E(d["range"])}</p><h2>{nl(d["rangeTitle"])}</h2></div><p>{E(d["rangeIntro"])}</p></div><div class="category-grid">'
  for n,kind,c,idx in [(1,'machines','heat','01'),(2,'knives','cut','02')]:
   body+=f'<a class="category {"dark" if n==2 else ""}" href="{url(l,n)}"><span class="eyebrow">{idx} / {E(d[c])}</span><div class="category-image">{photograph(d,"electric" if n==1 else "knife80")}</div><h3>{E(d[kind])}</h3><p>{E(d["machineIntro" if n==1 else "knifeIntro"])}</p></a>'
  body+='</div></section>'
  body+=f'<section class="section selection"><div class="section-heading"><div><p class="eyebrow">{E(d["guide"])}</p><h2>{E(d["guideTitle"])}</h2></div><a class="text-link" href="{url(l,3)}">{E(d["guide"])} ↗</a></div><div class="three">'+''.join(f'<div><span>0{n+1}</span><h3>{E(s[0])}</h3><p>{E(s[1])}</p></div>' for n,s in enumerate(d['steps'][:3]))+'</div></section>'+faq(d)+cta(l,d)
 elif i in [1,2]:
  body=f'<section class="section page-head"><p class="eyebrow">{E(d["range"])}</p><h1>{E(titles[i])}<span class="orange">.</span></h1><p class="lead">{E(desc)}</p><div class="products-grid">'
  for k,idx in ([('electric',5),('gas',6)] if i==1 else [('knife80',7),('knife120',8)]): body+=product_card(l,d,k,idx)
  body+='</div><p class="source-note">'+E(d['supplierNote'])+'</p></section>'+comparison(l,d,i)+cta(l,d)
 elif i==3:
  body=f'<section class="section page-head guide-head"><p class="eyebrow">{E(d["guide"])}</p><h1>{E(d["guideTitle"])}</h1><p class="lead">{E(d["guideIntro"])}</p><div class="guide-steps">'+''.join(f'<article><span class="step-number">0{n+1}</span><div><h2>{E(s[0])}</h2><p>{E(s[1])}</p></div></article>' for n,s in enumerate(d['steps']))+'</div>'+''.join('<section class="guide-decision"><h2>'+E(block[0])+'</h2>'+''.join('<p>'+E(t)+'</p>' for t in block[1:])+'</section>' for block in GUIDE_DEPTH.get(l,[]))+'<div class="guide-links">'+''.join(btn(url(l,n),d[k],True) for n,k in [(1,'machines'),(2,'knives')])+'</div>'+btn(url(l,4),d['guideCta'])+'</section>'+faq(d)
 elif i==4:
  opts=[(k,d[k]) for k in PRODUCTS]+[('both',d['fullSetup']),('advice',d['undecided'])]
  options=f'<option value="">{E(d["choose"])}</option>'+''.join(f'<option value="{k}">{E(v)}</option>' for k,v in opts)
  def field(key,typ,required,autocomplete):
   return f'<label>{E(d[key])}{" *" if required else ""}<input name="{key}" type="{typ}" {"required" if required else ""} autocomplete="{autocomplete}" maxlength="160"></label>'
  essential=field('email','email',True,'email')+field('country','text',True,'country-name')
  optional=field('business','text',False,'organization')+field('person','text',False,'name')+field('city','text',False,'address-level2')
  checklist='<aside class="checklist"><h2>'+E(d['checklist'])+'</h2><ul>'+''.join('<li>'+E(t)+'</li>' for t in d['checks'])+'</ul></aside>'
  body=f'<section class="section page-head"><div class="quote-layout"><div class="quote-intro"><p class="eyebrow">CH3F / {E(d["quote"])}</p><h1>{E(d["quoteTitle"])}</h1><p class="lead">{E(d["quoteIntro"])}</p></div><div class="quote-main"><p class="preview-note">{E(d["preview"])}</p><form id="quote-form"><p class="form-meta">* {E(d["required"])}</p><label>{E(d["interest"])} *<select name="interest" required>{options}</select></label><div class="form-grid essentials">{essential}</div><details class="optional-fields"><summary>{E(d["optionalDetails"])}</summary><div class="form-grid">{optional}</div><label>{E(d["notes"])}<textarea name="notes" rows="4" maxlength="2000" placeholder="{E(d["notesHint"])}"></textarea></label></details><p class="privacy-note">{E(d["privacy"])}</p><button class="button" type="submit">{E(d["prepare"])} <span aria-hidden="true">↗</span></button></form><section id="quote-result" class="quote-result" hidden tabindex="-1" aria-live="polite"><h2>{E(d["ready"])}</h2><p>{E(d["notSent"])}</p><dl id="summary-list"></dl><div class="actions"><button id="download" class="button">{E(d["download"])}</button><button id="edit" class="button outline">{E(d["edit"])}</button></div></section></div>{checklist}</div></section>'
  config={k:d[k] for k in ['summary','interest','business','person','email','country','city','notes','notSent']}
  body+='<script type="application/json" id="quote-config">'+json.dumps(config,ensure_ascii=False).replace('<',chr(92)+'u003c')+'</script>'
 else:
  k=PRODUCTS[i-5];category=1 if i in [5,6] else 2
  specs=specification(d,k)
  heading=DEPTH[l][k]['heading'] if l in DEPTH else d[k]
  body=f'<section class="section product-detail"><div><p class="eyebrow">TOROS / {E(d["machines" if category==1 else "knives"])}</p><h1>{E(heading)}<span class="orange">.</span></h1><p class="lead">{E(d[k+"Desc"])}</p>{btn(url(l,4)+"?product="+k,d["quote"])}<p class="source-note product-preview">{E(d["previewShort"])}</p><p><a class="text-link" href="{url(l,category)}">← {E(d["back"])}</a></p></div><div class="detail-spec"><div class="spec-display">{photograph(d,k,lazy=False)}</div><h2>{E(d["specs"])}</h2><dl>'+''.join(f'<div><dt>{E(a)}</dt><dd>{E(b)}</dd></div>' for a,b in specs)+f'</dl><p class="source-note">{E(d["confirm"])}</p><span class="source-note">{E(d["source"])}</span></div></section>'+product_guidance(l,d,k)+cta(l,d)
 if i>=5 and l in DEPTH:
  citation='<p class="catalogue-reference">'+E(DEPTH[l]['reviewed'])+' · <a href="'+SOURCES[PRODUCTS[i-5]]+'" target="_blank" rel="noopener noreferrer">'+E(DEPTH[l]['sourceLink'])+'</a></p>'
  body=body.replace('<span class="source-note">'+E(d['source'])+'</span>',citation)
 footer=f'</main><footer>{brand(l)}<div><p>{E(d["equipment"])}</p><span>{E(d["footerLine"])}</span></div><a href="{url(l,4)}">{E(d["quote"])}</a><span>© CH3F 2026</span><div class="footer-languages">'+''.join(f'<a href="{url(j,i)}" lang="{j}" hreflang="{j}">{LANGS[j]["name"]}</a>' for j in ORDER)+'</div></footer>'+chat(l,d,i)+'</body></html>'
 return head+body+footer
for l in ORDER:
 for i in range(9):
  p=OUT/url(l,i).lstrip('/')/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(page(l,i))
(OUT/'index.html').write_text(page('it',0))
urls=[ORIGIN+url(l,i) for l in ORDER for i in range(9) if i!=4]
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+E(u)+'</loc><lastmod>2026-09-16</lastmod></url>' for u in urls)+'</urlset>')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n')
(OUT/'404.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | CH3F</title><meta name="robots" content="noindex"><link rel="stylesheet" href="{asset("style.css")}"><link rel="preload" href="{asset("manrope-light.woff2")}" as="font" type="font/woff2" crossorigin></head><body><main class="section"><p class="eyebrow">CH3F / 404</p><h1>Page not found.</h1><p>Choose your language to continue.</p>'+''.join(btn(url(l,0),LANGS[l]['name'])+' ' for l in ORDER)+'</main></body></html>')
print('Built 63 localized pages + Italian entry page + 404. Indexable:',PUBLIC)

(OUT/'_headers').write_text('/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n'+('/*\n  X-Robots-Tag: noindex, follow\n' if not PUBLIC else ''))
(OUT/'asset-manifest.json').write_text(json.dumps(ASSETS,indent=2))
