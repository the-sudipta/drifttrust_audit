# Reproducibility

## Environment

The verified fallback implementation uses:

- Python 3.13.0,
- NumPy,
- pandas,
- scikit-learn,
- SciPy,
- matplotlib,
- seaborn,
- joblib.

For paper-grade replication, Python 3.10 or 3.11 is recommended if adding
PyTorch, SHAP, and River.

## Smoke Run

```powershell
cd drifttrust_audit
$env:DTA_N_SESSIONS="1600"
$env:DTA_EPOCHS="10"
$env:DTA_INCREMENTAL_EPOCHS="3"
python main.py
```

## Default Run

```powershell
cd drifttrust_audit
python main.py
```

## Outputs

- `data/telemetry.csv`
- `saved_models/best_temporal_mlp.joblib`
- `audit_logs/AJR-*.json`
- `results/ml_metrics.json`
- `results/baseline_metrics.json`
- `results/gov_metrics.json`
- `results/novelty_assessment.json`
- `results/*.png`

## Determinism

The simulator and core experiment use fixed random seeds from `config.py`.
