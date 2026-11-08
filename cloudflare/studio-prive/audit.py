import csv, datetime as dt, json, re, subprocess, sys, time
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo
from lxml import html

OUT = Path(__file__).parent
VM='https://velocemercato.fr'
VU='https://vmunivers.fr'
HOSTS={'velocemercato.fr','vmunivers.fr','www.velocemercato.fr','www.vmunivers.fr'}
PARIS=ZoneInfo('Europe/Paris')
def stamp(): return dt.datetime.now(PARIS).isoformat(timespec='seconds')

def fetch(url, head=False, retry=False):
    args=['curl','-sSL','--max-time','9','--max-redirs','7','--proto','=https,http',
          '--proto-redir','=https,http','--max-filesize','2500000',
          '--write-out','\n@@RESULT@@%{http_code}\t%{url_effective}\t%{content_type}\t%{num_redirects}\t%{time_total}']
    if head: args+=['-I']
    if retry: args+=['--retry','1','--retry-all-errors']
    p=subprocess.run(args+[url],capture_output=True)
    body,_,meta=p.stdout.rpartition(b'\n@@RESULT@@')
    if not meta: meta=b'000\t\t\t0\t0'
    code,end,ctype,hops,elapsed=meta.decode(errors='replace').split('\t',4)
    return dict(code=int(code),end=end or url,type=ctype,redirects=int(hops),seconds=round(float(elapsed),3),
                curl=p.returncode,error=p.stderr.decode(errors='replace').strip()[:180]),body

def split(base, href):
    try:
        if not href or href.startswith(('mailto:','tel:','data:','javascript:','blob:')): return
        s=urlsplit(urljoin(base,href))
        if s.scheme not in ('http','https') or not s.hostname or s.username or s.password:return
        # Une requête GET seulement, sans lien de session ni action explicite.
        if re.search(r'(?:logout|unsubscribe|token=|checkout\.stripe|buy\.stripe|sharer\.php)',s.geturl(),re.I):return
        q=s.query if s.hostname not in HOSTS or re.search(r'^(sport|theme|offre|region)=',s.query) else ''
        return urlunsplit((s.scheme,s.netloc,s.path or '/',q,'')),unquote(s.fragment)
    except ValueError:return

def inspect(url):
    row,body=fetch(url)
    row.update(url=url,ts=stamp(),title='',ids=[],links=[],assets=[],h1=0,canonical='',og=False,forms=[],manifest=[],bytes=len(body))
    if 'html' not in row['type'] or not body:return row
    try:
        root=html.fromstring(body)
        row.update(title=' '.join(root.xpath('string(//title)').split())[:230],
                   ids=list(set(root.xpath('//@id')+root.xpath('//a/@name'))),
                   h1=len(root.xpath('//h1')),canonical=root.xpath('string(//link[@rel="canonical"]/@href)'),
                   og=bool(root.xpath('//meta[@property="og:image"]')),
                   forms=[{'method':a.get('method','GET'),'action':a.get('action','')} for a in root.xpath('//form')],
                   manifest=root.xpath('//link[@rel="manifest"]/@href'))
        base=row['end']
        for a in root.xpath('//a[@href]'):
            parsed=split(base,a.get('href'))
            if parsed:row['links'].append((*parsed,' '.join(a.text_content().split())[:125]))
        for a in root.xpath('//img[@src]|//script[@src]|//link[@rel="stylesheet"]|//link[@rel="manifest"]'):
            parsed=split(base,a.get('src') or a.get('href'))
            if parsed:row['assets'].append((parsed[0],a.tag))
    except (ValueError,TypeError):pass
    return row

PRIORITY=[VM+'/',VU+'/',*[VM+x for x in ('/actus/','/vm-gaming/','/multisport/','/scores/','/belfort/','/foot-amateur/','/pronos/','/kit-du-jour','/kit-pronos','/selection-amazon','/web-studio','/pub/','/mangas/','/series/','/emploi/','/studio','/notifications/','/a/rss-v2-00b015a842df7be4ccd20c.html','/a/rss-v2-7620370f6c55de43261973.html')],*[VU+x for x in ('/professionnels/','/meteo/','/telechargements/','/studio/reseaux','/vm-audit-page-inexistante-20261108')],VM+'/vm-audit-page-inexistante-20261108']
def sitemap(url):
    meta,body=fetch(url,retry=True)
    try: locs=[x.text.strip() for x in ET.fromstring(body).iter() if x.tag.endswith('}loc') or x.tag=='loc']
    except (ET.ParseError,AttributeError):locs=[]
    return dict(url=url,**meta,locs=locs)
def media(url):
    p=urlsplit(url).path.lower()
    return bool(re.search(r'\.(?:json|xml|js|css|webmanifest|png|webp|jpe?g|ico|gif|svg|mp4|pdf|zip|m4a|woff2?)$',p))
def crawl():
    pages={}
    sitemaps=[sitemap(host+'/sitemap.xml') for host in (VM,VU)]
    new=list(dict.fromkeys(PRIORITY+[x for sm in sitemaps for x in sm['locs'] if urlsplit(x).hostname in HOSTS]))
    # Le plafond porte sur les URL, y compris les variantes .html et les redirections.
    cap=320
    with ThreadPoolExecutor(max_workers=14) as pool:
        for layer in range(5):
            queue=[x for x in new if x not in pages][:cap-len(pages)]
            if not queue: break
            for p in pool.map(inspect,queue): pages[p['url']]=p
            new=sorted({url for p in pages.values() for url,_,_ in p['links'] if
                urlsplit(url).hostname in HOSTS and not media(url) and url not in pages},
                key=lambda x:(not x.startswith(VU),'/a/' in x,'/episodes/' in x,x))
            print('Niveau',layer,'URL',len(pages),'restant',len(new),flush=True)
    edges={(row['url'],dst,fragment,title) for row in pages.values() if row['code']==200 for dst,fragment,title in row['links']}
    by_end={p['end']:p for p in pages.values() if p['code']==200}
    anchors=sorted((src,dst,frag,label) for src,dst,frag,label in edges if frag and not frag.startswith(('a=','vm=')) and
        (target:=pages.get(dst) or by_end.get(dst)) and target['code']==200 and 'html' in target['type'] and frag not in target['ids'])
    todo=[('external',u) for u in sorted({d for s,d,f,t in edges if urlsplit(d).hostname not in HOSTS})]
    todo.sort(key=lambda k: (not any(h in k[1] for h in ('facebook.com','youtube.com','dailymotion.com','amzn.to','amazon.fr','france.tv','tf1.fr','ligue1.com','github.com')),k[1]))
    assetrefs={u for p in pages.values() if p['code']==200 for u,t in p['assets'] if urlsplit(u).hostname in HOSTS}
    resource_links={d for s,d,f,t in edges if urlsplit(d).hostname in HOSTS and media(d)}
    def probe(pair):
        typ,url=pair
        p,_=fetch(url,head=True)
        if p['code'] in (400,403,405) and typ=='external':
            p,_=fetch(url)
        return dict(url=url,kind=typ,ts=stamp(),**p)
    # Priorité aux manifestes, puis aux ressources référencées le plus souvent.
    popularity=Counter(u for p in pages.values() for u,t in p['assets'])
    resources=sorted(assetrefs|resource_links,key=lambda x:(not x.endswith('.webmanifest'),-popularity[x],x))
    tests=todo[:180]+[('resource',u) for u in resources[:160]]
    with ThreadPoolExecutor(max_workers=15) as pool:
        checks=list(pool.map(probe,tests))
    result=dict(created=stamp(),pages=pages,anchors=anchors,sitemaps=sitemaps,checks=checks,
        edges=sorted(edges),page_cap=cap,pending=len(new),external_discovered=len(todo),resource_discovered=len(resources))
    (OUT/'crawl.json').write_text(json.dumps(result,ensure_ascii=False))
    print('Dossier crawl',len(pages),len(edges),len(checks),flush=True)

FEEDS={
 'Foot':'/articles.json','Actus':'/actus/news.json','Gaming':'/vm-gaming/news.json','Multisport':'/multisport/actualites.json',
 'Foot régional':'/foot-amateur/actus.json','Belfort':'/belfort/actus.json','Scores':'/scores.json','Flash':'/flash.json',
 'Vidéos':'/videos.json','Émissions':'/studio/emissions.json','Diffusions':'/studio/diffusions.json','Agenda':'/agenda.json',
 'Pronos sélection':'/pronos/selection.json','VM Emploi':'/emploi/offres.json'
}
def summarize(k,path):
    import hashlib
    result,body=fetch(VM+path,retry=True)
    out=dict(name=k,path=path,ts=stamp(),**result)
    try: data=json.loads(body)
    except ValueError:return out
    out['digest']=hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:12]
    if isinstance(data,list): rows=data
    elif isinstance(data,dict):
        out['updated']=next((data[x] for x in ('maj','misAJour','updatedAt','date','verifie_le') if isinstance(data.get(x),str)),None)
        if k=='Pronos sélection':out['expire']=data.get('expire')
        for key in ('sports','regions'):
            if isinstance(data.get(key),dict):
                out[key]={n:len(a) if isinstance(a,list) else a for n,a in data[key].items()}
        rows=next((data[x] for x in ('titres','matchs','items','articles','offres','results') if isinstance(data.get(x),list)),[])
        if k=='Multisport' and isinstance(data.get('sports'),dict):rows=[r for a in data['sports'].values() if isinstance(a,list) for r in a]
    else:return out
    out['count']=len(rows)
    candidates=[]
    for row in rows:
        if not isinstance(row,dict):continue
        for key in ('date_publication','publishedAt','d','date','published_at','pubDate','createdAt'):
            if isinstance(row.get(key),str):
                try:
                    z=dt.datetime.fromisoformat(row[key].replace('Z','+00:00'))
                    if z.tzinfo and z<=dt.datetime.now(dt.timezone.utc):
                        candidates.append((z,row.get('titre') or row.get('title') or row.get('t') or ''))
                except ValueError:pass
                break
    if candidates:
        at,title=max(candidates)
        out['latest']=at.astimezone(PARIS).isoformat(timespec='seconds')
        out['title']=str(title)[:170]
    return out
def samples():
    t=time.monotonic()
    rounds=[]
    for i in range(3):
        time.sleep(max(0,t+i*180-time.monotonic()))
        start=stamp()
        with ThreadPoolExecutor(max_workers=12) as pool:
            rows=list(pool.map(lambda item:summarize(*item),FEEDS.items()))
        rounds.append({'at':start,'rows':rows})
        (OUT/'samples.json').write_text(json.dumps(rounds,ensure_ascii=False))
        print('Relevé',i+1,start,[(r['name'],r['code'],r.get('count'),r.get('digest')) for r in rows],flush=True)
if __name__=='__main__':
    {'crawl':crawl,'samples':samples}[sys.argv[1]]()
