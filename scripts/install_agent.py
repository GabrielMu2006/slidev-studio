#!/usr/bin/env python3
"""Install/update the skills compatibility bundle; this does not register a native plugin."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
from release import PLUGIN,tree_hash,validate

def install(project,agent):
    validate();project=Path(project).resolve();base=project/{'cursor':'.cursor','claude':'.claude','generic':'.agents'}[agent]
    if not base.resolve().is_relative_to(project):raise ValueError('Agent directory escapes project')
    destination=base/'skills';receipt=base/'slidev-studio-install.json'
    release=json.loads((PLUGIN/'release.json').read_text());previous=json.loads(receipt.read_text()) if receipt.exists() else None
    names=list(release['skills'])
    for name in names:
        target=destination/name
        if not target.resolve().is_relative_to(project):raise ValueError('Skill path escapes project')
        if target.exists():
            expected=previous['skills'].get(name) if previous else release['skills'][name]
            if tree_hash(target)!=expected:raise ValueError('Local skill differs; merge it before update: '+name)
    base.mkdir(parents=True,exist_ok=True);destination.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.slidev-install-',dir=base) as temp:
        temp=Path(temp);changed=[]
        try:
            for name in names:
                target=destination/name;stage=temp/('new-'+name);backup=temp/('old-'+name)
                shutil.copytree(PLUGIN/'skills'/name,stage,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
                if target.exists():target.rename(backup)
                changed.append((target,backup));stage.rename(target)
            info={'installationType':'skills-compatibility','nativePluginRegistered':False,'plugin':'slidev-studio','version':release['version'],'repository':release['repository'],'skills':release['skills']}
            temporary=base/'.slidev-studio-install.tmp';temporary.write_text(json.dumps(info,indent=2)+'\n');temporary.replace(receipt)
        except Exception:
            for target,backup in reversed(changed):
                if target.exists():shutil.rmtree(target)
                if backup.exists():backup.rename(target)
            raise
    return {'installationType':'skills-compatibility','nativePluginRegistered':False,'agent':agent,'version':release['version'],'skills':str(destination),'receipt':str(receipt)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--agent',choices=['cursor','claude','generic'],required=True);p.add_argument('--project',type=Path,required=True);a=p.parse_args()
    try:print(json.dumps(install(a.project,a.agent),indent=2))
    except (ValueError,OSError,KeyError) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':main()
