#!/usr/bin/env python3
"""Validate, register, export and instantiate complete agent-created Slidev templates."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tempfile
from zipfile import ZipFile,ZIP_DEFLATED

FORBIDDEN={'node_modules','.git','.venv','__pycache__','.DS_Store','dist','.slidev'}

def write_json(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def relative(root,name):
    if not isinstance(name,str) or '\\' in name or not name or ':' in name:raise ValueError('Use relative POSIX paths')
    parts=PurePosixPath(name)
    if parts.is_absolute() or '..' in parts.parts or name.startswith('/'):raise ValueError('Path escapes template')
    p=root/name
    if not p.resolve().is_relative_to(root.resolve()):raise ValueError('Path escapes template')
    return p

def files(root):
    result=[]
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root)
        if p.is_symlink():raise ValueError('Symlinks are not allowed: '+str(rel))
        if any(part in FORBIDDEN or part=='.env' or part.startswith('.env.') for part in rel.parts):raise ValueError('Runtime or private file in template: '+str(rel))
        if p.is_file():result.append(p)
    return result

def digest(root):
    h=hashlib.sha256()
    for p in files(root):
        h.update(p.relative_to(root).as_posix().encode());h.update(b'\0');h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()

def validate(root,verified=False):
    root=Path(root).resolve();all_files=files(root)
    data=json.loads((root/'template.json').read_text(encoding='utf-8'))
    if data.get('schemaVersion')!=1 or data.get('kind')!='slidev-template':raise ValueError('Unsupported full-template schema')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,48}',data.get('id','')):raise ValueError('Invalid template id')
    if not re.fullmatch(r'\d+\.\d+\.\d+',data.get('version','')):raise ValueError('Use a stable MAJOR.MINOR.PATCH template version')
    if not isinstance(data.get('name'),str) or not data['name'].strip():raise ValueError('Missing template name')
    if data.get('status') not in {'draft','verified'}:raise ValueError('Invalid template status')
    for field in ['source']:
        if not relative(root,data.get(field,'')).is_file():raise ValueError('Missing '+field)
    for name in ['design.md','scaffold/slides.md','scaffold/package.json']:
        if not (root/name).is_file():raise ValueError('Missing '+name)
    package=json.loads((root/'scaffold/package.json').read_text(encoding='utf-8'))
    if '@slidev/cli' not in {**package.get('dependencies',{}),**package.get('devDependencies',{})}:raise ValueError('Scaffold must declare @slidev/cli')
    layouts=data.get('layouts',[])
    if not isinstance(layouts,list) or not layouts:raise ValueError('Declare at least one source-backed reusable layout')
    names=[]
    for layout in layouts:
        name=layout.get('name','')
        if not re.fullmatch(r'[a-z][a-z0-9-]*',name) or name in names:raise ValueError('Invalid/duplicate layout name')
        names.append(name)
        if not (root/'scaffold/layouts'/f'{name}.vue').is_file():raise ValueError('Missing layout implementation: '+name)
        if not layout.get('sourceSlides') or any(type(n) is not int or n<1 for n in layout['sourceSlides']):raise ValueError('Layouts need positive source slide numbers')
    if verified or data['status']=='verified':
        check=data.get('verification',{})
        if data['status']!='verified' or check.get('build')!='passed' or check.get('visual')!='passed':raise ValueError('Build and visual verification must be completed')
        report=relative(root,check.get('report',''))
        if not report.is_file() or len(report.read_text(encoding='utf-8').strip())<40:raise ValueError('Missing meaningful verification report')
        for key in ['sourceSlides','renderedSlides']:
            if not check.get(key) or any(type(n) is not int or n<1 for n in check[key]):raise ValueError('Verification needs inspected slide numbers')
        preview=root/'preview.png'
        if not preview.is_file() or not preview.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Missing rendered PNG preview')
        if not list((root/'verification').glob('*.png')):raise ValueError('Retain checked rendered template pages')
    return {**data,'sha256':digest(root),'fileCount':len(all_files)}

def init(out,identifier,name,analysis):
    out=Path(out).absolute();analysis=Path(analysis).resolve()
    files(analysis)
    data=json.loads((analysis/'analysis.json').read_text(encoding='utf-8'))
    source=relative(analysis,data['source'])
    if not source.is_file():raise ValueError('Missing retained source')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,48}',identifier):raise ValueError('Invalid template id')
    out.mkdir(parents=True,exist_ok=False)
    try:
        shutil.copytree(analysis,out/'reference')
        (out/'scaffold').mkdir();(out/'verification').mkdir()
        size=data.get('dimensionsEmu',{});cx=int(size.get('cx',16));cy=int(size.get('cy',9))
        import math
        gcd=math.gcd(cx,cy)
        write_json(out/'template.json',{'schemaVersion':1,'kind':'slidev-template','id':identifier,'name':name,'version':'1.0.0','status':'draft','description':'','aspectRatio':f'{cx//gcd}/{cy//gcd}','layouts':[],'source':'reference/'+data['source'],'verification':{'build':'pending','visual':'pending','sourceSlides':[],'renderedSlides':[],'report':'verification/report.md'}})
        (out/'design.md').write_text('# Design analysis\n\nRecord evidence-backed design rules and source-to-layout mapping before implementing.\n',encoding='utf-8')
    except Exception:
        shutil.rmtree(out);raise
    return {'draft':str(out),'next':'Agent must implement scaffold/layouts, inspect renders and record verification before install.'}

def unpack(source,workspace):
    with ZipFile(source) as z:
        infos=z.infolist()
        if len(infos)>10000 or sum(i.file_size for i in infos)>512*1024*1024:raise ValueError('Template ZIP exceeds extraction limits')
        seen=set()
        for info in infos:
            if info.filename in seen:raise ValueError('Duplicate ZIP entry')
            seen.add(info.filename)
            if stat.S_ISLNK(info.external_attr>>16):raise ValueError('ZIP symlinks are not allowed')
            p=relative(workspace,info.filename)
            if info.is_dir():p.mkdir(parents=True,exist_ok=True)
            else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
    if (workspace/'template.json').is_file():return workspace
    children=list(workspace.iterdir())
    if len(children)==1 and children[0].is_dir() and (children[0]/'template.json').is_file():return children[0]
    raise ValueError('ZIP needs exactly one full template bundle')

def install(source,library):
    source=Path(source).resolve();library=Path(library).absolute()
    with tempfile.TemporaryDirectory(prefix='slidev-import-') as temp:
        root=unpack(source,Path(temp)) if source.is_file() else source
        data=validate(root,verified=True)
        destination=relative(library,f"{data['id']}/{data['version']}")
        if destination.exists():
            if validate(destination,True)['sha256']==data['sha256']:return {'installed':str(destination),'changed':False,'sha256':data['sha256']}
            raise ValueError('Template version is immutable; increment the version')
        destination.parent.mkdir(parents=True,exist_ok=True)
        stage=Path(tempfile.mkdtemp(prefix='.import-',dir=destination.parent))
        try:shutil.copytree(root,stage,dirs_exist_ok=True);stage.rename(destination)
        finally:
            if stage.exists():shutil.rmtree(stage)
        return {'installed':str(destination),'changed':True,'sha256':data['sha256']}

def list_templates(library):
    library=Path(library);result=[]
    for path in sorted(library.glob('*/*/template.json')):
        data=validate(path.parent,True)
        result.append({k:data[k] for k in ['id','name','version','aspectRatio','sha256']})
    return result

def instantiate(identifier,library,out,version=None):
    choices=[p for p in list_templates(library) if p['id']==identifier and (not version or p['version']==version)]
    if not choices:raise ValueError('Template/version not found')
    data=max(choices,key=lambda p:tuple(map(int,p['version'].split('.'))))
    source=relative(Path(library),f"{identifier}/{data['version']}");out=Path(out).absolute()
    # copytree refuses even an existing empty destination.
    try:
        shutil.copytree(source/'scaffold',out)
    except FileExistsError:raise ValueError('Destination exists; no files changed')
    except Exception:
        if out.exists():shutil.rmtree(out)
        raise
    write_json(out/'.slidev-template.json',{'schemaVersion':1,'templateId':identifier,'templateVersion':data['version'],'templateSha256':data['sha256']})
    return {'created':str(out),'template':identifier,'version':data['version'],'sha256':data['sha256']}

def export(source,out):
    source=Path(source).resolve();out=Path(out).absolute();validate(source,True)
    if out.is_relative_to(source):raise ValueError('Export ZIP must be outside the source bundle')
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise ValueError('Export already exists')
    with ZipFile(out,'x',ZIP_DEFLATED) as z:
        for p in files(source):z.write(p,p.relative_to(source).as_posix())
    return {'exported':str(out),'includesReference':True}

def main():
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='cmd',required=True)
    s=subs.add_parser('init');s.add_argument('out',type=Path);s.add_argument('--id',required=True);s.add_argument('--name',required=True);s.add_argument('--analysis',required=True,type=Path)
    s=subs.add_parser('validate');s.add_argument('source',type=Path);s.add_argument('--verified',action='store_true')
    s=subs.add_parser('install');s.add_argument('source',type=Path);s.add_argument('--library',type=Path,required=True)
    s=subs.add_parser('list');s.add_argument('--library',type=Path,required=True)
    s=subs.add_parser('instantiate');s.add_argument('id');s.add_argument('--version');s.add_argument('--library',type=Path,required=True);s.add_argument('--out',type=Path,required=True)
    s=subs.add_parser('export');s.add_argument('source',type=Path);s.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    try:
        if a.cmd=='init':r=init(a.out,a.id,a.name,a.analysis)
        elif a.cmd=='validate':r=validate(a.source,a.verified)
        elif a.cmd=='install':r=install(a.source,a.library)
        elif a.cmd=='list':r=list_templates(a.library)
        elif a.cmd=='instantiate':r=instantiate(a.id,a.library,a.out,a.version)
        else:r=export(a.source,a.out)
        print(json.dumps(r,ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError,TypeError) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':main()
