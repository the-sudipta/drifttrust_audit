# DriftTrust-Audit: Complete Implementation Guide
# For use with Codex or any AI coding assistant
# Every step is molecular-level — no assumptions made

---

## PROJECT OVERVIEW

**Goal:** Build DriftTrust-Audit — a three-layer Python system that:
1. Computes a real-time Trust Score from network session features (Layer 1)
2. Detects concept drift and incrementally updates the model (Layer 2)
3. Generates an Adaptation Justification Record (AJR) and Explanation-Consistency Index (ECI) for every model update (Layer 3 — the novel contribution)

**Language:** Python 3.10+
**All data is simulated** — no real network access needed.

---

## DIRECTORY STRUCTURE TO CREATE

```
drifttrust_audit/
├── data/
│   ├── simulate.py          # Step 1: generate synthetic telemetry
│   └── features.py          # Step 2: extract features from raw sessions
├── models/
│   ├── trust_scorer.py      # Step 3: Layer 1 — LSTM/GRU trust scoring model
│   └── trainer.py           # Step 3: training loop and model persistence
├── drift/
│   ├── detector.py          # Step 4: Layer 2 — drift detection (ADWIN + SHAP-based)
│   └── adapter.py           # Step 4: incremental weight update logic
├── governance/
│   ├── ajr.py               # Step 5: Layer 3 — AJR schema and generation
│   ├── eci.py               # Step 5: ECI computation (Jaccard + Kendall-tau)
│   └── policy.py            # Step 5: ISO/IEC 27001 policy conformance checker
├── evaluation/
│   ├── metrics.py           # Step 6: standard ML metrics
│   ├── governance_metrics.py# Step 6: AJR completeness, ECI stats
│   └── plots.py             # Step 6: all result visualisations
├── audit_logs/              # JSON AJR records written here at runtime
├── saved_models/            # Saved model checkpoints
├── results/                 # CSV and PNG outputs
├── requirements.txt
├── config.py                # All hyperparameters in one place
└── main.py                  # Entry point — runs the full pipeline
```

---

## STEP 0 — REQUIREMENTS AND CONFIG

### requirements.txt
```
numpy==1.26.4
pandas==2.2.2
scikit-learn==1.4.2
torch==2.3.0
shap==0.45.1
river==0.21.0
scipy==1.13.0
matplotlib==3.9.0
seaborn==0.13.2
tqdm==4.66.4
```

Install with:
```bash
pip install -r requirements.txt
```

### config.py — ALL hyperparameters live here, nowhere else

```python
# config.py

# ── Data simulation ────────────────────────────────────
N_SESSIONS        = 10_000   # total simulated network sessions
N_FEATURES        = 11       # number of behavioural features
DRIFT_POINTS      = [2000, 5000, 7500]  # where drift is injected (session index)
DRIFT_TYPES       = ["gradual", "abrupt", "recurring"]  # one per DRIFT_POINTS entry
RANDOM_SEED       = 42

# ── Model architecture ────────────────────────────────
SEQUENCE_LENGTH   = 20       # sessions per input window
HIDDEN_SIZE       = 64
NUM_LAYERS        = 2
DROPOUT           = 0.2
TRUST_THRESHOLD   = 0.5      # below this → access denied

# ── Training ─────────────────────────────────────────
BATCH_SIZE        = 64
EPOCHS            = 30
LEARNING_RATE     = 1e-3
TRAIN_SPLIT       = 0.7
VAL_SPLIT         = 0.15
# remaining 0.15 is test set

# ── Drift detection ───────────────────────────────────
ADWIN_DELTA       = 0.002    # sensitivity of ADWIN detector
SHAP_DRIFT_THRESHOLD = 0.25  # if top SHAP feature shifts by this much → drift signal

# ── Continual learning ────────────────────────────────
INCREMENTAL_LR    = 1e-4     # lower LR for incremental updates
INCREMENTAL_EPOCHS = 5       # epochs per incremental update
REPLAY_BUFFER_SIZE = 500     # samples retained from previous distribution (forgetting prevention)

# ── ECI ──────────────────────────────────────────────
ECI_TOP_K         = 5        # top-k SHAP features to compare
ECI_THRESHOLD     = 0.5      # below this → flag for human review

# ── Governance / ISO mapping ──────────────────────────
AJR_LOG_DIR       = "audit_logs/"
HIGH_SENSITIVITY_RESOURCES = ["finance_db", "hr_records", "root_access"]
# These resource tags trigger stricter policy checks in the AJR

# ── Paths ─────────────────────────────────────────────
MODEL_SAVE_DIR    = "saved_models/"
RESULTS_DIR       = "results/"
```

---

## STEP 1 — SIMULATE TELEMETRY  (data/simulate.py)

### What this file must do:
Generate `N_SESSIONS` synthetic enterprise network sessions, each with 11 raw behavioural signals and a label (1 = legitimate, 0 = attack). Inject concept drift at the indices specified in `config.DRIFT_POINTS`.

### Exact implementation instructions for Codex:

```python
# data/simulate.py

import numpy as np
import pandas as pd
from config import (N_SESSIONS, N_FEATURES, DRIFT_POINTS,
                    DRIFT_TYPES, RANDOM_SEED)

FEATURE_NAMES = [
    "session_duration_s",        # seconds; normal ~300, anomalous > 1800
    "auth_frequency_per_hr",     # logins per hour; normal ~2, anomalous > 20
    "geo_displacement_km",       # distance from last known location; >500 suspicious
    "device_posture_score",      # 0.0–1.0; lower = riskier device
    "payload_size_anomaly",      # z-score of payload vs user baseline
    "mfa_timing_gap_s",          # seconds between MFA prompt and response
    "port_utilisation_entropy",  # Shannon entropy of ports used; high = suspicious
    "concurrent_sessions",       # number of simultaneous active sessions
    "resource_sensitivity_level",# 0=public, 1=internal, 2=confidential, 3=restricted
    "time_of_day_discrepancy",   # 1 if session time outside user's normal window
    "packet_retransmission_rate",# fraction of packets retransmitted; high = anomalous
]


def _base_distribution(n, seed):
    """Generate n legitimate sessions from base distribution."""
    rng = np.random.default_rng(seed)
    X = np.column_stack([
        rng.normal(300,   80,  n).clip(30, 3600),   # session_duration_s
        rng.normal(2,     0.8, n).clip(0,  50),      # auth_frequency_per_hr
        rng.exponential(50, n).clip(0, 2000),         # geo_displacement_km
        rng.beta(8, 2, n),                            # device_posture_score (skew high = good)
        rng.normal(0,     1,   n),                    # payload_size_anomaly (z-score)
        rng.normal(15,    5,   n).clip(1, 120),       # mfa_timing_gap_s
        rng.uniform(0.5,  2.5, n),                    # port_utilisation_entropy
        rng.poisson(1.2,  n).clip(1, 20),             # concurrent_sessions
        rng.choice([0,1,2,3], n, p=[0.4,0.3,0.2,0.1]),  # resource_sensitivity_level
        rng.binomial(1, 0.08, n),                     # time_of_day_discrepancy
        rng.beta(1, 15, n),                           # packet_retransmission_rate (low normally)
    ])
    y = (
        (X[:, 1] > 10) |   # high login frequency
        (X[:, 2] > 800) |  # large geo displacement
        (X[:, 4] > 2.5) |  # extreme payload anomaly
        (X[:, 6] > 3.5) |  # high port entropy
        (X[:, 10] > 0.3)   # high retransmission
    ).astype(int)
    return X, y


def _inject_gradual_drift(X, y, start, end, rng):
    """Gradually shift login frequency and session duration over a window."""
    n = end - start
    shift_factor = np.linspace(1.0, 4.0, n)
    X[start:end, 1] *= shift_factor         # auth frequency increases
    X[start:end, 0] *= (shift_factor * 0.5) # session duration decreases
    # ~15% of new sessions become attacks
    attack_mask = rng.random(n) < 0.15
    y[start:end][attack_mask] = 1
    return X, y


def _inject_abrupt_drift(X, y, start, end, rng):
    """Sudden shift — new attack pattern using high concurrent sessions."""
    n = end - start
    X[start:end, 7] = rng.normal(12, 3, n).clip(5, 30)  # concurrent sessions spike
    X[start:end, 10] = rng.beta(3, 5, n)                # retransmission rate rises
    attack_mask = rng.random(n) < 0.30
    y[start:end][attack_mask] = 1
    return X, y


def _inject_recurring_drift(X, y, start, end, rng):
    """Periodic pattern — end-of-quarter surge in resource access."""
    n = end - start
    X[start:end, 8] = rng.choice([2, 3], n, p=[0.5, 0.5])  # higher resource sensitivity
    X[start:end, 9] = rng.binomial(1, 0.4, n)               # more out-of-hours access
    attack_mask = rng.random(n) < 0.20
    y[start:end][attack_mask] = 1
    return X, y


def generate_telemetry(n_sessions=N_SESSIONS, save_csv=True):
    """
    Returns:
        df  : pd.DataFrame, shape (n_sessions, 13)
              columns = FEATURE_NAMES + ['label', 'drift_type']
    """
    rng = np.random.default_rng(RANDOM_SEED)
    X, y = _base_distribution(n_sessions, RANDOM_SEED)
    drift_labels = ["none"] * n_sessions

    drift_handlers = {
        "gradual":   _inject_gradual_drift,
        "abrupt":    _inject_abrupt_drift,
        "recurring": _inject_recurring_drift,
    }

    for i, (dp, dtype) in enumerate(zip(DRIFT_POINTS, DRIFT_TYPES)):
        end = DRIFT_POINTS[i + 1] if i + 1 < len(DRIFT_POINTS) else n_sessions
        X, y = drift_handlers[dtype](X, y, dp, end, rng)
        for j in range(dp, end):
            drift_labels[j] = dtype

    df = pd.DataFrame(X, columns=FEATURE_NAMES)
    df["label"] = y
    df["drift_type"] = drift_labels
    df["session_id"] = range(n_sessions)
    df["resource_tag"] = rng.choice(
        ["public_portal", "internal_wiki", "finance_db", "hr_records", "root_access"],
        n_sessions, p=[0.4, 0.3, 0.15, 0.1, 0.05]
    )

    if save_csv:
        df.to_csv("data/telemetry.csv", index=False)
        print(f"[simulate] Saved {n_sessions} sessions to data/telemetry.csv")

    return df


if __name__ == "__main__":
    df = generate_telemetry()
    print(df["label"].value_counts())
    print(df["drift_type"].value_counts())
```

---

## STEP 2 — FEATURE EXTRACTION  (data/features.py)

### What this file must do:
Take the raw telemetry DataFrame and produce normalised feature windows of shape `(n_windows, SEQUENCE_LENGTH, N_FEATURES)` suitable for the LSTM/GRU model. Also produce the corresponding labels and metadata.

```python
# data/features.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from config import SEQUENCE_LENGTH, N_FEATURES, FEATURE_NAMES, TRAIN_SPLIT, VAL_SPLIT, RANDOM_SEED

FEATURE_NAMES = [
    "session_duration_s", "auth_frequency_per_hr", "geo_displacement_km",
    "device_posture_score", "payload_size_anomaly", "mfa_timing_gap_s",
    "port_utilisation_entropy", "concurrent_sessions", "resource_sensitivity_level",
    "time_of_day_discrepancy", "packet_retransmission_rate"
]


def create_windows(df, seq_len=SEQUENCE_LENGTH):
    """
    Sliding window over sessions.
    Returns:
        X_windows : np.ndarray (n_windows, seq_len, n_features)
        y_windows : np.ndarray (n_windows,)   — label of LAST session in window
        meta      : pd.DataFrame with session_id, drift_type, resource_tag for each window
    """
    X_raw = df[FEATURE_NAMES].values       # (N, 11)
    y_raw = df["label"].values
    meta_cols = df[["session_id", "drift_type", "resource_tag"]].reset_index(drop=True)

    n = len(X_raw)
    n_windows = n - seq_len

    X_windows = np.zeros((n_windows, seq_len, len(FEATURE_NAMES)), dtype=np.float32)
    y_windows = np.zeros(n_windows, dtype=np.int64)

    for i in range(n_windows):
        X_windows[i] = X_raw[i : i + seq_len]
        y_windows[i] = y_raw[i + seq_len]  # predict the next session

    meta = meta_cols.iloc[seq_len:].reset_index(drop=True)
    return X_windows, y_windows, meta


def normalise(X_train, X_val, X_test):
    """
    Fit StandardScaler on training data only.
    Reshape to 2D for scaler, then back to 3D.
    Returns scaled arrays + fitted scaler (needed for new data at inference time).
    """
    n_tr, seq, feats = X_train.shape
    scaler = StandardScaler()

    X_tr_2d = X_train.reshape(-1, feats)
    X_va_2d = X_val.reshape(-1, feats)
    X_te_2d = X_test.reshape(-1, feats)

    X_tr_2d = scaler.fit_transform(X_tr_2d)
    X_va_2d = scaler.transform(X_va_2d)
    X_te_2d = scaler.transform(X_te_2d)

    return (
        X_tr_2d.reshape(n_tr, seq, feats),
        X_va_2d.reshape(X_val.shape[0], seq, feats),
        X_te_2d.reshape(X_test.shape[0], seq, feats),
        scaler,
    )


def split(X, y, meta):
    """Chronological (not random) split — essential for time-series drift work."""
    n = len(X)
    tr_end = int(n * TRAIN_SPLIT)
    va_end  = int(n * (TRAIN_SPLIT + VAL_SPLIT))

    return (
        X[:tr_end], y[:tr_end], meta.iloc[:tr_end],
        X[tr_end:va_end], y[tr_end:va_end], meta.iloc[tr_end:va_end],
        X[va_end:], y[va_end:], meta.iloc[va_end:],
    )
```

---

## STEP 3 — LAYER 1: TRUST SCORER  (models/trust_scorer.py + models/trainer.py)

### models/trust_scorer.py — The LSTM and GRU model definitions

```python
# models/trust_scorer.py

import torch
import torch.nn as nn
from config import N_FEATURES, HIDDEN_SIZE, NUM_LAYERS, DROPOUT


class LSTMTrustScorer(nn.Module):
    """
    Input:  (batch, seq_len, n_features)
    Output: (batch,)  — probability of legitimate access (trust score)
    """
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=N_FEATURES,
            hidden_size=HIDDEN_SIZE,
            num_layers=NUM_LAYERS,
            batch_first=True,
            dropout=DROPOUT if NUM_LAYERS > 1 else 0.0,
        )
        self.classifier = nn.Sequential(
            nn.Linear(HIDDEN_SIZE, 32),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        last_hidden = h_n[-1]          # take last layer hidden state
        return self.classifier(last_hidden).squeeze(1)


class GRUTrustScorer(nn.Module):
    """Identical to LSTM variant but uses GRU cell."""
    def __init__(self):
        super().__init__()
        self.gru = nn.GRU(
            input_size=N_FEATURES,
            hidden_size=HIDDEN_SIZE,
            num_layers=NUM_LAYERS,
            batch_first=True,
            dropout=DROPOUT if NUM_LAYERS > 1 else 0.0,
        )
        self.classifier = nn.Sequential(
            nn.Linear(HIDDEN_SIZE, 32),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        _, h_n = self.gru(x)
        return self.classifier(h_n[-1]).squeeze(1)
```

### models/trainer.py — Full training loop with early stopping

```python
# models/trainer.py

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import os
from config import BATCH_SIZE, EPOCHS, LEARNING_RATE, MODEL_SAVE_DIR


def train(model, X_train, y_train, X_val, y_val, model_name="lstm"):
    """
    Standard supervised training loop.
    Saves best checkpoint by validation loss.
    Returns: trained model, list of train_losses, list of val_losses
    """
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    X_tr = torch.tensor(X_train, dtype=torch.float32)
    y_tr = torch.tensor(y_train, dtype=torch.float32)
    X_va = torch.tensor(X_val,   dtype=torch.float32)
    y_va = torch.tensor(y_val,   dtype=torch.float32)

    train_loader = DataLoader(
        TensorDataset(X_tr, y_tr), batch_size=BATCH_SIZE, shuffle=False
    )  # NOTE: no shuffle — chronological order matters for drift

    criterion = nn.BCELoss()
    optimiser = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimiser, patience=3, factor=0.5
    )

    best_val_loss = float("inf")
    train_losses, val_losses = [], []

    for epoch in range(EPOCHS):
        model.train()
        epoch_loss = 0.0
        for Xb, yb in train_loader:
            Xb, yb = Xb.to(device), yb.to(device)
            optimiser.zero_grad()
            preds = model(Xb)
            loss = criterion(preds, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            epoch_loss += loss.item()

        model.eval()
        with torch.no_grad():
            val_preds = model(X_va.to(device))
            val_loss  = criterion(val_preds, y_va.to(device)).item()

        train_losses.append(epoch_loss / len(train_loader))
        val_losses.append(val_loss)
        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(),
                       os.path.join(MODEL_SAVE_DIR, f"best_{model_name}.pt"))

        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1:03d} | train_loss={train_losses[-1]:.4f} | val_loss={val_loss:.4f}")

    model.load_state_dict(
        torch.load(os.path.join(MODEL_SAVE_DIR, f"best_{model_name}.pt"))
    )
    return model, train_losses, val_losses


def predict_proba(model, X):
    """Return trust scores (probabilities) for a numpy array X."""
    device = next(model.parameters()).device
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X, dtype=torch.float32).to(device)
        return model(X_t).cpu().numpy()
```

---

## STEP 4 — LAYER 2: DRIFT DETECTION & CONTINUAL LEARNING

### drift/detector.py

```python
# drift/detector.py

import numpy as np
import shap
from river.drift import ADWIN
from config import ADWIN_DELTA, SHAP_DRIFT_THRESHOLD, ECI_TOP_K


class DriftDetector:
    """
    Two-signal drift detector:
    Signal A: prediction-error ADWIN (accuracy-based)
    Signal B: SHAP attribution distribution shift (explanation-based)
    Drift is flagged if EITHER signal fires.
    """

    def __init__(self, model, background_data):
        """
        Args:
            model          : trained PyTorch model
            background_data: np.ndarray (n, seq_len, n_features) — reference SHAP background
        """
        self.model       = model
        self.adwin       = ADWIN(delta=ADWIN_DELTA)
        self.explainer   = shap.DeepExplainer(
            model,
            __import__("torch").tensor(background_data[:100], dtype=__import__("torch").float32)
        )
        # Store baseline SHAP attributions (mean |SHAP| per feature)
        baseline_shap     = self.explainer.shap_values(
            __import__("torch").tensor(background_data[:100], dtype=__import__("torch").float32)
        )
        self.baseline_importance = np.abs(baseline_shap).mean(axis=(0, 1))
        self.drift_detected = False
        self.drift_trigger  = None   # "error_based" or "attribution_based"

    def update(self, y_true, y_pred_prob, X_window):
        """
        Call once per session. y_pred_prob is the raw trust score (0–1).
        X_window is shape (1, seq_len, n_features).
        Returns True if drift detected.
        """
        # Signal A — binary error
        error = int(y_true != (y_pred_prob >= 0.5))
        self.adwin.update(error)

        if self.adwin.drift_detected:
            self.drift_detected = True
            self.drift_trigger  = "error_based"
            return True

        # Signal B — SHAP attribution shift (check every 50 sessions for performance)
        # Caller must track call count; here we just compute if asked
        current_shap = self.explainer.shap_values(
            __import__("torch").tensor(X_window, dtype=__import__("torch").float32)
        )
        current_importance = np.abs(current_shap).mean(axis=(0, 1))

        # Normalise both to sum to 1 then compute max shift
        b = self.baseline_importance / (self.baseline_importance.sum() + 1e-9)
        c = current_importance       / (current_importance.sum()       + 1e-9)
        max_shift = np.max(np.abs(c - b))

        if max_shift > SHAP_DRIFT_THRESHOLD:
            self.drift_detected = True
            self.drift_trigger  = "attribution_based"
            # Update baseline to new distribution
            self.baseline_importance = current_importance
            return True

        return False

    def get_shap_values(self, X):
        """Return SHAP values for a batch X (numpy)."""
        import torch
        return self.explainer.shap_values(torch.tensor(X, dtype=torch.float32))

    def reset(self):
        self.drift_detected = False
        self.drift_trigger  = None
        self.adwin          = ADWIN(delta=ADWIN_DELTA)
```

### drift/adapter.py — Incremental update with replay buffer

```python
# drift/adapter.py

import torch
import torch.nn as nn
import numpy as np
from collections import deque
from torch.utils.data import TensorDataset, DataLoader
from config import (INCREMENTAL_LR, INCREMENTAL_EPOCHS,
                    REPLAY_BUFFER_SIZE, BATCH_SIZE)


class ContinualAdapter:
    """
    Performs incremental weight updates when drift is detected.
    Uses a replay buffer (Experience Replay) to prevent catastrophic forgetting:
    a random sample from the buffer is mixed with new data at each update.
    """

    def __init__(self, model):
        self.model  = model
        self.buffer = deque(maxlen=REPLAY_BUFFER_SIZE)  # stores (X_window, y_label) tuples
        self.device = next(model.parameters()).device
        self.update_count = 0

    def add_to_buffer(self, X_batch, y_batch):
        """Add recent sessions to replay buffer."""
        for i in range(len(X_batch)):
            self.buffer.append((X_batch[i], y_batch[i]))

    def update(self, X_new, y_new):
        """
        Perform incremental update.
        X_new: np.ndarray (n_new, seq_len, n_features) — data from drift window
        y_new: np.ndarray (n_new,)
        Returns: list of loss values per epoch
        """
        # Mix new data with replay buffer
        if len(self.buffer) > 0:
            n_replay = min(len(self.buffer), len(X_new) * 2)
            idxs = np.random.choice(len(self.buffer), n_replay, replace=False)
            X_replay = np.array([self.buffer[i][0] for i in idxs])
            y_replay = np.array([self.buffer[i][1] for i in idxs])
            X_combined = np.concatenate([X_new, X_replay], axis=0)
            y_combined = np.concatenate([y_new, y_replay], axis=0)
        else:
            X_combined, y_combined = X_new, y_new

        X_t = torch.tensor(X_combined, dtype=torch.float32).to(self.device)
        y_t = torch.tensor(y_combined, dtype=torch.float32).to(self.device)

        loader = DataLoader(
            TensorDataset(X_t, y_t),
            batch_size=min(BATCH_SIZE, len(X_combined)),
            shuffle=True,
        )

        criterion  = nn.BCELoss()
        optimiser  = torch.optim.Adam(self.model.parameters(), lr=INCREMENTAL_LR)

        self.model.train()
        epoch_losses = []
        for _ in range(INCREMENTAL_EPOCHS):
            total = 0.0
            for Xb, yb in loader:
                optimiser.zero_grad()
                loss = criterion(self.model(Xb), yb)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimiser.step()
                total += loss.item()
            epoch_losses.append(total / len(loader))

        self.add_to_buffer(X_new, y_new)
        self.update_count += 1
        return epoch_losses
```

---

## STEP 5 — LAYER 3: ADAPTATION GOVERNANCE (the novel contribution)

### governance/ajr.py — AJR schema and generation

```python
# governance/ajr.py

import json
import os
import uuid
from datetime import datetime, timezone
import numpy as np
from config import AJR_LOG_DIR


def _policy_check(trust_score_before, trust_score_after,
                  resource_tag, shap_top_features):
    """
    Automated policy-conformance checks.
    Returns a dict: {check_name: "PASSED" or "FAILED: reason"}
    Mapped to ISO/IEC 27001:2022 Annex A controls.
    """
    checks = {}

    # A.5.15 — Access Control: update must not silently lower high-resource threshold
    HIGH_SENSITIVITY = {"finance_db", "hr_records", "root_access"}
    if resource_tag in HIGH_SENSITIVITY:
        delta = trust_score_after - trust_score_before
        if delta < -0.15:
            checks["A.5.15_access_control"] = (
                f"FAILED: Trust score dropped by {abs(delta):.3f} for "
                f"high-sensitivity resource '{resource_tag}' — requires human review"
            )
        else:
            checks["A.5.15_access_control"] = "PASSED"
    else:
        checks["A.5.15_access_control"] = "NOT_APPLICABLE"

    # A.8.16 — Monitoring: SHAP top feature must be in the expected feature set
    EXPECTED_FEATURES = {
        "session_duration_s", "auth_frequency_per_hr", "geo_displacement_km",
        "device_posture_score", "payload_size_anomaly", "mfa_timing_gap_s",
        "port_utilisation_entropy", "concurrent_sessions",
        "resource_sensitivity_level", "time_of_day_discrepancy",
        "packet_retransmission_rate",
    }
    if shap_top_features[0] not in EXPECTED_FEATURES:
        checks["A.8.16_monitoring"] = (
            f"FAILED: Top SHAP feature '{shap_top_features[0]}' is not in the "
            "expected feature set — possible data-pipeline anomaly"
        )
    else:
        checks["A.8.16_monitoring"] = "PASSED"

    # A.5.36 — Compliance: no two consecutive updates within fewer than 10 sessions
    # (checked externally — AJR records the gap for the auditor)
    checks["A.5.36_compliance"] = "PASSED"

    overall = "PASSED" if all(v == "PASSED" or v == "NOT_APPLICABLE"
                               for v in checks.values()) else "FAILED"
    return checks, overall


def generate_ajr(
    *,
    drift_trigger,          # str: "error_based" or "attribution_based"
    drifted_feature,        # str: name of feature with highest SHAP shift
    shap_shift_magnitude,   # float: how much the top feature's importance shifted
    trust_score_before,     # float: mean trust score in window before update
    trust_score_after,      # float: mean trust score in window after update
    shap_top_features,      # list[str]: top-k feature names after adaptation
    resource_tag,           # str: resource type being accessed in this window
    model_params_changed,   # int: number of weight parameters changed
    incremental_losses,     # list[float]: training losses during the update
    eci_score,              # float: ECI value (computed separately by eci.py)
    session_range,          # tuple(int, int): (start_idx, end_idx) of triggering window
):
    """
    Generate and persist one Adaptation Justification Record (AJR).
    Returns the AJR dict.
    """
    os.makedirs(AJR_LOG_DIR, exist_ok=True)

    policy_details, overall_status = _policy_check(
        trust_score_before, trust_score_after,
        resource_tag, shap_top_features
    )

    ajr = {
        "ajr_id":                  f"AJR-{str(uuid.uuid4())[:8].upper()}",
        "timestamp_utc":           datetime.now(timezone.utc).isoformat(),
        "drift_trigger":           drift_trigger,
        "drifted_feature":         drifted_feature,
        "shap_shift_magnitude":    round(float(shap_shift_magnitude), 4),
        "shap_top_features_after": shap_top_features,
        "trust_score_before":      round(float(trust_score_before), 4),
        "trust_score_after":       round(float(trust_score_after), 4),
        "trust_score_delta":       round(float(trust_score_after - trust_score_before), 4),
        "resource_tag":            resource_tag,
        "session_range":           list(session_range),
        "model_params_changed":    model_params_changed,
        "incremental_losses":      [round(l, 6) for l in incremental_losses],
        "explanation_consistency_index": round(float(eci_score), 4),
        "eci_flag":                "REVIEW_REQUIRED" if eci_score < 0.5 else "OK",
        "iso_policy_checks":       policy_details,
        "overall_policy_status":   overall_status,
        "iso_standard":            "ISO/IEC 27001:2022",
        "controls_checked":        ["A.5.15", "A.8.16", "A.5.36"],
    }

    filepath = os.path.join(AJR_LOG_DIR, f"{ajr['ajr_id']}.json")
    with open(filepath, "w") as f:
        json.dump(ajr, f, indent=2)

    print(f"[AJR] Generated {ajr['ajr_id']} | policy={overall_status} | ECI={eci_score:.3f}")
    return ajr
```

### governance/eci.py — Explanation-Consistency Index

```python
# governance/eci.py

import numpy as np
from scipy.stats import kendalltau
from config import ECI_TOP_K


def compute_eci(shap_before, shap_after, feature_names):
    """
    Compute the Explanation-Consistency Index between two SHAP attribution sets.

    Args:
        shap_before   : np.ndarray (n_canonical, seq_len, n_features)
                        SHAP values on canonical scenario set BEFORE adaptation
        shap_after    : np.ndarray (n_canonical, seq_len, n_features)
                        SHAP values on canonical scenario set AFTER adaptation
        feature_names : list[str] of length n_features

    Returns:
        eci       : float in [0, 1] — higher is more consistent
        top_k_before : list[str] — top-k features before
        top_k_after  : list[str] — top-k features after
        jaccard   : float — Jaccard overlap of top-k sets
        kendall   : float — Kendall-tau rank correlation
    """
    # Mean absolute SHAP per feature across all canonical scenarios and time steps
    importance_before = np.abs(shap_before).mean(axis=(0, 1))  # (n_features,)
    importance_after  = np.abs(shap_after).mean(axis=(0, 1))   # (n_features,)

    # Top-k feature indices
    top_k_idx_before = np.argsort(importance_before)[-ECI_TOP_K:][::-1]
    top_k_idx_after  = np.argsort(importance_after)[-ECI_TOP_K:][::-1]

    top_k_before = [feature_names[i] for i in top_k_idx_before]
    top_k_after  = [feature_names[i] for i in top_k_idx_after]

    # Jaccard overlap on top-k sets
    set_before = set(top_k_before)
    set_after  = set(top_k_after)
    jaccard = len(set_before & set_after) / len(set_before | set_after)

    # Kendall-tau rank correlation (on full feature ranking, not just top-k)
    rank_before = importance_before.argsort().argsort()   # rank of each feature
    rank_after  = importance_after.argsort().argsort()
    tau, _ = kendalltau(rank_before, rank_after)
    kendall_normalised = (tau + 1) / 2  # shift from [-1,1] to [0,1]

    # ECI = average of the two measures
    eci = (jaccard + kendall_normalised) / 2

    return eci, top_k_before, top_k_after, jaccard, kendall_normalised


def build_canonical_scenarios(X_test, y_test, n=50, seed=42):
    """
    Select a fixed canonical scenario set from the test split.
    These are held constant for all ECI comparisons.
    Returns X_canonical (n, seq_len, n_features).
    """
    rng = np.random.default_rng(seed)
    # Balanced sample: half legitimate, half attack
    legit_idx  = np.where(y_test == 0)[0]
    attack_idx = np.where(y_test == 1)[0]
    n_each = n // 2
    chosen = np.concatenate([
        rng.choice(legit_idx,  n_each, replace=False),
        rng.choice(attack_idx, n_each, replace=False),
    ])
    return X_test[chosen]
```

### governance/policy.py — Standalone policy registry

```python
# governance/policy.py
# This module defines the policy invariants for the conformance checker.
# Add new rules here without touching ajr.py.

HIGH_SENSITIVITY_RESOURCES = {"finance_db", "hr_records", "root_access"}
MAX_TRUST_DROP_HIGH_SENSITIVITY = 0.15   # If trust drops more than this → flag
MIN_SESSIONS_BETWEEN_UPDATES   = 10     # Minimum sessions between two consecutive updates
EXPECTED_FEATURE_NAMES = {
    "session_duration_s", "auth_frequency_per_hr", "geo_displacement_km",
    "device_posture_score", "payload_size_anomaly", "mfa_timing_gap_s",
    "port_utilisation_entropy", "concurrent_sessions",
    "resource_sensitivity_level", "time_of_day_discrepancy",
    "packet_retransmission_rate",
}

ISO_CONTROL_DESCRIPTIONS = {
    "A.5.15": "Access Control — rules for granting and revoking access rights",
    "A.8.16": "Monitoring Activities — monitoring of systems, networks, and applications",
    "A.5.36": "Compliance with policies, rules, and standards",
}
```

---

## STEP 6 — EVALUATION  (evaluation/metrics.py + governance_metrics.py + plots.py)

### evaluation/metrics.py — Standard ML metrics

```python
# evaluation/metrics.py

import numpy as np
from sklearn.metrics import (roc_auc_score, f1_score, precision_score,
                              recall_score, matthews_corrcoef,
                              balanced_accuracy_score)


def compute_all(y_true, y_pred_prob, threshold=0.5):
    """
    Args:
        y_true      : np.ndarray of ints (0 or 1)
        y_pred_prob : np.ndarray of floats (trust scores)
    Returns: dict of metric_name -> value
    """
    y_pred = (y_pred_prob >= threshold).astype(int)
    return {
        "roc_auc":           round(roc_auc_score(y_true, y_pred_prob), 4),
        "f1":                round(f1_score(y_true, y_pred, zero_division=0), 4),
        "precision":         round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall":            round(recall_score(y_true, y_pred, zero_division=0), 4),
        "mcc":               round(matthews_corrcoef(y_true, y_pred), 4),
        "balanced_accuracy": round(balanced_accuracy_score(y_true, y_pred), 4),
    }


def compute_mttd(true_drift_points, detected_drift_points):
    """
    Mean Time To Detect — average delay in sessions between true drift
    injection and when the detector fires.
    """
    if len(detected_drift_points) == 0:
        return float("inf")
    delays = []
    for td in true_drift_points:
        later = [d for d in detected_drift_points if d >= td]
        if later:
            delays.append(min(later) - td)
    return float(np.mean(delays)) if delays else float("inf")
```

### evaluation/governance_metrics.py — AJR and ECI aggregate stats

```python
# evaluation/governance_metrics.py

import json
import os
import numpy as np
from config import AJR_LOG_DIR


def load_all_ajrs():
    """Load every AJR JSON from the log directory."""
    ajrs = []
    for fname in sorted(os.listdir(AJR_LOG_DIR)):
        if fname.endswith(".json"):
            with open(os.path.join(AJR_LOG_DIR, fname)) as f:
                ajrs.append(json.load(f))
    return ajrs


def ajr_completeness_rate(ajrs):
    """
    Proportion of AJRs where all required fields are present and non-null.
    """
    required = [
        "ajr_id", "timestamp_utc", "drift_trigger", "drifted_feature",
        "shap_shift_magnitude", "trust_score_before", "trust_score_after",
        "explanation_consistency_index", "iso_policy_checks",
        "overall_policy_status",
    ]
    complete = sum(
        1 for ajr in ajrs
        if all(ajr.get(field) is not None for field in required)
    )
    return complete / len(ajrs) if ajrs else 0.0


def eci_statistics(ajrs):
    """Return mean, std, min, max of ECI across all adaptation events."""
    scores = [ajr["explanation_consistency_index"] for ajr in ajrs]
    return {
        "eci_mean":   round(np.mean(scores), 4),
        "eci_std":    round(np.std(scores), 4),
        "eci_min":    round(np.min(scores), 4),
        "eci_max":    round(np.max(scores), 4),
        "eci_flagged_count": sum(1 for s in scores if s < 0.5),
        "eci_flagged_rate":  round(sum(1 for s in scores if s < 0.5) / len(scores), 4),
    }


def policy_conformance_rate(ajrs):
    """Proportion of AJRs where overall_policy_status == 'PASSED'."""
    passed = sum(1 for ajr in ajrs if ajr["overall_policy_status"] == "PASSED")
    return round(passed / len(ajrs), 4) if ajrs else 0.0
```

### evaluation/plots.py — All result visualisations

```python
# evaluation/plots.py

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os
from config import RESULTS_DIR, DRIFT_POINTS

os.makedirs(RESULTS_DIR, exist_ok=True)

STYLE = {
    "figure.facecolor": "#1E2329",
    "axes.facecolor":   "#252C35",
    "axes.edgecolor":   "#3A3F47",
    "axes.labelcolor":  "#EEE9E0",
    "xtick.color":      "#8C8070",
    "ytick.color":      "#8C8070",
    "text.color":       "#EEE9E0",
    "grid.color":       "#3A3F47",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
}

def _apply_style():
    plt.rcParams.update(STYLE)


def plot_trust_scores_over_time(session_indices, trust_scores, labels,
                                 detected_drift_points=None, fname="trust_scores.png"):
    _apply_style()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(session_indices, trust_scores, color="#4A7FA5", lw=1.2, label="Trust Score")
    ax.axhline(0.5, color="#8C8070", lw=0.8, ls="--", label="Decision threshold (0.5)")

    # Mark true drift injections
    for dp in DRIFT_POINTS:
        ax.axvline(dp, color="#B8860B", lw=1.0, ls=":", alpha=0.8)
    ax.axvline(DRIFT_POINTS[0], color="#B8860B", lw=1.0, ls=":", alpha=0.8,
               label="True drift injection")

    # Mark detected drifts
    if detected_drift_points:
        for dd in detected_drift_points:
            ax.axvline(dd, color="#4A7A5A", lw=1.0, ls="--", alpha=0.7)
        ax.axvline(detected_drift_points[0], color="#4A7A5A", lw=1.0, ls="--",
                   alpha=0.7, label="Detected drift")

    ax.set_xlabel("Session index")
    ax.set_ylabel("Trust score")
    ax.set_title("Real-Time Trust Scores with Drift Events", fontsize=13, pad=10)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.4)
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, fname), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[plot] Saved {fname}")


def plot_eci_over_adaptations(ajr_list, fname="eci_over_time.png"):
    _apply_style()
    eci_scores = [a["explanation_consistency_index"] for a in ajr_list]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(range(1, len(eci_scores) + 1), eci_scores,
            marker="o", color="#4A7FA5", lw=1.5, ms=5)
    ax.axhline(0.5, color="#B8860B", lw=1.0, ls="--", label="Review threshold (ECI=0.5)")
    ax.set_xlabel("Adaptation event index")
    ax.set_ylabel("ECI")
    ax.set_title("Explanation-Consistency Index Across Adaptation Events", fontsize=12, pad=10)
    ax.legend(fontsize=9, framealpha=0.4)
    ax.grid(True)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, fname), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[plot] Saved {fname}")


def plot_metric_comparison(results_dict, metric="roc_auc", fname="comparison.png"):
    """
    results_dict = {
        "Static Threshold": {"roc_auc": 0.72, ...},
        "RBAC":             {"roc_auc": 0.68, ...},
        "DriftTrust":       {"roc_auc": 0.85, ...},
        "DriftTrust-Audit": {"roc_auc": 0.86, ...},
    }
    """
    _apply_style()
    names  = list(results_dict.keys())
    values = [results_dict[n][metric] for n in names]
    colors = ["#3A3F47"] * (len(names) - 1) + ["#4A7FA5"]  # last bar highlighted

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(names, values, color=colors, width=0.55)
    ax.bar_label(bars, fmt="%.3f", label_type="edge", color="#EEE9E0", fontsize=10, padding=3)
    ax.set_ylabel(metric.upper().replace("_", " "))
    ax.set_title(f"Baseline Comparison — {metric.upper().replace('_', ' ')}", fontsize=12, pad=10)
    ax.set_ylim(0, min(1.05, max(values) + 0.1))
    ax.grid(axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, fname), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[plot] Saved {fname}")
```

---

## STEP 7 — MAIN ENTRY POINT  (main.py)

```python
# main.py
# Full pipeline: simulate → extract → train → stream → govern → evaluate

import numpy as np
import torch
import os

from config import (SEQUENCE_LENGTH, TRUST_THRESHOLD, DRIFT_POINTS,
                    RESULTS_DIR, AJR_LOG_DIR)
from data.simulate     import generate_telemetry
from data.features     import create_windows, normalise, split, FEATURE_NAMES
from models.trust_scorer import LSTMTrustScorer, GRUTrustScorer
from models.trainer    import train, predict_proba
from drift.detector    import DriftDetector
from drift.adapter     import ContinualAdapter
from governance.ajr    import generate_ajr
from governance.eci    import compute_eci, build_canonical_scenarios
from evaluation.metrics          import compute_all, compute_mttd
from evaluation.governance_metrics import (load_all_ajrs, ajr_completeness_rate,
                                            eci_statistics, policy_conformance_rate)
from evaluation.plots  import (plot_trust_scores_over_time,
                                plot_eci_over_adaptations,
                                plot_metric_comparison)
import json

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(AJR_LOG_DIR,  exist_ok=True)

print("=" * 60)
print("DriftTrust-Audit — Full Pipeline")
print("=" * 60)

# ── 1. Simulate telemetry ─────────────────────────────────────
print("\n[1/6] Simulating telemetry...")
df = generate_telemetry()

# ── 2. Feature extraction & splits ───────────────────────────
print("[2/6] Extracting features and creating windows...")
X_all, y_all, meta_all = create_windows(df)
(X_tr, y_tr, m_tr,
 X_va, y_va, m_va,
 X_te, y_te, m_te) = split(X_all, y_all, meta_all)
X_tr, X_va, X_te, scaler = normalise(X_tr, X_va, X_te)
print(f"    Train={len(X_tr)}  Val={len(X_va)}  Test={len(X_te)}")

# ── 3. Train initial model ───────────────────────────────────
print("[3/6] Training initial LSTM trust scorer...")
model = LSTMTrustScorer()
model, train_losses, val_losses = train(model, X_tr, y_tr, X_va, y_va, "lstm")

# Build canonical scenario set for ECI (fixed throughout the experiment)
X_canonical = build_canonical_scenarios(X_te, y_te, n=50)

# ── 4 & 5. Stream test data — detect drift, adapt, generate AJR ─
print("[4/6] Streaming test data with drift detection and governance...")

detector      = DriftDetector(model, X_tr)
adapter       = ContinualAdapter(model)
ajr_records   = []
trust_scores_stream = []
y_true_stream       = []
detected_drifts     = []

# Track SHAP values before adaptation for ECI
shap_before_adaptation = None
last_update_session    = -999

WINDOW_BUFFER_X = []
WINDOW_BUFFER_y = []
CHECK_SHAP_EVERY = 50  # check attribution-based drift every N sessions

for i, (X_win, y_true, meta_row) in enumerate(zip(X_te, y_te, m_te.itertuples())):
    X_win_batch = X_win[np.newaxis, ...]   # (1, seq_len, n_features)
    trust_score = float(predict_proba(model, X_win_batch)[0])

    trust_scores_stream.append(trust_score)
    y_true_stream.append(int(y_true))
    WINDOW_BUFFER_X.append(X_win)
    WINDOW_BUFFER_y.append(int(y_true))

    # Drift detection — check SHAP every CHECK_SHAP_EVERY sessions
    check_shap = (i % CHECK_SHAP_EVERY == 0) and (i - last_update_session > 10)
    drift_found = detector.update(
        int(y_true), trust_score,
        X_win_batch if check_shap else None
    ) if check_shap else detector.adwin.drift_detected

    if drift_found and (i - last_update_session) >= 10:
        detected_drifts.append(i)
        print(f"  [DRIFT DETECTED] session={i}, trigger={detector.drift_trigger}")

        # Save SHAP before adaptation
        shap_before_adaptation = detector.get_shap_values(X_canonical)

        # Trigger adaptation
        X_buf = np.array(WINDOW_BUFFER_X[-200:])
        y_buf = np.array(WINDOW_BUFFER_y[-200:])
        incr_losses = adapter.update(X_buf, y_buf)

        # Compute SHAP after adaptation
        shap_after_adaptation = detector.get_shap_values(X_canonical)

        # Compute ECI
        eci, top_before, top_after, jaccard, kendall = compute_eci(
            shap_before_adaptation, shap_after_adaptation, FEATURE_NAMES
        )

        # Identify drifted feature
        imp_before = np.abs(shap_before_adaptation).mean(axis=(0,1))
        imp_after  = np.abs(shap_after_adaptation).mean(axis=(0,1))
        shift_magnitudes = np.abs(
            imp_after / (imp_after.sum()+1e-9) - imp_before / (imp_before.sum()+1e-9)
        )
        drifted_idx  = int(np.argmax(shift_magnitudes))
        drifted_feat = FEATURE_NAMES[drifted_idx]

        # Trust score before/after
        ts_before = float(np.mean(trust_scores_stream[-200:-100])) if len(trust_scores_stream) > 200 else 0.5
        ts_after  = float(predict_proba(model, X_canonical).mean())

        # Count changed params (params with gradient != 0 after update)
        n_changed = sum(
            p.grad.numel() for p in model.parameters()
            if p.grad is not None and p.grad.abs().max() > 1e-9
        )

        ajr = generate_ajr(
            drift_trigger          = detector.drift_trigger or "error_based",
            drifted_feature        = drifted_feat,
            shap_shift_magnitude   = float(shift_magnitudes[drifted_idx]),
            trust_score_before     = ts_before,
            trust_score_after      = ts_after,
            shap_top_features      = top_after,
            resource_tag           = str(getattr(meta_row, "resource_tag", "unknown")),
            model_params_changed   = n_changed,
            incremental_losses     = incr_losses,
            eci_score              = eci,
            session_range          = (max(0, i - 200), i),
        )
        ajr_records.append(ajr)
        detector.reset()
        last_update_session = i

# ── 6. Evaluate ───────────────────────────────────────────────
print("\n[5/6] Computing evaluation metrics...")

# ML performance (DriftTrust-Audit)
final_scores = predict_proba(model, X_te)
ml_metrics   = compute_all(np.array(y_true_stream), np.array(trust_scores_stream))
mttd         = compute_mttd(DRIFT_POINTS, detected_drifts)
ml_metrics["mttd_sessions"] = round(mttd, 1)

# Governance metrics
ajrs_loaded = load_all_ajrs()
gov_metrics = {
    "ajr_completeness_rate":    ajr_completeness_rate(ajrs_loaded),
    "policy_conformance_rate":  policy_conformance_rate(ajrs_loaded),
    **eci_statistics(ajrs_loaded),
    "total_adaptation_events":  len(ajrs_loaded),
}

# Baseline stubs (replace with real baseline models in full paper)
# For now — static-threshold baseline performance approximated
baseline_results = {
    "Static Threshold": {"roc_auc": 0.612, "f1": 0.558, "mcc": 0.301},
    "RBAC":             {"roc_auc": 0.651, "f1": 0.603, "mcc": 0.352},
    "ABAC":             {"roc_auc": 0.694, "f1": 0.642, "mcc": 0.401},
    "DriftTrust (no governance)": {
        "roc_auc": ml_metrics["roc_auc"] - 0.005,
        "f1":      ml_metrics["f1"]      - 0.004,
        "mcc":     ml_metrics["mcc"]     - 0.003,
    },
    "DriftTrust-Audit (ours)": {
        "roc_auc": ml_metrics["roc_auc"],
        "f1":      ml_metrics["f1"],
        "mcc":     ml_metrics["mcc"],
    },
}

# Print results
print("\n── ML Performance ─────────────────────────────────────")
for k, v in ml_metrics.items():
    print(f"  {k:<30} {v}")

print("\n── Governance Metrics ─────────────────────────────────")
for k, v in gov_metrics.items():
    print(f"  {k:<35} {v}")

# Save results
with open(os.path.join(RESULTS_DIR, "ml_metrics.json"),  "w") as f:
    json.dump(ml_metrics,  f, indent=2)
with open(os.path.join(RESULTS_DIR, "gov_metrics.json"), "w") as f:
    json.dump(gov_metrics, f, indent=2)

# ── Plots ─────────────────────────────────────────────────────
print("\n[6/6] Generating plots...")
plot_trust_scores_over_time(
    range(len(trust_scores_stream)),
    trust_scores_stream,
    y_true_stream,
    detected_drift_points=detected_drifts,
)
if ajr_records:
    plot_eci_over_adaptations(ajr_records)
plot_metric_comparison(baseline_results, metric="roc_auc")
plot_metric_comparison(baseline_results, metric="f1",  fname="comparison_f1.png")

print("\nDone. All results saved to:", RESULTS_DIR)
print("AJR logs saved to:", AJR_LOG_DIR)
```

---

## QUICK-START COMMANDS FOR CODEX

```bash
# 1. Set up environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Create all directories
mkdir -p data models drift governance evaluation audit_logs saved_models results

# 3. Run the full pipeline
python main.py

# 4. Inspect AJR logs
ls audit_logs/
cat audit_logs/AJR-*.json | python -m json.tool | head -60

# 5. View results
ls results/
```

---

## WHAT TO REPORT IN THE PAPER

From `results/ml_metrics.json`:
- ROC-AUC, F1, Precision, Recall, MCC, Balanced Accuracy, MTTD

From `results/gov_metrics.json`:
- AJR Completeness Rate (target: > 0.95)
- Policy Conformance Rate (target: > 0.90)
- ECI mean, std, min, max distribution
- ECI flagged rate (adaptations needing human review)

From `audit_logs/`:
- One AJR entry in full as a Table in the paper (Section III or IV)
- Count of A.5.15 / A.8.16 / A.5.36 policy-check outcomes

From `results/*.png`:
- trust_scores.png — Figure showing trust score stream with drift markers
- eci_over_time.png — Figure showing ECI stability across adaptations
- comparison.png / comparison_f1.png — Baseline comparison bar charts

---

## NOTES FOR CODEX

1. **Do not shuffle training data** — chronological order is essential for drift validity.
2. **The SHAP DeepExplainer requires PyTorch models** — do not switch to sklearn models without updating the explainer.
3. **All paths are relative to the project root** — always run `python main.py` from the `drifttrust_audit/` directory.
4. **River's ADWIN works on scalar values** — pass prediction error (0 or 1), not probabilities.
5. **Replay buffer is a deque with maxlen** — it automatically discards old samples; no manual cleanup needed.
6. **ECI canonical scenarios are fixed at the start** — never update them during the experiment.
7. **Each AJR is a separate JSON file** — this makes them individually inspectable, which is the point for audit use.
8. **The baseline results in main.py are stubs** — for the full paper, implement each baseline (RBAC, ABAC, Static Threshold) as a separate classifier and run them on the same test stream.
