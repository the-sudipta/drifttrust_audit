# GitHub Pages execution and deployment guide

Primary research site: https://the-sudipta.github.io/drifttrust_audit/
Explained lab: https://the-sudipta.github.io/drifttrust_audit/lab.html
Interactive code guide: https://the-sudipta.github.io/drifttrust_audit/guide.html

## Where code executes

GitHub Pages serves static HTML, JavaScript, measured examples, trained weights and paper artifacts. The lab computes actual predictions and online updates in a browser Web Worker, importing the same runtime/engine.mjs used by the offline research. It does not call a ChatGPT-hosted API.

lab.mjs sends operation messages through runtime/browser-client.mjs to runtime/browser-worker.mjs. The latter loads model.json/replay.json/examples.json, validates measurements, invokes the shared engine and saves state in IndexedDB. Model preparation still runs offline in Python; online adaptation really changes weights through the shared JavaScript SGD implementation.

## What is accepted or rejected

A candidate is a proposed new model version. Audit-only activates candidates while recording failed checks. Gated mode activates a candidate only when ECI, anchor loss, anchor attack misses and spacing pass. A rejection retains old weights for subsequent predictions. It does not reject a person, network flow, packet or access request.

The compact gated replay produces 7 candidates: 4 activated and 3 discarded. At candidate 7 (flow 1280), ECI is about 0.94697, but anchor loss increases from 0.1132777 to 0.1922637, exceeding the 0.05 allowed increase. That alone rejects the candidate in gated mode.

## Storage and integrity

IndexedDB database drifttrust-pages-v1 holds one active model session for this site in the current browser profile. It includes current weights, recent/replay learning buffers, candidate records, request revision, most recent response and up to 512 stream predictions. Tabs in the same profile share state; different devices/profiles do not. No visitor inputs or labels are sent by model operations to an application backend.

Sessions expire after 24 hours and process at most 20,000 stream flows. Reset replaces the active session; export first. Clearing site data deletes local records. Inference alone does not change the scientific session counters or weights. Stream results and their chart restore on reload.

The Web Worker serializes requests within its tab. An IndexedDB read/write transaction checks session ID and revision before committing, preventing a stale operation from overwriting another tab's update or a reset. The most recent request_id supports retry; stale revisions are rejected.

AJRs are canonical-JSON SHA-256 linked records. Verification checks content and links against the provided head. A browser owner can rewrite the complete local history; this is not independent, immutable, centralized or externally notarized evidence. Timestamps depend on the device clock. Visitor labels remain assertions.

## Operating the lab

The dark animated-mathematics panel reads actual worker captures. **Animate selected flow** performs ordinary inference on the input form; Play, Replay and the animation timeline only inspect that completed calculation. Stream operations retain up to eight candidate captures and the last streamed probe in IndexedDB. Each candidate contains three sampled SGD steps (first row of each pass) and complete before/candidate/retained weights. Single-flow animation captures remain in tab memory. **[Every animation control, equation and code path](MATH_ANIMATIONS.md)** is documented separately and summarized in the fieldbook.

Start/reset after choosing a policy. Single flow computes scores and all twelve feature perturbations without training. Dataset replay processes 128 flows per click, internally in batches of 32, with labels revealed after each batch's predictions. Run remaining repeats this; Pause stops after the current request finishes. CSV stream accepts up to 256 rows and 2 MB, exact feature names, optional label 0/1/blank. An unlabelled-only batch cannot initiate learning.

The dynamic explanations cover every feature/unit/value, actual score calculation, observed flow versus candidate counters, chart axes and selected points, detector conditions, all four candidate checks, raw audit fields, fingerprints, filters, verification and exports. The guide includes a complete control glossary.

## Local preview and publication

```sh
pnpm install --frozen-lockfile
pnpm build:pages
pnpm dev:pages
# http://localhost:8788/drifttrust_audit/lab.html
```

The .pages output contains only intended public assets and the browser runtime. .github/workflows/pages.yml builds it and publishes through GitHub Actions. The repository Pages setting must use GitHub Actions (build_type workflow). No secret, external database or backend account is required for this browser execution.

Double-clicking lab.html cannot load the module worker and fetched JSON reliably; use the HTTPS site or local server. guide.html is self-contained and works offline by double-click. Its learning progress stays only in memory and can be exported explicitly.

## Optional earlier server implementation

runtime/worker.mjs, db/schema.ts and drizzle/ retain the earlier HTTP/D1 implementation for a separate server deployment. pnpm dev runs that local server adapter at port 8787; tests/api-check.mjs tests its HTTP endpoints. The new GitHub Pages UI does not use those HTTP routes. The existing .openai/hosting.json belongs to the prior optional deployment; it is not used by the GitHub Pages workflow.

The earlier assets/research/deployment_verification.json is historical server verification, not evidence of the new browser migration. Use browser verification and actual current page behavior for the latter.

## Research scope

The animation adds optional trace collection to the shared engine without changing its update arithmetic, candidate policy or checkpoint. Traced/untraced replays are tested for identical predictions and candidate weights. Source bytes and measured execution overhead do change; archived paper manifests and latency results describe their original experiment, not this instrumented UI. Numerical trace exports supplement AJRs and are not independently attested evidence.

Initial weights are predetermined seed 11. The online replay is a compact 1280-flow subset, not the full 7972-flow shifted paper evaluation. Predictions precede feedback; scores are uncalibrated. Compatible traffic collection, enterprise identity integration, trusted delayed feedback and policy enforcement are still separate work. A working browser research lab does not establish guaranteed security, ISO compliance or reviewer acceptance.

GitHub documentation: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
