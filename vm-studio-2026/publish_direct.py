"""Publication ponctuelle du studio VM, autorisée par le propriétaire le 16/11/2026.

Réutilise les connexions existantes. Pas de reconnexion ni de modification des secrets.
Un reçu est enregistré AVANT chaque envoi pour éviter une seconde publication.
"""
import sys, os, json, re, datetime as dt, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.publier_meta import Graph, instagram_reel, ensure_meta_targets
from tools.diffuser_jt import State, DeliveryError, git_save, HTTP, YouTube, access_token
PAGES={'meta':'1384363904759072','meta_univers':'1349998758205153','meta_pronos':'112294796981981'}
NAMES={'meta':'VeloceMercato','meta_univers':'VMunivers.fr','meta_pronos':'VM actus et pronos'}
BASE=ROOT/'vm-studio-2026'
def safe_error(e):
    return str(e)[:250] if isinstance(e,DeliveryError) else type(e).__name__
def facebook_file(meta,file,description):
    # L'envoi du fichier local garde le journal HD sans dépendre d'une URL CDN.
    import requests
    with Path(file).open('rb') as stream:
        result=requests.post('https://graph-video.facebook.com/'+meta['page_id']+'/videos',
            data={'description':description,'published':'true','access_token':meta['page_token']},
            files={'source':(Path(file).name,stream,'video/mp4')},timeout=(30,600),allow_redirects=False)
    try:data=result.json()
    except Exception:raise DeliveryError('Réponse vidéo Facebook illisible.') from None
    if result.status_code>=300 or data.get('error'):
        code=data.get('error',{}).get('code','?')
        raise DeliveryError(f'Facebook a refusé le fichier (HTTP {result.status_code}, code {code}).')
    return data.get('id')
def run():
    req=json.loads((BASE/'diffusion.json').read_text())
    if req.get('publish') is not True or req.get('id')!='vm-jt3d-2026-11-16-v1':
        raise DeliveryError('Publication ponctuelle non autorisée dans la demande.')
    today=dt.datetime.now(dt.timezone.utc).astimezone(__import__('zoneinfo').ZoneInfo('Europe/Paris')).date().isoformat()
    if today!='2026-11-16':raise DeliveryError('Édition datée : pas de diffusion automatique un autre jour.')
    media=json.loads((BASE/'published-media.json').read_text())
    if not re.fullmatch(r'https://cdn\.jsdelivr\.net/gh/Velocemercato/velocemercato\.fr@[0-9a-f]{40}/VM-[A-Za-z0-9-]+\.mp4',media['reel']['url']):
        raise DeliveryError('Adresse du Reel non autorisée.')
    statepath=Path(os.environ['RUNNER_TEMP'])/'vm-broadcast-state/state.enc'
    state=State(statepath,os.environ.get('VM_DIFFUSION_STATE_KEY',''),lambda:git_save(statepath))
    ensure_meta_targets(state);graph=Graph()
    receipts=state.data.setdefault('studio3d_publications',{}).setdefault(req['id'],{})
    results=[]
    def save(key,status,**data):
        receipts[key]={**receipts.get(key,{}),'status':status,'at':dt.datetime.now(dt.timezone.utc).isoformat(),**data};state.save()
    def record(key,status,**data):
        row=dict(destination=key,status=status,**data)
        old=next((r for r in results if r['destination']==key),None)
        if old is None:results.append(row)
        else:old.clear();old.update(row)
        print('::notice::STUDIO3D '+json.dumps(row,ensure_ascii=False),flush=True)
    credits='Personnages fictifs, voix de synthèse. Musique et plateau 3D originaux. Voix Piper UPMC (CC BY-SA 4.0) et SIWIS (CC BY 4.0), modifiées.'
    sources='Sources :\nhttps://www.fff.fr/article/17785-au-rendez-vous-des-quarts.html\nhttps://www.nhl.com/canucks/news/canucks-go-all-in-for-6-3-win-over-vegas-golden-knights\nhttps://www.rockstargames.com/VI'
    caption=('🎬 Le nouveau studio VM ouvre ses portes !\nVM Pronos, Pablo, Black, Scorpion et notre créatrice présentent le journal du 16 novembre.\n'
             'Au programme : les Bleus en quarts, les résultats de la nuit et le rendez-vous gaming de la semaine.\n\n'+credits+'\n\n'+sources+'\n\n#VeloceMercato #VMUnivers #ActualiteSportive #Animation3D')
    # Le Reel sur les cinq comptes ; le journal complet sur les trois pages.
    for fmt in ('reel','jt'):
        for account,pageid in PAGES.items():
            meta=state.data.get('tokens',{}).get(account,{})
            destinations=['facebook']+(['instagram'] if fmt=='reel' and account in ('meta','meta_univers') else [])
            for network in destinations:
                key=f'{fmt}/{network}/{account}'
                old=receipts.get(key,{})
                if old:
                    record(key,old.get('status','inconnu'),url=old.get('url',''),message='Reçu existant : aucun second envoi.');continue
                try:
                    if str(meta.get('page_id'))!=pageid or not meta.get('page_token'):raise DeliveryError('Destination absente ou différente de la page autorisée.')
                    identity=graph.call('GET',pageid,{'fields':'id,name','access_token':meta['page_token']})
                    if str(identity.get('id'))!=pageid:raise DeliveryError('Identité de page non confirmée.')
                    if network=='instagram':
                        if not meta.get('ig_id'):raise DeliveryError('Compte Instagram non connecté.')
                        ident=graph.call('GET',meta['ig_id'],{'fields':'id,username','access_token':meta['page_token']})
                        expected={'meta':'veloce.mercato','meta_univers':'vmunivers.fr'}[account]
                        if ident.get('username')!=expected:raise DeliveryError('Identité Instagram différente du compte autorisé.')
                    save(key,'envoi',media_sha256=media[fmt]['sha256'])
                    description=caption if fmt=='reel' else caption.replace('🎬 Le nouveau studio VM ouvre ses portes !','🎬 Le journal VM en intégralité — 10 minutes')
                    if network=='facebook':
                        filename='VM-Reel-3D-16-novembre-2026.mp4' if fmt=='reel' else 'VM-Journal-3D-16-novembre-2026.mp4'
                        ident=facebook_file(meta,ROOT/'output'/filename,description)
                        if not ident:raise DeliveryError('Identifiant vidéo Facebook absent.')
                        save(key,'traitement',id=str(ident))
                        data=graph.call('GET',str(ident),{'fields':'id,permalink_url,status','access_token':meta['page_token']})
                        url=data.get('permalink_url','')
                        if url.startswith('/'):url='https://www.facebook.com'+url
                        status='publie' if data.get('status',{}).get('video_status')=='ready' and url else 'traitement'
                    else:
                        ident=instagram_reel(graph,meta,{'verticale':media[fmt]['url'],'texte_vertical':description},wait=480)
                        if not ident:raise DeliveryError('Identifiant média Instagram absent.')
                        save(key,'traitement',id=str(ident))
                        data=graph.call('GET',str(ident),{'fields':'id,permalink,media_type','access_token':meta['page_token']})
                        url=data.get('permalink','');status='publie' if url else 'traitement'
                    save(key,status,id=str(ident),url=url);record(key,status,url=url,id=str(ident))
                except Exception as e:
                    # Conserver un éventuel ID : ne pas renvoyer une vidéo dont le résultat est incertain.
                    status='verification_requise' if receipts.get(key,{}).get('id') else 'echec'
                    save(key,status,error=safe_error(e));record(key,status,error=safe_error(e))
    key='jt/youtube'
    try:
        if receipts.get(key,{}).get('status')=='published':record(key,'published',url=receipts[key].get('url',''))
        elif os.getenv('VM_AUTO_YOUTUBE')!='true':record(key,'bloque',message='Interrupteur YouTube désactivé dans le projet.')
        else:
            http=HTTP();token=access_token('youtube',state,http);client=YouTube(http,state,token);client.verify_channel()
            receipt=receipts.setdefault(key,{})
            all_sources=json.loads((BASE/'scriptpack.json').read_text())['sources']
            desc='Le journal VM du 16 novembre 2026. Présenté par VM Pronos, avec Pablo, Black, Scorpion et notre créatrice.\n\n'+credits+'\n\nSources :\n'+'\n'.join(s[1]+' : '+s[3] for s in all_sources)
            metadata={'snippet':{'title':'Le nouveau JT VM en 3D — Les Bleus qualifiés, NHL, NBA et gaming | 16/11/2026','description':desc[:4900],'categoryId':'25','defaultLanguage':'fr'},'status':{'privacyStatus':'public','selfDeclaredMadeForKids':False,'containsSyntheticMedia':True}}
            client.upload(ROOT/'output/VM-Journal-3D-16-novembre-2026.mp4',metadata,receipt)
            client.make_public(receipt,timeout=600)
            record(key,receipt.get('status'),url=receipt.get('url',''))
    except Exception as e:record(key,'verification_requise',error=safe_error(e))
    # Relecture finale des vidéos encore en cours de traitement ; aucun nouvel envoi.
    for key,receipt in list(receipts.items()):
        if receipt.get('status') not in ('traitement','verification_requise') or not receipt.get('id'):continue
        try:
            fmt,network,account=key.split('/');meta=state.data['tokens'][account]
            fields='id,permalink_url,status' if network=='facebook' else 'id,permalink,media_type'
            data=graph.call('GET',receipt['id'],{'fields':fields,'access_token':meta['page_token']})
            url=data.get('permalink_url' if network=='facebook' else 'permalink','')
            if url.startswith('/'):url='https://www.facebook.com'+url
            ready=bool(url) and (network=='instagram' or data.get('status',{}).get('video_status')=='ready')
            if ready:save(key,'publie',url=url);record(key,'publie',url=url,id=receipt['id'])
        except Exception as e:record(key,'verification_requise',error=safe_error(e))
    (BASE/'publication-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    if any(r['status'] in ('echec','bloque','verification_requise') for r in results):sys.exit(1)
if __name__=='__main__':
    try:run()
    except Exception as e:print('::error::'+safe_error(e),flush=True);sys.exit(1)
