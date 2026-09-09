# Methodology

DriftTrust-Audit evaluates an adaptive trust model under simulated concept
drift and then records each model adaptation as auditable evidence.

## Step 1: Simulated Enterprise Telemetry

The simulator generates session-level behavioral features such as authentication
frequency, geographic displacement, device posture, concurrent sessions,
resource sensitivity, and packet retransmission rate.

Labels use:

- `1`: legitimate access,
- `0`: attack or suspicious access.

The simulator injects:

- gradual drift,
- abrupt drift,
- recurring drift.

## Step 2: Temporal Feature Windows

Session records are converted into sliding temporal windows. Each window is used
to predict the trust state of the most recent session.

## Step 3: Trust Scoring

The current verified implementation uses a temporal MLP over flattened windows.
The intended paper-grade extension is a PyTorch LSTM/GRU model.

The trust score is interpreted as:

```text
P(legitimate access)
```

## Step 4: Drift Detection

Two signals are used:

- prediction-error shift,
- attribution-distribution shift.

The verified implementation uses a windowed error detector and perturbation
attribution. The paper-grade extension should use River ADWIN and SHAP.

## Step 5: Incremental Adaptation

When drift is detected, the model is incrementally updated using recent stream
windows mixed with replay-buffer examples. Replay reduces catastrophic
forgetting risk.

## Step 6: Adaptation Governance

Each adaptation generates an AJR containing:

- drift trigger,
- drifted feature,
- attribution shift,
- trust score before and after adaptation,
- top explanatory features,
- adaptation losses,
- ECI,
- ISO/IEC 27001 policy checks.

## Step 7: Evaluation

The implementation reports:

- ROC-AUC,
- F1,
- precision,
- recall,
- Matthews correlation coefficient,
- balanced accuracy,
- mean time to detect,
- AJR completeness,
- policy conformance,
- ECI distribution.
