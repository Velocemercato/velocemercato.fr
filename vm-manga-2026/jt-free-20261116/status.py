"""Read-only progress check. Print only public publication receipt fields."""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.diffuser_jt import State
from tools.publier_meta import Graph
sp=Path(os.environ['RUNNER_TEMP'])/'vm-broadcast-state/state.enc'
state=State(sp,os.environ.get('VM_DIFFUSION_STATE_KEY',''))
rows=state.data.get('manga_jt_publications',{}).get('vm-jt-manga-free-20261116-v1',{})
for key,row in rows.items():
 safe={k:row[k] for k in ['status','id','url','container_id','at','error'] if k in row}
 if row.get('id') and row.get('status')!='published':
  _,network,account=key.split('/');meta=state.data['tokens'][account]
  try:
   fields='id,permalink_url,status' if network=='facebook' else 'id,permalink,media_type'
   live=Graph().call('GET',row['id'],{'fields':fields,'access_token':meta['page_token']})
   url=live.get('permalink_url' if network=='facebook' else 'permalink','')
   if url.startswith('/'):url='https://www.facebook.com'+url
   if url and (network=='instagram' or live.get('status',{}).get('video_status')=='ready'):
    safe.update(status='published',url=url,verification='live read-only check')
  except Exception:safe['verification']='status temporarily unavailable'
 print('JT_STATUS '+json.dumps({'destination':key,**safe},ensure_ascii=False))
 if row.get('container_id') and row.get('status')!='published':
  account=key.split('/')[-1];meta=state.data['tokens'][account]
  try:
   info=Graph().call('GET',row['container_id'],{'fields':'status_code,status','access_token':meta['page_token']})
   print('JT_CONTAINER '+json.dumps({'destination':key,'status_code':info.get('status_code'),'detail':str(info.get('status',''))[:200]},ensure_ascii=False))
  except Exception:print('JT_CONTAINER '+json.dumps({'destination':key,'status_code':'unavailable'}))
