from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];p=R/'qa/content.json';c=json.loads(p.read_text(encoding='utf-8'))
replacements={
'https://drifttrust-audit-lab.pipratools.chatgpt.site/lab.html':'https://the-sudipta.github.io/drifttrust_audit/lab.html',
'Model online · database connected':'Real model ready · local browser storage connected',
'Start lab session':'Start / reset model session',
'Audit-only · record policy flags':'Audit-only · record failed checks',
'Gated · reject failed candidates':'Gated · veto failed model updates',
'Run actual inference':'Run actual inference',
'Refresh records':'Refresh saved records',
'node scripts/dev.mjs':'node scripts/serve-pages.mjs',
}
def sub(v):
    if isinstance(v,str):
        for a,b in replacements.items():v=v.replace(a,b)
        return v
    if isinstance(v,list):return [sub(x) for x in v]
    if isinstance(v,dict):return {k:sub(x) for k,x in v.items()}
    return v
c=sub(c);c['version']='GitHub Pages browser migration inspected 9 September 2026. The scientific engine and published initial weights remain from the measured experiment; the interface and persistence now run locally in the browser.'
c['quickstart'][5]+=' The gated replay produces seven candidates: four activated and three discarded. Read the numeric check table before opening raw JSON. Verify record chain checks content and links; it does not establish independent truth.'
c['quickstart'][6]=c['quickstart'][6].replace("because the new session replaces the browser's session cookie","because Start/reset replaces this browser’s active stored model session")
m=c['modules']
m[0]['formal'][0]='The current public-data path is research/prepare.py → exported JSON model and streams → runtime/engine.mjs → research/run.mjs → research/report.py. GitHub Pages serves the model and code as static assets. runtime/browser-worker.mjs imports the identical engine and executes it in a browser background thread. The initial Worker API remains an optional separate server deployment in runtime/worker.mjs.'
m[0]['formal'][1]='index.html + site.mjs + site.css render recorded results with dynamic metric and figure explanations. lab.html defines controls; lab.mjs reads user inputs and renders results. browser-client.mjs exchanges messages with browser-worker.mjs. That background worker performs real inference, detection, SGD, governance and IndexedDB persistence. No current lab operation needs an HTTP /api request or the former ChatGPT-hosted service.'
m[0]['worked'][1]='Choose score this flow: lab.mjs calls api("/api/infer", {x}). The name is a message operation, not an HTTP fetch. browser-client.mjs posts it to a Web Worker; browser-worker.mjs reads IndexedDB state and calls predict()/explain() from engine.mjs.'
m[0]['checklist'][1]='Identify the shared engine, browser worker and local IndexedDB persistence.'
m[0]['quiz']['why']='engine.mjs is imported by the offline run.mjs and browser-worker.mjs. worker.mjs remains a separate optional server API; main.py remains the legacy synthetic path.'
m[0]['refs']+=['runtime/browser-worker.mjs','runtime/browser-client.mjs']
m[1]['formal'][0]='Start/reset creates an anonymous local model session after choosing a policy. No sign-up or server cookie is required. The active session is stored in this browser profile’s IndexedDB and expires after 24 hours. Other tabs on the same site share it; other devices and browser profiles do not. Audit-only activates candidates while recording failed checks. Gated mode discards a candidate if any required check fails. Neither mode authorizes network access.'
m[1]['formal'].append('The stream chart now persists its latest 512 predictions and restores them on reload alongside counters. The point-inspection slider explains a selected flow’s score, source and label. The detector explanation reports actual evidence and missing conditions. Raw JSON is secondary to the readable candidate decision table. Resetting clears this browser session’s stored history; export first.')
m[3]['formal'][2]+=' The lab now displays all 12 contributions, with expandable explanations of each signed difference and the bar scaling.'
m[4]['formal'][3]='No candidate does not mean no attacks. It can mean insufficient labels, no threshold crossing, insufficient spacing or use of single-flow inference only. The new lab shows actual per-batch detector evidence and explains why a candidate did or did not occur. Full error-history counts are shown before the post-attempt reset.'
m[6]['worked']+=['Actual screenshot reproduction: at flow 1,280, candidate 7 has ECI 0.94697 (passes). Anchor loss changes from 0.1132777 to 0.1922637: increase 0.078986, above the 0.05 limit. Attack-anchor misses improve from 8.333% to 6.25% (passes). Gated mode rejects because anchor loss alone fails. The entire gated compact replay has 7 attempts = 4 activated + 3 discarded.']
m[7]['formal'][2]='browser-worker.mjs stores an active session ID, revision, expiry, model state, candidate AJRs and the latest 512 stream predictions in IndexedDB. Recent and replay buffers contain submitted feature values. No input is uploaded by the lab’s model operations. The session is shared across tabs in the same browser profile; it is not a shared server database or centralized collection from all visitors.'
m[7]['formal'][3]='The Web Worker serializes requests within its tab. Before committing a computed stream result, an IndexedDB read/write transaction rechecks the session ID and revision, preventing a stale tab from overwriting another tab’s update or a reset. The latest request_id can return a saved reply; stale revisions return a conflict. Sessions expire after 24 hours and accept up to 20,000 flows. Unlike the old server API, the browser lab has no IP creation-rate limit. Local audit timestamps depend on the device clock; browser-controlled records are not independently trusted evidence.'
m[7]['checklist'][2]='Explain browser-profile isolation, shared tabs, 24-hour expiry and browser-controlled evidence.'
m[8]['formal'][2]+=' The GitHub Pages migration is checked separately for actual browser inference, replay parity, local persistence, CSV input and explained decisions; the earlier server verification file is historical evidence, not a test of this new hosting architecture.'
c['glossary']=[row for row in c['glossary'] if row[0]!='D1']+[['IndexedDB','This browser profile’s persistent local database; clearing site data deletes local sessions.'],['Web Worker','Background JavaScript execution keeping real model computation off the page’s main UI thread.'],['D1','Database used by the optional earlier server API, not the primary GitHub Pages lab.']]
for row in c['filemap']:
    if row[0]=='runtime/worker.mjs':row[1]='Optional earlier HTTP/D1 server API. The GitHub Pages lab does not call it.'
    if row[0]=='db/schema.ts; drizzle/':row[1]='Database schema/migrations for the optional server API; not required by browser IndexedDB.'
c['filemap'] += [['runtime/browser-worker.mjs','Actual browser-side model operations, evidence explanations and IndexedDB transactions.'],['runtime/browser-client.mjs','Message bridge from lab UI to the Web Worker; operation names resemble API paths but do not send HTTP requests.'],['explanations.mjs','Feature meanings, metric definitions, precise audit-decision arithmetic and field dictionary.'],['scripts/build-pages.mjs; scripts/serve-pages.mjs; .github/workflows/pages.yml','Build static GitHub Pages assets, preview the subpath locally, and deploy through GitHub Actions.']]
c['api']=[[route.replace('GET ','').replace('POST ',''),meaning] for route,meaning in c['api']]
c['ui_elements']=[
['Navigation and DT mark','Research results returns to evidence; Full interactive guide opens the offline-capable study tool; Code flow jumps to the operation trace; Source code opens GitHub. DT is branding, not a metric.'],
['Runtime status and dot','Loading means assets/storage are not ready; ready means trained weights and local IndexedDB are accessible. The green dot is availability, not a safety rating.'],
['Policy dropdown','Chooses the policy for the next reset session. It does not silently change the current session. The adjacent text warns when the selected policy differs from the active one.'],
['Start / reset model session','Loads initial weights and replaces the browser’s current model state, replay position and records. Export first.'],
['Session revision and labels','Revision counts completed stream operations; it is not the candidate count. Labels received counts rows with known/supplied 0/1 feedback.'],
['Single flow tab','Shows the one-flow prediction form. Switching tabs changes the visible panel, not model weights.'],
['Held-out example dropdown','Loads an exact measured source row and shows its original label/family. It does not run inference until requested. Edited values invalidate that reference label for the modified input.'],
['Feature fields and meaning panels','All twelve fields show their unit, semantic definition, current value and training min/max. These bounds describe observed training data, not universal physical limits or a correctness guarantee.'],
['Run actual inference','Scores one input with current weights and explains all features. No training, stream increment or AJR.'],
['Dataset replay tab','Shows the compact 1,280-flow constructed sequence. The supplied dataset labels are revealed after prediction, enabling supervised updates.'],
['Regime boxes and progress bar','Four 320-flow known/novel/known-return/novel-return phases. Highlighting is data mix; it is not detector ground truth. Progress is processed replay rows divided by 1,280.'],
['Process next 128 flows','Runs four consecutive internal batches of 32. An accepted update can affect later batches within this request.'],
['Run remaining replay','Repeats 128-flow requests until the replay ends or Pause is requested. It does not guarantee an update after each request.'],
['Pause after this batch','Stops before the next request after the current one completes. It does not roll back results or kill a half-committed update.'],
['CSV stream tab and file chooser','Selecting a file shows name and size. It does not calculate or upload measurements. Exact header names map the twelve features, independently of CSV order.'],
['Process CSV stream','Validates all rows, then computes locally. Maximum 256 rows and 2 MB. Optional labels use 0/1/blank. Unlabelled uploads cannot initiate training.'],
['Download CSV example','Saves a header and one measured example as a starting format. Replace it with your measurements, not invented credentials or identity fields.'],
['Trust score and risk badge','Trust is 100 times one minus the raw attack score. The badge flags attack score at least 0.5. The dynamic paragraph shows arithmetic and correctness against a valid supplied label. Neither is an authorization decision.'],
['Model fingerprint panel','SHA-256 identifies current weight content. A changed hash means changed content, not improved performance.'],
['Input Predict Detect Candidate Audit buttons','Selecting any stage explains its code function. Green indicates stages involved in the last operation; an amber audit stage indicates flagged checks. These colors are not user access permissions.'],
['Four counters','Observed stream flows; candidate models trained; candidates activated; candidates discarded. Attempts equal activated plus discarded. Single inference does not increment them.'],
['Stream chart and point slider','Y is trust 0–100; X is flow position. Dashed line is 50. A point is one prediction. The slider explains exact source, label and score. Lines connect record order, not elapsed time. Latest 512 values persist and restore.'],
['Why an update happened panel','Shows actual last-batch error-history size, recent/reference error, attribution shift, label count and spacing. It distinguishes a detector signal from eligibility for candidate training.'],
['Feature contribution rows','All twelve signed perturbation comparisons are ranked by absolute size. Expand to read each meaning. Bar width is relative to the largest contribution for this input, not a probability.'],
['Refresh saved records','Reads current IndexedDB audit records without training or changing decisions.'],
['Verify record chain','Recomputes record hashes, links and chain head. It checks internal consistency, not ground-truth labels or independent immutability.'],
['Export AJRs','Downloads the actual local session audit as JSON. No new model update occurs and the download is not a server submission.'],
['Audit filter','Shows all, activated or discarded candidates. Filtering never modifies the stored audit or model.'],
['Candidate row header','Candidate number, processed-flow position, activated/discarded state and ECI. Expand to see the exact reason and old/candidate comparison.'],
['Candidate check table','Each check shows old value, candidate value, threshold, pass/fail and an explanation of the arithmetic. One failing check rejects a gated candidate, even with a high ECI.'],
['Raw audit field dictionary and JSON','Every top-level field has a definition. Training IDs can repeat through replay; top-feature IDs are zero-based indices. Raw JSON is for independent verification, not the first explanatory view.'],
['Chain head','The newest record hash links the end of the audit. Keep a trusted copy elsewhere if detecting substitution matters.'],
['Code-flow operation selector','Changes the displayed function/file path and explanation for inference, replay, audit or initial research fitting. It is an explanation selector, not an execution button.'],
['Error messages','Describe missing sessions, invalid values/files, stale revisions or load/storage failures. A technical error is not the same as a risky flow or rejected candidate.'],
['Research protocol selector','Chooses recorded stationary versus shifted results. It does not run new experiments.'],
['Research table configuration buttons','Select a model to explain below the table. They do not activate that configuration in the live session.'],
['Configuration and metric explanation selectors','Dynamically translate the selected measured mean/SD, model method, metric formula and scope. F1 is not accuracy; false-alarm rate uses benign flows as its denominator.'],
['Research figures and legends','Each figure’s expansion explains axes, colors, aggregation, baseline/reference lines, primary-seed versus five-run scope and interpretation limits. Workflow arrows indicate operations, not causal proof.'],
['PDF SVG PNG and archive links','Download static paper artifacts. PDF/SVG are vectors; PNG is raster. The figure archive contains 27 files; the numerical archive contains predictions and event results. Downloading does not train.'],
['Model manifest dataset and source links','Open reproducibility files: fitted weights/scaler, actual data counts/checksums, execution provenance and source code. They are evidence locators, not endorsements or certifications.'],
['Fieldbook module navigation and three stages','Select a topic, then Understand, Work it out or Explain it. Activities compute locally and never mutate a live model session.'],
['Fieldbook Reset and quizzes','Reset restores illustrative exercise inputs. Quizzes give explanatory feedback and allow retry; they do not evaluate research validity.'],
['Fieldbook explain-back and completion','Write your own explanation, reveal a checklist, and explicitly self-mark completion. No AI grades it. Drafts remain in memory until reload.'],
['Review deck and note export','27 cards can be revealed, self-graded, shuffled, filtered to আবার and restored. Export notes downloads drafts/progress; reload resets study memory.'],
['Glossary search and Close','Filters local definitions. Close or Escape returns to the lesson. No search query leaves the device.'],
['Footer attribution and CC BY 4.0','Names the dataset creators/license. It is reuse attribution, not evidence of security certification.']
]
p.write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
# Reconcile the authored document generator with the new deployment contract.
p=R/'qa/build_dossier.py';s=p.read_text(encoding='utf-8').replace('HTTP request map','Browser operation map').replace('HTTP route map','Browser operation map')
s=s.replace("doc.add_heading('Developer commands and safe interpretation',1)","doc.add_heading('Every page control and display',1);table(['Control or text','Meaning and consequence'],C['ui_elements'],[2.4,4.6])\ndoc.add_heading('Developer commands and safe interpretation',1)")
s=s.replace('pnpm dev → local lab at http://localhost:8787/lab.html with SQLite-backed session state.','pnpm build:pages then pnpm dev:pages → local static lab at http://localhost:8788/drifttrust_audit/lab.html with browser IndexedDB state. pnpm dev retains the optional server API for separate API tests.')
s=s.replace('Live lab: https://drifttrust-audit-lab.pipratools.chatgpt.site/lab.html','Live lab: https://the-sudipta.github.io/drifttrust_audit/lab.html')
s=s.replace('open the deployed lab or run pnpm dev; double-clicking lab.html alone cannot run its Worker API.','open GitHub Pages or run pnpm build:pages and pnpm dev:pages; double-clicking lab.html alone cannot load its browser module worker and JSON assets.')
s=s.replace('Repository at the inspected snapshot: https://github.com/the-sudipta/drifttrust_audit/tree/32e224d901843acc4761f25fd02d93f73a5174f0.','Current repository and browser migration: https://github.com/the-sudipta/drifttrust_audit. The scientific engine remains the same as the original measured snapshot.')
s=s.replace('The offline guide never modifies a hosted model, submits measurements or creates live AJRs.','The offline guide never modifies a lab model session or submits measurements. Its audit activity edits only a copied record.')
p.write_text(s,encoding='utf-8')
p=R/'qa/fieldbook.source.html';s=p.read_text(encoding='utf-8')
s=s.replace('SOURCE SNAPSHOT 32e224d','GITHUB PAGES · BROWSER ENGINE').replace('https://drifttrust-audit-lab.pipratools.chatgpt.site/lab.html','https://the-sudipta.github.io/drifttrust_audit/lab.html').replace('https://github.com/the-sudipta/drifttrust_audit/tree/32e224d901843acc4761f25fd02d93f73a5174f0','https://github.com/the-sudipta/drifttrust_audit')
s=s.replace("['lab.mjs','POST /api/infer','worker.mjs','engine.predict / explain']","['lab.mjs','browser-client message','browser-worker.mjs','engine.predict / explain']").replace("['lab.mjs','POST /api/replay','processBatch × batches','D1 state + AJRs']","['lab.mjs','browser-worker message','processBatch × batches','IndexedDB state + AJRs']")
s=s.replace('the Worker computes a fresh score','the browser worker computes a fresh score').replace('D1','IndexedDB')
s=s.replace("table(['Route','Purpose'],C.api)","table(['Message operation','Purpose'],C.api)+'<p>These path names identify Web Worker messages in the current browser lab, not HTTP API requests.</p><h3>Every control and display</h3>'+table(['Control or text','Meaning and consequence'],C.ui_elements)")
s=s.replace('<button id="mapOpen">Code map</button>','<button id="mapOpen">Code and every control</button>')
s=s.replace('Reload resets study progress</span>','Reload resets study progress</span>')
s=s.replace('Study notes stay in memory until reload.','Every control: Visitor walkthrough gives eight operating steps; Code and every control opens the file/API map and complete interface glossary; Glossary searches terms; Review deck starts self-graded recall; Export notes saves your drafts. Understand teaches definitions, Work it out runs an activity, and Explain it checks your own recall. Study notes stay in memory until reload.')
p.write_text(s,encoding='utf-8')
print('Reconciled nine modules and',len(c['ui_elements']),'interface explanation groups for GitHub Pages.')
