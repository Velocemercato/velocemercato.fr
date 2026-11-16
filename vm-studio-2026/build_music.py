from pathlib import Path
import numpy as np
from scipy.io.wavfile import write
from scipy.signal import butter,sosfilt
R=(Path(__file__).resolve().parents[1]/'reel3d');R.mkdir(exist_ok=True)
SR=44100;D=60;N=SR*D;B=60/112
rng=np.random.default_rng(3206)
mix=np.zeros((N,2),np.float32);wet=np.zeros_like(mix)
def hz(m):return 440*2**((m-69)/12)
def add(sig,start,amp=1,pan=0,reverb=False):
 i=round(start*SR)
 if i<0:sig=sig[-i:];i=0
 n=min(len(sig),N-i)
 if n<=0:return
 a=np.stack([sig[:n]*np.sqrt((1-pan)/2),sig[:n]*np.sqrt((1+pan)/2)],axis=1)*amp
 mix[i:i+n]+=a
 if reverb:wet[i:i+n]+=a
def tt(d):return np.arange(int(d*SR))/SR
def keys(m,d=1.3):
 t=tt(d);f=hz(m)
 env=(1-np.exp(-t*75))*np.exp(-t*2.0)*np.minimum(1,(d-t)*20)
 return (.72*np.sin(2*np.pi*f*t+1.2*np.exp(-t*4)*np.sin(2*np.pi*2*f*t))+.2*np.sin(2*np.pi*3*f*t)*np.exp(-t*7))*env
def bell(m,d=.55):
 t=tt(d);f=hz(m)
 return (np.sin(2*np.pi*f*t+.005*np.sin(t*29))+.18*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*5))*np.exp(-t*5)*(1-np.exp(-t*250))*np.minimum(1,(d-t)*30)
def bass(m,d=.3):
 t=tt(d);f=hz(m)
 x=np.sin(2*np.pi*f*t)+.27*np.sin(2*np.pi*f*2*t)+.1*np.sin(2*np.pi*f*3*t)
 return np.tanh(x*1.5)*np.exp(-t*5)*(1-np.exp(-t*180))*np.minimum(1,(d-t)*60)
def kick():
 t=tt(.36);phase=2*np.pi*(45*t+95*(1-np.exp(-t*38))/38)
 return np.sin(phase)*np.exp(-t*13)+.08*rng.normal(size=len(t))*np.exp(-t*260)
def clap():
 t=tt(.2);n=rng.normal(size=len(t));n=sosfilt(butter(2,[1100,7500],btype='bandpass',fs=SR,output='sos'),n)
 e=sum(np.where(t>=s,np.exp(-np.maximum(0,t-s)*55),0) for s in [0,.011,.022])
 return n*e*.7
def hat(opened=False):
 t=tt(.24 if opened else .065);n=rng.normal(size=len(t));n=sosfilt(butter(2,7000,btype='highpass',fs=SR,output='sos'),n)
 return n*np.exp(-t*(19 if opened else 80))
chords=[[50,53,57,60,64],[46,50,53,57,60],[48,52,55,58,62],[45,48,52,55,59]]
roots=[38,34,36,33]
melodies=[[74,None,77,81,79,None,77,74],[72,None,74,77,74,72,69,None],[74,77,None,79,81,None,84,81],[79,77,74,None,72,69,72,None]]
for bar in range(28):
 start=bar*4*B;ci=bar%4
 if bar==27:ci=0
 # Syncopated, warm electric-piano chords with independent stereo voices.
 for pos in ([0,1.5,2.75] if 2<=bar<26 else [0,2]):
  for j,m in enumerate(chords[ci]):add(keys(m),start+pos*B,.075,(-.65+.32*j),True)
 full=2<=bar<26 and bar not in [18,19]
 if full:
  for b in [0,1,2,3]:add(kick(),start+b*B,.58)
  for b in [1,3]:add(clap(),start+b*B,.29,.05)
  for b in range(8):add(hat(b%4==3),start+b*.5*B,.13 if b%2==0 else .1,.4)
  for pos,shift in [(0,0),(.75,12),(1.5,0),(2,0),(2.75,7),(3.5,12)]:add(bass(roots[ci]+shift),start+pos*B,.31,-.08)
 elif bar>=2:
  for b in [0,2]:add(bass(roots[ci],.55),start+b*B,.23)
 if bar>=4 and bar not in [18,19,27]:
  for j,m in enumerate(melodies[bar%4]):
   if m is not None:add(bell(m,.7),start+j*.5*B,.14 if bar<16 else .17,(-.22 if j%2 else .22),True)
 # A soft glistening upstroke gives the track lift without a vocal sample.
 if bar in [3,7,11,15,23,25]:
  for j,m in enumerate([62,65,69,72,77,81]):add(bell(m,.4),start+3.5*B+j*.055,.11,(-.5+j*.2),True)
for s in [8,16,24,32]:
 for j,m in enumerate([74,77,81]):add(bell(m,.75),s+j*.075,.22,0,True)
# Comic spring sound for the deliberately wobbly dance step.
t=tt(.65);f=190+280*np.exp(-t*7)*np.sin(2*np.pi*8*t)
x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6)
add(x,42,.28,0,True)
for delay,gain in [(.113,.18),(.197,.14),(.307,.1),(.431,.07)]:
 k=int(delay*SR);mix[k:]+=wet[:-k,::-1]*gain
# Fade-in and a resolving final D-minor chord.
for j,m in enumerate([50,57,62,65,69,74]):add(keys(m,2),58+j*.012,.15,-.6+j*.24,True)
fade=np.ones(N);fade[:int(.35*SR)]=np.linspace(0,1,int(.35*SR));fade[-int(1.1*SR):]=np.linspace(1,0,int(1.1*SR))
mix*=fade[:,None];mix=np.tanh(mix*1.12);mix*=.88/max(.001,np.max(abs(mix)))
write(R/'musique-originale.wav',SR,(mix*32767).astype(np.int16))

print("Musique originale VM terminée.")
