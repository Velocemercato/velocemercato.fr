"""Préparation et validation des médias publics de la nouvelle édition."""
import os, sys, json, re, hashlib, subprocess, urllib.request, datetime as dt, shutil
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'vm-studio-2026'
def command(*args,**kw):return subprocess.check_output(args,**kw).decode().strip()
def request():
    req=json.loads((ROOT/'.github/vm-studio3d-request.json').read_text())
    if req.get('id')!='vm-jt3d-2026-11-16-v1' or req.get('publish') is not True:raise RuntimeError('Demande de diffusion non autorisée.')
    if dt.datetime.now(ZoneInfo('Europe/Paris')).date().isoformat()!='2026-11-16':raise RuntimeError('Édition périmée : ne pas republier.')
    if not re.fullmatch('[0-9a-f]{40}',req.get('asset_commit','')):raise RuntimeError('Plans 3D non référencés par un commit exact.')
    return req
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obtain():
    req=request();(BASE/'renders').mkdir(exist_ok=True);(ROOT/'voices').mkdir(exist_ok=True)
    for name in ('wide','vm','portrait','pablo','black','scorpion','creatrice'):
        out=BASE/'renders'/f'{name}.mp4'
        urllib.request.urlretrieve(f'https://cdn.jsdelivr.net/gh/Velocemercato/velocemercato.fr@{req["asset_commit"]}/{name}.mp4',out)
        if digest(out)!=req['asset_sha256'][name]:raise RuntimeError('Plan 3D différent de la version vérifiée : '+name)
    for name in ('upmc','siwis'):
        for ext in ('.onnx','.onnx.json'):
            out=ROOT/'voices'/f'fr_FR-{name}-medium{ext}'
            urllib.request.urlretrieve(f'https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/{name}/medium/fr_FR-{name}-medium{ext}',out)
def download_masters():
    req=request();(ROOT/'output').mkdir(exist_ok=True)
    for field in ('parts_commit','reel_commit'):
        if not re.fullmatch('[0-9a-f]{40}',req.get(field,'')):raise RuntimeError('Version exacte des médias manquante.')
    media={}
    for name,(filename,*_) in videos().items():
        spec=req['masters'][name]
        if not re.fullmatch('[0-9a-f]{64}',spec.get('sha256','')):raise RuntimeError('Empreinte média invalide.')
        out=ROOT/'output'/filename
        with out.open('wb') as target:
            for part in spec['parts']:
                if not re.fullmatch(r'masters/(reel|jt|pastille)-[0-9]{3}\.bin',part):raise RuntimeError('Chemin média non autorisé.')
                url=f'https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/{req["parts_commit"]}/{part}'
                with urllib.request.urlopen(url,timeout=120) as source:shutil.copyfileobj(source,target)
        if digest(out)!=spec['sha256']:raise RuntimeError('La vidéo reçue diffère de la vidéo validée : '+name)
        media[name]={'sha256':spec['sha256']}
    media['reel']['url']=f'https://cdn.jsdelivr.net/gh/Velocemercato/velocemercato.fr@{req["reel_commit"]}/VM-Reel-3D-16-novembre-2026.mp4'
    (BASE/'published-media.json').write_text(json.dumps(media,ensure_ascii=False,indent=2))
    print('Trois vidéos exactes récupérées ; empreintes vérifiées.',flush=True)
def videos():
    return {'reel':('VM-Reel-3D-16-novembre-2026.mp4',60,1080,1920),'jt':('VM-Journal-3D-16-novembre-2026.mp4',600,1280,720),'pastille':('VM-Pastille-3D-16-novembre-2026.mp4',150,1280,720)}
def validate():
    request()
    for name,(filename,duration,width,height) in videos().items():
        p=ROOT/'output'/filename
        data=json.loads(command('ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)))
        v=next(x for x in data['streams'] if x['codec_type']=='video');a=next(x for x in data['streams'] if x['codec_type']=='audio')
        if abs(float(data['format']['duration'])-duration)>.12 or (v['width'],v['height'],v['codec_name'],a['codec_name'])!=(width,height,'h264','aac'):raise RuntimeError('Format ou durée non conforme : '+name)
        if v['avg_frame_rate']!='24/1':raise RuntimeError('Cadence vidéo non conforme.')
        command('ffmpeg','-v','error','-i',str(p),'-f','null','-')
        print('VALIDÉ',name,duration,width,height,digest(p),flush=True)
def publish_media():
    validate();req=request()
    repo=Path(os.environ['RUNNER_TEMP'])/'vm-studio3d-media'
    subprocess.run(['git','-c','credential.helper=!gh auth git-credential','clone','--quiet','--depth','1','--branch','vm-studio3d-media','https://github.com/Velocemercato/velocemercato.fr.git',str(repo)],check=True)
    for filename,*_ in videos().values():shutil.copy2(ROOT/'output'/filename,repo/filename)
    def git(*args):return command('git','-c','credential.helper=!gh auth git-credential','-C',str(repo),*args)
    git('add','*.mp4');git('-c','user.name=github-actions[bot]','-c','user.email=41898282+github-actions[bot]@users.noreply.github.com','commit','-m','Édition VM 3D du 16 novembre, médias contrôlés')
    git('push','origin','HEAD:vm-studio3d-media');sha=git('rev-parse','HEAD')
    media={k:{'url':f'https://cdn.jsdelivr.net/gh/Velocemercato/velocemercato.fr@{sha}/{v[0]}','sha256':digest(ROOT/'output'/v[0])} for k,v in videos().items()}
    (BASE/'published-media.json').write_text(json.dumps(media,ensure_ascii=False,indent=2))
    print('MÉDIAS CONTRÔLÉS À DISPOSITION',sha,flush=True)
if __name__=='__main__':
    if '--download-masters' in sys.argv:download_masters()
    elif '--validate' in sys.argv:validate()
    elif '--publish-media' in sys.argv:publish_media()
    else:obtain()
