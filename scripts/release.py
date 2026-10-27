#!/usr/bin/env python3
"""One release version for plugin code, host manifests and every bundled skill."""
import argparse
import gzip
import io
import tarfile
import hashlib
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
PLUGIN=ROOT/'plugins/slidev-studio'
REPOSITORY='https://github.com/GabrielMu2006/slidev-studio'

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def skill_files(root):
    return [p for p in sorted(root.rglob('*'),key=lambda p:p.relative_to(root).as_posix()) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']

def tree_hash(root):
    h=hashlib.sha256()
    for p in skill_files(root):h.update(p.relative_to(root).as_posix().encode()+b'\0'+hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()

def sync(version):
    if not re.fullmatch(r'\d+\.\d+\.\d+',version):raise ValueError('Version must be MAJOR.MINOR.PATCH')
    (ROOT/'VERSION').write_text(version+'\n')
    package=json.loads((ROOT/'package.json').read_text(encoding='utf-8'));package['version']=version;write(ROOT/'package.json',package)
    main=json.loads((PLUGIN/'plugin.json').read_text(encoding='utf-8'));main['version']=version;main['repository']=REPOSITORY;main['homepage']=REPOSITORY;main['author']={'name':'Li Muzhi','url':'https://github.com/GabrielMu2006'}
    write(PLUGIN/'plugin.json',main)
    overlay=json.loads((PLUGIN/'.codex-plugin/plugin.json').read_text(encoding='utf-8'));overlay.update({k:main[k] for k in ['version','repository','homepage','author']});write(PLUGIN/'.codex-plugin/plugin.json',overlay)
    write(PLUGIN/'.claude-plugin/plugin.json',{k:main[k] for k in ['name','version','description','author','homepage','repository','license']})
    claude={'name':'slidev-local','metadata':{'description':'Slidev authoring and reference-backed full template import'},'owner':main['author'],'plugins':[{'name':'slidev-studio','source':'./plugins/slidev-studio','version':version,'description':main['description']}]}
    write(ROOT/'.claude-plugin/marketplace.json',claude)
    write(PLUGIN/'.zcode-plugin/plugin.json',{**{k:main[k] for k in ['name','version','description','author','homepage','repository','license']},'skills':'./skills'})
    write(ROOT/'marketplace.json',{'name':'slidev-local','description':'Slidev Studio plugin marketplace','plugins':[{'name':'slidev-studio','source':'./plugins/slidev-studio','version':version,'description':main['description'],'category':'productivity'}]})
    for path in (PLUGIN/'skills').glob('*/SKILL.md'):
        text=path.read_text(encoding='utf-8');first,body=text[4:].split('\n---',1)
        if re.search(r'^metadata:\s*$',first,re.M):first=re.sub(r'(^  version:).*$',lambda m:m[1]+' "'+version+'"',first,flags=re.M)
        else:first+='\nmetadata:\n  version: "'+version+'"'
        path.write_text('---\n'+first+'\n---'+body,encoding='utf-8')
    write(PLUGIN/'release.json',{'version':version,'repository':REPOSITORY,'skills':{p.parent.name:tree_hash(p.parent) for p in sorted((PLUGIN/'skills').glob('*/SKILL.md'))}})

def validate():
    version=(ROOT/'VERSION').read_text().strip()
    package=json.loads((ROOT/'package.json').read_text(encoding='utf-8'))
    if package.get('version')!=version or package.get('name')!='slidev-studio' or package.get('dsh',{}).get('bundle',{}).get('patch')!='./adapters/dsh/cordis.patch.yml':raise ValueError('DSH package metadata mismatch')
    for path in [PLUGIN/'plugin.json',PLUGIN/'.codex-plugin/plugin.json',PLUGIN/'.claude-plugin/plugin.json',PLUGIN/'.zcode-plugin/plugin.json',PLUGIN/'release.json']:
        if json.loads(path.read_text(encoding='utf-8'))['version']!=version:raise ValueError('Version mismatch: '+str(path))
    for manifest in [ROOT/'marketplace.json',ROOT/'.claude-plugin/marketplace.json']:
        catalog=json.loads(manifest.read_text(encoding='utf-8'))
        entry=next((p for p in catalog['plugins'] if p['name']=='slidev-studio'),None)
        if not entry or entry.get('version')!=version or entry.get('source')!='./plugins/slidev-studio':
            raise ValueError('Marketplace version/source mismatch: '+str(manifest))
    data=json.loads((PLUGIN/'release.json').read_text())
    for name,sha in data['skills'].items():
        folder=PLUGIN/'skills'/name
        if tree_hash(folder)!=sha:raise ValueError('Release skill hash mismatch; run sync after edits: '+name)
        text=(folder/'SKILL.md').read_text(encoding='utf-8')
        if '  version: "'+version+'"' not in text:raise ValueError('Skill version mismatch')
        for path in folder.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if re.match(r'[a-z]+:|#|/',link):continue
                if not (path.parent/link.split('#')[0]).exists():raise ValueError('Broken link: '+str(path)+' -> '+link)
    for p in skill_files(PLUGIN):
        if p.is_symlink():raise ValueError('Symlink in plugin')
        if '/Users/' in p.read_text(encoding='utf-8',errors='ignore'):raise ValueError('Personal absolute path in release: '+str(p))
    print('Validated release '+version+' with '+str(len(data['skills']))+' skills')

def zip_files(out,entries):
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        for path,name in entries:
            info=ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,path.read_bytes())

def build(out):
    validate();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);version=(ROOT/'VERSION').read_text().strip()
    plugin=out/f'slidev-studio-{version}.zip'
    zip_files(plugin,[(p,'slidev-studio/'+p.relative_to(PLUGIN).as_posix()) for p in skill_files(PLUGIN)])
    portable=out/f'slidev-studio-skills-{version}.zip'
    zip_files(portable,[(p,'.agents/skills/'+p.relative_to(PLUGIN/'skills').as_posix()) for p in skill_files(PLUGIN/'skills')])
    dsh=out/f'slidev-studio-dsh-{version}.tgz'
    entries=[(ROOT/'package.json','package/package.json'),(ROOT/'README.md','package/README.md'),(ROOT/'INSTALL.md','package/INSTALL.md')]
    entries += [(p,'package/adapters/dsh/'+p.relative_to(ROOT/'adapters/dsh').as_posix()) for p in skill_files(ROOT/'adapters/dsh')]
    entries += [(p,'package/plugins/slidev-studio/'+p.relative_to(PLUGIN).as_posix()) for p in skill_files(PLUGIN)]
    with dsh.open('wb') as raw, gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as compressed, tarfile.open(fileobj=compressed,mode='w') as archive:
        for path,name in entries:
            data=path.read_bytes();info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;archive.addfile(info,io.BytesIO(data))
    sums=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in [plugin,portable,dsh])
    (out/'SHA256SUMS').write_text(sums)
    print(str(plugin));print(str(portable))

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True)
    a=s.add_parser('sync');a.add_argument('version');s.add_parser('validate');a=s.add_parser('build');a.add_argument('--out',type=Path,default=ROOT/'dist')
    args=p.parse_args()
    try:
        if args.cmd=='sync':sync(args.version)
        elif args.cmd=='validate':validate()
        else:build(args.out)
    except (ValueError,OSError,KeyError) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':main()
