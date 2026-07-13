import numpy as np
from sklearn.preprocessing import StandardScaler

from config import DRIFT_POINTS, FEATURE_NAMES, SEQUENCE_LENGTH, VALIDATION_SESSIONS


def create_windows(df, seq_len=SEQUENCE_LENGTH):
    x_raw = df[FEATURE_NAMES].to_numpy(dtype=np.float32)
    y_raw = df["label"].to_numpy(dtype=np.int64)
    meta_cols = df[["session_id", "drift_type", "resource_tag"]].reset_index(drop=True)

    n_windows = len(df) - seq_len + 1
    if n_windows <= 0:
        raise ValueError("Not enough sessions to create temporal windows.")

    x_windows = np.zeros((n_windows, seq_len, len(FEATURE_NAMES)), dtype=np.float32)
    y_windows = np.zeros(n_windows, dtype=np.int64)

    for i in range(n_windows):
        last = i + seq_len - 1
        x_windows[i] = x_raw[i : i + seq_len]
        y_windows[i] = y_raw[last]

    meta = meta_cols.iloc[seq_len - 1 :].reset_index(drop=True)
    return x_windows, y_windows, meta


def split_pre_drift_stream(x, y, meta):
    first_drift = DRIFT_POINTS[0]
    train_mask = meta["session_id"] < first_drift
    train_indices = np.where(train_mask.to_numpy())[0]
    if len(train_indices) < 80:
        raise ValueError("Pre-drift training segment is too small. Increase N_SESSIONS.")

    train_end = train_indices[-1] + 1
    val_count = min(VALIDATION_SESSIONS, max(40, train_end // 4))
    val_start = max(1, train_end - val_count)

    x_train, y_train, m_train = x[:val_start], y[:val_start], meta.iloc[:val_start]
    x_val, y_val, m_val = x[val_start:train_end], y[val_start:train_end], meta.iloc[val_start:train_end]
    x_stream, y_stream, m_stream = x[train_end:], y[train_end:], meta.iloc[train_end:]

    if len(np.unique(y_train)) < 2:
        raise ValueError("Training split contains one class only; adjust simulation parameters.")

    return x_train, y_train, m_train, x_val, y_val, m_val, x_stream, y_stream, m_stream


def normalise_stream(x_train, x_val, x_stream):
    n_train, seq_len, n_features = x_train.shape
    scaler = StandardScaler()

    x_train_2d = x_train.reshape(-1, n_features)
    scaler.fit(x_train_2d)

    def transform(arr):
        return scaler.transform(arr.reshape(-1, n_features)).reshape(arr.shape)

    return transform(x_train), transform(x_val), transform(x_stream), scaler

