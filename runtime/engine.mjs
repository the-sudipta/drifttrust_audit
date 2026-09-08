/** Shared scientific/runtime engine. Label 1 means attack; trust = 1 - P(attack). */
export const ENGINE_VERSION = 'rtiot-mlp-v1';
export const clone = x => structuredClone(x);
const avg = xs => xs.length ? xs.reduce((a,b)=>a+b,0)/xs.length : 0;
const clamp = (x,a,b) => Math.max(a,Math.min(b,x));
export function canonical(value) {
  if (Array.isArray(value)) return '['+value.map(canonical).join(',')+']';
  if (value && typeof value==='object') return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
  return JSON.stringify(value);
}
export async function digest(value) {
  const bytes = new TextEncoder().encode(typeof value==='string'?value:canonical(value));
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
}
export function transform(bundle, raw) {
  if (!Array.isArray(raw)||raw.length!==bundle.features.length) throw new Error(`Expected ${bundle.features.length} numeric flow features.`);
  return raw.map((v,j)=>{
    if (typeof v!=='number'||!Number.isFinite(v)||v<0||v>1e15) throw new Error(`Invalid ${bundle.features[j]}: use a finite non-negative number <= 1e15.`);
    return clamp((Math.log1p(v)-bundle.mean[j])/bundle.scale[j],-8,8);
  });
}
export function forward(m,x) {
  const hidden=m.b1.map((b,k)=>Math.tanh(b+x.reduce((s,v,j)=>s+v*m.w1[j][k],0)));
  const logit=m.b2+hidden.reduce((s,v,k)=>s+v*m.w2[k],0);
  const p=logit>=0?1/(1+Math.exp(-logit)):Math.exp(logit)/(1+Math.exp(logit));
  return {p,hidden};
}
export function predict(bundle,model,raw) {return forward(model,transform(bundle,raw)).p;}
export function explain(bundle,model,raw) {
  const x=transform(bundle,raw), p=forward(model,x).p;
  return bundle.features.map((name,j)=>{const altered=x.slice();altered[j]=0;return {feature:name,contribution:p-forward(model,altered).p};});
}
function importance(bundle,model,rows) {
  const out=bundle.features.map(()=>0);
  for (const row of rows) for (const [j,e] of explain(bundle,model,row.x).entries()) out[j]+=Math.abs(e.contribution)/rows.length;
  return out;
}
const normalise = x => x.map(v=>v/(x.reduce((a,b)=>a+b,0)||1));
export function consistency(a,b,k=5) {
  const rank=x=>x.map((v,i)=>i).sort((i,j)=>x[j]-x[i]||i-j);
  const ra=rank(a), rb=rank(b), sa=new Set(ra.slice(0,k)), sb=new Set(rb.slice(0,k));
  const overlap=[...sa].filter(i=>sb.has(i)).length;
  const jaccard=overlap/new Set([...sa,...sb]).size;
  let con=0,dis=0,tieA=0,tieB=0;
  for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){
    const x=Math.sign(a[i]-a[j]), y=Math.sign(b[i]-b[j]);
    if(!x&&!y)continue; if(!x)tieA++;else if(!y)tieB++;else if(x===y)con++;else dis++;
  }
  const den=Math.sqrt((con+dis+tieA)*(con+dis+tieB));
  const tau=den?(con-dis)/den:(a.every((v,i)=>v===b[i])?1:0);
  return {eci:(jaccard+(tau+1)/2)/2,jaccard,kendall_tau:tau,top_before:ra.slice(0,k),top_after:rb.slice(0,k)};
}
function anchorMetrics(bundle,model) {
  const rows=bundle.anchors, ps=rows.map(r=>clamp(predict(bundle,model,r.x),1e-9,1-1e-9));
  return {loss:avg(ps.map((p,i)=>-rows[i].y*Math.log(p)-(1-rows[i].y)*Math.log(1-p))),
    attack_miss:avg(ps.flatMap((p,i)=>rows[i].y===1?[Number(p<.5)]:[])),
    mean_trust:1-avg(ps)};
}
function fit(bundle,m,rows) {
  const c=bundle.config, processed=rows.map(r=>({x:transform(bundle,r.x),y:r.y}));
  const losses=[];
  for(let e=0;e<c.update_epochs;e++){
    let loss=0;
    for(const {x,y} of processed){
      const {p,hidden}=forward(m,x), error=p-y;
      loss+=-y*Math.log(clamp(p,1e-9,1-1e-9))-(1-y)*Math.log(clamp(1-p,1e-9,1-1e-9));
      const dh=hidden.map((h,k)=>error*m.w2[k]*(1-h*h));
      for(let k=0;k<hidden.length;k++){
        m.w2[k]-=c.update_lr*(error*hidden[k]+.0001*m.w2[k]);
        m.b1[k]-=c.update_lr*dh[k];
        for(let j=0;j<x.length;j++)m.w1[j][k]-=c.update_lr*(dh[k]*x[j]+.0001*m.w1[j][k]);
      }
      m.b2-=c.update_lr*error;
    }
    losses.push(loss/processed.length);
  }
  return losses;
}
export function newState(bundle,mode='governed') {
  return {mode,model:clone(bundle.model),seen:0,labeled:0,last_attempt:0,errors:[],recent:[],replay:clone(bundle.replay),
    baseline:normalise(importance(bundle,bundle.model,bundle.anchors)),attempts:0,accepted:0,rejected:0,chain_head:null};
}
export async function processBatch(bundle,state,rows,options={}) {
  const c=bundle.config, start=state.seen, beforeModel=state.model;
  if(!Array.isArray(rows)||!rows.length||rows.length>c.batch_size)throw new Error(`Batch must contain 1–${c.batch_size} flows.`);
  for(const r of rows){transform(bundle,r.x);if(r.y!==null&&r.y!==undefined&&r.y!==0&&r.y!==1)throw new Error('Feedback label must be 0, 1 or null.');}
  const scores=rows.map(r=>predict(bundle,beforeModel,r.x)); // ALL predictions precede this batch's labels.
  const evidence=rows.filter(r=>r.y===0||r.y===1);
  for(let i=0;i<rows.length;i++)if(rows[i].y===0||rows[i].y===1){
    state.errors.push(Number(Number(scores[i]>=.5)!==rows[i].y));state.recent.push(clone(rows[i]));state.labeled++;
  }
  state.errors=state.errors.slice(-c.error_long);state.recent=state.recent.slice(-c.adaptation_window);state.seen+=rows.length;
  if(state.mode==='static')return {scores,event:null};
  const full=state.errors.length>=c.error_long;
  const short=avg(state.errors.slice(-c.error_short)),long=avg(state.errors.slice(0,-c.error_short));
  const errorDrift=full&&short>long+c.error_margin;
  let shift=0,current=null;
  if(state.mode!=='no_attribution'){
    current=normalise(importance(bundle,state.model,rows));shift=Math.max(...current.map((v,j)=>Math.abs(v-state.baseline[j])));
  }
  const triggered=errorDrift||shift>c.attribution_threshold;
  if(!triggered||state.seen-state.last_attempt<c.min_update_gap||state.recent.length<64||!evidence.length)return {scores,event:null,signals:{short,long,shift,triggered}};
  const t=performance.now(),candidate=clone(state.model);
  const training=state.mode==='no_replay'?state.recent:[...state.recent,...state.replay];
  const losses=fit(bundle,candidate,training);
  state.attempts++;state.last_attempt=state.seen;
  const checkGovernance=state.mode!=='ungoverned';
  const pre=checkGovernance?anchorMetrics(bundle,state.model):null, post=checkGovernance?anchorMetrics(bundle,candidate):null;
  const eci=checkGovernance?consistency(importance(bundle,state.model,bundle.anchors),importance(bundle,candidate,bundle.anchors)):null;
  const checks=checkGovernance?{
    explanation_consistency:eci.eci>=c.eci_threshold,
    anchor_loss:post.loss<=pre.loss+c.max_anchor_loss_increase,
    attack_miss:post.attack_miss<=pre.attack_miss+c.max_attack_miss_increase,
    minimum_gap:state.seen-(state.previous_attempt??0)>=c.min_update_gap
  }:null;
  const accepted=!checkGovernance||state.mode==='monitor_only'||Object.values(checks).every(Boolean);
  state.previous_attempt=state.seen;
  const oldHash=checkGovernance?await digest(state.model):null;
  const candidateHash=checkGovernance?await digest(candidate):null;
  if(accepted){state.model=candidate;state.accepted++;}else state.rejected++;
  state.replay=[...state.replay,...state.recent].slice(-c.replay_size);
  state.errors=[];
  state.baseline=normalise(importance(bundle,state.model,state.recent));
  if(!checkGovernance)return {scores,event:{attempt:state.attempts,position:state.seen,accepted:true,governance:false,elapsed_ms:performance.now()-t}};
  const record={schema_version:'1.0',engine_version:ENGINE_VERSION,attempt:state.attempts,position:state.seen,
    timestamp_utc:options.timestamp??new Date().toISOString(),trigger:errorDrift?'error_shift':'attribution_shift',
    signals:{short_error:short,reference_error:long,attribution_shift:shift},
    training_record_ids:training.map(r=>r.id),anchor_record_ids:bundle.anchors.map(r=>r.id),
    model_before_sha256:oldHash,candidate_sha256:candidateHash,active_model_sha256:accepted?candidateHash:oldHash,
    same_anchor_before:pre,same_anchor_candidate:post,explanation_consistency:eci,
    checks,policy_mapping:{attack_miss:'A.5.15',anchor_loss:'A.5.15',explanation_consistency:'A.8.16',minimum_gap:'A.5.36'},
    mapping_scope:'Research policy proxies; not an ISO certification or full control assessment.',
    accepted,status:accepted?(Object.values(checks).every(Boolean)?'ACCEPTED':'ACCEPTED_WITH_FLAGS'):'REJECTED',failed_checks:Object.keys(checks).filter(k=>!checks[k]),
    incremental_losses:losses,previous_record_sha256:state.chain_head,
    feedback_source:options.feedbackSource??'benchmark labels revealed after batch prediction',
    elapsed_ms:performance.now()-t};
  record.record_sha256=await digest(record);state.chain_head=record.record_sha256;
  return {scores,event:record,signals:{short,long,shift,triggered}};
}
