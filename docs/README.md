# Project documentation and learning materials

This directory brings the original workspace's project documents into the
repository. The deployed website remains at
[GitHub Pages](https://the-sudipta.github.io/drifttrust_audit/).

## Current implementation and evidence

- [Public-data research report](PUBLIC_DATA_RESEARCH_REPORT.md): measured
  RT-IoT2022 experiment, methods, results and figure captions. The canonical
  website copy is [the research report](../assets/research/RESEARCH_REPORT.md).
- [Interactive learning package](DriftTrust_Code_and_Live_Lab_20260909/learning_module.html):
  download and open offline, or use the [published guide](../guide.html).
- [Word dossier](DriftTrust_Code_and_Live_Lab_20260909/docs/DriftTrust_learning_dossier.docx),
  [rendered PDF](DriftTrust_Code_and_Live_Lab_20260909/qa/word_final/dossier.pdf)
  and [teaching brief](DriftTrust_Code_and_Live_Lab_20260909/docs/DriftTrust_learning_module_instructions.md).
- [Completion and verification record](DriftTrust_Code_and_Live_Lab_20260909/COMPLETION.md).

## Original planning documents

The implementation guide, methodology, reproducibility notes, reference list,
funding prospectus and two slide decks are retained as project source material.
They include earlier synthetic-prototype descriptions and proposals. Their
LSTM/GRU, SHAP, ADWIN or enterprise-integration proposals do not establish that
the current public-data lab implements those capabilities. Use the current
research report, runtime source and deployment guide for implemented behavior.

## Rebuilding the learning package

From `docs/DriftTrust_Code_and_Live_Lab_20260909`, with Python and `python-docx`
available:

```sh
python qa/build_dossier.py
python qa/build_fieldbook.py
```

The builders use `qa/content.json`, `qa/interface-reference.json` and
`qa/fieldbook.source.html`. The fieldbook builder locates the repository's
published model, examples and audit record, and verifies the Word source before
generating `learning_module.html` and the complete `qa/fieldbook.template.html`.
Publishing a regenerated guide requires copying it to the repository's
`guide.html` and updating the downloadable dossier assets after render review.

For browser QA, make Playwright available as `playwright` or set
`PLAYWRIGHT_MODULE` to its installed module path. Optionally set
`BROWSER_EXECUTABLE` to a browser binary, then run:

```sh
node qa/test_fieldbook.cjs
```

`qa/word_final` contains the final 26-page document render and contact sheets.
`qa/word_render` is an earlier 16-page render retained as historical QA evidence.
`qa/migrate_guide.py` is the already-applied, one-time migration script: do not
rerun it against the current content. The exported study notes are automated
test fixtures, not a learner's submitted work. Verification JSON and screenshots
record completed checks, not continuous monitoring.

The private conversation export remains excluded by the existing `.gitignore`.
