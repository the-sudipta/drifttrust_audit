from pathlib import Path
import json
from docx import Document
R=Path(__file__).resolve().parents[1]
# Support a normal repository checkout and the original sibling docs layout.
REPO=next((p for p in [*R.parents, R.parents[1]/'drifttrust_audit']
           if (p/'assets/research/model.json').is_file()), None)
if REPO is None:
    raise FileNotFoundError('Cannot locate assets/research/model.json above this package.')
C=json.loads((R/'qa/content.json').read_text(encoding='utf-8'))
read='\n'.join(p.text for p in Document(R/'docs/DriftTrust_learning_dossier.docx').paragraphs)
assert all(all(s in read for s in m['formal']) for m in C['modules'])
B=json.loads((REPO/'assets/research/model.json').read_text());E=json.loads((REPO/'assets/research/examples.json').read_text())
A=json.loads((REPO/'assets/research/audit_records.json').read_text())[0]
packed={'course':C,'bundle':{k:B[k] for k in ['features','mean','scale','model']},'examples':E,'record':A}
template=(R/'qa/fieldbook.source.html').read_text(encoding='utf-8')
html=template.replace('/*DATA_PLACEHOLDER*/',json.dumps(packed,ensure_ascii=False).replace('</','<\\/'))
(R/'learning_module.html').write_text(html,encoding='utf-8')
(R/'qa/fieldbook.template.html').write_text(html,encoding='utf-8')
print('Standalone fieldbook authored from reconciled dossier:',(R/'learning_module.html').stat().st_size,'bytes')
