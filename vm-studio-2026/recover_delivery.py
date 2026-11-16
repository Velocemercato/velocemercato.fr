"""Reconstruction et livraison ponctuelles, séparées de la publication sociale."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'vm-studio-2026'
OUT = ROOT / 'output'
REPO = 'https://github.com/Velocemercato/velocemercato.fr.git'
RAW = 'https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/'
ASSET = '3e1de38dc40d425aa7cbf7fe6093df610533c425'
SHOTS = {
    'pablo':'c9c99e8aa0678df6477d6b34a8aff7f0b4d05f6c14d9c2a9ffe613384a326005',
    'creatrice':'17f9141b70b720d4516352eabd1ecba55ada74e157dbb213f8f1996befcbbd13',
    'scorpion':'8ea49ae4c177d0b5b1f63348576d12b54649c8ece1e0eaedd5de3f39904f5786',
    'black':'fa02586bb6aebe7451f314dc34786116ca7be21869df3744fe280fa110a55caa',
    'portrait':'6ed0c48e1f4c87f39b9b49068101831c837232f0ff52783db435af2fafd43a66',
    'vm':'71bfc36e4d3af86c1d87425497ab51174b9ad9c5e5faeb7e6c8e7fa488f6842b',
    'wide':'66ccdb1dfb54bf6160a5dbef6ef4fb29db3b6218a897798ce7b56318fd618128',
}
FORMATS = {
    'reel':('VM-Reel-3D-16-novembre-2026.mp4',60,1080,1920),
    'pastille':('VM-Pastille-3D-16-novembre-2026.mp4',150,1280,720),
    'jt':('VM-Journal-3D-16-novembre-2026.mp4',600,1280,720),
}

def run(*args, cwd=ROOT):
    return subprocess.check_output(list(map(str,args)),cwd=cwd).decode().strip()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def request():
    req=json.loads((ROOT/'.github/vm-studio3d-recovery.json').read_text())
    if req.get('id')!='vm-jt3d-2026-11-16-v1':
        raise ValueError('Édition inattendue')
    if dt.datetime.now(ZoneInfo('Europe/Paris')).date().isoformat()!='2026-11-16':
        raise ValueError('Édition périmée')
    return req

def fetch(url,path,sha=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(url,timeout=120) as response, path.open('wb') as target:
        shutil.copyfileobj(response,target)
    if sha and digest(path)!=sha:
        raise ValueError('Empreinte non conforme : '+path.name)

def prepare():
    request()
    for name,sha in SHOTS.items():
        fetch(RAW+ASSET+'/'+name+'.mp4',BASE/'renders'/f'{name}.mp4',sha)
    for name in ('upmc','siwis'):
        for ext in ('.onnx','.onnx.json'):
            filename=f'fr_FR-{name}-medium{ext}'
            fetch(f'https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/{name}/medium/{filename}',ROOT/'voices'/filename)

def validate():
    manifest={}
    OUT.mkdir(exist_ok=True)
    for name,(filename,duration,width,height) in FORMATS.items():
        path=OUT/filename
        data=json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',path))
        video=next(s for s in data['streams'] if s['codec_type']=='video')
        audio=next(s for s in data['streams'] if s['codec_type']=='audio')
        if (video['width'],video['height'],video['codec_name'],audio['codec_name'],video['avg_frame_rate'])!=(width,height,'h264','aac','24/1'):
            raise ValueError('Format non conforme : '+name)
        if abs(float(data['format']['duration'])-duration)>.12:
            raise ValueError('Durée non conforme : '+name)
        # Décodage intégral, puis mesure du niveau sonore.
        run('ffmpeg','-v','error','-i',path,'-f','null','-')
        measured=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True).stderr
        peak=float(re.search(r'max_volume: ([-.0-9]+) dB',measured).group(1))
        if peak>=0 or peak < -35:
            raise ValueError('Niveau sonore non conforme : '+name)
        manifest[name]={'filename':filename,'sha256':digest(path),'duration':float(data['format']['duration']),'width':width,'height':height,'bytes':path.stat().st_size,'max_volume_db':peak}
        for number,at in enumerate((1,duration*.30,duration*.65,duration-2)):
            run('ffmpeg','-v','error','-y','-ss',at,'-i',path,'-frames:v','1','-vf','scale=480:-2',OUT/f'{name}-preview-{number}.jpg')
        print('VALIDÉ',name,duration,width,height,peak,flush=True)
    (OUT/'media-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return manifest

def git(*args,cwd):
    return run('git','-c','credential.helper=!gh auth git-credential',*args,cwd=cwd)

def save_media():
    request()
    validate()
    folder=Path(os.environ['RUNNER_TEMP'])/'vm-studio3d-media'
    branch='vm-studio3d-media'
    exists=run('git','ls-remote','--heads',REPO,'refs/heads/'+branch)
    if exists:
        git('clone','--quiet','--depth','1','--branch',branch,REPO,folder,cwd=ROOT)
    else:
        folder.mkdir()
        git('init','-b',branch,cwd=folder)
        git('remote','add','origin',REPO,cwd=folder)
    for path in OUT.iterdir():
        if path.suffix in ('.mp4','.json','.jpg'):
            shutil.copy2(path,folder/path.name)
    git('add','.',cwd=folder)
    git('-c','user.name=github-actions[bot]','-c','user.email=41898282+github-actions[bot]@users.noreply.github.com','commit','-m','Trois exports VM 3D contrôlés du 16 novembre',cwd=folder)
    git('push','origin','HEAD:'+branch,cwd=folder)
    print('MEDIA_COMMIT='+git('rev-parse','HEAD',cwd=folder),flush=True)

def download_reviewed():
    req=request()
    sha=req.get('media_commit','')
    if req.get('mode')!='publish' or not re.fullmatch('[a-f0-9]{40}',sha):
        raise ValueError('Médias à publier non validés')
    media={}
    for name,(filename,*_) in FORMATS.items():
        expected=req['media_sha256'][name]
        if not re.fullmatch('[a-f0-9]{64}',expected):
            raise ValueError('Empreinte absente')
        fetch(RAW+sha+'/'+filename,OUT/filename,expected)
        media[name]={'sha256':expected,'url':f'https://cdn.jsdelivr.net/gh/Velocemercato/velocemercato.fr@{sha}/{filename}'}
    validate()
    (BASE/'published-media.json').write_text(json.dumps(media,indent=2))
    (BASE/'diffusion.json').write_text(json.dumps({'id':req['id'],'publish':True}))

if __name__=='__main__':
    {'prepare':prepare,'validate':validate,'save-media':save_media,'download-reviewed':download_reviewed}[sys.argv[1]]()
