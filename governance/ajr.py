import json
import os
import uuid
from datetime import datetime, timezone

from config import AJR_LOG_DIR, ECI_THRESHOLD
from governance.policy import ISO_CONTROL_DESCRIPTIONS, run_policy_checks


def generate_ajr(
    *,
    drift_trigger,
    drifted_feature,
    attribution_method,
    attribution_shift_magnitude,
    trust_score_before,
    trust_score_after,
    shap_top_features,
    resource_tag,
    model_params_changed,
    incremental_losses,
    eci_score,
    eci_jaccard,
    eci_kendall,
    session_range,
    sessions_since_last_update,
):
    os.makedirs(AJR_LOG_DIR, exist_ok=True)
    policy_details, overall_status = run_policy_checks(
        trust_score_before=trust_score_before,
        trust_score_after=trust_score_after,
        resource_tag=resource_tag,
        shap_top_features=shap_top_features,
        sessions_since_last_update=sessions_since_last_update,
    )

    ajr = {
        "ajr_id": f"AJR-{str(uuid.uuid4())[:8].upper()}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "drift_trigger": drift_trigger,
        "drifted_feature": drifted_feature,
        "attribution_method": attribution_method,
        "attribution_shift_magnitude": round(float(attribution_shift_magnitude), 4),
        "shap_top_features_after": shap_top_features,
        "trust_score_before": round(float(trust_score_before), 4),
        "trust_score_after": round(float(trust_score_after), 4),
        "trust_score_delta": round(float(trust_score_after - trust_score_before), 4),
        "resource_tag": resource_tag,
        "session_range": list(session_range),
        "sessions_since_last_update": int(sessions_since_last_update),
        "model_params_changed": int(model_params_changed),
        "incremental_losses": [round(float(loss), 6) for loss in incremental_losses],
        "explanation_consistency_index": round(float(eci_score), 4),
        "eci_components": {
            "top_k_jaccard": round(float(eci_jaccard), 4),
            "kendall_tau_normalised": round(float(eci_kendall), 4),
        },
        "eci_flag": "REVIEW_REQUIRED" if eci_score < ECI_THRESHOLD else "OK",
        "iso_policy_checks": policy_details,
        "overall_policy_status": overall_status,
        "iso_standard": "ISO/IEC 27001:2022",
        "controls_checked": ["A.5.15", "A.8.16", "A.5.36"],
        "control_descriptions": ISO_CONTROL_DESCRIPTIONS,
    }

    filepath = os.path.join(AJR_LOG_DIR, f"{ajr['ajr_id']}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(ajr, f, indent=2)
    return ajr

