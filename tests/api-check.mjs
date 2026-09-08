/** Integration check against the actual running Worker adapter or deployed service. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {digest,predict,newState,processBatch} from '../runtime/engine.mjs';
const base=process.argv[2]||'http://localhost:8787';
const bundle=JSON.parse(fs.readFileSync('assets/research/model.json'));
const replay=JSON.parse(fs.readFileSync('assets/research/replay.json')).rows;
function client(){let cookie='';return async(path,body,expected=200,extra={})=>{
 const r=await fetch(base+path,{method:body===undefined?'GET':'POST',headers:{Cookie:cookie,...(body!==undefined?{'Content-Type':'application/json'}:{}),...extra},body:body===undefined?undefined:JSON.stringify(body)});
 if(r.headers.get('set-cookie'))cookie=r.headers.get('set-cookie').split(';')[0];
 const data=await r.json();assert.equal(r.status,expected,JSON.stringify(data));return data;
};}
const a=client(),b=client();
assert.equal((await a('/api/health')).status,'ok');
await a('/api/session',undefined,401);
let sa=await a('/api/session',{mode:'monitor_only'},201);let sb=await b('/api/session',{mode:'governed'},201);
const x=replay[0].x;
const baseline=await a('/api/infer',{x});assert.ok(Math.abs(baseline.attack_probability-predict(bundle,bundle.model,x))<1e-10);
await a('/api/infer',{x:[]},400);await a('/api/infer',{x:x.map(()=>-1)},400);
await a('/api/infer',{x},403,{Origin:'https://untrusted.example'});
await a('/api/stream',{revision:0,request_id:crypto.randomUUID(),rows:[{x,y:3}]},400);
assert.equal((await a('/api/session')).revision,0);
// Replay parity uses the exact same records, batch ordering and actual shared engine.
const state=newState(bundle,'monitor_only');const expected=[];
for(let i=0;i<128;i+=32){const r=await processBatch(bundle,state,replay.slice(i,i+32));expected.push(...r.scores);}
const id=crypto.randomUUID(),body={revision:sa.revision,request_id:id,count:128};
const first=await a('/api/replay',body);assert.deepEqual(first.predictions.map(p=>p.attack_probability),expected);
const retry=await a('/api/replay',body);assert.deepEqual(retry,first);sa=first;
await a('/api/replay',{revision:0,request_id:crypto.randomUUID(),count:32},409);
assert.equal((await b('/api/session')).seen,0);assert.equal((await b('/api/audit')).records.length,0);
while(sa.replay_cursor<replay.length)sa=await a('/api/replay',{revision:sa.revision,request_id:crypto.randomUUID(),count:256});
const audit=await a('/api/audit');assert.ok(audit.records.length>0);let head=null;
for(const record of audit.records){const {record_sha256,...rest}=record;assert.equal(await digest(rest),record_sha256);assert.equal(rest.previous_record_sha256,head);head=record_sha256;}
assert.equal(head,audit.chain_head);
assert.equal((await b('/api/infer',{x})).model_sha256,baseline.model_sha256);
// A visitor supplied stream without labels is inference-only.
sb=await b('/api/stream',{revision:sb.revision,request_id:crypto.randomUUID(),rows:[{x,y:null}]});
assert.equal(sb.labeled,0);assert.equal(sb.attempts,0);
await b('/api/stream',{revision:sb.revision,request_id:crypto.randomUUID(),rows:[]},400);
const report={base,checked_at_utc:new Date().toISOString(),passed:true,checks:['health and database','independent Python inference parity','same-engine replay parity','invalid input rejection','cross-origin write rejection','session isolation','idempotent retries','stale revision rejection','full replay','audit hash-chain integrity','unlabelled inference-only stream'],replay_flows:sa.seen,actual_candidates:audit.records.length,accepted:sa.accepted,rejected:sa.rejected};
console.log(JSON.stringify(report,null,2));
fs.mkdirSync('.local',{recursive:true});fs.writeFileSync('.local/api-check.json',JSON.stringify(report,null,2));
