import numpy as np

from config import FEATURE_NAMES


class PerturbationAttributor:
    """Model-agnostic feature attribution for temporal windows.

    For each feature, replace that feature across all time steps with the
    background mean and measure the absolute trust-score change.
    """

    method_name = "perturbation_attribution"

    def __init__(self, model, background_data):
        self.model = model
        self.background_mean = background_data.mean(axis=(0, 1))

    def values(self, x):
        base = self.model.predict_proba(x)
        n, seq_len, n_features = x.shape
        values = np.zeros((n, seq_len, n_features), dtype=np.float32)

        for feature_idx in range(n_features):
            perturbed = x.copy()
            perturbed[:, :, feature_idx] = self.background_mean[feature_idx]
            changed = self.model.predict_proba(perturbed)
            delta = np.abs(base - changed)
            values[:, :, feature_idx] = (delta / max(seq_len, 1))[:, None]

        return values

    @staticmethod
    def importance(attribution_values):
        return np.abs(attribution_values).mean(axis=(0, 1))


def top_features(attribution_values, k):
    importance = PerturbationAttributor.importance(attribution_values)
    idx = np.argsort(importance)[-k:][::-1]
    return [FEATURE_NAMES[i] for i in idx], importance

