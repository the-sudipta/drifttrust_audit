import bundle from '../assets/research/model.json';
import replay from '../assets/research/replay.json';
import examples from '../assets/research/examples.json';
import {newState,processBatch,predict,explain,transform,digest,ENGINE_VERSION} from './engine.mjs';

const TTL=86400;
const json=(value,status=200,extra={})=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff',...extra}});
const fail=(status,message)=>{const e=new Error(message);e.status=status;throw e;};
async function readBody(request){
 if(!(request.headers.get('content-type')||'').startsWith('application/json'))fail(415,'Send application/json.');
 const reader=request.body?.getReader();if(!reader)fail(400,'Missing request body.');
 const chunks=[];let size=0;
 while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>400000){await reader.cancel();fail(413,'Maximum request size is 400 KB.');}chunks.push(value);}
 const merged=new Uint8Array(size);let i=0;for(const c of chunks){merged.set(c,i);i+=c.length;}
 let value;try{value=JSON.parse(new TextDecoder().decode(merged));}catch{fail(400,'Invalid JSON.');}
 if(!value||typeof value!=='object'||Array.isArray(value))fail(400,'JSON body must be an object.');
 return value;
}
function policyContext(s){return {mode:s.mode,seen:s.seen,labeled:s.labeled,attempts:s.attempts,accepted:s.accepted,rejected:s.rejected,chain_head:s.chain_head,replay_cursor:s.replay_cursor??0};}
function description(){return {engine_version:ENGINE_VERSION,features:bundle.features,bounds:bundle.bounds,config:bundle.config,
 dataset:bundle.provenance,model_artifact_sha256:bundle.model_sha256,examples,replay_size:replay.rows.length,replay_boundaries:replay.boundaries,
 notice:'Live inference and per-session adaptation on measured flow features. Network-risk assessment, not a connected access-enforcement system. Feedback labels are provided by the dataset or asserted by the visitor.'};}
async function session(request,env){
 const token=(request.headers.get('cookie')||'').match(/(?:^|;\s*)dta_session=([a-f0-9]{64})(?:;|$)/)?.[1];
 if(!token)fail(401,'Start a lab session first.');
 const id=await digest(token),row=await env.DB.prepare('SELECT * FROM sessions WHERE id = ? AND expires > ?').bind(id,Math.floor(Date.now()/1000)).first();
 if(!row)fail(401,'This lab session has expired. Start a new session.');
 return {...row,parsed:JSON.parse(row.state)};
}
async function createSession(request,env,ctx){
 const body=await readBody(request),mode=body.mode??'monitor_only';
 if(!['monitor_only','governed'].includes(mode))fail(400,'Choose audit-only or gated mode.');
 const now=Math.floor(Date.now()/1000),bucket=Math.floor(now/3600);
 const ip=request.headers.get('CF-Connecting-IP')||'local';const key=await digest(`session-rate:${bucket}:${ip}`);
 const count=await env.DB.prepare('INSERT INTO limits (id,count,expires) VALUES (?,1,?) ON CONFLICT(id) DO UPDATE SET count=count+1 RETURNING count').bind(key,now+7200).first();
 if(count.count>20)fail(429,'Session creation limit reached. Reuse your existing session or try again in an hour.');
 const token=[...crypto.getRandomValues(new Uint8Array(32))].map(x=>x.toString(16).padStart(2,'0')).join('');
 const id=await digest(token),state=newState(bundle,mode);state.replay_cursor=0;
 await env.DB.prepare('INSERT INTO sessions (id,state,revision,expires) VALUES (?,?,0,?)').bind(id,JSON.stringify(state),now+TTL).run();
 ctx.waitUntil(env.DB.batch([env.DB.prepare('DELETE FROM sessions WHERE expires <= ?').bind(now),env.DB.prepare('DELETE FROM limits WHERE expires <= ?').bind(now)]));
 const secure=new URL(request.url).protocol==='https:'?'; Secure':'';
 return json({revision:0,expires_utc:new Date((now+TTL)*1000).toISOString(),...policyContext(state)},201,{'Set-Cookie':`dta_session=${token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${TTL}${secure}`});
}
async function mutate(request,env,path){
 const body=await readBody(request),row=await session(request,env);
 if(typeof body.request_id!=='string'||!/^[a-zA-Z0-9_-]{12,80}$/.test(body.request_id))fail(400,'A unique request_id (12–80 letters, numbers, _ or -) is required.');
 if(body.request_id===row.last_op&&row.last_reply)return json(JSON.parse(row.last_reply));
 if(!Number.isInteger(body.revision)||body.revision!==row.revision)fail(409,'Session changed. Refresh its status before retrying.');
 if(row.parsed.seen>=20000)fail(429,'This session has reached its 20,000-flow limit. Export the audit and start a new session.');
 const state=row.parsed;let records;
 if(path==='/api/replay'){
  const count=body.count??128;if(!Number.isInteger(count)||count<1||count>256)fail(400,'Replay count must be 1–256.');
  const cursor=state.replay_cursor??0;
  records=replay.rows.slice(cursor,cursor+count);if(!records.length)fail(400,'Replay complete. Start a new session to replay again.');
  state.replay_cursor=cursor+records.length;
 }else{
  if(!Array.isArray(body.rows)||!body.rows.length||body.rows.length>256)fail(400,'Submit 1–256 measured flow rows.');
  if(body.rows.some(r=>!r||typeof r!=='object'||Array.isArray(r)))fail(400,'Each row must be an object with x and optional y.');
  records=body.rows.map((r,i)=>({id:`visitor-${state.seen+i}`,x:r.x,y:r.y??null,family:'visitor supplied'}));
 }
 if(state.seen+records.length>20000)fail(429,'This batch exceeds the 20,000-flow session limit.');
 // Validate the ENTIRE transaction before any computation or persistence.
 for(const r of records){try{transform(bundle,r.x);}catch(e){fail(400,e.message);}if(r.y!==null&&r.y!==0&&r.y!==1)fail(400,'Label must be null, 0 (benign), or 1 (attack).');}
 const events=[],predictions=[],start=state.seen;
 for(let i=0;i<records.length;i+=bundle.config.batch_size){
  const batch=records.slice(i,i+bundle.config.batch_size);
  const {scores,event}=await processBatch(bundle,state,batch,{feedbackSource:path==='/api/replay'?'UCI held-out dataset labels, revealed after prediction':'Visitor-asserted labels; not independently verified'});
  scores.forEach((p,j)=>predictions.push({position:start+i+j+1,source_row:batch[j].id,attack_probability:p,trust_score:1-p,label:batch[j].y,family:batch[j].family}));
  if(event)events.push(event);
 }
 const response={revision:row.revision+1,...policyContext(state),predictions,events};
 const queries=[env.DB.prepare('UPDATE sessions SET state=?,revision=revision+1,last_op=?,last_reply=? WHERE id=? AND revision=?').bind(JSON.stringify(state),body.request_id,JSON.stringify(response),row.id,row.revision)];
 for(const e of events)queries.push(env.DB.prepare('INSERT INTO audit (id,session,position,record) SELECT ?,?,?,? WHERE EXISTS (SELECT 1 FROM sessions WHERE id=? AND last_op=?)').bind(crypto.randomUUID(),row.id,e.position,JSON.stringify(e),row.id,body.request_id));
 const result=await env.DB.batch(queries);
 if(result[0].meta.changes!==1)fail(409,'Concurrent operation detected. Refresh and retry.');
 return json(response);
}
export default {
 async fetch(request,env,ctx){
  const url=new URL(request.url),path=url.pathname;
  if(!path.startsWith('/api/'))return env.ASSETS.fetch(request);
  try{
   if(!['GET','POST'].includes(request.method))fail(405,'Method not allowed.');
   if(request.method==='POST'){
    const origin=request.headers.get('origin');if(origin&&origin!==url.origin)fail(403,'Cross-origin writes are not allowed.');
    if(request.headers.get('sec-fetch-site')==='cross-site')fail(403,'Cross-site writes are not allowed.');
   }
   if(path==='/api/health'&&request.method==='GET'){
    await env.DB.prepare('SELECT 1 FROM sessions LIMIT 1').first();
    return json({status:'ok',engine_version:ENGINE_VERSION,database:'connected',model:bundle.model_sha256});
   }
   if(path==='/api/model'&&request.method==='GET')return json(description());
   if(path==='/api/session'&&request.method==='POST')return await createSession(request,env,ctx);
   if(path==='/api/session'&&request.method==='GET'){const r=await session(request,env);return json({revision:r.revision,...policyContext(r.parsed)});}
   if(path==='/api/infer'&&request.method==='POST'){
    const r=await session(request,env),body=await readBody(request);
    try{transform(bundle,body.x);}catch(e){fail(400,e.message);}
    const p=predict(bundle,r.parsed.model,body.x);
    return json({attack_probability:p,trust_score:1-p,decision:p>=.5?'FLAG_NETWORK_RISK':'LOWER_NETWORK_RISK',
      explanation:explain(bundle,r.parsed.model,body.x).sort((a,b)=>Math.abs(b.contribution)-Math.abs(a.contribution)),
      model_sha256:await digest(r.parsed.model),revision:r.revision,
      outside_training_range:body.x.map((v,j)=>v<bundle.bounds[j].min||v>bundle.bounds[j].max?bundle.features[j]:null).filter(Boolean),
      calibration_notice:'Raw model score, not a calibrated guarantee or access authorization.'});
   }
   if(['/api/replay','/api/stream'].includes(path)&&request.method==='POST')return await mutate(request,env,path);
   if(path==='/api/audit'&&request.method==='GET'){
    const r=await session(request,env),records=await env.DB.prepare('SELECT record FROM audit WHERE session=? ORDER BY position').bind(r.id).all();
    return json({schema_version:'1.0',engine_version:ENGINE_VERSION,revision:r.revision,chain_head:r.parsed.chain_head,records:records.results.map(x=>JSON.parse(x.record))});
   }
   fail(404,'Unknown API route.');
  }catch(e){return json({error:e.status?e.message:'The service could not complete this operation. Retry or refresh session status.'},e.status??500);}
 }
};
