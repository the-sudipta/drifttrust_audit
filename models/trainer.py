import os

import joblib
import numpy as np
from sklearn.metrics import log_loss

from config import EARLY_STOPPING_PATIENCE, EPOCHS, MODEL_SAVE_DIR
from models.trust_scorer import TemporalMLPTrustScorer


def _binary_log_loss(y_true, trust_scores):
    clipped = np.clip(trust_scores, 1e-6, 1 - 1e-6)
    return float(log_loss(y_true, np.column_stack([1 - clipped, clipped]), labels=[0, 1]))


def train(model, x_train, y_train, x_val, y_val, model_name="temporal_mlp"):
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    best_model = None
    best_val = float("inf")
    patience_left = EARLY_STOPPING_PATIENCE
    train_losses = []
    val_losses = []

    for _epoch in range(EPOCHS):
        model.fit_epoch(x_train, y_train)
        train_loss = _binary_log_loss(y_train, model.predict_proba(x_train))
        val_loss = _binary_log_loss(y_val, model.predict_proba(x_val))
        train_losses.append(train_loss)
        val_losses.append(val_loss)

        if val_loss < best_val - 1e-5:
            best_val = val_loss
            best_model = model.clone()
            patience_left = EARLY_STOPPING_PATIENCE
        else:
            patience_left -= 1
            if patience_left <= 0:
                break

    if best_model is not None:
        model.restore_from(best_model)

    joblib.dump(model, os.path.join(MODEL_SAVE_DIR, f"best_{model_name}.joblib"))
    return model, train_losses, val_losses


def predict_proba(model, x):
    return model.predict_proba(x)


def make_model():
    return TemporalMLPTrustScorer()

