import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {DatabaseSync} from 'node:sqlite';
import {build} from 'esbuild';
import {Readable} from 'node:stream';
fs.mkdirSync('.local',{recursive:true});
await build({entryPoints:['runtime/worker.mjs'],outfile:'.local/worker.mjs',bundle:true,format:'esm',platform:'node',target:'es2022'});
const worker=(await import('../.local/worker.mjs')).default;
const db=new DatabaseSync('.local/lab.sqlite');db.exec('PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL;');
db.exec('CREATE TABLE IF NOT EXISTS local_migrations (name TEXT PRIMARY KEY)');
for(const f of fs.readdirSync('drizzle').filter(f=>f.endsWith('.sql')).sort())if(!db.prepare('SELECT name FROM local_migrations WHERE name=?').get(f)){
 db.exec(fs.readFileSync(`drizzle/${f}`,'utf8'));db.prepare('INSERT INTO local_migrations (name) VALUES (?)').run(f);
}
function prepared(sql,args=[]){return {sql,args,bind(...v){return prepared(sql,v)},async first(){return db.prepare(sql).get(...args)??null},async all(){return {results:db.prepare(sql).all(...args)}},async run(){const r=db.prepare(sql).run(...args);return {meta:{changes:Number(r.changes)}}}};}
const DB={prepare:sql=>prepared(sql),async batch(queries){db.exec('BEGIN IMMEDIATE');try{const out=[];for(const q of queries){const r=db.prepare(q.sql).run(...q.args);out.push({meta:{changes:Number(r.changes)}});}db.exec('COMMIT');return out;}catch(e){db.exec('ROLLBACK');throw e;}}};
const types={'.html':'text/html; charset=utf-8','.css':'text/css','.mjs':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.pdf':'application/pdf','.zip':'application/zip','.csv':'text/csv','.md':'text/plain; charset=utf-8'};
const ASSETS={async fetch(request){
 const name=decodeURIComponent(new URL(request.url).pathname);const relative=name==='/'?'index.html':name.slice(1);
 const allowed=['index.html','lab.html','guide.html','site.css','site.mjs','lab.mjs','explanations.mjs','runtime/engine.mjs','runtime/browser-client.mjs','runtime/browser-worker.mjs'];
 if(!allowed.includes(relative)&&!relative.startsWith('assets/research/'))return new Response('Not found',{status:404});
 const file=path.resolve(relative);if(!file.startsWith(path.resolve('.')+path.sep))return new Response('Not found',{status:404});
 try{return new Response(fs.readFileSync(file),{headers:{'Content-Type':types[path.extname(file)]??'application/octet-stream'}})}catch{return new Response('Not found',{status:404})}
}};
const port=Number(process.env.PORT||8787);
http.createServer(async(req,res)=>{
 try{
  const request=new Request(`http://localhost:${port}${req.url}`,{method:req.method,headers:req.headers,...(!['GET','HEAD'].includes(req.method)?{body:Readable.toWeb(req),duplex:'half'}:{})});
  const response=await worker.fetch(request,{DB,ASSETS},{waitUntil(p){p.catch(e=>console.error('Background cleanup failed',e.message))}});
  res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));
 }catch(e){console.error(e);res.writeHead(500);res.end('Local service error');}
}).listen(port,'127.0.0.1',()=>console.log(`Local: http://localhost:${port}`));
