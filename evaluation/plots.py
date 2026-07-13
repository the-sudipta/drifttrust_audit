import os

import matplotlib.pyplot as plt

from config import DRIFT_POINTS, RESULTS_DIR


def _ensure_results():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def plot_trust_scores_over_time(session_ids, trust_scores, detected_drift_points=None, fname="trust_scores.png"):
    _ensure_results()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(session_ids, trust_scores, color="#2f6f9f", linewidth=1.1, label="Trust score")
    ax.axhline(0.5, color="#6b7280", linestyle="--", linewidth=0.9, label="Decision threshold")
    for point in DRIFT_POINTS:
        ax.axvline(point, color="#b45309", linestyle=":", linewidth=1.0, alpha=0.8)
    if detected_drift_points:
        for point in detected_drift_points:
            ax.axvline(point, color="#15803d", linestyle="--", linewidth=0.9, alpha=0.75)
    ax.set_xlabel("Session id")
    ax.set_ylabel("Trust score")
    ax.set_title("Trust Score Stream with True and Detected Drift Events")
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, fname), dpi=150)
    plt.close(fig)


def plot_eci_over_adaptations(ajr_records, fname="eci_over_time.png"):
    _ensure_results()
    if not ajr_records:
        return
    scores = [ajr["explanation_consistency_index"] for ajr in ajr_records]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(range(1, len(scores) + 1), scores, marker="o", color="#2f6f9f")
    ax.axhline(0.5, color="#b45309", linestyle="--", linewidth=1.0, label="Review threshold")
    ax.set_xlabel("Adaptation event")
    ax.set_ylabel("ECI")
    ax.set_ylim(0, 1.05)
    ax.set_title("Explanation-Consistency Index Across Adaptations")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, fname), dpi=150)
    plt.close(fig)


def plot_metric_comparison(results_dict, metric="f1", fname=None):
    _ensure_results()
    fname = fname or f"comparison_{metric}.png"
    names = list(results_dict.keys())
    values = [results_dict[name][metric] or 0 for name in names]
    colors = ["#9ca3af"] * len(names)
    colors[-1] = "#2f6f9f"
    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(names, values, color=colors)
    ax.bar_label(bars, fmt="%.3f", fontsize=8)
    ax.set_ylim(0, min(1.05, max(values) + 0.15))
    ax.set_ylabel(metric.upper().replace("_", " "))
    ax.set_title(f"Baseline Comparison: {metric.upper().replace('_', ' ')}")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, fname), dpi=150)
    plt.close(fig)

