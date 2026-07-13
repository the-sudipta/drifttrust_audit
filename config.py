import os


def _env_int(name, default):
    return int(os.getenv(name, str(default)))


def _env_float(name, default):
    return float(os.getenv(name, str(default)))


RANDOM_SEED = _env_int("DTA_RANDOM_SEED", 42)

# Data simulation
N_SESSIONS = _env_int("DTA_N_SESSIONS", 10_000)
N_FEATURES = 11
DRIFT_POINTS = [
    max(100, int(N_SESSIONS * 0.20)),
    max(200, int(N_SESSIONS * 0.50)),
    max(300, int(N_SESSIONS * 0.75)),
]
DRIFT_TYPES = ["gradual", "abrupt", "recurring"]

FEATURE_NAMES = [
    "session_duration_s",
    "auth_frequency_per_hr",
    "geo_displacement_km",
    "device_posture_score",
    "payload_size_anomaly",
    "mfa_timing_gap_s",
    "port_utilisation_entropy",
    "concurrent_sessions",
    "resource_sensitivity_level",
    "time_of_day_discrepancy",
    "packet_retransmission_rate",
]

# Model architecture/training
SEQUENCE_LENGTH = _env_int("DTA_SEQUENCE_LENGTH", 20)
HIDDEN_SIZE = _env_int("DTA_HIDDEN_SIZE", 64)
DROPOUT = _env_float("DTA_DROPOUT", 0.15)
TRUST_THRESHOLD = _env_float("DTA_TRUST_THRESHOLD", 0.5)
BATCH_SIZE = _env_int("DTA_BATCH_SIZE", 64)
EPOCHS = _env_int("DTA_EPOCHS", 24)
LEARNING_RATE = _env_float("DTA_LEARNING_RATE", 0.001)
EARLY_STOPPING_PATIENCE = _env_int("DTA_PATIENCE", 6)

# Initial model is trained before the first injected drift, then the rest is
# treated as an operational stream. This makes drift detection measurable.
VALIDATION_SESSIONS = _env_int("DTA_VALIDATION_SESSIONS", max(120, N_SESSIONS // 20))

# Drift detection
ERROR_SHORT_WINDOW = _env_int("DTA_ERROR_SHORT_WINDOW", 40)
ERROR_LONG_WINDOW = _env_int("DTA_ERROR_LONG_WINDOW", 160)
ERROR_DRIFT_MARGIN = _env_float("DTA_ERROR_DRIFT_MARGIN", 0.08)
ATTRIBUTION_DRIFT_THRESHOLD = _env_float("DTA_ATTRIBUTION_DRIFT_THRESHOLD", 0.18)
CHECK_ATTRIBUTION_EVERY = _env_int("DTA_CHECK_ATTRIBUTION_EVERY", 25)

# Continual learning
INCREMENTAL_EPOCHS = _env_int("DTA_INCREMENTAL_EPOCHS", 5)
INCREMENTAL_LR = _env_float("DTA_INCREMENTAL_LR", 0.0005)
REPLAY_BUFFER_SIZE = _env_int("DTA_REPLAY_BUFFER_SIZE", 500)
ADAPTATION_WINDOW = _env_int("DTA_ADAPTATION_WINDOW", 180)
MIN_SESSIONS_BETWEEN_UPDATES = _env_int("DTA_MIN_UPDATE_GAP", 30)

# Governance
ECI_TOP_K = _env_int("DTA_ECI_TOP_K", 5)
ECI_THRESHOLD = _env_float("DTA_ECI_THRESHOLD", 0.5)
HIGH_SENSITIVITY_RESOURCES = ["finance_db", "hr_records", "root_access"]

# Paths
DATA_DIR = "data"
AJR_LOG_DIR = "audit_logs"
MODEL_SAVE_DIR = "saved_models"
RESULTS_DIR = "results"

