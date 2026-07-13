from collections import deque

import numpy as np

from config import (
    ATTRIBUTION_DRIFT_THRESHOLD,
    ERROR_DRIFT_MARGIN,
    ERROR_LONG_WINDOW,
    ERROR_SHORT_WINDOW,
)
from drift.attribution import PerturbationAttributor


class WindowedErrorDetector:
    """ADWIN-inspired detector using short-vs-long error-rate change."""

    def __init__(self):
        self.errors = deque(maxlen=ERROR_LONG_WINDOW)

    def update(self, error):
        self.errors.append(int(error))
        if len(self.errors) < ERROR_LONG_WINDOW:
            return False, 0.0, 0.0

        arr = np.array(self.errors, dtype=float)
        short_rate = float(arr[-ERROR_SHORT_WINDOW:].mean())
        long_rate = float(arr[: -ERROR_SHORT_WINDOW].mean())
        drift = short_rate > long_rate + ERROR_DRIFT_MARGIN
        return drift, short_rate, long_rate

    def reset(self):
        self.errors.clear()


class DriftDetector:
    """Two-signal drift detector: error-rate shift and attribution shift."""

    def __init__(self, model, background_data):
        self.model = model
        self.error_detector = WindowedErrorDetector()
        self.attributor = PerturbationAttributor(model, background_data[: min(250, len(background_data))])
        baseline_values = self.attributor.values(background_data[: min(80, len(background_data))])
        self.baseline_importance = self.attributor.importance(baseline_values)
        self.drift_trigger = None
        self.last_error_rates = {"short": 0.0, "long": 0.0}
        self.last_attribution_shift = 0.0

    def update(self, y_true, trust_score, x_window=None):
        y_pred = int(trust_score >= 0.5)
        error = int(y_true != y_pred)
        error_drift, short_rate, long_rate = self.error_detector.update(error)
        self.last_error_rates = {"short": short_rate, "long": long_rate}
        if error_drift:
            self.drift_trigger = "error_based"
            return True

        if x_window is None:
            return False

        current_values = self.attributor.values(x_window)
        current_importance = self.attributor.importance(current_values)
        baseline = self.baseline_importance / (self.baseline_importance.sum() + 1e-9)
        current = current_importance / (current_importance.sum() + 1e-9)
        max_shift = float(np.max(np.abs(current - baseline)))
        self.last_attribution_shift = max_shift
        if max_shift > ATTRIBUTION_DRIFT_THRESHOLD:
            self.drift_trigger = "attribution_based"
            return True
        return False

    def get_attribution_values(self, x):
        return self.attributor.values(x)

    def refresh_baseline(self, x_reference):
        values = self.attributor.values(x_reference[: min(80, len(x_reference))])
        self.baseline_importance = self.attributor.importance(values)

    def reset_error_state(self):
        self.drift_trigger = None
        self.error_detector.reset()

