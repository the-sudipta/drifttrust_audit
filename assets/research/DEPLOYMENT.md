# DriftTrust-Audit live deployment

Research site: https://drifttrust-audit-lab.pipratools.chatgpt.site/

Live lab: https://drifttrust-audit-lab.pipratools.chatgpt.site/lab.html

These are the configured addresses. Check `/api/health` for current operational availability.

## What runs

The Cloudflare Worker executes the exported 12–24–1 MLP, preprocessing, perturbation explanations, error/attribution drift detection, incremental SGD, ECI, and audit policy logic. `runtime/engine.mjs` is also the offline experiment engine. Cloudflare D1 stores the model and records for each anonymous session. A browser does not approximate the model with a hand-written risk formula.

The published model is the predetermined seed-11 checkpoint; it is not selected as the best test-performing seed. The lab's 1,280-flow replay is a compact, explicitly reordered subset of held-out measured records. It does not reproduce the complete 7,972-flow paper evaluation; run the experiment scripts for that.

Audit-only is the original evidence-producing approach: updates are accepted and failed checks are recorded. Gated mode is an additional experiment: failed candidates are discarded. Start a new session to compare policies from identical initial weights. Never interpret an accepted audit-only update as evidence that all policy checks passed.

## Local setup

Use Node.js 24 and pnpm. Python 3.12 plus `requirements-research.lock.txt` is needed to regenerate the experiment, not for deployed inference.

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Open http://localhost:8787/lab.html. Local state is SQLite under `.local/`; it is ignored by Git. Migrations are applied by the local development adapter. Production migrations run during Sites deployment, never during API startup.

```sh
pnpm test
node tests/api-check.mjs http://localhost:8787
pnpm build
```

## API

All writes use JSON and same-origin requests. Session cookies are HttpOnly, SameSite=Strict and Secure over HTTPS. Use a cookie jar for command-line clients. API results are never cached. Session creation is limited to 20 per hour per source IP bucket. Each session expires after 24 hours and processes at most 20,000 flows. Expired data is purged on later session creation; expiration is not an independent scheduled deletion guarantee.

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health` | Check deployed model and database availability |
| GET | `/api/model` | Feature schema, model version, examples and configuration |
| POST | `/api/session` | Start isolated state; body `{"mode":"monitor_only"}` or `{"mode":"governed"}` |
| GET | `/api/session` | Current revision, counters and replay cursor |
| POST | `/api/infer` | Actual inference with `{"x":[12 numeric feature values]}`; no learning |
| POST | `/api/replay` | Process 1–256 held-out flows with `revision`, unique `request_id`, and `count` |
| POST | `/api/stream` | Process 1–256 custom rows with `revision`, `request_id`, and `rows:[{"x":[...],"y":0}]` |
| GET | `/api/audit` | Export actual session records and chain head |

`x` follows the exact order from `/api/model`. Values must be finite, non-negative and at most 1e15. The server transforms them with the trained preprocessing parameters. API request bodies are limited to 400 KB. Browser CSV files are limited to 2 MB and 256 rows.

Label `y`: 0 = benign, 1 = attack, null/omitted = unknown. Unknown labels never become pseudo-labels. A whole batch is predicted before any supplied labels influence an update. Visitor labels are explicitly marked as visitor assertions and only affect that visitor's model. They are not verified incidents.

`request_id` is 12–80 letters, numbers, underscores or hyphens. Retrying the most recent request with the same ID returns the saved result. Stale revisions return HTTP 409. Writes use a conditional revision update and atomic database batch, so concurrent requests cannot silently overwrite model state. Only the most recent operation is deduplicated; older retries are rejected by revision.

## Real measurements

The required fields are flow duration (seconds), forward/backward packet counts, packet rate (packets/s), down/up ratio, SYN/RST/ACK counts, payload mean/std (bytes), and forward/backward initial TCP window size (bytes). See the dataset's Zeek/Flowmeter feature definitions. Measurements must describe the same bidirectional flow and use compatible collector semantics.

The browser cannot capture arbitrary network traffic. Use an authorized collector to export compatible flow measurements and submit its CSV or call the API. Do not fabricate device posture, MFA, identity, or resource permissions from flow statistics. Identity provider, policy enforcement point, organizational authorization rules, trusted analyst feedback and production operational controls are not integrated here.

## Audit verification

```sh
node scripts/verify-audit.mjs downloaded-session-audit.json
```

The verifier recomputes canonical-JSON SHA-256 hashes and checks record links and the exported chain head. Keep the head separately if you need to detect later alteration. This is not immutable storage or externally notarized evidence. Records include exact training/anchor IDs and model fingerprints; benchmark source IDs can be resolved against the checksum-pinned CSV. Visitor source IDs are session-relative.

## Privacy and isolation

No sign-up is required. Session access is controlled by an unguessable cookie whose hash keys the database. Session models and AJRs persist server-side for the session lifetime. Learning buffers and the last response can contain submitted feature values; do not submit secrets or personal data. Raw IP addresses are not stored in session records; short-lived hashed IP buckets enforce session creation limits. The browser display history is temporary; audit records and model state are authoritative in D1.

## Limits

This is a working research deployment for network-risk inference and adaptation governance, not a validated autonomous enterprise access-control product. Scores are uncalibrated. A testbed benchmark does not establish operational security, legal compliance, or publication acceptance. Audit-only can accept harmful changes; gated mode can block useful learning. See `RESEARCH_REPORT.md` for measured tradeoffs.
