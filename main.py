import json
import os

import numpy as np

from config import (
    ADAPTATION_WINDOW,
    AJR_LOG_DIR,
    CHECK_ATTRIBUTION_EVERY,
    DATA_DIR,
    DRIFT_POINTS,
    ECI_THRESHOLD,
    FEATURE_NAMES,
    MIN_SESSIONS_BETWEEN_UPDATES,
    MODEL_SAVE_DIR,
    RESULTS_DIR,
)
from data.features import create_windows, normalise_stream, split_pre_drift_stream
from data.simulate import generate_telemetry
from drift.adapter import ContinualAdapter
from drift.detector import DriftDetector
from evaluation.baselines import abac_scores, logistic_baseline_scores, rbac_scores, static_threshold_scores
from evaluation.governance_metrics import (
    ajr_completeness_rate,
    eci_statistics,
    load_all_ajrs,
    policy_conformance_rate,
)
from evaluation.metrics import compute_all, compute_mttd
from evaluation.plots import plot_eci_over_adaptations, plot_metric_comparison, plot_trust_scores_over_time
from governance.ajr import generate_ajr
from governance.eci import build_canonical_scenarios, compute_eci
from models.trainer import make_model, predict_proba, train


def _prepare_dirs():
    for directory in [DATA_DIR, AJR_LOG_DIR, MODEL_SAVE_DIR, RESULTS_DIR]:
        os.makedirs(directory, exist_ok=True)
    for directory in [AJR_LOG_DIR, RESULTS_DIR]:
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            if os.path.isfile(path):
                os.remove(path)


def _trust_window_mean(values, fallback=0.5):
    return float(np.mean(values)) if values else fallback


def _novelty_assessment(ajr_records, gov_metrics):
    achieved = {
        "AJR_generated_for_adaptations": len(ajr_records) > 0,
        "AJR_contains_iso_27001_mapping": all("controls_checked" in ajr for ajr in ajr_records),
        "ECI_computed_for_adaptations": all("explanation_consistency_index" in ajr for ajr in ajr_records),
        "policy_conformance_checked": all("iso_policy_checks" in ajr for ajr in ajr_records),
        "audit_logs_are_individual_json_records": len(ajr_records) == len(
            [name for name in os.listdir(AJR_LOG_DIR) if name.endswith(".json")]
        ),
        "ajr_completeness_rate_target_met": gov_metrics.get("ajr_completeness_rate", 0) >= 0.95,
        "policy_conformance_rate_target_met": gov_metrics.get("policy_conformance_rate", 0) >= 0.90,
    }
    achieved["novelty_layer_operational"] = all(achieved.values())
    return achieved


def main():
    _prepare_dirs()
    print("DriftTrust-Audit: simulate -> train -> stream -> adapt -> govern -> evaluate")

    df = generate_telemetry(save_csv=True)
    x_all, y_all, meta_all = create_windows(df)
    (
        x_train_raw,
        y_train,
        _m_train,
        x_val_raw,
        y_val,
        _m_val,
        x_stream_raw,
        y_stream,
        m_stream,
    ) = split_pre_drift_stream(x_all, y_all, meta_all)
    x_train, x_val, x_stream, _scaler = normalise_stream(x_train_raw, x_val_raw, x_stream_raw)

    print(f"Train windows: {len(x_train)} | Validation windows: {len(x_val)} | Stream windows: {len(x_stream)}")
    print(f"Injected drift session ids: {DRIFT_POINTS}")

    model = make_model()
    model, train_losses, val_losses = train(model, x_train, y_train, x_val, y_val)
    detector = DriftDetector(model, x_train)
    adapter = ContinualAdapter(model)
    x_canonical = build_canonical_scenarios(x_stream, y_stream)

    trust_scores = []
    detected_drifts = []
    ajr_records = []
    buffer_x = []
    buffer_y = []
    last_update_session = int(m_stream["session_id"].iloc[0]) - MIN_SESSIONS_BETWEEN_UPDATES

    for idx, (x_win, y_true, meta_row) in enumerate(zip(x_stream, y_stream, m_stream.itertuples(index=False))):
        x_batch = x_win[np.newaxis, ...]
        trust_score = float(predict_proba(model, x_batch)[0])
        trust_scores.append(trust_score)
        buffer_x.append(x_win)
        buffer_y.append(int(y_true))

        session_id = int(meta_row.session_id)
        should_check_attr = idx % CHECK_ATTRIBUTION_EVERY == 0
        drift_found = detector.update(int(y_true), trust_score, x_batch if should_check_attr else None)
        gap = session_id - last_update_session

        if drift_found and gap >= MIN_SESSIONS_BETWEEN_UPDATES and len(buffer_x) >= 30:
            detected_drifts.append(session_id)
            attribution_before = detector.get_attribution_values(x_canonical)
            recent_x = np.array(buffer_x[-ADAPTATION_WINDOW:])
            recent_y = np.array(buffer_y[-ADAPTATION_WINDOW:])
            losses = adapter.update(recent_x, recent_y)
            attribution_after = detector.get_attribution_values(x_canonical)
            eci, top_before, top_after, jaccard, kendall = compute_eci(
                attribution_before, attribution_after, FEATURE_NAMES
            )

            importance_before = np.abs(attribution_before).mean(axis=(0, 1))
            importance_after = np.abs(attribution_after).mean(axis=(0, 1))
            before_norm = importance_before / (importance_before.sum() + 1e-9)
            after_norm = importance_after / (importance_after.sum() + 1e-9)
            shifts = np.abs(after_norm - before_norm)
            drifted_idx = int(np.argmax(shifts))

            before_scores = trust_scores[-ADAPTATION_WINDOW:-max(1, ADAPTATION_WINDOW // 2)]
            trust_before = _trust_window_mean(before_scores)
            trust_after = float(predict_proba(model, x_canonical).mean())

            ajr = generate_ajr(
                drift_trigger=detector.drift_trigger or "unknown",
                drifted_feature=FEATURE_NAMES[drifted_idx],
                attribution_method=detector.attributor.method_name,
                attribution_shift_magnitude=float(max(detector.last_attribution_shift, shifts[drifted_idx])),
                trust_score_before=trust_before,
                trust_score_after=trust_after,
                shap_top_features=top_after,
                resource_tag=str(meta_row.resource_tag),
                model_params_changed=sum(layer.size for layer in model.estimator.coefs_),
                incremental_losses=losses,
                eci_score=eci,
                eci_jaccard=jaccard,
                eci_kendall=kendall,
                session_range=(max(0, session_id - len(recent_x)), session_id),
                sessions_since_last_update=gap,
            )
            ajr["top_features_before"] = top_before
            ajr_records.append(ajr)
            detector.refresh_baseline(recent_x)
            detector.reset_error_state()
            last_update_session = session_id

    y_stream = np.asarray(y_stream)
    trust_scores = np.asarray(trust_scores)
    ml_metrics = compute_all(y_stream, trust_scores)
    ml_metrics["mttd_sessions"] = compute_mttd(DRIFT_POINTS, detected_drifts)
    ml_metrics["detected_drift_count"] = len(detected_drifts)
    ml_metrics["adaptation_event_count"] = len(ajr_records)

    baseline_results = {
        "Static Threshold": compute_all(y_stream, static_threshold_scores(x_stream_raw)),
        "RBAC": compute_all(y_stream, rbac_scores(x_stream_raw)),
        "ABAC": compute_all(y_stream, abac_scores(x_stream_raw)),
        "Logistic Baseline": compute_all(y_stream, logistic_baseline_scores(x_train, y_train, x_stream)),
        "DriftTrust-Audit": ml_metrics,
    }

    ajrs_loaded = load_all_ajrs()
    gov_metrics = {
        "ajr_completeness_rate": ajr_completeness_rate(ajrs_loaded),
        "policy_conformance_rate": policy_conformance_rate(ajrs_loaded),
        "total_adaptation_events": len(ajrs_loaded),
        **eci_statistics(ajrs_loaded),
    }
    novelty = _novelty_assessment(ajr_records, gov_metrics)

    session_ids = m_stream["session_id"].to_numpy()
    plot_trust_scores_over_time(session_ids, trust_scores, detected_drifts)
    plot_eci_over_adaptations(ajr_records)
    plot_metric_comparison(baseline_results, "f1")
    plot_metric_comparison(baseline_results, "balanced_accuracy")

    with open(os.path.join(RESULTS_DIR, "ml_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(ml_metrics, f, indent=2)
    with open(os.path.join(RESULTS_DIR, "baseline_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(baseline_results, f, indent=2)
    with open(os.path.join(RESULTS_DIR, "gov_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(gov_metrics, f, indent=2)
    with open(os.path.join(RESULTS_DIR, "novelty_assessment.json"), "w", encoding="utf-8") as f:
        json.dump(novelty, f, indent=2)

    print("\nML metrics")
    print(json.dumps(ml_metrics, indent=2))
    print("\nGovernance metrics")
    print(json.dumps(gov_metrics, indent=2))
    print("\nNovelty assessment")
    print(json.dumps(novelty, indent=2))
    print(f"\nResults saved to {RESULTS_DIR}; AJR logs saved to {AJR_LOG_DIR}")


if __name__ == "__main__":
    main()
