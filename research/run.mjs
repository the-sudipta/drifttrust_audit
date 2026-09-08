import fs from 'node:fs';
import {newState,processBatch,ENGINE_VERSION,digest} from '../runtime/engine.mjs';
const out='assets/research';fs.mkdirSync(out,{recursive:true});
const seeds=[11,23,37,53,71];
const modes=['static','ungoverned','monitor_only','governed','no_replay','no_attribution'];
const runs=[];
for(const seed of seeds){
 const bundle=JSON.parse(fs.readFileSync(`data/prepared/bundle-${seed}.json`));
 for(const protocol of ['stationary','shifted']){
  const data=JSON.parse(fs.readFileSync(`data/prepared/${protocol}-${seed}.json`));
  const result={seed,protocol,boundaries:data.boundaries,split:data.split,labels:data.rows.map(r=>r.y),families:data.rows.map(r=>r.family),models:{}};
  for(const mode of modes){
   const state=newState(bundle,mode),scores=[],events=[];const start=performance.now();
   for(let i=0;i<data.rows.length;i+=bundle.config.batch_size){
    const res=await processBatch(bundle,state,data.rows.slice(i,i+bundle.config.batch_size));
    scores.push(...res.scores);if(res.event)events.push(res.event);
   }
   result.models[mode]={scores,events,elapsed_ms:performance.now()-start,accepted:state.accepted,rejected:state.rejected};
   console.log(seed,protocol,mode,'flows',scores.length,'accepted',state.accepted,'rejected',state.rejected);
  }
  for(const [name,scores] of Object.entries(data.baselines))result.models[name]={scores,events:[],elapsed_ms:null,accepted:0,rejected:0};
  fs.writeFileSync(`data/prepared/results-${protocol}-${seed}.json`,JSON.stringify(result));
  runs.push({seed,protocol,path:`results-${protocol}-${seed}.json`});
  if(seed===11&&protocol==='shifted'){
   fs.writeFileSync(`${out}/audit_records.json`,JSON.stringify(result.models.governed.events,null,2));
  }
 }
}
fs.writeFileSync(`${out}/execution.json`,JSON.stringify({engine_version:ENGINE_VERSION,engine_sha256:await digest(fs.readFileSync('runtime/engine.mjs','utf8')),node:process.version,runs,finished_at_utc:new Date().toISOString()},null,2));
