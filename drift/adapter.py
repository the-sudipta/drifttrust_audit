from collections import deque

import numpy as np
from sklearn.metrics import log_loss

from config import INCREMENTAL_EPOCHS, REPLAY_BUFFER_SIZE


class ContinualAdapter:
    """Incremental adaptation with experience replay."""

    def __init__(self, model):
        self.model = model
        self.buffer = deque(maxlen=REPLAY_BUFFER_SIZE)
        self.update_count = 0

    def add_to_buffer(self, x_batch, y_batch):
        for idx in range(len(x_batch)):
            self.buffer.append((x_batch[idx], int(y_batch[idx])))

    def update(self, x_new, y_new):
        if len(self.buffer):
            n_replay = min(len(self.buffer), len(x_new) * 2)
            idx = np.random.default_rng(1000 + self.update_count).choice(len(self.buffer), n_replay, replace=False)
            x_replay = np.array([self.buffer[i][0] for i in idx])
            y_replay = np.array([self.buffer[i][1] for i in idx])
            x_combined = np.concatenate([x_new, x_replay], axis=0)
            y_combined = np.concatenate([y_new, y_replay], axis=0)
        else:
            x_combined = x_new
            y_combined = y_new

        losses = []
        for _ in range(INCREMENTAL_EPOCHS):
            self.model.fit_epoch(x_combined, y_combined)
            probs = np.clip(self.model.predict_proba(x_combined), 1e-6, 1 - 1e-6)
            losses.append(float(log_loss(y_combined, np.column_stack([1 - probs, probs]), labels=[0, 1])))

        self.add_to_buffer(x_new, y_new)
        self.update_count += 1
        return losses

