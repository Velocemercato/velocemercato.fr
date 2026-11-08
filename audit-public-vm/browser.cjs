const fs = require('node:fs');
const {chromium}=require('playwright');
const base='https://velocemercato.fr';
const routes=['/','/actus/','/multisport/','/multisport/nba/','/multisport/tennis/','/vm-gaming/','/gaming','/foot-amateur/','/foot-amateur/?region=GES','/foot-amateur/territoires/','/belfort/','/scores/','/pronos/','/pronos/#pronos-du-jour','/mangas/','/series/','/studio','/web-studio#devis','/pub/#packs','/soutenir','/kit-du-jour','/kit-pronos','/immo/','/comparateur/','/emplois/','/emploi/','/services/','/cv/','/ou-regarder','/archives','/regions/','/selection-amazon','/shop/','/allolivre/','/pepite/','/menu/','/mentions-legales','/vm-page-audit-inexistante-20261108'];
const sizes=[320,390,768,1440];
const out=[], controls=[], interactive=[], checks=[];
const ptime=()=>new Date().toLocaleString('sv-SE',{timeZone:'Europe/Paris'});
async function run(){
  const browser=await chromium.launch();
  let pos=0;
  const queue=routes.flatMap(route=>sizes.map(width=>({route,width})));
  async function worker(){
    while(pos<queue.length){
      const {route,width}=queue[pos++];const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'});
      const errors=[],resources=[];
      page.on('pageerror',e=>errors.push(e.message.slice(0,200)));
      page.on('response',r=>{const u=r.url();if(r.status()>=400&&u.startsWith(base)) resources.push([r.status(),u.replace(/\?.*$/,'')]);});
      const record={route,width,at:ptime()};
      try{
        const reply=await page.goto(base+route,{waitUntil:'domcontentloaded',timeout:17000});
        await page.locator('body').waitFor({timeout:4000});
        if(width===390) await page.waitForLoadState('load',{timeout:4000}).catch(()=>{});
        Object.assign(record,{http:reply?.status(),url:page.url()},await page.evaluate(()=>{
          const d=document, w=d.documentElement.clientWidth;
          const shown=e=>!!e.getClientRects().length && getComputedStyle(e).visibility!=='hidden';
          const hash=decodeURIComponent(location.hash.slice(1));
          const widgets=[...d.querySelectorAll('button, [role=button], [role=tab], summary, input[type=button], input[type=submit], select')];
          return {title:d.title,h1:[...d.querySelectorAll('h1')].filter(shown).length,scroll:d.documentElement.scrollWidth,client:w,
            anchors:[...d.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href')).filter(x=>x.length>1&&!d.getElementById(x.slice(1))&&!x.includes('=')),
            target:hash?!!d.getElementById(hash):null,
            controls:widgets.length,visible:widgets.filter(shown).length,
            noName:widgets.filter(e=>shown(e)&&!(e.innerText||e.getAttribute('aria-label')||e.getAttribute('aria-labelledby')||e.getAttribute('title')||e.value||e.labels?.length)).map(e=>[e.tagName,e.id]).slice(0,12),
            floating:[...d.querySelectorAll('a,button')].filter(e=>shown(e)&&getComputedStyle(e).position==='fixed').map(e=>e.innerText.trim()).slice(0,8),
            overflow:d.documentElement.scrollWidth>w?[...d.querySelectorAll('body *')].filter(e=>shown(e)&&!e.closest('svg')).map(e=>[e.tagName,e.id,Math.round(e.getBoundingClientRect().right)]).filter(e=>e[2]>w+3).sort((a,b)=>b[2]-a[2]).slice(0,8):[],
            hero:!!d.querySelector('.hero-img')?.naturalWidth};
        }));
        if(width===390&&reply?.ok()){
          const detail=await page.evaluate(()=>{
            const shown=e=>!!e.getClientRects().length && getComputedStyle(e).visibility!=='hidden';
            return [...document.querySelectorAll('button,[role=button],[role=tab],summary,input[type=button],input[type=submit],select')].map((e,i)=>({i,tag:e.tagName,id:e.id,label:(e.getAttribute('aria-label')||e.innerText||e.getAttribute('title')||e.value||'').trim().slice(0,120),visible:shown(e),type:e.getAttribute('type')||'',role:e.getAttribute('role')||''}));
          });
          controls.push(...detail.map(e=>({route,...e})));
          const details=page.locator('details > summary:visible');
          const n=await details.count();
          for(let i=0;i<n;i++){
            const el=details.nth(i);
            const label=(await el.innerText({timeout:3000})).slice(0,120);
            if(/don|paiement|inscription|connexion|authentification/i.test(label))continue;
            try{
              const before=await el.evaluate(e=>e.parentElement.open);
              await el.click({timeout:2400});
              const after=await el.evaluate(e=>e.parentElement.open);
              interactive.push({route,kind:'volet',label,state:before!==after?'ok':'inchange'});
              if(before!==after) await el.click({timeout:2400});
            }catch(e){interactive.push({route,kind:'volet',label,state:'non conclu',reason:e.message.split('\n')[0].slice(0,150)});}
          }
          for(const sel of ['[role=tab]:visible','button[aria-pressed]:visible']){
            const els=page.locator(sel);
            const num=Math.min(await els.count(),12);
            for(let i=0;i<num;i++){
              const el=els.nth(i);
              const label=(await el.innerText({timeout:3000})).trim().slice(0,90);
              if(!label||/alert|favori|signal|connexion|partager|acheter|envoi|consent|notifi|install|réserver|localis|abonn|suivre|découvrir|lire|comment|copier/i.test(label)||!(/tout|basket|nba|foot|sport|région|district|europe|international|direct|termin|venir|actus|gaming|warzone|tennis|manga|séries|saison|coupe|f1|motogp|nfl|n2|ligue|filtre/i.test(label)))continue;
              try{
                const get=()=>el.evaluate(e=>[e.getAttribute('aria-pressed'),e.getAttribute('aria-selected'),e.className,document.querySelector('main')?.innerText.slice(0,200)]);
                const before=JSON.stringify(await get());await el.click({timeout:2500});const after=JSON.stringify(await get());
                interactive.push({route,kind:'filtre/onglet',label,state:before!==after?'ok':'inchange'});
              }catch(e){interactive.push({route,kind:'filtre/onglet',label,state:'non conclu',reason:e.message.split('\n')[0].slice(0,150)});}
            }
          }
          if(route==='/'){
            checks.push({case:'lien VM Univers',route,result:await page.locator('header .nav-univers').getAttribute('href').catch(()=>null)});
          }
          if(route==='/kit-du-jour'||route==='/kit-pronos'){
            const click=page.getByRole('button',{name:/copier le texte/i}).first();
            if(await click.count()) {
              try{
                await page.context().grantPermissions(['clipboard-read','clipboard-write']);
                await click.click({timeout:4000});
                const clip=await page.evaluate(()=>navigator.clipboard.readText());
                checks.push({case:'copie',route,result:clip.length});
              }catch(e){checks.push({case:'copie',route,result:e.message.split('\n')[0].slice(0,150)});}
            }
            const btn=page.getByRole('button',{name:/télécharger le visuel/i}).first();
            if(await btn.count()) {
              try{
                const [download]=await Promise.all([page.waitForEvent('download',{timeout:5000}),btn.click({timeout:4000})]);
                const file=await download.path();
                const img=fs.readFileSync(file);
                checks.push({case:'PNG',route,result:[img.subarray(1,4).toString(),img.readUInt32BE(16),img.readUInt32BE(20),img.length]});
              }catch(e){checks.push({case:'PNG',route,result:e.message.split('\n')[0].slice(0,150)});}
            }
          }
        }
      }catch(e){record.error=e.message.split('\n')[0].slice(0,200);}
      record.pageErrors=[...new Set(errors)].slice(0,8);
      record.httpErrors=[...new Map(resources.map(x=>[x[1],x])).values()].slice(0,15);
      out.push(record);await page.close();
    }
  }
  try{await Promise.all(Array.from({length:5},worker));}finally{await browser.close();}
  const summary={at:ptime(),cases:out.length,routes:routes.length,overflow:out.filter(x=>x.scroll>x.client).map(({route,width,scroll,overflow})=>({route,width,scroll,overflow})),missing:out.filter(x=>x.http>=400||x.error).map(({route,width,http,error})=>({route,width,http,error})),hash:out.filter(x=>x.target===false).map(x=>[x.route,x.width]),renderedAnchors:out.filter(x=>x.width===390&&x.anchors?.length).map(x=>[x.route,[...new Set(x.anchors)].slice(0,10)]),duplicateH1:out.filter(x=>x.width===390&&x.h1>1).map(x=>[x.route,x.h1]),noName:out.filter(x=>x.width===390&&x.noName?.length).map(x=>[x.route,x.noName]),pageErrors:out.filter(x=>x.width===390&&x.pageErrors.length).map(x=>[x.route,x.pageErrors]),httpErrors:out.filter(x=>x.width===390&&x.httpErrors.length).map(x=>[x.route,x.httpErrors]),controls:controls.length,visibleControls:controls.filter(x=>x.visible).length,tested:interactive.length,ok:interactive.filter(x=>x.state==='ok').length,interactionFindings:interactive.filter(x=>x.state!=='ok').slice(0,35),checks};
  for(const [file,data] of Object.entries({'browser':out,'controles':controls,'interactions':interactive,'synthese-browser':summary}))fs.writeFileSync('evidence/'+file+'.json',JSON.stringify(data,null,2));
  console.log('VM_BROWSER '+JSON.stringify(summary));
}
run().catch(e=>{console.error(e);process.exitCode=1;});
