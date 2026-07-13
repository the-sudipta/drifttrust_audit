import numpy as np
from scipy.stats import kendalltau

from config import ECI_TOP_K, RANDOM_SEED


def compute_eci(attribution_before, attribution_after, feature_names):
    importance_before = np.abs(attribution_before).mean(axis=(0, 1))
    importance_after = np.abs(attribution_after).mean(axis=(0, 1))

    top_before_idx = np.argsort(importance_before)[-ECI_TOP_K:][::-1]
    top_after_idx = np.argsort(importance_after)[-ECI_TOP_K:][::-1]
    top_before = [feature_names[i] for i in top_before_idx]
    top_after = [feature_names[i] for i in top_after_idx]

    set_before = set(top_before)
    set_after = set(top_after)
    jaccard = len(set_before & set_after) / max(len(set_before | set_after), 1)

    rank_before = importance_before.argsort().argsort()
    rank_after = importance_after.argsort().argsort()
    tau, _ = kendalltau(rank_before, rank_after)
    if np.isnan(tau):
        tau = 0.0
    kendall_normalised = (float(tau) + 1.0) / 2.0
    eci = (jaccard + kendall_normalised) / 2.0
    return float(eci), top_before, top_after, float(jaccard), float(kendall_normalised)


def build_canonical_scenarios(x_stream, y_stream, n=60, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    n = min(n, len(x_stream))
    legit = np.where(y_stream == 1)[0]
    attack = np.where(y_stream == 0)[0]

    if len(legit) == 0 or len(attack) == 0:
        chosen = rng.choice(np.arange(len(x_stream)), n, replace=False)
        return x_stream[chosen]

    n_each = min(n // 2, len(legit), len(attack))
    remainder = n - (2 * n_each)
    chosen = np.concatenate(
        [
            rng.choice(legit, n_each, replace=False),
            rng.choice(attack, n_each, replace=False),
        ]
    )
    if remainder > 0:
        remaining = np.setdiff1d(np.arange(len(x_stream)), chosen)
        chosen = np.concatenate([chosen, rng.choice(remaining, remainder, replace=False)])
    return x_stream[chosen]

