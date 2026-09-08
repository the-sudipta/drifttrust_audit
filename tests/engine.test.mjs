import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {newState,processBatch,predict,transform,digest,consistency,clone} from '../runtime/engine.mjs';
const read=name=>JSON.parse(fs.readFileSync(`assets/research/${name}.json`));
const b=read('model'),replay=read('replay').rows,parity=read('parity');
test('JavaScript inference matches independent sklearn predictions to 1e-10',()=>{
 for(let i=0;i<parity.rows.length;i++)assert.ok(Math.abs(predict(b,b.model,parity.rows[i].x)-parity.attack_probabilities[i])<1e-10);
});
test('invalid inputs never silently coerce or clip invalid values',()=>{
 for(const x of [[],['1'],Array(12).fill(NaN),Array(12).fill(-1),Array(12).fill(Infinity)])assert.throws(()=>transform(b,x));
});
test('identical, reversed and tied rankings have defined ECI',()=>{
 assert.equal(consistency([1,2,3],[1,2,3]).eci,1);
 assert.equal(consistency([0,0,0],[0,0,0]).eci,1);
 assert.ok(consistency([1,2,3],[3,2,1]).eci<1);
});
test('current batch predictions do not depend on its unrevealed feedback',async()=>{
 const a=newState(b),c=newState(b);const input=replay.slice(0,32);
 const x=await processBatch(b,a,input),y=await processBatch(b,c,input.map(r=>({...r,y:1-r.y})));
 assert.deepEqual(x.scores,y.scores);
});
test('unlabelled streams never train on predictions or invented labels',async()=>{
 const s=newState(b);const initial=await digest(s.model);
 for(let i=0;i<256;i+=32)await processBatch(b,s,replay.slice(i,i+32).map(r=>({...r,y:null})));
 assert.equal(s.labeled,0);assert.equal(s.attempts,0);assert.equal(await digest(s.model),initial);
});
test('audit-only instrumentation preserves ungoverned prediction sequence',async()=>{
 const a=newState(b,'ungoverned'),c=newState(b,'monitor_only');
 for(let i=0;i<replay.length;i+=32){
  const x=await processBatch(b,a,replay.slice(i,i+32)),y=await processBatch(b,c,replay.slice(i,i+32));
  assert.deepEqual(x.scores,y.scores);
 }
 assert.equal(await digest(a.model),await digest(c.model));assert.ok(c.attempts>0);
});
test('rejected candidate leaves model unchanged and audit chain is verifiable',async()=>{
 const cfg=clone(b);cfg.config.attribution_threshold=-1;cfg.config.max_anchor_loss_increase=-10;
 const s=newState(cfg);const initial=await digest(s.model);const events=[];
 for(let i=0;i<512;i+=32){const r=await processBatch(cfg,s,replay.slice(i,i+32));if(r.event)events.push(r.event);}
 assert.ok(events.length>0);assert.equal(s.accepted,0);assert.equal(await digest(s.model),initial);
 let prev=null;
 for(const event of events){const {record_sha256,...content}=event;assert.equal(event.previous_record_sha256,prev);assert.equal(await digest(content),record_sha256);assert.equal(event.model_before_sha256,event.active_model_sha256);prev=record_sha256;}
});
