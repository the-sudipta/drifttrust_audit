import numpy as np
from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)


def compute_all(y_true, y_pred_prob, threshold=0.5):
    y_true = np.asarray(y_true)
    y_pred_prob = np.asarray(y_pred_prob)
    y_pred = (y_pred_prob >= threshold).astype(int)
    return {
        "roc_auc": round(float(roc_auc_score(y_true, y_pred_prob)), 4)
        if len(np.unique(y_true)) > 1
        else None,
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "mcc": round(float(matthews_corrcoef(y_true, y_pred)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(y_true, y_pred)), 4),
    }


def compute_mttd(true_drift_points, detected_drift_points):
    delays = []
    for true_point in true_drift_points:
        later = [detected for detected in detected_drift_points if detected >= true_point]
        if later:
            delays.append(min(later) - true_point)
    return round(float(np.mean(delays)), 2) if delays else None

