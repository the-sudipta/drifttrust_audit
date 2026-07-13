# DriftTrust-Audit

**Audit-ready adaptive Zero Trust access control for concept-drifting enterprise environments**

[![Python Smoke Check](https://github.com/the-sudipta/drifttrust_audit/actions/workflows/python-smoke.yml/badge.svg)](https://github.com/the-sudipta/drifttrust_audit/actions/workflows/python-smoke.yml)
![Research Prototype](https://img.shields.io/badge/status-research%20prototype-226f8f)
![Governance Layer](https://img.shields.io/badge/novelty-AJR%20%2B%20ECI%20%2B%20ISO%2027001-1d8a7a)
![License: MIT](https://img.shields.io/badge/license-MIT-d9902f)

> Adaptive AI security is useful only when its updates can be explained, reviewed, and governed.

DriftTrust-Audit is a research prototype for studying how adaptive AI access-control systems can remain accountable after concept drift. It combines simulated enterprise network telemetry, adaptive trust scoring, drift detection, incremental model updates, and a governance layer that records why each model update occurred.

The core contribution is not only that a trust model can adapt. The central contribution is that each adaptation can be made auditable, explanation-aware, and policy-traceable through structured governance artifacts.

## Interactive Research Showcase

Open [this](https://the-sudipta.github.io/drifttrust_audit/) in a browser to explore a one-page interactive explanation of the project. The page includes:

- a simple story-flow explanation of the research gap,
- an interactive methodology workflow,
- result counters and baseline comparison,
- a generated figure and artifact showcase,
- an Adaptation Justification Record viewer,
- a "Try Yourself" mini-lab where session behavior changes the trust score and audit response,
- a local reference-notes section based only on the Claude/user-provided citation cues.

The page is intentionally written as plain HTML, CSS, and JavaScript so it can be hosted by GitHub Pages or opened locally without a build step.

<table width="100%">
  <tr>
    <td width="33%"><strong>For professors</strong><br>Clear research gap, methodology, novelty, and paper-grade extension path.</td>
    <td width="33%"><strong>For reviewers</strong><br>Transparent evidence of what was implemented, what was measured, and what remains a caveat.</td>
    <td width="33%"><strong>For organizations</strong><br>Shows why adaptive access control needs audit records, not only trust scores.</td>
  </tr>
</table>

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
├── REFERENCES.md
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
├── assets/
│   └── showcase/
│       ├── trust_scores.png
│       ├── eci_over_time.png
│       ├── comparison_f1.png
│       ├── comparison_balanced_accuracy.png
│       └── logs/sample_ajr.json
└── informations/
    ├── IMPLEMENTATION_STATUS.md
    ├── GOVERNANCE.md
    ├── REFERENCE_NOTES.md
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

A verified smoke run produced the committed showcase artifacts below. The values in this table match the JSON files copied into `assets/showcase/` for the website.

<table width="100%">
  <thead>
    <tr>
      <th align="left">Evidence Category</th>
      <th align="left">Metric</th>
      <th align="right">Value</th>
      <th align="left">Why it matters</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Adaptation</td><td>Adaptation events</td><td align="right">14</td><td>Shows the system actually encountered drift and adapted.</td></tr>
    <tr><td>Auditability</td><td>AJR completeness rate</td><td align="right">1.0000</td><td>Every adaptation produced a complete audit artifact.</td></tr>
    <tr><td>Governance</td><td>Policy conformance rate</td><td align="right">1.0000</td><td>All showcased smoke-run adaptations passed automated ISO-mapped checks.</td></tr>
    <tr><td>Explainability</td><td>ECI mean</td><td align="right">0.9206</td><td>Model reasoning stayed mostly consistent after adaptation.</td></tr>
    <tr><td>Explainability</td><td>ECI minimum</td><td align="right">0.7424</td><td>Even the weakest adaptation remained above the review threshold.</td></tr>
    <tr><td>Review workload</td><td>ECI flagged rate</td><td align="right">0.0000</td><td>No smoke-run adaptations required explanation-consistency review.</td></tr>
    <tr><td>ML performance</td><td>DriftTrust-Audit F1</td><td align="right">0.6999</td><td>Trust scoring remains functional while governance evidence is added.</td></tr>
    <tr><td>ML performance</td><td>Balanced accuracy</td><td align="right">0.5478</td><td>Useful for judging class imbalance in simulated telemetry.</td></tr>
    <tr><td>Drift response</td><td>Mean time to detect</td><td align="right">43.33 sessions</td><td>Measures how quickly drift is detected after injected changes.</td></tr>
  </tbody>
</table>

Generated runtime artifacts include:

- `audit_logs/AJR-*.json`,
- `results/ml_metrics.json`,
- `results/baseline_metrics.json`,
- `results/gov_metrics.json`,
- `results/novelty_assessment.json`,
- `results/trust_scores.png`,
- `results/eci_over_time.png`,
- `results/comparison_f1.png`,
- `results/comparison_balanced_accuracy.png`.

The raw `results/` and `audit_logs/` folders are intentionally ignored by Git so the repository stays clean. Curated copies for the public showcase are committed under `assets/showcase/`.

## Result Artifact Showcase

The website now includes a dedicated evidence gallery. These committed files are the public-facing proof pack:

<table width="100%">
  <thead>
    <tr>
      <th align="left">Showcase artifact</th>
      <th align="left">What it shows</th>
      <th align="left">Why it matters for the research claim</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>assets/showcase/trust_scores.png</code></td><td>Trust-score movement across the session stream.</td><td>Makes the core gap visible: adaptive Zero Trust changes over time, so adaptation needs reviewable evidence.</td></tr>
    <tr><td><code>assets/showcase/eci_over_time.png</code></td><td>Explanation-Consistency Index values after adaptation events.</td><td>Shows the novelty beyond ordinary ML metrics: reasoning stability is measured after the model learns.</td></tr>
    <tr><td><code>assets/showcase/comparison_f1.png</code></td><td>F1 comparison against static threshold, RBAC, ABAC, and logistic baseline.</td><td>Keeps the benchmark honest while showing that baselines do not provide AJR/ECI/ISO governance evidence.</td></tr>
    <tr><td><code>assets/showcase/comparison_balanced_accuracy.png</code></td><td>Imbalance-aware baseline comparison.</td><td>Helps reviewers understand model behavior under uneven access-control classes.</td></tr>
    <tr><td><code>assets/showcase/gov_metrics.json</code></td><td>AJR completeness, policy conformance, ECI summary, and review flags.</td><td>Directly supports the claim that the governance layer is operational.</td></tr>
    <tr><td><code>assets/showcase/logs/sample_ajr.json</code></td><td>One generated Adaptation Justification Record.</td><td>Shows the actual audit receipt: drift trigger, drifted feature, trust-score delta, ECI, and ISO checks.</td></tr>
  </tbody>
</table>

## Verified References

The verified bibliography supplied for this project is now included in [REFERENCES.md](REFERENCES.md), with a mirrored copy in [informations/REFERENCE_NOTES.md](informations/REFERENCE_NOTES.md).

The list preserves the supplied status labels:

- verified references,
- arXiv preprints,
- references that still need manual checking before final paper submission,
- one excluded original proposal reference documented for traceability.

Key clickable references include:

<table width="100%">
  <thead>
    <tr>
      <th align="left">Ref</th>
      <th align="left">Source</th>
      <th align="left">Role in DriftTrust-Audit</th>
      <th align="left">Link</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>R1</td><td>NIST SP 800-207</td><td>Zero Trust Architecture foundation.</td><td><a href="https://doi.org/10.6028/NIST.SP.800-207">DOI</a></td></tr>
    <tr><td>R2</td><td>Zero Trust Architecture survey</td><td>Broad ZTA research landscape.</td><td><a href="https://doi.org/10.1109/ACCESS.2022.3174679">DOI</a></td></tr>
    <tr><td>R4</td><td>Transcend, USENIX Security 2017</td><td>Security concept-drift detection baseline literature.</td><td><a href="https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/jordaney">USENIX</a></td></tr>
    <tr><td>R5</td><td>INSOMNIA, AISec 2021</td><td>Concept-drift robustness in intrusion detection.</td><td><a href="https://doi.org/10.1145/3474369.3486864">DOI</a></td></tr>
    <tr><td>R6</td><td>METANOIA</td><td>Lifelong intrusion detection under concept drift.</td><td><a href="https://arxiv.org/abs/2501.00438">arXiv</a></td></tr>
    <tr><td>R8</td><td>SHAP foundation paper</td><td>Explainability basis for attribution-driven drift reasoning.</td><td><a href="https://proceedings.neurips.cc/paper_files/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf">Paper</a></td></tr>
    <tr><td>R11</td><td>DriftGuard</td><td>SHAP attribution shifts for drift root-cause analysis.</td><td><a href="https://arxiv.org/abs/2601.08928">arXiv</a></td></tr>
    <tr><td>R16</td><td>Continual learning for ZTA patent</td><td>Prior art showing Layer 1+2 alone are not the novelty.</td><td><a href="https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12549572">USPTO PDF</a></td></tr>
    <tr><td>R17</td><td>ISO/IEC 27001:2022</td><td>Governance basis for AJR policy-control mapping.</td><td><a href="https://www.iso.org/standard/27001">ISO</a></td></tr>
  </tbody>
</table>

The project website also includes a clickable reference section for the most important sources. The full list should still be re-checked before final journal submission, especially entries marked "needs verification" or "preprint."

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

<table width="100%">
  <thead>
    <tr>
      <th align="left">Research Strength</th>
      <th align="left">What DriftTrust-Audit already provides</th>
      <th align="left">PhD-scale expansion</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Technical feasibility</td><td>Runnable prototype with simulation, adaptation, AJR, ECI, and policy checks.</td><td>Upgrade to LSTM/GRU, SHAP, River ADWIN, and real-world log studies.</td></tr>
    <tr><td>Novel governance angle</td><td>Adaptation is evaluated as an auditable event, not only a model update.</td><td>Formal AJR schema, reviewer studies, compliance automation, and human review workflows.</td></tr>
    <tr><td>Publication potential</td><td>Clear gap between adaptive security ML and information security management auditability.</td><td>Journal-ready ablations, multi-seed statistics, and cross-domain case studies.</td></tr>
  </tbody>
</table>

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
