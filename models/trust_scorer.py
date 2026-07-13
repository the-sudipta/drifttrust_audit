import copy

import numpy as np
from sklearn.neural_network import MLPClassifier

from config import HIDDEN_SIZE, LEARNING_RATE, RANDOM_SEED


class TemporalMLPTrustScorer:
    """Temporal trust scorer over flattened session windows.

    The public output is a trust score: P(label=1), where label 1 means
    legitimate access and label 0 means attack.
    """

    def __init__(self, learning_rate=LEARNING_RATE, hidden_size=HIDDEN_SIZE, random_state=RANDOM_SEED):
        self.learning_rate = learning_rate
        self.hidden_size = hidden_size
        self.random_state = random_state
        self.estimator = MLPClassifier(
            hidden_layer_sizes=(hidden_size, max(16, hidden_size // 2)),
            activation="relu",
            solver="adam",
            alpha=0.0005,
            batch_size="auto",
            learning_rate_init=learning_rate,
            max_iter=1,
            warm_start=True,
            random_state=random_state,
        )
        self.classes_ = np.array([0, 1], dtype=np.int64)
        self._is_fitted = False

    @staticmethod
    def _flatten(x):
        return x.reshape(x.shape[0], -1)

    def fit_epoch(self, x, y):
        x_flat = self._flatten(x)
        if not self._is_fitted:
            self.estimator.partial_fit(x_flat, y, classes=self.classes_)
            self._is_fitted = True
        else:
            self.estimator.partial_fit(x_flat, y)

    def partial_fit(self, x, y, epochs=1):
        for _ in range(epochs):
            self.fit_epoch(x, y)

    def predict_proba(self, x):
        if not self._is_fitted:
            raise RuntimeError("Trust scorer is not fitted.")
        probs = self.estimator.predict_proba(self._flatten(x))
        class_to_idx = {cls: idx for idx, cls in enumerate(self.estimator.classes_)}
        return probs[:, class_to_idx[1]]

    def clone(self):
        return copy.deepcopy(self)

    def restore_from(self, other):
        self.estimator = copy.deepcopy(other.estimator)
        self._is_fitted = other._is_fitted

