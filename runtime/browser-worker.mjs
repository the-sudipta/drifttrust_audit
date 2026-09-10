/** GitHub Pages runtime: actual shared engine in a Web Worker, state in IndexedDB. */
import {newState,processBatch,predict,explain,transform,digest,ENGINE_VERSION} from './engine.mjs';
import {forwardTrace} from './math-trace.mjs';
const json=async name=>{const r=await fetch(new URL(`../assets/research/${name}.json`,import.meta.url));if(!r.ok)throw Error(`Could not load ${name}. Reload the page when online.`);return r.json()};
const ready=Promise.all([json('model'),json('replay'),json('examples')]);
const TTL=24*60*60*1000;
const fail=(status,message)=>{const e=Error(message);e.status=status;throw e};
const dbReady=new Promise((resolve,reject)=>{const r=indexedDB.open('drifttrust-pages-v1',1);r.onupgradeneeded=()=>r.result.createObjectStore('state');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(Error('Browser storage is unavailable. Allow site storage or use a regular browser window.'))});
async function read(){const db=await dbReady;return new Promise((resolve,reject)=>{const tx=db.transaction('state','readonly'),r=tx.objectStore('state').get('active');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)})}
async function persist(value,expected){const db=await dbReady;return new Promise((resolve,reject)=>{const tx=db.transaction('state','readwrite'),store=tx.objectStore('state'),r=store.get('active');let conflict=false;r.onsuccess=()=>{if(expected&&(!r.result||r.result.id!==expected.id||r.result.revision!==expected.revision)){conflict=true;tx.abort();return}store.put(value,'active')};tx.oncomplete=resolve;tx.onabort=()=>reject(conflict?Object.assign(Error('Another tab changed this model session. Refresh before retrying.'),{status:409}):tx.error);tx.onerror=()=>reject(tx.error)})}
async function active(){const s=await read();if(!s||s.expires<=Date.now())fail(401,'Start a model session. Any previous session has expired.');return s}
function summary(s){const a=s.state;return {revision:s.revision,session_id:s.id,mode:a.mode,seen:a.seen,labeled:a.labeled,attempts:a.attempts,accepted:a.accepted,rejected:a.rejected,chain_head:a.chain_head,replay_cursor:a.replay_cursor??0,expires_utc:new Date(s.expires).toISOString(),trace:s.trace??[],last_inference:s.last_inference??null,last_diagnostics:s.last_diagnostics??null,active_model_sha256:s.active_hash}}
function description(bundle,replay,examples){return {engine_version:ENGINE_VERSION,features:bundle.features,bounds:bundle.bounds,config:bundle.config,examples,replay_size:replay.rows.length,replay_boundaries:replay.boundaries,execution:'Browser Web Worker',persistence:'This browser’s IndexedDB',model_artifact_sha256:bundle.model_sha256}}
async function handle(path,body){const [bundle,replay,examples]=await ready;
 if(path==='/api/health'){await dbReady;return {status:'ok',engine_version:ENGINE_VERSION,execution:'browser',database:'local IndexedDB'}}
 if(path==='/api/model')return description(bundle,replay,examples);
 if(path==='/api/session'&&body!==undefined){if(!['monitor_only','governed'].includes(body.mode))fail(400,'Choose audit-only or gated policy.');const s={id:crypto.randomUUID(),revision:0,expires:Date.now()+TTL,state:newState(bundle,body.mode),audit:[],trace:[],active_hash:await digest(bundle.model)};s.state.replay_cursor=0;await persist(s);return summary(s)}
 const s=await active();
 if(path==='/api/session')return summary(s);
 if(path==='/api/visuals')return {items:[...(s.visual_history??[]),...(s.last_visual?[s.last_visual]:[])]};
 if(path==='/api/audit')return {schema_version:'1.0',engine_version:ENGINE_VERSION,execution:'browser',revision:s.revision,chain_head:s.state.chain_head,records:s.audit};
 if(path==='/api/infer'){
  try{transform(bundle,body.x)}catch(e){fail(400,e.message)}
  const p=predict(bundle,s.state.model,body.x),result={attack_probability:p,trust_score:1-p,explanation:explain(bundle,s.state.model,body.x).sort((a,b)=>Math.abs(b.contribution)-Math.abs(a.contribution)),model_sha256:await digest(s.state.model),revision:s.revision,input:body.x,outside_training_range:body.x.map((v,j)=>v<bundle.bounds[j].min||v>bundle.bounds[j].max?bundle.features[j]:null).filter(Boolean)};
  // Inference remains read-only; reload restores the last saved stream prediction.
  result.visual={id:crypto.randomUUID(),kind:'inference',title:'Single flow · current weights',captured_at:new Date().toISOString(),
   model_sha256:result.model_sha256,forward:forwardTrace(bundle,s.state.model,body.x)};
  return result;
 }
 if(!['/api/replay','/api/stream'].includes(path))fail(404,'Unknown browser operation.');
 if(typeof body.request_id!=='string'||!/^[a-zA-Z0-9_-]{12,80}$/.test(body.request_id))fail(400,'A unique request identifier is required.');
 if(body.request_id===s.last_op)return s.last_reply;
 if(body.revision!==s.revision)fail(409,'Session changed. Refresh its status before retrying.');
 const expected={id:s.id,revision:s.revision};let rows;
 if(path==='/api/replay'){
  const count=body.count??128;if(!Number.isInteger(count)||count<1||count>256)fail(400,'Choose 1–256 replay flows.');rows=replay.rows.slice(s.state.replay_cursor,s.state.replay_cursor+count);if(!rows.length)fail(400,'Replay complete. Start a new model session to repeat it.');
 }else{
  if(!Array.isArray(body.rows)||!body.rows.length||body.rows.length>256)fail(400,'Submit 1–256 measured flows.');
  rows=body.rows.map((r,i)=>{if(!r||typeof r!=='object')fail(400,'Each row needs x and an optional label.');return {id:`visitor-${s.state.seen+i}`,x:r.x,y:r.y??null,family:'visitor supplied'}});
 }
 if(s.state.seen+rows.length>20000)fail(429,'This session reached its 20,000-flow limit. Export the audit and start another session.');
 for(const r of rows){try{transform(bundle,r.x)}catch(e){fail(400,e.message)}if(r.y!==null&&r.y!==0&&r.y!==1)fail(400,'Labels must be 0 benign, 1 attack, or blank unknown.')}
 const predictions=[],events=[],diagnostics=[],visuals=[];
 for(let i=0;i<rows.length;i+=bundle.config.batch_size){
  const batch=rows.slice(i,i+bundle.config.batch_size),start=s.state.seen,currentLabels=batch.filter(r=>r.y===0||r.y===1).length;
  const errorLabels=Math.min(bundle.config.error_long,s.state.errors.length+currentLabels),gap=start+batch.length-s.state.last_attempt;
  const learning={},probe=batch.at(-1),observed=forwardTrace(bundle,s.state.model,probe.x);
  const {scores,event,signals}=await processBatch(bundle,s.state,batch,{trace:learning,feedbackSource:path==='/api/replay'?'UCI held-out labels revealed after batch prediction':'Visitor-asserted labels; not independently verified'});
  const position=start+batch.length;
  if(event){const visual={id:`${s.id}-candidate-${event.attempt}`,kind:'candidate',mode:s.state.mode,title:`Candidate #${event.attempt} · flow ${position} · ${event.status}`,
   captured_at:event.timestamp_utc,source_row:probe.id,position,label:probe.y,record:event,steps:learning.steps,training_size:learning.training_size,
   forward:observed,candidate:forwardTrace(bundle,learning.candidate,probe.x),active:forwardTrace(bundle,learning.active,probe.x),config:bundle.config};
   visuals.push(visual);s.visual_history=[...(s.visual_history??[]),visual].slice(-8);
  }
  s.last_visual={id:`${s.id}-flow-${position}`,kind:'stream',title:`Observed flow ${position} · source ${probe.id}`,captured_at:new Date().toISOString(),
   position,source_row:probe.id,label:probe.y,model_sha256:event?.model_before_sha256??await digest(observed.model),forward:observed};
  scores.forEach((p,j)=>predictions.push({position:start+j+1,source_row:batch[j].id,attack_probability:p,trust_score:1-p,label:batch[j].y,family:batch[j].family}));
  if(event)events.push(event);
  diagnostics.push({position:s.state.seen,batch_size:batch.length,current_labels:currentLabels,error_history_labels:errorLabels,recent_labels:s.state.recent.length,flows_since_previous_attempt:gap,signals:signals??event?.signals,attempted:!!event});
 }
 if(path==='/api/replay')s.state.replay_cursor+=rows.length;
 s.audit.push(...events);s.trace=[...(s.trace??[]),...predictions].slice(-512);s.active_hash=await digest(s.state.model);s.last_diagnostics=diagnostics.at(-1);s.revision++;s.last_op=body.request_id;
 const response={...summary(s),predictions,events,diagnostics,visuals:[s.last_visual,...visuals]};s.last_reply=response;
 await persist(s,expected);return response;
}
// Serialize requests within a tab; the IndexedDB revision transaction handles other tabs.
let queue=Promise.resolve();self.onmessage=e=>{const {id,path,body}=e.data;queue=queue.then(async()=>{try{self.postMessage({id,result:await handle(path,body)})}catch(err){self.postMessage({id,error:err.message,status:err.status??500})}})};
