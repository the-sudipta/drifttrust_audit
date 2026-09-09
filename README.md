# DriftTrust-Audit

Working research software for inspecting how network-risk models adapt and what evidence they leave.

**[Live research site](https://the-sudipta.github.io/drifttrust_audit/) · [Try the actual model](https://the-sudipta.github.io/drifttrust_audit/lab.html) · [GitHub Pages](https://the-sudipta.github.io/drifttrust_audit/)**

The public-data backend runs actual inference, incremental updates, explanation-consistency checks, and audit recording. The GitHub Pages lab runs the same engine in a browser Web Worker, with model state and records in local IndexedDB. Other tabs in the same browser profile share the session; no model input is posted to the former hosted API. The old hand-written browser risk formula has been removed.

## Execution and explanations

The primary lab is now hosted on GitHub Pages. It performs actual trained inference, incremental SGD, drift checks and candidate governance in the browser. `runtime/worker.mjs` remains an optional HTTP/D1 server implementation; the current UI uses `runtime/browser-client.mjs` and `runtime/browser-worker.mjs` instead. Local records are browser-controlled evidence, not independently trusted server logs.

[Full interactive code guide](guide.html) explains nine modules and every interface control. The lab explains all twelve features, exact score arithmetic, chart points, detector eligibility and each audit check. **Accepted/rejected counts refer to proposed model versions, not users or flows.** On the compact gated replay, 7 candidates produce 4 activations and 3 discards.

Local GitHub Pages preview:

```sh
pnpm build:pages
pnpm dev:pages
# http://localhost:8788/drifttrust_audit/lab.html
```

## Public dataset and measured results

Source: [RT-IoT2022 at UCI](https://archive.ics.uci.edu/dataset/942/rt-iot2022), B. S. Sharmila and Rohini Nagapadma, [DOI 10.24432/C5P338](https://doi.org/10.24432/C5P338), CC BY 4.0. Captured IoT device traffic includes testbed-generated attacks.

- 123,117 source rows; 17,701 unique valid vectors after selected-feature deduplication and conflict exclusion.
- Twelve measured numeric flow features. No fabricated identity, MFA or device-posture values.
- Five seeds, two explicitly constructed replay protocols, eight model configurations.
- Disjoint training, validation and test vectors; novel attack families are entirely held out.
- Predictions precede label feedback for each 32-flow batch.
- Exact numerical parity between the exported Python-trained model and JavaScript inference, tested to 1e-10.

Shifted replay, attack-positive F1 (mean ± sample SD across five splits):

| Configuration | Attack F1 |
|---|---:|
| Frozen MLP | 0.4060 ± 0.1239 |
| Adaptive MLP without governance | 0.9064 ± 0.0191 |
| Audit-only adaptation | 0.9064 ± 0.0191 |
| Gated adaptation | 0.5872 ± 0.1600 |

Audit-only adds inspectable evidence while preserving the adaptive model's predictions. The gate rejects changes that damage fixed anchors, but also blocks useful learning about new traffic. That limitation is reported explicitly.

**[Full methods and results](assets/research/RESEARCH_REPORT.md) · [All per-seed metrics](assets/research/metrics_per_seed.csv) · [Numerical replication results](assets/research/replication_results.zip)**

## Paper figures

Nine figures are supplied in PDF, SVG and 300-DPI PNG:

1. Dataset audit and family counts.
2. Baseline and ablation comparisons.
3. Stream performance through constructed regime changes.
4. ROC and precision–recall curves.
5. Confusion matrices.
6. Candidate ECI and governance outcomes.
7. Per-family performance and support.
8. Experimental workflow.
9. Live system architecture.

[Download all 27 figure files](assets/research/paper_figures.zip). Figure captions and limitations are in the report. Detailed figures use the predetermined primary seed, 11; aggregate comparisons use all five seeds.

## Reproduce

Python 3.12 and Node.js 24 were used. Keep the Python and pnpm lockfiles.

```sh
python -m venv .venv
# Activate .venv using your shell.
python -m pip install -r requirements-research.lock.txt
pnpm install --frozen-lockfile
python research/prepare.py
node research/run.mjs
python research/report.py
pnpm test
```

The downloader validates the official archive SHA-256. Source data and intermediate files are ignored by Git. Dataset and model provenance are committed under `assets/research/`.

## Run the actual lab locally

```sh
pnpm dev
# Open http://localhost:8787/lab.html
node tests/api-check.mjs http://localhost:8787
```

Use single-flow inference, actual held-out replay, or a compatible CSV stream with optional explicit labels. Audit-only records failed checks; gated mode can reject candidates. Unknown labels never turn into invented training labels. Export AJRs and verify them:

```sh
node scripts/verify-audit.mjs downloaded-session-audit.json
```

[Execution, storage, privacy and deployment guide](assets/research/DEPLOYMENT.md). GitHub Pages serves both the evidence page and the working browser lab. The optional HTTP server can also be exercised with the API checks above.

## Structure

| Path | Role |
|---|---|
| `research/prepare.py` | Dataset download, audit, split, fitting, model export |
| `runtime/engine.mjs` | Shared inference, drift, learning, ECI and policy engine |
| `research/run.mjs` | Actual repeated experiments and ablations |
| `research/report.py` | Metrics, statistical summaries and publication figures |
| `runtime/worker.mjs` | Server API, validated inputs, isolated sessions, audit persistence |
| `db/`, `drizzle/` | Database schema and generated migrations |
| `index.html`, `lab.html` | Evidence page and actual model interface |
| `tests/` | Numerical, governance and API integration verification |

## Scope and research integrity

This is a working **network-risk research deployment**, not a validated enterprise access-enforcement product. The source CSV has no capture timestamps, so schedules are explicitly constructed; naturally occurring concept drift is not established. Data are testbed measurements, not an enterprise authorization dataset. Immediate replay labels are an assumption. Splits reuse source data; statistical intervals describe split variability. Perturbation attribution is not SHAP, and ECI does not establish causal correctness. ISO references are research policy mappings, not certification. A hash chain is not independently immutable storage.

Production identity, collection and enforcement integration, external datasets, delayed labels, robust gate calibration and independent novelty review remain necessary for stronger claims. No publication acceptance or operational security guarantee is made.

## Legacy synthetic prototype

The original Python prototype remains available through `python main.py` and its original `requirements.txt`. It uses simulated 11-feature temporal windows and the opposite label convention (1 = legitimate). It is not used for the new public-data results. Old files in `assets/showcase/` and historical `informations/` describe that earlier experiment; their reported values must not be combined with this study.

MIT license for code. RT-IoT2022 data and derived example rows retain CC BY 4.0 attribution. See LICENSE and CITATION.cff.

## Browser verification

`tests/browser-pages.cjs` exercises the GitHub Pages UI using Playwright: both complete replays, actual example predictions, pause, CSV feedback/no-feedback, rejection arithmetic, audit export/verification, persistence, browser-profile isolation and responsive overflow. Provide an installed `playwright` module (or its path in `PLAYWRIGHT_MODULE`), and optionally a browser executable in `BROWSER_EXECUTABLE`.

```sh
node tests/browser-pages.cjs http://localhost:8788/drifttrust_audit/
# Or pass https://the-sudipta.github.io/drifttrust_audit/
```

Outputs go to ignored `.local/`. The test creates its own disposable browser context. [Complete explanation PDF](assets/research/learning/DriftTrust_learning_dossier.pdf) and [Word dossier](assets/research/learning/DriftTrust_learning_dossier.docx) accompany the offline fieldbook.

[Recorded public GitHub Pages verification](assets/research/browser_verification.json) includes the tested URL, timestamp, source commit and actual replay outcomes.
