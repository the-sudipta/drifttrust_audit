import os

import numpy as np
import pandas as pd

from config import DATA_DIR, DRIFT_POINTS, DRIFT_TYPES, FEATURE_NAMES, N_SESSIONS, RANDOM_SEED


def _base_distribution(n, seed):
    rng = np.random.default_rng(seed)
    x = np.column_stack(
        [
            rng.normal(300, 80, n).clip(30, 3600),
            rng.normal(2, 0.8, n).clip(0, 50),
            rng.exponential(50, n).clip(0, 2000),
            rng.beta(8, 2, n),
            rng.normal(0, 1, n),
            rng.normal(15, 5, n).clip(1, 120),
            rng.uniform(0.5, 2.5, n),
            rng.poisson(1.2, n).clip(1, 20),
            rng.choice([0, 1, 2, 3], n, p=[0.4, 0.3, 0.2, 0.1]),
            rng.binomial(1, 0.08, n),
            rng.beta(1, 15, n),
        ]
    )

    suspicious = (
        (x[:, 1] > 8)
        | (x[:, 2] > 700)
        | (x[:, 3] < 0.35)
        | (x[:, 4] > 2.4)
        | ((x[:, 8] >= 3) & (x[:, 9] == 1))
        | (x[:, 10] > 0.28)
    )
    seeded_attacks = rng.random(n) < 0.12
    x[seeded_attacks, 1] = rng.normal(10, 3, seeded_attacks.sum()).clip(4, 50)
    x[seeded_attacks, 2] = rng.exponential(500, seeded_attacks.sum()).clip(150, 2000)
    x[seeded_attacks, 3] = rng.beta(2, 8, seeded_attacks.sum())
    x[seeded_attacks, 4] = rng.normal(2.8, 0.8, seeded_attacks.sum())
    x[seeded_attacks, 10] = rng.beta(3, 4, seeded_attacks.sum())
    suspicious = suspicious | seeded_attacks
    y = np.where(suspicious, 0, 1).astype(int)
    return x, y


def _inject_gradual_drift(x, y, start, end, rng):
    n = end - start
    if n <= 0:
        return x, y
    shift = np.linspace(1.0, 3.8, n)
    x[start:end, 1] *= shift
    x[start:end, 0] *= np.linspace(1.0, 0.55, n)
    x[start:end, 5] *= np.linspace(1.0, 1.8, n)
    attacks = rng.random(n) < 0.16
    segment = y[start:end]
    segment[attacks] = 0
    y[start:end] = segment
    return x, y


def _inject_abrupt_drift(x, y, start, end, rng):
    n = end - start
    if n <= 0:
        return x, y
    x[start:end, 7] = rng.normal(11, 3, n).clip(4, 30)
    x[start:end, 10] = rng.beta(3, 5, n)
    x[start:end, 6] = rng.uniform(2.4, 4.5, n)
    attacks = rng.random(n) < 0.32
    segment = y[start:end]
    segment[attacks] = 0
    y[start:end] = segment
    return x, y


def _inject_recurring_drift(x, y, start, end, rng):
    n = end - start
    if n <= 0:
        return x, y
    x[start:end, 8] = rng.choice([2, 3], n, p=[0.45, 0.55])
    x[start:end, 9] = rng.binomial(1, 0.42, n)
    x[start:end, 2] = rng.exponential(180, n).clip(0, 2000)
    attacks = rng.random(n) < 0.22
    segment = y[start:end]
    segment[attacks] = 0
    y[start:end] = segment
    return x, y


def generate_telemetry(n_sessions=N_SESSIONS, save_csv=True):
    rng = np.random.default_rng(RANDOM_SEED)
    x, y = _base_distribution(n_sessions, RANDOM_SEED)
    drift_labels = np.array(["none"] * n_sessions, dtype=object)

    handlers = {
        "gradual": _inject_gradual_drift,
        "abrupt": _inject_abrupt_drift,
        "recurring": _inject_recurring_drift,
    }

    for idx, (point, drift_type) in enumerate(zip(DRIFT_POINTS, DRIFT_TYPES)):
        end = DRIFT_POINTS[idx + 1] if idx + 1 < len(DRIFT_POINTS) else n_sessions
        point = min(point, n_sessions)
        end = min(end, n_sessions)
        x, y = handlers[drift_type](x, y, point, end, rng)
        drift_labels[point:end] = drift_type

    df = pd.DataFrame(x, columns=FEATURE_NAMES)
    df["label"] = y
    df["drift_type"] = drift_labels
    df["session_id"] = np.arange(n_sessions)
    df["resource_tag"] = rng.choice(
        ["public_portal", "internal_wiki", "finance_db", "hr_records", "root_access"],
        n_sessions,
        p=[0.4, 0.3, 0.15, 0.1, 0.05],
    )

    if save_csv:
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(os.path.join(DATA_DIR, "telemetry.csv"), index=False)
    return df


if __name__ == "__main__":
    telemetry = generate_telemetry()
    print(telemetry["label"].value_counts().rename({1: "legitimate", 0: "attack"}))
    print(telemetry["drift_type"].value_counts())
