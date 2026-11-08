import concurrent.futures as cf
import csv, hashlib, html, json, re, ssl, sys, time
from collections import Counter, defaultdict, deque
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote
from urllib.request import Request, urlopen
from xml.etree import ElementTree
from zoneinfo import ZoneInfo

BASE = 'https://velocemercato.fr'
HOST = 'velocemercato.fr'
ROOT = Path('evidence')
ROOT.mkdir(exist_ok=True)
NOW = lambda: datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds')
MAX_PAGES = 1200
MAX_EXTERNAL = 450
SECRET_PARAM = re.compile(r'([?&](?:token|key|auth|code|session|signature|secret|password)=)[^&#\s]+',re.I)
SKIP = re.compile(r'(^|/)(?:logout|unsubscribe|desinscription|checkout|paiement|login|atelier[^/]*|admin|api)(?:[/.]|$)|(?:stripe\.com|paypal\.com|wa\.me|formsubmit\.co|amzn\.to|amazon\.fr)|[?&](?:token|key|auth|code)=', re.I)
STATIC = re.compile(r'\.(?:json|xml|txt|js|css|png|jpg|jpeg|svg|webp|gif|ico|mp4|pdf|webmanifest|woff2|avif)$', re.I)
REQ = {'User-Agent':'Mozilla/5.0 (compatible; VM-Quality-Audit/1.0)', 'Accept-Encoding':'identity'}
def fetch(url, limit=2_500_000, timeout=10):
    at = NOW()
    try:
        with urlopen(Request(url, headers=REQ), timeout=timeout) as r:
            return (r.status, r.geturl(), dict(r.headers.items()), r.read(limit), '', at)
    except HTTPError as e:
        return (e.code, e.geturl(), dict(e.headers.items()), e.read(min(limit, 5000)), '', at)
    except Exception as e:
        return (0, url, {}, b'', type(e).__name__ + ': ' + str(e)[:200], at)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.assets, self.buttons, self.forms, self.ids, self.metas = [], [], [], [], set(), {}
        self.heading_count, self.details = 0, 0
        self.title, self.anchor, self.is_title = '', None, False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag == 'a':
            if a.get('name'): self.ids.add(a['name'])
            self.anchor = [a.get('href') or '', a.get('aria-label') or a.get('title') or '']
            if self.anchor[0]: self.links.append(self.anchor)
        if tag == 'title': self.is_title = True
        if tag == 'h1': self.heading_count += 1
        if tag == 'details': self.details += 1
        if tag == 'button' or a.get('role') == 'button':
            self.buttons.append([a.get('id',''), a.get('type',''), a.get('aria-label') or a.get('title') or ''])
        if tag == 'form':
            self.forms.append({'method': (a.get('method') or 'get').lower(), 'action':a.get('action') or '', 'id':a.get('id') or ''})
        if tag in ('img','script','source') and a.get('src'): self.assets.append((tag,a['src']))
        if tag == 'link' and a.get('href'):
            rel = a.get('rel','')
            if rel in ('stylesheet','manifest','icon','preload'): self.assets.append((rel,a['href']))
            if rel == 'canonical': self.metas['canonical'] = a['href']
        if tag == 'meta' and a.get('content') and (a.get('name') in ('robots','viewport','description') or a.get('property') in ('og:image','og:title')):
            self.metas[a.get('name') or a['property']] = a['content']
    def handle_endtag(self, tag):
        if tag == 'title': self.is_title = False
        if tag == 'a': self.anchor = None
    def handle_data(self, data):
        if self.is_title: self.title += data
        if self.anchor is not None: self.anchor[1] = (self.anchor[1]+' '+data.strip()).strip()[:180]

def normal(url, base=BASE):
    try:
        u = urlsplit(urljoin(base, url.strip()))
        if u.scheme not in ('https','http') or not u.hostname or u.username or u.password: return None
        net = u.netloc.lower()
        if net == 'www.'+HOST: net = HOST
        return urlunsplit((u.scheme,net,u.path or '/',u.query,'')), unquote(u.fragment)
    except ValueError: return None

def group(u):
    p = urlsplit(u).path.strip('/')
    return p.split('/')[0].split('.')[0] or 'accueil'

def load(url):
    code, final, headers, data, error, at = fetch(url)
    p = None
    if code == 200 and ('html' in next((v for k,v in headers.items() if k.lower()=='content-type'),'') or data[:400].lower().find(b'<html') >= 0):
        p = Page()
        p.feed(data.decode('utf-8','replace'))
    return url, code, final, headers, p, error, at

def writecsv(name, header, rows):
    with (ROOT/name).open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.writer(f);w.writerow(header)
        for row in rows:
            safe = [SECRET_PARAM.sub(r'\1[masque]',x) if isinstance(x,str) else x for x in row]
            w.writerow(["'"+x if isinstance(x,str) and x[:1] in ('=','+','-','@') else x for x in safe])

def sitemap():
    found, attempted, work = [], set(), [BASE+'/sitemap.xml']
    while work and len(attempted) < 12:
        u=work.pop()
        if u in attempted: continue
        attempted.add(u)
        st,_,_,b,_,_=fetch(u)
        if st != 200: continue
        try: x=ElementTree.fromstring(b)
        except ElementTree.ParseError: continue
        for loc in x.findall('.//{*}loc'):
            n=normal(loc.text or '')
            if not n or urlsplit(n[0]).hostname != HOST: continue
            if x.tag.endswith('sitemapindex'): work.append(n[0])
            else: found.append(n[0])
    return list(dict.fromkeys(found))

def crawl():
    site = sitemap()
    queue=deque(dict.fromkeys([BASE+'/']+site+[BASE+'/pronos/',BASE+'/kit-du-jour',BASE+'/foot-amateur/',BASE+'/scores/',BASE+'/web-studio']))
    queued=set(queue); visited={}; links=[]; assets=set(); skipped=set(); external=defaultdict(set)
    with cf.ThreadPoolExecutor(max_workers=10) as pool:
        while queue and len(visited)<MAX_PAGES:
            batch=[queue.popleft() for _ in range(min(45,len(queue),MAX_PAGES-len(visited)))]
            for url, code, final, headers, page, error, at in pool.map(load,batch):
                visited[url]=(code,final,headers,page,error,at)
                if not page: continue
                for ref,label in page.links:
                    n=normal(ref,final)
                    if not n:
                        links.append([url,ref,label,'','protocole ou action']);continue
                    dest,frag=n
                    kind='interne' if urlsplit(dest).hostname==HOST else 'externe'
                    links.append([url,dest,label,frag,kind])
                    if SKIP.search(dest):
                        skipped.add(dest);continue
                    if kind=='externe':
                        external[dest].add(url)
                    elif STATIC.search(urlsplit(dest).path):
                        assets.add(dest)
                    elif dest not in queued:
                        queued.add(dest);queue.append(dest)
                for _,ref in page.assets:
                    n=normal(ref,final)
                    if n and urlsplit(n[0]).hostname==HOST and not SKIP.search(n[0]): assets.add(n[0])
    return visited,links,assets,skipped,external,site,list(queue)

def latest(body):
    try: j=json.loads(body)
    except Exception: return None
    if isinstance(j,list): a=j; meta={}
    elif isinstance(j,dict):
        meta=j
        a=next((j[k] for k in ('titres','articles','items','matchs','news','data') if isinstance(j.get(k),list)),[])
        if not a and isinstance(j.get('sports'),dict):
            a=[i for v in j['sports'].values() if isinstance(v,list) for i in v]
    else: return None
    dates=[str(v) for i in a if isinstance(i,dict) for k,v in i.items() if k in ('date','publishedAt','pubDate','published_at','timestamp') and isinstance(v,str)]
    return dict(entries=len(a),latest=max(dates,default=None),generation=next((meta[k] for k in ('maj','updatedAt','misAJour','generatedAt') if k in meta),None),public_advice=bool(meta.get('publicAdvice')) if 'publicAdvice' in meta else None)
def feeds():
    paths=['articles.json','actus/news.json','vm-gaming/news.json','multisport/actualites.json','foot-amateur/actus.json','belfort/actus.json','scores.json','pronos/selection.json']
    data=[]
    start=time.monotonic()
    for i in range(3):
        if i: time.sleep(max(0, start+180*i-time.monotonic()))
        with cf.ThreadPoolExecutor(max_workers=8) as p:
            for path,(code,final,head,body,error,at) in zip(paths,p.map(fetch,[BASE+'/'+x for x in paths])):
                data.append({'pass':i+1,'at':at,'path':path,'code':code,'digest':hashlib.sha256(body).hexdigest()[:12],**(latest(body) or {})})
    (ROOT/'flux.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    for d in data: print('VM_FEED '+json.dumps(d,ensure_ascii=False),flush=True)

def probe(url):
    st,final,headers,body,error,at=fetch(url,4096,8)
    return url,st,final,error,at,next((v for k,v in headers.items() if k.lower()=='content-type'),'')
def run():
    visited,links,assets,skipped,external,site,remaining=crawl()
    by_host=defaultdict(list)
    for url in sorted(external):by_host[urlsplit(url).hostname].append(url)
    externals=[]; max_domain=20
    for i in range(max_domain):
        externals.extend(u[i] for u in by_host.values() if len(u)>i)
    externals=externals[:MAX_EXTERNAL]
    asset_list=sorted(assets)
    with cf.ThreadPoolExecutor(max_workers=12) as p:
        checks=dict((x[0],x[1:]) for x in p.map(probe,asset_list+externals))
    all_dest={u:(r[0],r[1],r[4],r[5]) for u,r in visited.items()}
    all_dest.update({u:(r[0],r[1],r[2],r[3]) for u,r in checks.items()})
    anchors=[]; relbroken=[]; errors=[]
    for source,dest,label,frag,kind in links:
        st,final,error,at=all_dest.get(dest,(None,'','',''))
        finding=''
        if st in (404,410) and kind=='interne': finding='HTTP interne '+str(st)
        if frag and kind=='interne' and dest in visited and visited[dest][3] and not frag.startswith((':~:','a=')) and frag not in visited[dest][3].ids:
            finding=finding or 'ancre absente du HTML initial'
            anchors.append([source,dest,frag,label])
        if finding and finding.startswith('HTTP'): relbroken.append([source,dest,st,label])
        if dest in skipped: finding='action ou destination exclue'
        errors.append([source,label,dest,frag,kind,st,final,error,at,finding])
    writecsv('liens.csv',['source','libelle','cible','ancre','type','http','destination_finale','erreur','paris','constat'],errors)
    writecsv('ressources.csv',['url','http','destination_finale','erreur','paris','type'],[(u,*checks[u]) for u in checks])
    pages=[]
    for u,(st,fin,head,p,err,at) in visited.items():
        normalized={k.lower():v for k,v in head.items()}
        pages.append((u,st,fin,p.title.strip() if p else '',p.heading_count if p else '',len(p.links) if p else '',len(p.buttons) if p else '',p.details if p else '',len(p.forms) if p else '',p.metas.get('canonical','') if p else '',p.metas.get('og:image','') if p else '',normalized.get('strict-transport-security',''),normalized.get('content-security-policy',''),err,at))
    writecsv('pages.csv',['url','http','destination','titre','h1','liens','boutons_html','volets_details','formulaires','canonical','og_image','hsts','csp','erreur','paris'],pages)
    writecsv('hors-couverture.csv',['url','raison'],[(u,'limite crawl') for u in remaining]+[(u,'externe au-delà des limites') for u in sorted(set(external)-set(externals))]+[(u,'action ou destination exclue') for u in sorted(skipped)])
    groups=Counter(group(u) for u,r in visited.items() if r[3])
    title_dupes=defaultdict(set)
    for u,st,fin,t,*rest in pages:
        if st==200 and t: title_dupes[t].add(fin)
    form_examples=[]
    for u,r in visited.items():
        if r[3] and r[3].forms:
            for f in r[3].forms:
                action=normal(f['action'],u)
                action_host=urlsplit(action[0]).hostname if action else urlsplit(f['action']).scheme or ''
                form_examples.append([u,f['method'],action_host,f['id']])
    writecsv('formulaires.csv',['page','methode','hote_ou_protocole','id'],form_examples)
    summary=dict(at=NOW(),sitemap=len(site),requested=len(visited),html=sum(bool(r[3]) for r in visited.values()),unique_final_html=len({r[1] for r in visited.values() if r[3]}),page_status=dict(Counter(r[0] for r in visited.values())),links=len(links),internal=len({e[1] for e in links if e[4]=='interne'}),external=len(external),external_tested=len(externals),external_status=dict(Counter(checks[x][0] for x in externals)),assets=len(assets),assets_status=dict(Counter(checks[x][0] for x in asset_list)),asset_bad=[(u,checks[u][0]) for u in asset_list if checks[u][0] not in range(200,400)][:22],skipped=len(skipped),remaining=len(remaining),groups=dict(groups.most_common()),redirected=sum(r[0]==200 and u!=r[1] for u,r in visited.items()),no_canonical=sum(bool(r[3]) and not r[3].metas.get('canonical') for r in visited.values()),no_og=sum(bool(r[3]) and not r[3].metas.get('og:image') for r in visited.values()),duplicated_titles=[(t,len(v)) for t,v in sorted(title_dupes.items(),key=lambda kv:-len(kv[1])) if len(v)>1][:15],form_count=len(form_examples),anchor_count=len(anchors),anchor_unique=len({(x[1],x[2]) for x in anchors}),anchors=anchors[:22],broken_count=len(relbroken),broken_unique=len({x[1] for x in relbroken}),broken=relbroken[:30],missing_pages=[(u,r[0]) for u,r in visited.items() if r[0] in (0,404,410)][:35],home_headers={k:v for k,v in visited[BASE+'/'][2].items() if k.lower() in ('strict-transport-security','content-security-policy','permissions-policy','x-frame-options','x-content-type-options','cache-control','referrer-policy')})
    (ROOT/'synthese-crawl.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print('VM_CRAWL '+json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=='__main__':
    (feeds if sys.argv[1]=='feeds' else run)()
