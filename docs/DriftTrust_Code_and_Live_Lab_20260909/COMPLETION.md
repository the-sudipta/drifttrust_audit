# Completion and verification — 9 September 2026

Primary website: https://the-sudipta.github.io/drifttrust_audit/
Actual browser lab: https://the-sudipta.github.io/drifttrust_audit/lab.html
Interactive guide: https://the-sudipta.github.io/drifttrust_audit/guide.html

The primary lab executes the unchanged scientific engine in a browser Web Worker with IndexedDB. No ChatGPT-hosted API is required. Full dynamic explanations now cover input attributes, score arithmetic, model settings, detector eligibility, policy checks, records, charts and code paths.

Package: completed teaching brief; 26-page Word dossier and rendered PDF; offline HTML with 9 modules, 9 activities and 27 review cards. qa/fieldbook.template.html is a complete working copy; edit qa/fieldbook.source.html before regenerating it. The interface reference includes 46 control/display groups, all 12 features, 13 configuration fields, all AJR fields and explanations of 9 scientific figures.

Verification performed:
- Seven scientific engine tests passed, including sklearn prediction parity to 1e-10 and rejected-model integrity.
- Offline file browser tests passed across all activities, boundary cases, reset, quizzes, review, glossary and exports. No unexpected network requests or runtime errors.
- Word exported with Microsoft Word after the canonical LibreOffice renderer was unavailable; all 26 rendered pages visually inspected. Final renders are in qa/word_final.
- Public GitHub Pages browser tests passed at 2026-09-09T13:07:02.724Z against source commit 0846eff692b1bfda6a47ed215228e9f9a25a1b1a.
- Public replay: audit-only 1280 flows, 5 candidates, 5 activated; gated 1280 flows, 7 candidates, 4 activated, 3 discarded.
- Actual example outputs, explanation arithmetic, pause, labelled/unlabelled CSV, invalid input atomic rejection, hash verification/export, local reload persistence, browser-profile isolation and desktop/tablet/phone overflow checked.
- GitHub Pages, public-data engine/API and Python smoke workflows all passed on the implementation commit.

Acceptance/rejection refers to trained candidate model versions. It does not allow or block people, packets or network access. Candidate 7 has ECI about 0.94697 but anchor loss rises by 0.07899, exceeding 0.05: gated policy retains the previous weights.

Functional evidence is point-in-time. The score is uncalibrated; browser-controlled audit hashes alone do not establish independently trusted evidence. The reported empirical results and original shared engine remain unchanged by this interface/hosting migration.
