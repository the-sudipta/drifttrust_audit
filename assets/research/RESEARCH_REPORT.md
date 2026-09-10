# DriftTrust-Audit: RT-IoT2022 experiment report

## Scope and provenance

Deployment update (10 September 2026): the GitHub Pages lab now includes [animated numerical traces](MATH_ANIMATIONS.md) from actual inference and sampled SGD steps. The experiment, figures and archived execution manifest below remain unchanged. Tests verify tracing preserves replay predictions, candidate weights and policy outcomes; animation capture adds overhead and changes source bytes, so current UI timing is not the original experiment's latency.

This is an executed public-data research experiment and a working network-risk demonstration. It is not an enterprise access-control field trial, ISO certification, or evidence that publication acceptance is assured.

Dataset: B. S. Sharmila and Rohini Nagapadma, RT-IoT2022, UCI Machine Learning Repository, DOI https://doi.org/10.24432/C5P338, CC BY 4.0. Official source: https://archive.ics.uci.edu/dataset/942/rt-iot2022. Captured IoT testbed traffic includes generated attacks. The archived CSV, rather than the inconsistent class-count prose on the source page, is the numerical source of truth. See dataset.json for checksums and observed counts.

## Data audit and experimental unit

The downloaded archive contains 123,117 rows. Twelve numeric flow fields form the deployed input vector. No identifier, port, protocol category, service category, label, or attack-family name is a predictor. There are no invalid selected numeric rows. Nine exact input-vector groups contain conflicting binary labels (2,098 source rows); these are excluded. Exact remaining input vectors are deduplicated, leaving 17,701 records. This removes repeated vectors, not statistically dependent captures: nearby or similar flows may remain dependent. Deduplication radically changes prevalence; these metrics describe unique vectors, not raw traffic-frequency performance.

Features: flow_duration, fwd_pkts_tot, bwd_pkts_tot, flow_pkts_per_sec, down_up_ratio, flow_SYN_flag_count, flow_RST_flag_count, flow_ACK_flag_count, flow_pkts_payload.avg, flow_pkts_payload.std, fwd_init_window_size, bwd_init_window_size.

The new public-data backend uses 1 = attack and 0 = benign; trust = 1 - P(attack). The legacy synthetic code uses the opposite label convention. The backends are deliberately separate and must not share labels without conversion.

## Protocol

Known families are stratified 60/20/20: 7,297 training, 2,432 validation and 2,433 known-family test records for each seed. ARP_poisioning, DDOS_Slowloris and NMAP_XMAS_TREE_SCAN are entirely absent from training and validation (5,539 held-out records). The shifted test has 7,972 records. Fixed seeds: 11, 23, 37, 53, 71. The primary detailed-figure seed was fixed at 11, not chosen by test performance.

Stationary replay shuffles known-family test records. Shifted replay alternates known and novel attack-family pools across four phases, splitting benign records across all four phases. Each held-out record appears once per protocol/seed. There are no released capture timestamps, so these are explicitly constructed mixture-shift schedules; the experiment does not establish natural chronological concept drift. The held-out family counts after deduplication include only 10 Xmas-tree vectors and 5 total FIN-scan vectors, limiting family-specific inference.

Predictions precede label revelation for all records in each batch of 32. Model updates occur only after those predictions. Labels are promptly available by assumption. Training-derived log1p transformation, mean, standard deviation, and clipping to [-8,8] are fixed. The canonical anchor set comes only from validation; the initial replay buffer comes only from training.

## Model, adaptation, and governance

The deployed model is a 12-input, 24-tanh-hidden-unit, sigmoid-output MLP. Initial fitting uses scikit-learn Adam and training-only balanced resampling for at most 45 epochs. The checkpoint is selected using known-family validation log loss, with seven-epoch patience. This is a per-flow backend, not the proposed temporal LSTM/GRU; it does not invent enterprise-session features from unrelated flow data.

All inference and online update equations are implemented once in runtime/engine.mjs, shared by the offline experiment and the Worker. Exported model inference is checked independently against scikit-learn predictions (80 records, absolute tolerance 1e-10). Incremental learning uses three SGD passes, learning rate 0.003 and L2 coefficient 0.0001, over up to 128 recent records plus up to 128 replay records.

Drift triggers: a 64-label error window exceeds the previous 192-label reference by 0.08, or the maximum normalized perturbation-importance change exceeds 0.15. Candidate attempts require 128 records since the last attempt and at least 64 labelled recent records. Attribution comparisons use the current batch against a reference distribution. Stationary false triggers are therefore measured rather than assumed absent. Error-only ablation disables the attribution trigger.

ECI averages top-5 Jaccard overlap and normalized Kendall tau-b of absolute perturbation importances on the identical fixed anchors before and after the candidate. Ties are handled explicitly. Perturbation replaces one transformed feature with zero (its training mean in log space); this is not SHAP and is not causal attribution.

Audit-only accepts candidates while recording all policy flags. Gated mode accepts only if ECI >= 0.5, anchor log-loss increase <= 0.05, attack-miss-rate increase on attack anchors <= 0.05, and minimum update spacing passes. Failed candidates leave the active weights unchanged. The mapping to A.5.15, A.8.16 and A.5.36 is a research policy mapping; no claim of complete ISO compliance is made.

AJR records identify the exact training and canonical source rows, before/candidate/active model SHA-256 values, drift evidence, candidate losses, policy outcomes, and previous/current record hashes. Hash chaining detects modification against a separately trusted chain head; it does not prevent a database administrator rewriting the complete chain.

## Results

Attack is the positive class. Entries are mean +/- sample SD across five seeded splits. All classifiers use the same 12 transformed inputs and 0.5 threshold within each split. Logistic regression (C=1, balanced class weights) and random forest (200 trees, depth 16, min leaf 2, balanced weights) are static baselines. No test-driven hyperparameter search was performed. Training algorithms differ; these are implementation baselines, not exhaustive tuned state-of-the-art comparisons.

### Stationary replay

| Model | Attack F1 | Balanced accuracy | Attack recall | Benign false alarms |
|---|---:|---:|---:|---:|
| Logistic regression | 0.6586 +/- 0.0168 | 0.9398 +/- 0.0155 | 0.9030 +/- 0.0314 | 0.0234 +/- 0.0015 |
| Random forest | 0.9121 +/- 0.0188 | 0.9695 +/- 0.0199 | 0.9424 +/- 0.0407 | 0.0035 +/- 0.0015 |
| DriftTrust gated | 0.7936 +/- 0.0389 | 0.9593 +/- 0.0147 | 0.9303 +/- 0.0332 | 0.0117 +/- 0.0045 |
| Audit-only MLP | 0.7995 +/- 0.0384 | 0.9552 +/- 0.0189 | 0.9212 +/- 0.0420 | 0.0109 +/- 0.0047 |
| Gated: error only | 0.7719 +/- 0.0270 | 0.9715 +/- 0.0187 | 0.9576 +/- 0.0377 | 0.0146 +/- 0.0020 |
| Gated: no replay | 0.8125 +/- 0.0207 | 0.9514 +/- 0.0162 | 0.9121 +/- 0.0328 | 0.0093 +/- 0.0014 |
| Frozen MLP | 0.7719 +/- 0.0270 | 0.9715 +/- 0.0187 | 0.9576 +/- 0.0377 | 0.0146 +/- 0.0020 |
| Adaptive MLP | 0.7995 +/- 0.0384 | 0.9552 +/- 0.0189 | 0.9212 +/- 0.0420 | 0.0109 +/- 0.0047 |

### Shifted replay

| Model | Attack F1 | Balanced accuracy | Attack recall | Benign false alarms |
|---|---:|---:|---:|---:|
| Logistic regression | 0.5077 +/- 0.0375 | 0.6604 +/- 0.0169 | 0.3442 +/- 0.0342 | 0.0234 +/- 0.0015 |
| Random forest | 0.2999 +/- 0.1571 | 0.5908 +/- 0.0562 | 0.1851 +/- 0.1136 | 0.0035 +/- 0.0015 |
| DriftTrust gated | 0.5872 +/- 0.1600 | 0.7053 +/- 0.0801 | 0.4352 +/- 0.1665 | 0.0245 +/- 0.0120 |
| Audit-only MLP | 0.9064 +/- 0.0191 | 0.8800 +/- 0.0186 | 0.8667 +/- 0.0324 | 0.1066 +/- 0.0186 |
| Gated: error only | 0.5624 +/- 0.1734 | 0.6953 +/- 0.0857 | 0.4127 +/- 0.1817 | 0.0221 +/- 0.0128 |
| Gated: no replay | 0.5339 +/- 0.0760 | 0.6761 +/- 0.0337 | 0.3697 +/- 0.0692 | 0.0176 +/- 0.0034 |
| Frozen MLP | 0.4060 +/- 0.1239 | 0.6239 +/- 0.0507 | 0.2625 +/- 0.1002 | 0.0146 +/- 0.0020 |
| Adaptive MLP | 0.9064 +/- 0.0191 | 0.8800 +/- 0.0186 | 0.8667 +/- 0.0324 | 0.1066 +/- 0.0186 |

### Interpretation

The audit-only and ungoverned adaptive models have exactly equal prediction sequences by design and by test. On shifted replay their mean attack F1 is 0.9064 +/- 0.0191. The frozen MLP achieves 0.4060 +/- 0.1239. This supports the feasibility of adding audit evidence without changing those predictions, not a claim that logging itself improves classification.

The gated variant achieves shifted attack F1 0.5872 +/- 0.1600. It improves the average over the frozen MLP but substantially underperforms unconstrained adaptation. In one split all shifted candidate updates are rejected. The fixed old-family anchor gate can impede learning unfamiliar attack patterns. Threshold calibration and anchor design are unresolved research problems, not hidden experimental successes.

Uncertainty intervals in results.json are descriptive t intervals across five seeded splits. Those splits reuse the dataset and novel-family records; they are not independent population experiments. No p-value or acceptance/superiority guarantee is claimed. All per-seed differences are in paired_differences.csv. One-seed figures are explicitly labelled as primary-seed diagnostics.

Alarm delay is measured to the first candidate trigger within each following constructed regime; unmatched transitions are separately counted. Alarms are candidate attempts, not accepted updates. These are regime-response measurements, not estimates of true natural-drift MTTD. False alarms and missed transitions remain limitations.

Local runtime wall times include prediction, detector work, candidate training, and hashing, excluding initial model fitting and I/O. They are not a controlled cloud-overhead benchmark. The audit-only versus ungoverned pairs can be inspected, but no latency advantage is inferred from a single ordered timing pass.

## Figure captions

1. Raw and deduplicated RT-IoT2022 class counts. Log horizontal scale; counts after conflict exclusion and exact selected-feature deduplication.
2. Attack-class F1 for eight configurations under stationary and constructed shifted replay. Bars: five-split mean; error bars: one sample SD.
3. Primary-seed rolling balanced accuracy and error fraction. Nonoverlapping 256-flow reporting windows; vertical dotted lines mark constructed regime boundaries.
4. Primary-seed ROC and precision-recall curves on shifted replay. Attack is positive; the PR reference is observed test attack prevalence.
5. Primary-seed shifted confusion matrices. Cells show counts and within-true-class percentages.
6. Primary-seed gated candidate ECI and anchor log-loss changes. Green circles accepted; red crosses rejected. Dashed thresholds are predefined policy thresholds.
7. Primary-seed correct classification by family, with test support counts. Small classes are descriptive only.
8. Public-data experimental workflow, including disjoint preprocessing, model-selection, and evaluation stages.
9. Live deployment architecture. GitHub Pages serves static files; a browser Web Worker executes the shared model engine on submitted measurements. Candidate checks compare fixed validation anchors, and IndexedDB stores the local model and audit chain. Passing candidates, or flagged candidates under audit-only policy, activate; failed candidates under gated policy are discarded. Browser-controlled records require a separately trusted chain head for independent evidence. The optional HTTP/D1 implementation remains in the repository but is not required by this deployed lab.

All nine figures are supplied in vector PDF/SVG and 300-DPI PNG. Editing source: research/report.py.

## Reproduction

Create a Python 3.12 environment and install requirements-research.lock.txt. Install Node dependencies with pnpm install --frozen-lockfile. Then run:

```sh
python research/prepare.py
node research/run.mjs
python research/report.py
node --test tests/*.test.mjs
```

The downloader validates the pinned ZIP hash. Model bundles, split hashes, software versions, and runtime source hash are exported. Timings, timestamps and session identifiers are not bitwise deterministic. Numerical reruns should use the dependency lock and stated versions. Full predictions and actual AJRs for all configurations/seeds are included in replication_results.zip. Original archive and prepared intermediates remain in ignored data directories and can be rebuilt.

## Remaining work before strong deployment or publication claims

Independent datasets; timestamped capture-level or device-level splits; less correlated flow groups; delayed/incorrect-label experiments; calibrated scores; rigorous drift ground truth; gate-threshold/anchor sensitivity; poisoned-feedback robustness; auditor evaluation; realistic access-authorization ground truth; organizational policy validation; independent literature novelty review. The public live lab is working research software, not evidence that all these claims are established.
