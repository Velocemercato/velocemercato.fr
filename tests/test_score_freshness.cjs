const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const code=fs.readFileSync(require('path').join(__dirname,'../scores/app.js'),'utf8');
const start=code.indexOf('function freshRows('),end=code.indexOf('async function load()',start),ctx={};vm.createContext(ctx);vm.runInContext(code.slice(start,end),ctx);
const now=Date.parse('2026-11-25T21:00:00Z');
const tests=[
 ['recent', '2026-11-25T20:59:00Z','2026-11-25T20:00:00Z','IN_PLAY','IN_PLAY'],
 ['stale','2026-11-25T18:00:00Z','2026-11-25T20:00:00Z','IN_PLAY','UNAVAILABLE'],
 ['invalid','bad','2026-11-25T20:00:00Z','PAUSED','UNAVAILABLE'],
 ['missing',null,'2026-11-25T20:00:00Z','IN_PLAY','UNAVAILABLE'],
 ['old kickoff','2026-11-25T20:59:00Z','2026-11-24T20:00:00Z','IN_PLAY','UNAVAILABLE'],
 ['future clock','2026-11-26T20:59:00Z','2026-11-25T20:00:00Z','IN_PLAY','UNAVAILABLE'],
 ['future kickoff','2026-11-25T20:59:00Z','2026-11-26T20:00:00Z','IN_PLAY','UNAVAILABLE'],
 ['finished preserved',null,'2026-11-24T20:00:00Z','FINISHED','FINISHED'],
 ['scheduled',null,'2026-11-26T20:00:00Z','TIMED','TIMED'],
 ['halftime fresh','2026-11-25T20:59:00Z','2026-11-25T20:00:00Z','PAUSED','PAUSED']
];
for(const sport of ['foot','basket'])for(const [name,stamp,date,statut,expect] of tests){const row={sport,date,statut,score:[1,1]};const got=ctx.freshRows([row],stamp,now)[0];assert.equal(got.statut,expect);assert.equal(row.statut,statut);console.log('PASS',sport,name)}
console.log('20/20 freshness scenarios; synthetic fixtures, not verification of 20 live results.');
