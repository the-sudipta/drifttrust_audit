# Contributing

Thank you for your interest in DriftTrust-Audit.

This repository is a research prototype, so contributions should preserve both
software quality and research validity.

## Useful Contribution Areas

- PyTorch LSTM/GRU implementation.
- SHAP attribution backend.
- River ADWIN drift detector backend.
- Stronger RBAC, ABAC, and static-threshold baselines.
- Multi-seed experiment runner.
- Ablation studies for AJR, ECI, and ISO policy checks.
- Manuscript-ready tables and plots.
- Documentation for security-management and compliance audiences.

## Development Workflow

1. Create a feature branch.
2. Keep changes focused.
3. Run at least:

```powershell
cd drifttrust_audit
python -m compileall .
```

4. For behavior changes, run a smoke experiment:

```powershell
$env:DTA_N_SESSIONS="1600"
$env:DTA_EPOCHS="10"
$env:DTA_INCREMENTAL_EPOCHS="3"
python main.py
```

5. Include a short explanation of research impact in the pull request.

## Research Integrity

Please do not overstate results. If a change improves governance evidence but
not predictive performance, say that clearly. If a result depends on simulated
data, keep that limitation visible.

## Commit messages

Every new commit must have a meaningful emoji, a space, a colon, another space,
and a descriptive title:

```text
📚 : Publish complete research documentation and learning materials
```

Choose the emoji for the change: ✨ for a feature, 🐛 for a fix, 📚 for research
documentation, 🧪 for tests, 🚀 for deployment, or 🔧 for configuration.

After a blank line, provide a detailed commit body covering:

- The problem or purpose of the change.
- The files or components changed and the resulting behavior.
- Relevant research implications, provenance and compatibility decisions.
- Validation actually performed and its results; state when checks were not run.
- Material limitations or follow-up work, when applicable.

Do not claim tests passed unless they ran. For multiline messages, write the
complete UTF-8 message to a file and use `git commit --file <message-file>`.
This convention applies to new commits; changing already published history
requires a separate explicit request.
