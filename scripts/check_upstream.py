#!/usr/bin/env python3
"""Report upstream changes without replacing the customized skills."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

root=Path(__file__).resolve().parents[1]
baseline=json.loads((root/'upstream.json').read_text())
with urlopen('https://registry.npmjs.org/@slidev/cli/latest',timeout=30) as r:package=json.load(r)
with urlopen(baseline['skillUrl'],timeout=30) as r:sha=hashlib.sha256(r.read()).hexdigest()
result={'baseline':baseline,'current':{'cliVersion':package['version'],'skillSha256':sha},'changed':package['version']!=baseline['cliVersion'] or sha!=baseline['skillSha256'],'next':'Review upstream changes, merge deliberately, test, then issue one new plugin release. User templates are never overwritten.'}
print(json.dumps(result,indent=2))
