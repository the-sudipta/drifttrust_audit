# DriftTrust-Audit

**Audit-ready adaptive Zero Trust access control for concept-drifting enterprise environments**

DriftTrust-Audit is a research prototype for studying how adaptive AI access-control systems can remain accountable after concept drift. It combines simulated enterprise network telemetry, adaptive trust scoring, drift detection, incremental model updates, and a governance layer that records why each model update occurred.

The core contribution is not only that a trust model can adapt. The central contribution is that each adaptation can be made auditable, explanation-aware, and policy-traceable through structured governance artifacts.

## Interactive Research Showcase

Open [index.html](index.html) in a browser to explore a one-page interactive explanation of the project. The page includes:

- a simple story-flow explanation of the research gap,
- an interactive methodology workflow,
- result counters and baseline comparison,
- an Adaptation Justification Record viewer,
- a "Try Yourself" mini-lab where session behavior changes the trust score and audit response.

The page is intentionally written as plain HTML, CSS, and JavaScript so it can be hosted by GitHub Pages or opened locally without a build step.

## Why This Research Matters

Modern Zero Trust Architecture depends on continuous, risk-based access decisions. A user, device, session, or resource request is not trusted once and forgotten; it is continuously evaluated. Machine learning can support this by generating a trust score from behavioral telemetry.

However, enterprise behavior changes:

- employees move roles or departments,
- remote-work patterns shift,
- attack strategies evolve,
- privileged resource access changes over time,
- network baselines drift after organizational or infrastructure changes.

This is concept drift. Adaptive models can respond to drift, but adaptation introduces a governance problem:

> If an AI trust model updates itself, how can an auditor, security officer, professor, regulator, or organization owner verify why that update happened and whether it remained policy-compliant?

Most adaptive security ML work optimizes performance metrics such as accuracy, F1, or latency. DriftTrust-Audit focuses on the missing accountability layer: adaptation evidence.

## Research Gap

Existing work in concept drift, continual learning, explainable AI, and Zero Trust access control provides important building blocks. But the following gap remains under-addressed:

**Adaptive trust models are usually evaluated as prediction systems, not as auditable governance systems.**

That means a model may adapt successfully while still leaving unanswered questions:

- What triggered the update?
- Which feature or behavior drifted?
- Did the trust score become more permissive for sensitive resources?
- Did the model's explanation remain consistent after adaptation?
- Can the update be mapped to security-management controls?
- Can an auditor inspect a durable record of the decision?

DriftTrust-Audit converts those questions into executable methodology.

## Novel Contributions

### 1. Adaptation Justification Record

An Adaptation Justification Record (AJR) is generated for every model adaptation event. Each AJR is stored as an individual JSON audit artifact and includes:

- adaptation identifier,
- timestamp,
- drift trigger,
- drifted feature,
- attribution method,
- attribution shift magnitude,
- trust score before adaptation,
- trust score after adaptation,
- model-update loss trajectory,
- top explanatory features after adaptation,
- resource sensitivity context,
- ISO/IEC 27001:2022 policy checks,
- overall policy status,
- Explanation-Consistency Index.

This makes adaptation inspectable after the fact.

### 2. Explanation-Consistency Index

The Explanation-Consistency Index (ECI) measures whether the model's reasoning remains stable after adaptation. It compares feature-attribution rankings before and after adaptation using:

- top-k feature overlap,
- Kendall rank consistency.

Low ECI values indicate that the model may have changed its reasoning in a way that deserves human review, even if predictive performance remains acceptable.

### 3. ISO/IEC 27001 Mapping

Each AJR includes policy checks mapped to ISO/IEC 27001:2022 controls:

- A.5.15: Access control,
- A.8.16: Monitoring activities,
- A.5.36: Compliance with policies, rules, and standards.

This positions the project for information security management research, not only machine-learning benchmarking.

## System Architecture

```text
Simulated Enterprise Telemetry
        |
        v
Temporal Feature Windows
        |
        v
Layer 1: Trust Scorer
        |
        v
Layer 2: Drift Detection + Incremental Adaptation
        |
        v
Layer 3: Adaptation Governance
        |
        +--> AJR JSON audit logs
        +--> ECI explanation-consistency metrics
        +--> ISO/IEC 27001 policy checks
        +--> Result plots and evaluation metrics
```

## Repository Structure

```text
.
├── index.html
├── main.py
├── config.py
├── data/
│   ├── simulate.py
│   └── features.py
├── models/
│   ├── trust_scorer.py
│   └── trainer.py
├── drift/
│   ├── attribution.py
│   ├── detector.py
│   └── adapter.py
├── governance/
│   ├── ajr.py
│   ├── eci.py
│   └── policy.py
├── evaluation/
│   ├── baselines.py
│   ├── metrics.py
│   ├── governance_metrics.py
│   └── plots.py
└── informations/
    ├── IMPLEMENTATION_STATUS.md
    ├── GOVERNANCE.md
    ├── ROADMAP.md
    └── SECURITY.md
```

## Quick Start

Use Python 3.10 or later. The verified local fallback path currently runs with common scientific Python packages.

```powershell
python -m pip install -r requirements.txt
python main.py
```

For a faster smoke run:

```powershell
$env:DTA_N_SESSIONS="1600"
$env:DTA_EPOCHS="10"
$env:DTA_INCREMENTAL_EPOCHS="3"
python main.py
```

## Reproduced Smoke-Run Evidence

A verified smoke run produced:

| Metric | Value |
|---|---:|
| Adaptation events | 18 |
| AJR completeness rate | 1.0000 |
| Policy conformance rate | 0.9444 |
| ECI mean | 0.9106 |
| ECI minimum | 0.7424 |
| ECI flagged rate | 0.0000 |
| DriftTrust-Audit F1 | 0.7608 |
| Balanced accuracy | 0.6067 |
| Mean time to detect | 46.67 sessions |

Generated artifacts include:

- `audit_logs/AJR-*.json`,
- `results/ml_metrics.json`,
- `results/baseline_metrics.json`,
- `results/gov_metrics.json`,
- `results/novelty_assessment.json`,
- `results/trust_scores.png`,
- `results/eci_over_time.png`,
- `results/comparison_f1.png`,
- `results/comparison_balanced_accuracy.png`.

Generated artifacts are intentionally ignored by Git so the repository stays clean.

## Important Research Caveat

The current verified implementation uses:

- scikit-learn temporal MLP trust scoring,
- windowed error-rate drift detection,
- perturbation-based attribution.

This was done because the local verification environment uses Python 3.13 and does not currently include PyTorch, SHAP, or River. The code is still sufficient to validate the core novelty: audit-ready adaptation governance.

For paper-grade experiments, the same architecture should be upgraded to:

- PyTorch LSTM/GRU trust scorer,
- SHAP DeepExplainer or a comparable attribution method,
- River ADWIN for online drift detection,
- larger experimental runs across multiple random seeds,
- formal ablation studies for AJR, ECI, and policy checks.

## Why This Is PhD-Fundable

DriftTrust-Audit sits at the intersection of:

- Zero Trust Architecture,
- adaptive cyber-defense,
- trustworthy machine learning,
- explainable AI,
- security governance,
- compliance automation,
- information security management systems.

This makes it attractive for supervisors and assistant professors looking for research that is technically implementable, publishable, and institutionally relevant. The work can mature into a PhD agenda around one core question:

> How can adaptive AI security systems remain accountable, explainable, and policy-conformant while learning from changing operational environments?

Possible PhD extensions include:

- formal AJR schema design and validation,
- human-in-the-loop review workflows for low-ECI adaptations,
- adversarial drift and model-poisoning scenarios,
- real-world enterprise log integration,
- ISO 27001, SOC 2, NIST SP 800-207, and AI governance mapping,
- comparative studies across healthcare, banking, education, and government systems,
- multi-agent or federated adaptive trust governance,
- longitudinal deployment simulation with auditor feedback.

## Repository Roadmap

- Build PyTorch LSTM/GRU model variant.
- Add SHAP-based attribution backend.
- Add River ADWIN backend.
- Run full 10,000+ session experiments.
- Add multi-seed statistical reporting.
- Expand baselines: RBAC, ABAC, static threshold, non-governed DriftTrust.
- Add ablation experiments for AJR, ECI, and policy checks.
- Prepare manuscript-ready tables and figures.
- Package a professor-facing research dashboard.

## Intended Audience

This repository is intended for:

- information security management researchers,
- cybersecurity and Zero Trust researchers,
- assistant professors seeking fundable applied security projects,
- PhD supervisors evaluating research feasibility,
- graduate students building publishable security AI prototypes,
- organization owners interested in accountable adaptive security systems.

## Citation

If you use this repository or build on the DriftTrust-Audit methodology, please cite it using the metadata in [CITATION.cff](CITATION.cff).

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
