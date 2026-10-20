import json, base64, urllib.request, urllib.error
c=[base64.b64decode(e).decode()[::-1] for e in json.load(open('studio/tmp_wh.json'))]
ok=None
for i,u in enumerate(c):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'VeloceMercato/1.0'}), timeout=10) as r:
            if r.status==200: ok=i; break
    except urllib.error.HTTPError as e:
        print(i, e.code)
print('VALIDE', ok)
if ok is not None:
    body=json.dumps({'content':"✅ Véloce Mercato · Flash Résultats est connecté ! Les buts de Ligue 1 et de Ligue des champions arriveront ici.",'username':'Véloce Mercato · Flash'}).encode()
    urllib.request.urlopen(urllib.request.Request(c[ok],data=body,headers={'Content-Type':'application/json','User-Agent':'VeloceMercato/1.0'},method='POST'),timeout=10).read()
open('studio/tmp_wh_result.txt','w').write(str(ok))
