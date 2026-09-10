import fs from 'node:fs';import path from 'node:path';
const root=path.resolve('.'),out=path.resolve('.pages');if(path.dirname(out)!==root)throw Error('Invalid build target');fs.rmSync(out,{recursive:true,force:true});fs.mkdirSync(out,{recursive:true});
for(const p of ['index.html','lab.html','guide.html','site.css','site.mjs','lab.mjs','explanations.mjs','math-theatre.mjs','math-theatre.css'])fs.copyFileSync(p,path.join(out,p));
fs.mkdirSync(path.join(out,'runtime'));for(const p of ['math-trace.mjs','engine.mjs','browser-client.mjs','browser-worker.mjs'])fs.copyFileSync('runtime/'+p,path.join(out,'runtime',p));
fs.mkdirSync(path.join(out,'assets'),{recursive:true});fs.cpSync('assets/research',path.join(out,'assets/research'),{recursive:true});fs.writeFileSync(path.join(out,'.nojekyll'),'');
console.log('GitHub Pages build complete: static files + actual browser model engine.');
