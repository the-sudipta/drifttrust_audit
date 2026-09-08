const fmt=x=>x?x.mean.toFixed(3)+' ± '+x.sd.toFixed(3):'—';
const data=await fetch('assets/research/results.json').then(r=>{if(!r.ok)throw Error();return r.json()}).catch(()=>null);
if(['localhost','127.0.0.1','drifttrust-audit-lab.pipratools.chatgpt.site'].includes(location.hostname))document.querySelectorAll('[data-lab]').forEach(a=>a.href='lab.html');
function render(){
 if(!data){document.getElementById('resultHighlights').textContent='Results unavailable. Download the CSV table below.';return}
 const map=Object.fromEntries(data.summary.filter(r=>r.protocol===document.getElementById('protocol').value).map(r=>[r.model,r]));
 const root=document.getElementById('resultsBody');root.replaceChildren();
 for(const key of ['Logistic regression','Random forest','static','ungoverned','monitor_only','governed','no_replay','no_attribution']){
 const r=map[key],tr=document.createElement('tr');if(['monitor_only','governed'].includes(key))tr.className='highlight';
 for(const v of [r.name,fmt(r.attack_f1),fmt(r.balanced_accuracy),fmt(r.attack_recall),fmt(r.benign_false_alarm_rate),r.attempts.mean.toFixed(1)]){const td=document.createElement('td');td.textContent=v;tr.append(td)}root.append(tr)}
 const h=document.getElementById('resultHighlights');h.replaceChildren();
 for(const [key,label] of [['static','Frozen model · attack F1'],['monitor_only','Audit-only adaptation · attack F1'],['governed','Gated adaptation · attack F1']]){
 const d=document.createElement('div');d.className='metric';const b=document.createElement('b');b.textContent=map[key].attack_f1.mean.toFixed(3);const s=document.createElement('span');s.textContent=label;d.append(b,s);h.append(d)}
}
document.getElementById('protocol').addEventListener('change',render);render();
const figures=[['01_dataset_audit','Dataset composition','Raw versus unique input vectors by family.'],['02_baselines_and_ablations','Baselines and ablations','Eight configurations, two protocols, and five splits.'],['03_stream_performance','Performance through the stream','Balanced accuracy and error rate over primary-seed replay.'],['04_roc_pr','ROC and precision–recall','Primary-seed threshold-independent comparisons.'],['05_confusion_matrices','Class-specific errors','Raw counts and row-normalized rates.'],['06_governance_decisions','Accepted and rejected candidates','Explanation consistency and fixed-anchor loss change.'],['07_per_family','Performance by traffic family','Accuracy and actual held-out support counts.'],['08_research_workflow','Experimental workflow','Provenance, preprocessing, split, fitting, and evaluation.'],['09_live_architecture','Deployed methodology','Server inference, updates, and session audit storage.']];
for(const [id,title,description] of figures){const c=document.createElement('article');c.className='figure-card';const img=document.createElement('img');img.src='assets/research/figures/'+id+'.svg';img.alt=description;img.loading='lazy';const h=document.createElement('h3');h.textContent=title;const p=document.createElement('p');p.textContent=description;const links=document.createElement('div');links.className='figure-links';for(const ext of ['pdf','svg','png']){const a=document.createElement('a');a.href='assets/research/figures/'+id+'.'+ext;a.textContent=ext.toUpperCase();a.download=id+'.'+ext;links.append(a)}c.append(img,h,p,links);document.getElementById('figureGrid').append(c)}
