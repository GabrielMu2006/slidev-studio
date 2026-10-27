#!/usr/bin/env python3
"""Verify an installed snapshot and exercise its bundled tools without a model API."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from release import PLUGIN, tree_hash


def verify(skills, receipt=None):
    skills = Path(skills).resolve()
    expected = json.loads((PLUGIN / 'release.json').read_text(encoding='utf-8'))
    if receipt is not None:
        installed = json.loads(Path(receipt).read_text(encoding='utf-8'))
        if installed.get('version') != expected['version'] or installed.get('skills') != expected['skills']:
            raise ValueError('Installed receipt differs from this checkout; update before verifying')
    for name, sha in expected['skills'].items():
        folder = skills / name
        if not (folder / 'SKILL.md').is_file() or tree_hash(folder) != sha:
            raise ValueError('Missing or modified installed skill: ' + name)
    environment = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    # Run installed paths, never substitute the source checkout's helpers.
    result = subprocess.run([sys.executable, str(skills / 'slidev/scripts/studio.py'), 'list'],
                            check=True, capture_output=True, text=True, encoding='utf-8', timeout=30, env=environment)
    presets = json.loads(result.stdout)
    source = json.loads((PLUGIN / 'skills/slidev/assets/studio/templates.json').read_text(encoding='utf-8'))
    if [p['id'] for p in presets] != [p['id'] for p in source]:
        raise ValueError('Installed preset catalog differs from this checkout')
    subprocess.run([sys.executable, str(skills / 'slidev-template-import/scripts/template_bundle.py'), '--help'],
                   check=True, capture_output=True, text=True, encoding='utf-8', timeout=30, env=environment)
    return {'verified': True, 'version': expected['version'], 'skills': list(expected['skills']),
            'presetCount': len(presets), 'skillsDirectory': str(skills),
            'scope': 'Installed content hashes and helper execution; host discovery/model execution is separate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument('--plugin-root', type=Path, help='Installed plugin root returned by the native host')
    targets.add_argument('--agent', choices=['cursor', 'claude', 'generic'])
    parser.add_argument('--project', type=Path)
    args = parser.parse_args()
    try:
        if args.plugin_root:
            result = verify(args.plugin_root / 'skills')
        else:
            if args.project is None:
                parser.error('--project is required with --agent')
            base = args.project / {'cursor': '.cursor', 'claude': '.claude', 'generic': '.agents'}[args.agent]
            result = verify(base / 'skills', base / 'slidev-studio-install.json')
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
