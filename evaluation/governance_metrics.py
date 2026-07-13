import json
import os

import numpy as np

from config import AJR_LOG_DIR, ECI_THRESHOLD


def load_all_ajrs():
    if not os.path.isdir(AJR_LOG_DIR):
        return []
    ajrs = []
    for filename in sorted(os.listdir(AJR_LOG_DIR)):
        if filename.endswith(".json"):
            with open(os.path.join(AJR_LOG_DIR, filename), encoding="utf-8") as f:
                ajrs.append(json.load(f))
    return ajrs


def ajr_completeness_rate(ajrs):
    required = [
        "ajr_id",
        "timestamp_utc",
        "drift_trigger",
        "drifted_feature",
        "attribution_shift_magnitude",
        "trust_score_before",
        "trust_score_after",
        "explanation_consistency_index",
        "iso_policy_checks",
        "overall_policy_status",
    ]
    if not ajrs:
        return 0.0
    complete = sum(all(ajr.get(field) is not None for field in required) for ajr in ajrs)
    return round(complete / len(ajrs), 4)


def eci_statistics(ajrs):
    if not ajrs:
        return {
            "eci_mean": None,
            "eci_std": None,
            "eci_min": None,
            "eci_max": None,
            "eci_flagged_count": 0,
            "eci_flagged_rate": 0.0,
        }
    scores = np.array([ajr["explanation_consistency_index"] for ajr in ajrs], dtype=float)
    flagged = scores < ECI_THRESHOLD
    return {
        "eci_mean": round(float(scores.mean()), 4),
        "eci_std": round(float(scores.std()), 4),
        "eci_min": round(float(scores.min()), 4),
        "eci_max": round(float(scores.max()), 4),
        "eci_flagged_count": int(flagged.sum()),
        "eci_flagged_rate": round(float(flagged.mean()), 4),
    }


def policy_conformance_rate(ajrs):
    if not ajrs:
        return 0.0
    passed = sum(ajr["overall_policy_status"] == "PASSED" for ajr in ajrs)
    return round(passed / len(ajrs), 4)

