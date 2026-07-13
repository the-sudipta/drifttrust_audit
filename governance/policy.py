from config import FEATURE_NAMES, HIGH_SENSITIVITY_RESOURCES, MIN_SESSIONS_BETWEEN_UPDATES


EXPECTED_FEATURE_NAMES = set(FEATURE_NAMES)
MAX_HIGH_SENSITIVITY_TRUST_INCREASE = 0.15
MAX_REASONABLE_TRUST_SHIFT = 0.35

ISO_CONTROL_DESCRIPTIONS = {
    "A.5.15": "Access control rules for granting, reviewing, and changing access.",
    "A.8.16": "Monitoring activities for systems, networks, and applications.",
    "A.5.36": "Compliance with policies, rules, and standards.",
}


def run_policy_checks(
    *,
    trust_score_before,
    trust_score_after,
    resource_tag,
    shap_top_features,
    sessions_since_last_update,
):
    checks = {}
    delta = trust_score_after - trust_score_before

    if resource_tag in HIGH_SENSITIVITY_RESOURCES and delta > MAX_HIGH_SENSITIVITY_TRUST_INCREASE:
        checks["A.5.15_access_control"] = (
            "FAILED: high-sensitivity resource became more permissive by "
            f"{delta:.3f}; human review required"
        )
    elif abs(delta) > MAX_REASONABLE_TRUST_SHIFT:
        checks["A.5.15_access_control"] = (
            f"REVIEW: large trust-score movement ({delta:.3f}) after adaptation"
        )
    else:
        checks["A.5.15_access_control"] = "PASSED"

    unexpected = [feature for feature in shap_top_features if feature not in EXPECTED_FEATURE_NAMES]
    if unexpected:
        checks["A.8.16_monitoring"] = (
            "FAILED: attribution contains unknown feature(s): " + ", ".join(unexpected)
        )
    else:
        checks["A.8.16_monitoring"] = "PASSED"

    if sessions_since_last_update < MIN_SESSIONS_BETWEEN_UPDATES:
        checks["A.5.36_compliance"] = (
            f"FAILED: only {sessions_since_last_update} sessions since previous update"
        )
    else:
        checks["A.5.36_compliance"] = "PASSED"

    overall = "PASSED"
    if any(value.startswith("FAILED") for value in checks.values()):
        overall = "FAILED"
    elif any(value.startswith("REVIEW") for value in checks.values()):
        overall = "REVIEW"

    return checks, overall

