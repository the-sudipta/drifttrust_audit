import numpy as np
from sklearn.linear_model import LogisticRegression

from config import FEATURE_NAMES


def static_threshold_scores(x_stream):
    latest = x_stream[:, -1, :]
    feature_idx = {name: idx for idx, name in enumerate(FEATURE_NAMES)}
    risk = np.zeros(len(latest), dtype=float)
    risk += latest[:, feature_idx["auth_frequency_per_hr"]] > 8
    risk += latest[:, feature_idx["geo_displacement_km"]] > 700
    risk += latest[:, feature_idx["device_posture_score"]] < 0.35
    risk += latest[:, feature_idx["payload_size_anomaly"]] > 2.4
    risk += latest[:, feature_idx["packet_retransmission_rate"]] > 0.28
    return np.clip(1.0 - (risk / 5.0), 0.0, 1.0)


def rbac_scores(x_stream):
    latest = x_stream[:, -1, :]
    sensitivity = latest[:, FEATURE_NAMES.index("resource_sensitivity_level")]
    out_of_hours = latest[:, FEATURE_NAMES.index("time_of_day_discrepancy")]
    allowed = ~((sensitivity >= 3) & (out_of_hours >= 0.5))
    return np.where(allowed, 0.72, 0.28)


def abac_scores(x_stream):
    latest = x_stream[:, -1, :]
    idx = {name: i for i, name in enumerate(FEATURE_NAMES)}
    score = np.full(len(latest), 0.85, dtype=float)
    score -= 0.18 * (latest[:, idx["resource_sensitivity_level"]] >= 3)
    score -= 0.20 * (latest[:, idx["time_of_day_discrepancy"]] >= 0.5)
    score -= 0.16 * (latest[:, idx["device_posture_score"]] < 0.45)
    score -= 0.14 * (latest[:, idx["concurrent_sessions"]] > 7)
    return np.clip(score, 0.0, 1.0)


def logistic_baseline_scores(x_train, y_train, x_stream):
    model = LogisticRegression(max_iter=500, class_weight="balanced")
    model.fit(x_train.reshape(len(x_train), -1), y_train)
    probs = model.predict_proba(x_stream.reshape(len(x_stream), -1))
    class_to_idx = {cls: idx for idx, cls in enumerate(model.classes_)}
    return probs[:, class_to_idx[1]]

