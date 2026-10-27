import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

scripts=Path(__file__).resolve().parents[1]/'skills/slidev-template-import/scripts'
spec=importlib.util.spec_from_file_location('template_bundle',scripts/'template_bundle.py')
bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)
spec=importlib.util.spec_from_file_location('inspect_pptx',scripts/'inspect_pptx.py')
inspector=importlib.util.module_from_spec(spec);spec.loader.exec_module(inspector)
PNG=bytes.fromhex('89504e470d0a1a0a')+b'structural-test-only'

def fixture(root):
    # Synthetic structure-only test; real visual acceptance is separate.
    for folder in ['scaffold/layouts','scaffold/components','scaffold/public','reference','verification']:(root/folder).mkdir(parents=True,exist_ok=True)
    data={'schemaVersion':1,'kind':'slidev-template','id':'sample','name':'Sample','version':'1.0.0','status':'verified','aspectRatio':'16/9','layouts':[{'name':'cover','sourceSlides':[1]}],'source':'reference/source.pptx','verification':{'build':'passed','visual':'passed','sourceSlides':[1],'renderedSlides':[1],'report':'verification/report.md'}}
    (root/'template.json').write_text(json.dumps(data));(root/'design.md').write_text('Synthetic structural fixture; not visual evidence.')
    (root/'preview.png').write_bytes(PNG);(root/'verification/slide1.png').write_bytes(PNG)
    (root/'verification/report.md').write_text('Synthetic unit-test record. This fixture does not assert visual quality or execute a real build.')
    (root/'reference/source.pptx').write_bytes(b'synthetic-source')
    (root/'scaffold/slides.md').write_text('---\nlayout: cover\n---\n# Example\n')
    (root/'scaffold/package.json').write_text(json.dumps({'devDependencies':{'@slidev/cli':'53.0.0'}}))
    (root/'scaffold/layouts/cover.vue').write_text('<template><div class="slidev-layout"><slot /></div></template>')
    (root/'scaffold/components/Example.vue').write_text('<template><span>Reusable</span></template>')
    (root/'scaffold/public/logo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    return data

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.package=self.root/'package';self.data=fixture(self.package);self.library=self.root/'library'
    def tearDown(self):self.temp.cleanup()
    def test_files_use_portable_case_sensitive_order(self):
        for name in ['a.txt','Z.txt']:(self.package/name).write_bytes(b'fixture')
        actual=[p.relative_to(self.package).as_posix() for p in bundle.files(self.package)]
        self.assertEqual(actual,sorted(actual))
    def test_full_install_and_instantiate(self):
        bundle.install(self.package,self.library);out=self.root/'talk';bundle.instantiate('sample',self.library,out)
        for rel in ['layouts/cover.vue','components/Example.vue','public/logo.svg','slides.md']:
            self.assertEqual((out/rel).read_bytes(),(self.package/'scaffold'/rel).read_bytes())
        self.assertEqual(json.loads((out/'.slidev-template.json').read_text())['templateSha256'],bundle.digest(self.package))
    def test_immutable_versions(self):
        bundle.install(self.package,self.library);self.assertFalse(bundle.install(self.package,self.library)['changed'])
        (self.package/'design.md').write_text('changed')
        with self.assertRaises(ValueError):bundle.install(self.package,self.library)
    def test_existing_destination_preserved(self):
        bundle.install(self.package,self.library);out=self.root/'talk';out.mkdir();(out/'keep').write_text('original')
        with self.assertRaises(ValueError):bundle.instantiate('sample',self.library,out)
        self.assertEqual((out/'keep').read_text(),'original')
    def test_zip_roundtrip(self):
        archive=self.root/'export.zip';bundle.export(self.package,archive);bundle.install(archive,self.library)
        self.assertEqual(bundle.validate(self.package,True)['sha256'],bundle.validate(self.library/'sample/1.0.0',True)['sha256'])
    def test_draft_cannot_register(self):
        self.data['status']='draft';(self.package/'template.json').write_text(json.dumps(self.data))
        with self.assertRaises(ValueError):bundle.install(self.package,self.library)
        self.assertFalse(self.library.exists())
    def test_missing_real_layout_rejected(self):
        (self.package/'scaffold/layouts/cover.vue').unlink()
        with self.assertRaises(ValueError):bundle.validate(self.package,True)
    def test_reference_path_escape_rejected(self):
        self.data['source']='../outside.pptx';(self.package/'template.json').write_text(json.dumps(self.data))
        with self.assertRaises(ValueError):bundle.validate(self.package,True)
    def test_missing_visual_evidence_rejected(self):
        (self.package/'verification/slide1.png').unlink()
        with self.assertRaises(ValueError):bundle.validate(self.package,True)
    def test_dependency_directory_rejected(self):
        (self.package/'scaffold/node_modules').mkdir()
        with self.assertRaises(ValueError):bundle.validate(self.package,True)
    def test_zip_traversal_rejected(self):
        archive=self.root/'evil.zip'
        with ZipFile(archive,'w') as z:z.writestr('../outside','data')
        with self.assertRaises(ValueError):bundle.install(archive,self.library)
        self.assertFalse((self.root/'outside').exists())
    def test_version_sort_is_semantic(self):
        bundle.install(self.package,self.library)
        for version in ['2.0.0','10.0.0']:
            self.data['version']=version;(self.package/'template.json').write_text(json.dumps(self.data));bundle.install(self.package,self.library)
        result=bundle.instantiate('sample',self.library,self.root/'talk')
        self.assertEqual(result['version'],'10.0.0')
    def test_pptx_order_dimensions_and_text(self):
        source=self.root/'source.pptx'
        with ZipFile(source,'w') as z:
            z.writestr('ppt/presentation.xml','<p:presentation xmlns:p="'+inspector.NS['p']+'" xmlns:r="'+inspector.NS['r']+'"><p:sldIdLst><p:sldId id="1" r:id="r1"/></p:sldIdLst><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
            z.writestr('ppt/_rels/presentation.xml.rels','<Relationships xmlns="'+inspector.REL+'"><Relationship Id="r1" Target="slides/slide2.xml" Type="slide"/></Relationships>')
            z.writestr('ppt/slides/slide2.xml','<p:sld xmlns:p="'+inspector.NS['p']+'" xmlns:a="'+inspector.NS['a']+'"><p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>Actual slide order</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>')
        inspector.inspect(source,self.root/'analysis')
        data=json.loads((self.root/'analysis/analysis.json').read_text())
        self.assertEqual(data['slides'][0]['part'],'ppt/slides/slide2.xml');self.assertEqual(data['slides'][0]['shapes'][0]['text'],'Actual slide order');self.assertEqual(data['dimensionsEmu']['cx'],'12192000')
    def test_malicious_pptx_rejected_before_write(self):
        source=self.root/'bad.pptx'
        with ZipFile(source,'w') as z:z.writestr('ppt/theme/../../outside.xml','bad')
        with self.assertRaises(ValueError):inspector.inspect(source,self.root/'analysis')
        self.assertFalse((self.root/'analysis').exists())

if __name__=='__main__':unittest.main()
