/** Request/response bridge. Path names preserve the optional server API contract; no API HTTP calls occur. */
const worker=new Worker(new URL('./browser-worker.mjs',import.meta.url),{type:'module'});
const pending=new Map();let next=0,failed=null;
worker.onmessage=({data})=>{const entry=pending.get(data.id);if(!entry)return;pending.delete(data.id);clearTimeout(entry.timer);if(data.error)entry.reject(Object.assign(Error(data.error),{status:data.status}));else entry.resolve(data.result)};
worker.onerror=e=>{failed=Error('The local model worker could not load. Open the GitHub Pages site or run the local server; this lab cannot start from file://.');for(const p of pending.values()){clearTimeout(p.timer);p.reject(failed)}pending.clear()};
export function api(path,body){if(failed)return Promise.reject(failed);return new Promise((resolve,reject)=>{const id=++next;const timer=setTimeout(()=>{pending.delete(id);reject(Error('The model operation took too long. Reload to read the saved session state before retrying.'))},120000);pending.set(id,{resolve,reject,timer});worker.postMessage({id,path,body})})}
