# Animated model mathematics — visitor and code guide

Added 10 September 2026. [Open the animated lab](https://the-sudipta.github.io/drifttrust_audit/lab.html#mathTheatre).

## A first visit

1. Choose **Gated** and press **Start / reset model session** above the dark animation panel. This creates actual, initially trained weights in this browser. Reset replaces the existing session, so export anything you need first.
2. Press **Animate selected flow**. The initial example is a held-out MQTT flow. Watch twelve measured inputs feed twenty-four hidden neurons, one attack output, and the trust equation. **Choose a flow below** goes to the input form; it does not submit it. Run actual inference there has the same computation as the animation button.
3. Automatic focus selects the neuron with the largest absolute activation × output-weight term. All 24 neurons still participate. Pause, select any input and hidden neuron, and expand its weighted sums exactly as before. Choosing a neuron switches to Manual inspection and keeps your choice across playback, new captures and model comparisons. A high score can still be wrong: an unedited labelled example shows whether it was correctly classified. Edited inputs have unknown correctness.
4. Open **Dataset replay**, then **Run remaining replay**. The engine predicts each batch before receiving its labels. Eligible drift evidence causes real candidate training. The animation captures the calculation, then slows it for inspection.
5. Choose **Candidate #7** in **Captured calculation** after the gated replay. Select **Learn a candidate**, **Compare models**, and **Policy decision**. Its new weights fail the anchor-loss check; the previous weights remain active. Export its numerical trace or inspect the corresponding AJR below.
6. To compare policies, create a fresh **Audit-only** session and replay again. This policy activates candidates even when checks flag them. The animation explicitly says **ACTIVATED WITH FLAGS** in those cases.

The default checkpoint and compact 1,280-flow replay produce 7 candidates / 4 activations / 3 discards in gated mode and 5 / 5 / 0 in audit-only mode. Candidate timing differs because each accepted model changes later predictions and drift signals. These counts describe proposed model versions, never visitors or network access requests.

## Every animation control and visual

| Item | Meaning and effect |
|---|---|
| Inside DriftTrust · 12 → 24 → 1 | Twelve measured features, twenty-four tanh hidden neurons, one sigmoid output; 337 trainable parameters including biases. This is an MLP, not a convolutional image network. |
| Animate selected flow ↗ | Validates and scores the current twelve input fields with the actual session model. Enables after a session starts. Does not learn, consume feedback, or create an AJR. |
| Choose a flow below ↓ | Navigates to the existing Single flow form. Held-out examples fill all twelve fields; editing them produces a user-supplied vector. |
| Captured calculation | Selects a prior inference, streamed probe, or candidate snapshot. Its title identifies the source or attempt. Selecting history never retrains. |
| Capture timestamp | Device-clock time of the recorded operation. Historical snapshots do not claim to be the current model. |
| Neuron focus: Automatic | Recomputes the largest absolute hidden activation × output weight for the selected flow and forward-pass model. This is a signed contribution to the pre-sigmoid total (logit), not a percentage or causal importance. Bias is excluded from neuron selection. Exact ties choose the lowest neuron number and are disclosed. |
| Neuron focus: Manual inspection | Keeps the selected neuron across playback, new runs, history selections, resets and model comparisons in this tab. Selecting any network neuron, contribution bar or Hidden neuron dropdown enters Manual mode. Switching back from Automatic restores your last manual choice. Reload starts in Automatic mode; no model state is affected. |
| Replay ↺ | Starts explanation playback from the beginning of the selected capture. This is separate from Dataset replay, which processes traffic. |
| Play / Pause | Starts or stops explanation stages. No weights, labels, session revision, or scientific counters change. Selecting a neuron, input, equation disclosure or model pauses playback for inspection. |
| ← / → | Moves one explanation stage backward/forward. Disabled at the corresponding end. |
| Speed | 0.5×, 1× or 2× explanation pace; does not change inference speed, learning rate, or SGD. |
| Reduced motion | Removes motion effects and prevents automatic playback of new captures. Follows the system setting initially. Explicit Play can still advance stages without animation effects. |
| Glowing network | Shows actual mathematical connectivity. Twelve input-to-hidden products feed each selected neuron; all twenty-four activations feed the output. Moving dashes indicate dependencies, not captured packets or measured wall-clock execution. |
| Teal / violet | Nodes encode the sign of transformed inputs/activations; incoming edges encode weight sign. Output edges and chart bars encode the sign of activation × output weight. Positive output terms push the attack score up, negative terms push it down. A negative activation multiplied by a negative weight makes a positive contribution. |
| All 24 output edges | All remain visible and animate together during the Attack score stage. Thickness represents absolute logit contribution; the inspection ring does not mark the only participating neuron. Node brightness still represents activation magnitude, which differs from output contribution. |
| Slanted translucent planes | Visual separation and depth for the layers. They do not add model layers or computations. |
| Input node / hidden node | Click or use keyboard Enter/Space to inspect its real values. The labelled dropdowns provide equivalent access. H1–H24 index hidden units; they have no assigned semantic classes. |
| Step buttons 01–07 | Jump to preprocessing, hidden calculation, attack score, trust score, learning, comparison, or governance. Inference-only captures have four stages because no training happened. |
| Calculation step slider | Scrubs the same discrete explanation stages. It is not a training-history time axis. |
| Input to inspect | Selects one measured feature and its weight into the selected hidden neuron. All twelve still participate in prediction. |
| Hidden neuron | Selects any of H1–H24 and enters Manual inspection. Its sum includes all twelve inputs, regardless of the highlighted input. The 24 neurons belong to one hidden layer; the diagram's two columns do not represent two layers. |
| Every contribution chart | Displays all 24 signed activation × output-weight terms in neuron order. All bars share a symmetric scale; each bar has a centre-zero marker and a signed numerical label. Click any bar or use Enter/Space to inspect that neuron. The selected outline follows Manual/Automatic focus; largest-magnitude terms receive an explicit badge. |
| Separate Bias row and total | Shows the output bias on the same scale, separately from the 24 neurons. Their sum plus bias equals the logit sent to sigmoid. Bias is not clickable because it is not a hidden neuron. Zero terms have zero-length bars; an all-zero chart uses a finite ±1 display scale. |
| Forward-pass model | Chooses original, candidate, or retained weights for the same probe flow. Candidate/retained options require a candidate capture. These rescored values are diagnostic comparisons, not replacements for the observed pre-feedback prediction. |
| Number boxes | Label above, real numerical endpoint below. Display rounds to six decimal places or scientific notation; hover shows full values where provided, and export retains full precision. A reveal/colour flash marks the result or updated parameter; intermediate invented weights are never displayed. |
| Expand all 12 input products | Lists each transformed input, selected neuron's weight, and their product. Sum all twelve and add the hidden bias. |
| Expand all 24 output terms | Lists each hidden activation, output weight, and product. Sum all twenty-four and add output bias. |
| Captured training step | First actual training row in each of three SGD passes. These are three samples, not consecutive updates and not the entire optimization trajectory. The displayed row ID and training size identify the training context. |
| Parameter | Selects input→hidden weight, hidden bias, hidden→output weight, or output bias. Weight selectors follow the chosen feature and neuron. |
| Actual change | Exact new-minus-old parameter value for that captured SGD step, with the gradient formula explained below. |
| Gradient disclosure | Shows training prediction, supplied label, output error, hidden activation/gradient, input, learning rate and L2 term. The training row differs from the held-out probe used in the forward comparison. |
| Before / Trained candidate / Retained model cards | Scores and weight fingerprints for identical input under three snapshots. Clicking changes the equations above. A rejected candidate has retained weights identical to the before snapshot. |
| Checkmark / cross and policy verdict | Candidate activated, activated with flags, or discarded. The four checks explain their actual numbers and thresholds; colour supplements explicit text. |
| Export this numerical trace | Downloads the selected capture as JSON, including raw measurements and weight snapshots. Local download only; separate from Export AJRs. |
| Animate this model decision | Button inside an AJR opens its corresponding retained candidate capture. If an older trace is unavailable, the lab says so instead of fabricating an animation. |
| Ready / disabled controls | No real capture exists yet, or that action is unavailable for the selected capture. No placeholder computation is presented as an observation. |

On a phone, controls and equations stack and the network has a labelled horizontal scroll region. Use the dropdowns to inspect every neuron without scrolling the diagram. Keyboard focus survives diagram updates; open equation tables remain open when values change.

The original H1 selection was only an inspector default. For the initial checkpoint, Slowloris row 20635 now automatically focuses H16 (logit term approximately −1.36109), while SSH brute-force row 115485 focuses H10 (approximately +1.80987). These choices can change when model weights or inputs change. Automatic focus is based on the currently selected forward-pass snapshot, not on the gradient of the separate sampled SGD training row.

## The exact equations

For measured feature r[j], using the checkpoint's training mean μ[j] and standard deviation σ[j]:

```text
x[j] = clip((log(1 + r[j]) − μ[j]) / σ[j], −8, 8)
z[k] = b1[k] + Σ(j=1..12) x[j] × w1[j,k]
h[k] = tanh(z[k])
a    = b2 + Σ(k=1..24) h[k] × w2[k]
p    = sigmoid(a) = 1 / (1 + exp(−a))
trust = 100 × (1 − p)
```

The engine uses a numerically stable sigmoid. The output is an uncalibrated attack score; p ≥ 0.5 flags network risk. Trust ≤ 50 is the same boundary. The input normalization parameters remain fixed during online learning. All twelve input fields and units are explained in the form and existing fieldbook.

For one labelled training row, y = 0 means benign and y = 1 means attack:

```text
error = p − y
dh[k] = error × old_w2[k] × (1 − h[k]²)
w1[j,k] ← old_w1[j,k] − 0.003 × (dh[k] × x[j] + 0.0001 × old_w1[j,k])
b1[k]   ← old_b1[k]   − 0.003 × dh[k]
w2[k]   ← old_w2[k]   − 0.003 × (error × h[k] + 0.0001 × old_w2[k])
b2      ← old_b2      − 0.003 × error
```

Biases receive no L2 penalty. Hidden gradients use the old output weights. A candidate trains over the recent labelled window mixed with older replay records, in three passes; final candidate snapshots include every update, even though the animation samples only three training steps.

## When does a candidate exist, and what does the gate decide?

Error drift is recent labelled error (last 64) greater than the preceding reference error plus 0.08, after 256 labelled errors exist. Attribution drift is maximum absolute change in normalized feature importance greater than 0.15. Either signal can trigger eligibility. The engine also requires at least 64 recent labelled entries, a current batch with feedback, and 128 flows since the previous attempt. Merely pressing a button does not force learning.

| Candidate check | Passing rule |
|---|---|
| Explanation consistency | ECI ≥ 0.5 on the fixed anchors. ECI measures feature-ranking agreement, not explanation truth. |
| Anchor loss | Candidate cross-entropy ≤ previous loss + 0.05 on the same 96 anchors. |
| Anchor attack misses | Candidate miss rate ≤ previous rate + 0.05 on anchor attacks. |
| Minimum gap | At least 128 observed flows since the previous attempt. |

Gated mode requires all four. Audit-only mode records failures but activates the candidate. For compact gated candidate 7 at flow 1280, ECI ≈ 0.94697 passes, while anchor loss rises from ≈ 0.11328 to ≈ 0.19226: an increase of ≈ 0.07899 exceeds 0.05. The gate discards its weights. Rejection does not roll back already observed flows, delete the AJR, or prevent the engine from evaluating later evidence.

## Code and data flow

```text
lab.html + math-theatre.css
  → lab.mjs handles a real inference / replay / CSV operation
  → runtime/browser-client.mjs posts an operation to the Web Worker
  → runtime/browser-worker.mjs validates inputs and reads session state
  → runtime/engine.mjs predicts before feedback, detects, trains and gates
       optional trace captures before/after of first SGD step in each pass
  → runtime/math-trace.mjs expands exact forward arithmetic from snapshots
  → IndexedDB revision transaction commits stream state and retained traces
  → worker sends numerical captures and ordinary results to lab.mjs
  → math-theatre.mjs renders SVG, boxed equations and policy evidence
       Play / inspect / export only read these captures
```

`/api/visuals` is a local worker message name; it is not an HTTP request. Inference-only snapshots return without a learning-state write. The existing request serialization, revision checking, idempotent retry, AJR schema and hash chain remain in place. No new external service, framework, database account or animation dependency is required. Pages publishes the modules through the existing GitHub Actions workflow.

## Persistence, sampling, and evidence scope

The UI retains up to 18 recent captures in memory. IndexedDB retains up to eight recent candidate traces plus the last streamed probe; the most recent response is also cached for operation retry. Single-flow captures are not persisted. Reload restores available stream/candidate captures without autoplay. Session reset clears history only after the reset succeeds. A saved old session may have AJRs but no animation traces.

Each stream probe is the final row of a processed batch, predicted under that batch's original weights. The stream chart still records all processed predictions; the animation does not claim to record every forward pass or every SGD step. Its pace is pedagogical playback of a completed operation. Runtime work stays in the worker so the interface remains responsive.

`drifttrust-math-trace-v1` exports have a `capture` containing forward intermediates, complete model snapshots, raw inputs, and, for candidates, three training-step samples, configuration and the AJR. Candidate fingerprints can be checked against `model_before_sha256`, `candidate_sha256` and `active_model_sha256`. This is a local numerical witness, not independent attestation: a browser owner can rewrite local evidence. Share raw visitor measurements only intentionally.

The original paper experiment and its execution manifest remain historical artifacts. Optional tracing preserves the predictions, candidate weights and policy outcomes under numerical tests, but changes source bytes and adds capture overhead. Current animation timings must not be quoted as the archived experiment's latency; timestamps, elapsed times and resulting AJR record hashes can differ between runs.

## Reproduce the checks

```sh
node --test tests/*.test.mjs
node scripts/build-pages.mjs
node scripts/serve-pages.mjs
# In another terminal, with Playwright and a compatible browser installed:
node tests/browser-math.cjs http://localhost:8788/drifttrust_audit/
node tests/browser-pages.cjs http://localhost:8788/drifttrust_audit/
```

`PLAYWRIGHT_MODULE` can point to an installed Playwright package; `BROWSER_EXECUTABLE` can point to Edge/Chromium. Unit tests compare traced and untraced full replays and independently reconstruct all 337 parameters in every captured step. Browser checks exercise real controls, exports, policy outcomes, persistence, motion preferences and responsive layouts. Published verification identifies its tested source commit separately from later report-only commits.

The visual treatment takes inspiration from the supplied boxed linear-equation sketches and [the supplied neural-network video](https://www.youtube.com/shorts/vfVgD0EZOTI). The network, SVG and interface are original implementation of this project's actual MLP; the reference video's CNN is not substituted for the research model.
