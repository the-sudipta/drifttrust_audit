# DriftTrust Audit code and live lab teaching brief



## Purpose and learner

এই guide-এর লক্ষ্য: repository বুঝতে পারা, browser-এর ভিতরে model ও audit পর্যন্ত একটি operation অনুসরণ করা, এবং একজন visitor-কে সৎভাবে system দেখানো। The deployed product scores measured network flows and studies model adaptation with audit evidence. It does not automatically inspect the visitor's network or grant enterprise access.

GitHub Pages browser migration inspected 9 September 2026. The scientific engine and published initial weights remain from the measured experiment; the interface and persistence now run locally in the browser. Current primary site: GitHub Pages; model execution and session storage stay in the browser.

Learner: Sudipta, CSE graduate and instructor. Prerequisites: basic functions, HTTP and elementary classification; every project-specific term is defined. Mastery: trace a request, operate all three input routes, distinguish scoring from learning, interpret governance records, reproduce the experiment and explain its limitations.

## Deliverables

This completed brief; a substantive Word dossier; an offline single-file learning_module.html. Store everything in this new topic directory. Preserve the deployed repository and supplied research artifacts.

## Language and depth

English technical explanations with natural বাংলা bridges. Nine ordered modules, five labelled teaching steps per module, a worked application, an activity beyond recall, a quiz, and an explain-back checklist. Simple arithmetic first; no unexplained symbolic notation. Actual checkpoint outputs are marked separately from teaching examples.

## Module specifications

### 1 What is actually running

Outcome: Three connected parts: evidence website, working browser lab, and reproducible experiment. Accent: #127d79.

Question and prediction: Before selecting an action, predict whether it needs only static files, a Worker request, or the offline experiment.

Action, consequence, explanation, reset and boundary: Select a task. The highlighted code path changes between static presentation, live Worker processing and offline experiment. Reset to paper results; no network calls are made.

Explain-back: Explain the difference between the evidence page, live lab and old Python prototype.

Sources: README.md, main.py, models/trust_scorer.py, research/run.mjs, runtime/worker.mjs, runtime/browser-worker.mjs, runtime/browser-client.mjs.

### 2 A visitor's first ten minutes

Outcome: Start with actual examples; use replay to see adaptation; upload measurements only when available. Accent: #426aa6.

Question and prediction: Choose a visitor goal and whether trusted labels are available; predict which control to use and whether it can learn.

Action, consequence, explanation, reset and boundary: Choose example, replay or own CSV and toggle label availability. The recommended controls and learning eligibility update. Reset to first-time visitor; do not imply the offline guide contacts the live service.

Explain-back: Guide a visitor from first opening the lab to exporting their first audit record.

Sources: lab.html, lab.mjs, runtime/worker.mjs, assets/research/examples.json.

### 3 Data provenance and initial training

Outcome: Real measurements support a bounded experiment, not every proposed enterprise claim. Accent: #8b683c.

Question and prediction: Predict which partition may supply scaler statistics, anchors and initial weights; assign each source before checking leakage.

Action, consequence, explanation, reset and boundary: Assign sources for scaler, anchors and initial weights. Report protocol leakage or valid selection. Reset to an intentionally incorrect assignment; use actual fixed partition counts.

Explain-back: Explain what makes this a real-data experiment and why it is not natural chronological drift evidence.

Sources: research/prepare.py, assets/research/dataset.json, assets/research/RESEARCH_REPORT.md.

### 4 How one flow becomes a score

Outcome: Twelve numbers enter trained equations; the returned number is an uncalibrated attack score. Accent: #166c86.

Question and prediction: Before changing packet rate, predict whether this fixed trained model's score must rise. Then test it; nonlinear models need not be monotonic.

Action, consequence, explanation, reset and boundary: Choose a real example and change packet rate. Compute the actual frozen MLP locally, show score/flag and edited-input caveat. Reset restores the original row. Zero and large rates are boundary probes, not new measurements.

Explain-back: Trace raw flow measurements through preprocessing, the MLP and the displayed trust score.

Sources: runtime/engine.mjs, runtime/worker.mjs, assets/research/model.json, lab.mjs.

### 5 When the stream suggests drift

Outcome: An attack flag concerns one flow; a drift signal concerns changing model behavior over evidence. Accent: #98554c.

Question and prediction: Predict whether the detector triggers and whether training is permitted; these are two different answers.

Action, consequence, explanation, reset and boundary: Change recent/reference error counts, attribution difference, available labels and spacing. Show signal and candidate eligibility separately using the actual thresholds. Reset to the worked case; equality does not pass strict drift thresholds.

Explain-back: Explain an observed zero-candidate count without assuming the service is broken.

Sources: runtime/engine.mjs, assets/research/model.json, drift/detector.py.

### 6 How a candidate learns

Outcome: Training changes a copy first; the current batch is never rescored as if it had known its own labels. Accent: #715a9c.

Question and prediction: Arrange prediction, feedback, candidate training, policy checks and activation in their valid order. Predict what is wrong with revealing labels first.

Action, consequence, explanation, reset and boundary: Use selects to place prediction, feedback, training, checking and activation in order. Show the first order violation and why it matters. Reset scrambles the steps; no retroactive prediction rewriting is allowed.

Explain-back: Explain why offline and live results use a test-then-train sequence.

Sources: runtime/engine.mjs, runtime/worker.mjs, research/run.mjs, tests/engine.test.mjs.

### 7 Why a candidate is accepted or rejected

Outcome: Audit-only documents checks; gated mode makes those same checks veto an update. Accent: #9b6c2f.

Question and prediction: Choose the mode, then vary ECI and anchor changes. Predict which single failure is enough to block a gated candidate.

Action, consequence, explanation, reset and boundary: Change ECI, loss/miss increases and policy mode. Show failed checks, activation/rejection and active model identity. Reset to the failed-loss example; equality passes gate limits.

Explain-back: Explain the measured benefit and cost of gating without claiming it is always superior.

Sources: runtime/engine.mjs, assets/research/RESEARCH_REPORT.md, assets/research/results.json.

### 8 Audit records and session persistence

Outcome: The evidence describes actual candidate attempts and links each record to the previous one. Accent: #3c6e68.

Question and prediction: Verify a copied real experiment record, then change its status and predict whether the stored fingerprint still matches.

Action, consequence, explanation, reset and boundary: Verify a copied real primary-run AJR using canonical JSON SHA-256; edit status and reverify. Show mismatch and explain trusted-head limits. Reset restores the untouched copy; no original records change.

Explain-back: Describe what an audit export proves and what it cannot prove.

Sources: runtime/engine.mjs, runtime/worker.mjs, db/schema.ts, scripts/verify-audit.mjs, assets/research/DEPLOYMENT.md.

### 9 Reading evidence and defending the project

Outcome: A working research system is valuable when its measured behavior and remaining scope are clear. Accent: #725d87.

Question and prediction: Change false positives and missed attacks while keeping correct detections fixed; predict which metric responds and what a visitor should infer.

Action, consequence, explanation, reset and boundary: Adjust TP/FP/FN counts and compute precision, recall and F1. Show each denominator and distinguish F1 from accuracy. Reset to 80/20/40; empty denominators return zero by a stated teaching convention.

Explain-back: Give a 60-second project explanation including one strength, one measured tradeoff and one unimplemented integration.

Sources: research/report.py, tests/engine.test.mjs, tests/api-check.mjs, assets/research/deployment_verification.json, assets/research/RESEARCH_REPORT.md.

## Evidence and claim ledger

Primary sources are the inspected repository snapshot, actual model.json, examples.json, dataset.json, execution/results files and recorded hosted verification. Dataset attribution: B. S. Sharmila and Rohini Nagapadma, RT-IoT2022, UCI, DOI 10.24432/C5P338, CC BY 4.0; https://archive.ics.uci.edu/dataset/942/rt-iot2022. Figures and reported F1 come from the executed repository experiment. No new empirical result is inferred from an interactive teaching calculation.

Resolve contradictions: legacy label 1 is legitimate, current label 1 is attack; legacy temporal MLP is not an LSTM; public replay has 1,280 rows whereas full shifted test has 7,972. Recorded checks are historical evidence, not continuous monitoring. No claim of full ADWIN, SHAP, ISO certification, network enforcement, independent population trials or reviewer acceptance.

## Interaction and accessibility

One active lesson card, nine navigation items, distinct accents, local Nirmala UI Bengali font fallback, high contrast, keyboard controls, reduced-motion support, 27 shuffled review cards, glossary search and explicit note export. Retain answers and drafts in JavaScript memory only; reload clears them. Progress is self-assessed and never inferred from typing.

## Acceptance criteria

All three files contain substantive consistent content. Read the completed Word dossier back before authoring HTML. Render Word and inspect every page. Run the skill static checker. Exercise every activity, reset/boundary behavior, wrong/correct quiz, draft retention and safe angle brackets, notes export, shuffled/filtered/restored deck and reload reset in a browser with offline file loading. Inspect laptop/tablet/phone layouts and confirm no unexpected requests or console errors. Report precise verification limitations if a required check cannot run.