import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {newState,processBatch,predict,clone,digest} from '../runtime/engine.mjs';
import {forwardTrace,parameterStep,logitContributions} from '../runtime/math-trace.mjs';
const b=JSON.parse(fs.readFileSync('assets/research/model.json'));
const rows=JSON.parse(fs.readFileSync('assets/research/replay.json')).rows;
const close=(a,c)=>assert.ok(Math.abs(a-c)<1e-12,`${a} differs from ${c}`);
test('logit contribution ranking uses signed activation times weight and excludes the bias',()=>{
 const examples=JSON.parse(fs.readFileSync('assets/research/examples.json'));
 for(const [id,expected] of [[20635,15],[115485,9]]){
  const t=forwardTrace(b,b.model,examples.find(r=>r.id===id).x),original=clone(t),c=logitContributions(t);
  assert.equal(c.strongest,expected);assert.deepEqual(c.terms,t.output_terms);close(c.sum+c.bias,t.logit);assert.deepEqual(t,original);
 }
 const t={hidden:[1,-1,0],model:{w2:[2,2,9],b2:100}},c=logitContributions(t);
 assert.equal(c.strongest,0);assert.deepEqual(c.ties,[0,1]);assert.deepEqual(c.terms,[2,-2,0]);assert.equal(c.extent,100);
 const zero=logitContributions({hidden:[0,0],model:{w2:[0,0],b2:0}});assert.equal(zero.extent,1);assert.deepEqual(zero.ties,[0,1]);
});
test('forward witnesses reconstruct every neuron and the published prediction without mutation',()=>{
 const model=clone(b.model);
 for(const row of [rows[0],rows[700],{x:Array(12).fill(1e15)}]){
  const t=forwardTrace(b,model,row.x);
  t.hidden.forEach((h,k)=>{close(t.hidden_terms[k].reduce((a,c)=>a+c,0)+model.b1[k],t.hidden_sums[k]);close(Math.tanh(t.hidden_sums[k]),h)});
  close(t.output_terms.reduce((a,c)=>a+c,0)+model.b2,t.logit);
  close(t.p,predict(b,model,row.x));close(t.trust,100*(1-t.p));
 }
 assert.deepEqual(model,b.model);
});
for(const mode of ['monitor_only','governed'])test(`capturing SGD preserves the entire ${mode} replay and all candidate weights`,async()=>{
 const plain=newState(b,mode),traced=newState(b,mode);let count=0;
 for(let i=0;i<rows.length;i+=32){
  const witness={};const a=await processBatch(b,plain,rows.slice(i,i+32));const c=await processBatch(b,traced,rows.slice(i,i+32),{trace:witness});
  assert.deepEqual(a.scores,c.scores);assert.deepEqual(plain.model,traced.model);
  if(c.event){count++;assert.equal(witness.steps.length,3);assert.equal(a.event.status,c.event.status);assert.deepEqual(a.event.checks,c.event.checks);
   assert.equal(await digest(witness.before),c.event.model_before_sha256);assert.equal(await digest(witness.candidate),c.event.candidate_sha256);assert.equal(await digest(witness.active),c.event.active_model_sha256);
   for(const step of witness.steps){close(step.error,step.p-step.y);assert.equal(step.record_id,c.event.training_record_ids[0]);
    for(let k=0;k<24;k++){
     close(step.dh[k],step.error*step.before.w2[k]*(1-step.hidden[k]*step.hidden[k]));
     for(let j=0;j<12;j++){const p=parameterStep(step,'w1',j,k);close(p.after,p.before-.003*(step.dh[k]*step.x[j]+.0001*p.before))}
     for(const kind of ['w2','b1']){const p=parameterStep(step,kind,0,k);const gradient=kind==='w2'?step.error*step.hidden[k]+.0001*step.before.w2[k]:step.dh[k];close(p.after,p.before-.003*gradient)}
    }
    const p=parameterStep(step,'b2',0,0);close(p.after,p.before-.003*(step.p-step.y));
   }
   if(!c.event.accepted)assert.deepEqual(witness.active,witness.before);
   // A UI inspector cannot mutate the active model through a captured snapshot.
   witness.active.w1[0][0]=123456;assert.deepEqual(traced.model,plain.model);
  }
 }
 assert.equal(count,mode==='governed'?7:5);assert.equal(traced.accepted,mode==='governed'?4:5);assert.equal(traced.rejected,mode==='governed'?3:0);
});
test('unlabelled batches do not fabricate learning traces',async()=>{
 const s=newState(b);for(let i=0;i<256;i+=32){const witness={};const r=await processBatch(b,s,rows.slice(i,i+32).map(r=>({...r,y:null})),{trace:witness});assert.equal(r.event,null);assert.deepEqual(witness,{})}
});
