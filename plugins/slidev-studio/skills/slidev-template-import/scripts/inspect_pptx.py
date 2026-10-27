#!/usr/bin/env python3
"""Inspect a local PPTX as data; optionally render with LibreOffice and Poppler."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile

NS={"p":"http://schemas.openxmlformats.org/presentationml/2006/main","a":"http://schemas.openxmlformats.org/drawingml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL="http://schemas.openxmlformats.org/package/2006/relationships"

def relations(z, part):
    name=str(PurePosixPath(part).parent/"_rels"/(PurePosixPath(part).name+".rels"))
    if name not in z.namelist():return {}
    return {e.attrib["Id"]:e.attrib for e in ET.fromstring(z.read(name))}

def target(part, rel):
    if rel.get("TargetMode")=="External":return None
    value=posixpath.normpath(posixpath.join(posixpath.dirname(part),rel["Target"]))
    if value.startswith("../") or value.startswith("/"):raise ValueError("Relationship escapes PPTX")
    return value

def inspect(source,out,render=False):
    source=Path(source).resolve();out=Path(out).absolute()
    if source.suffix.lower()!=".pptx":raise ValueError("Provide .pptx; convert legacy .ppt first")
    if out.exists():raise ValueError("Analysis output already exists")
    with ZipFile(source) as z:
        if len(z.infolist())>10000:raise ValueError("PPTX has too many entries")
        for item in z.infolist():
            p=PurePosixPath(item.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in item.filename or ':' in item.filename:raise ValueError('Unsafe PPTX entry')
        if sum(i.file_size for i in z.infolist())>512*1024*1024:raise ValueError("PPTX exceeds the 512 MB uncompressed inspection limit")
        root=ET.fromstring(z.read("ppt/presentation.xml"));size=root.find("p:sldSz",NS)
        links=relations(z,"ppt/presentation.xml");slides=[]
        for index,item in enumerate(root.findall("p:sldIdLst/p:sldId",NS),1):
            part=target("ppt/presentation.xml",links[item.attrib['{'+NS['r']+'}id']]);xml=ET.fromstring(z.read(part));rels=relations(z,part)
            shapes=[]
            for shape in xml.findall(".//p:spTree/*",NS):
                runs=[]
                for run in shape.findall(".//a:r",NS):
                    props=run.find("a:rPr",NS)
                    runs.append({"text":"".join(run.itertext()) if run.find("a:t",NS) is None else run.find("a:t",NS).text,"properties":ET.tostring(props,encoding="unicode") if props is not None else None})
                xform=shape.find(".//a:xfrm",NS)
                shapes.append({"kind":shape.tag.split('}')[-1],"text":"\n".join(t.text or '' for t in shape.findall('.//a:t',NS)),"transformXml":ET.tostring(xform,encoding="unicode") if xform is not None else None,"runs":runs})
            slides.append({"number":index,"part":part,"shapes":shapes,"relationships":list(rels.values())})
        out.mkdir(parents=True)
        shutil.copy2(source,out/'source.pptx')
        for name in z.namelist():
            if name.startswith(("ppt/theme/","ppt/slideMasters/","ppt/slideLayouts/")) and name.endswith('.xml'):
                dest=out/'xml'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(name))
            if name.startswith('ppt/media/') and not name.endswith('/'):
                raw=z.read(name);suffix=PurePosixPath(name).suffix
                dest=out/'media'/(hashlib.sha256(raw).hexdigest()[:16]+suffix);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        result={"source":"source.pptx","sourceSha256":hashlib.sha256(source.read_bytes()).hexdigest(),"dimensionsEmu":dict(size.attrib) if size is not None else {},"slideCount":len(slides),"slides":slides,"render":{"status":"not-requested"},"notes":"Grouped shapes retain their XML transforms; styles may inherit from retained masters/layouts. Inspect rendered pages."}
    if render:
        office=shutil.which('soffice') or shutil.which('libreoffice');poppler=shutil.which('pdftoppm')
        if not office or not poppler:
            result['render']={"status":"unavailable","missing":[n for n,v in [('LibreOffice',office),('pdftoppm',poppler)] if not v]}
        else:
            renders=out/'renders';renders.mkdir()
            with tempfile.TemporaryDirectory(prefix='slidev-office-') as temp:
                command=[office,'-env:UserInstallation='+Path(temp).as_uri(),'--headless','--convert-to','pdf','--outdir',str(renders),str(out/'source.pptx')]
                done=subprocess.run(command,capture_output=True,text=True,timeout=120)
                pdf=renders/'source.pdf'
                if done.returncode or not pdf.exists():result['render']={"status":"failed","detail":(done.stdout+done.stderr)[-3000:]}
                else:
                    subprocess.run([poppler,'-png','-scale-to','1600',str(pdf),str(renders/'slide')],check=True,capture_output=True,timeout=120)
                    pages=list(renders.glob('slide-*.png'))
                    result['render']={"status":"passed" if len(pages)==len(slides) else "incomplete","pages":len(pages),"pdf":"renders/source.pdf"}
    (out/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {"output":str(out),"slides":len(slides),"render":result['render']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--render',action='store_true');a=p.parse_args()
    try:print(json.dumps(inspect(a.source,a.out,a.render),ensure_ascii=False,indent=2))
    except (ValueError,OSError,ET.ParseError,KeyError,subprocess.SubprocessError) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':main()
