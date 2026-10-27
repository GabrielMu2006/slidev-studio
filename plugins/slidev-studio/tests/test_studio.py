import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

skill=Path(os.environ.get("SLIDEV_STUDIO_SKILL",Path(__file__).resolve().parents[1]/"skills/slidev"))
spec=importlib.util.spec_from_file_location("studio",skill/"scripts/studio.py")
studio=importlib.util.module_from_spec(spec);spec.loader.exec_module(studio)

class StudioTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.project=self.root/"talk"
        studio.create(self.project,studio.default_config(title="中文: \"课程\""))
    def tearDown(self):
        self.temp.cleanup()
    def test_all_templates_apply_without_changing_slide_body(self):
        original=(self.project/"slides.md").read_text().split("\n---\n",2)[2]
        for template in studio.catalog():
            config=studio.default_config(template=template["id"],title="中文课程")
            studio.apply(self.project,config)
            self.assertEqual((self.project/"slides.md").read_text().split("\n---\n",2)[2],original)
            self.assertEqual(studio.load_config(self.project)["template"],template["id"])
    def test_legacy_course_id_loads_without_losing_settings_or_content(self):
        config=studio.load_config(self.project);config['template']='ics-course';config['settings']['accent']='#123456'
        (self.project/studio.CONFIG).write_text(json.dumps(config))
        original=(self.project/'slides.md').read_text().split('\n---\n',2)[2]
        normalized=studio.load_config(self.project)
        self.assertEqual(normalized['template'],'cyan-classroom');self.assertEqual(normalized['settings']['accent'],'#123456')
        studio.apply(self.project,normalized)
        self.assertEqual((self.project/'slides.md').read_text().split('\n---\n',2)[2],original)
        self.assertEqual(studio.default_config(template='ics-course')['template'],'cyan-classroom')
        with self.assertRaises(ValueError):studio.save_template(self.project,'ics-course','Reserved alias')
    def test_reapply_is_noop(self):
        config=studio.load_config(self.project)
        count=len(list((self.project/".slidev-studio/backups").iterdir()))
        self.assertFalse(studio.apply(self.project,config)["changed"])
        self.assertEqual(count,len(list((self.project/".slidev-studio/backups").iterdir())))
    def test_restore_exact_files(self):
        paths=["slides.md",studio.STYLE,studio.CONFIG]
        before={p:(self.project/p).read_bytes() for p in paths}
        studio.apply(self.project,studio.default_config(template="terminal-dark",title="changed"))
        studio.restore(self.project)
        self.assertEqual(before,{p:(self.project/p).read_bytes() for p in paths})
    def test_preserves_css_outside_managed_block(self):
        path=self.project/studio.STYLE
        original=path.read_text();path.write_text("/* custom before */\n"+original+"\n/* custom after */")
        studio.apply(self.project,studio.default_config(template="academic-paper"))
        self.assertTrue(path.read_text().startswith("/* custom before */"))
        self.assertTrue(path.read_text().endswith("/* custom after */"))
        self.assertEqual(path.read_text().count(studio.BEGIN),1)
    def test_refuses_existing_destination(self):
        before=(self.project/"slides.md").read_bytes()
        with self.assertRaises(Exception):studio.create(self.project,studio.default_config())
        self.assertEqual(before,(self.project/"slides.md").read_bytes())
    def test_invalid_settings_no_file_changes(self):
        before=(self.project/"slides.md").read_bytes()
        for key,value in [("accent","red;display:none"),("titleSize",100),("pageNumbers","false"),("coverImage","/../other.svg"),("unknown",True)]:
            config=studio.default_config();config["settings"][key]=value
            with self.assertRaises(ValueError):studio.apply(self.project,config)
        self.assertEqual(before,(self.project/"slides.md").read_bytes())
    def test_complex_headmatter_refused_before_writing(self):
        path=self.project/"slides.md";original=path.read_text()
        title_line=next(line for line in original.splitlines() if line.startswith("title:"))
        path.write_text(original.replace(title_line,"title: |\n  Multiline title",1))
        before=path.read_bytes()
        with self.assertRaises(ValueError):studio.apply(self.project,studio.default_config())
        self.assertEqual(before,path.read_bytes())
    def test_broken_markers_refused(self):
        path=self.project/studio.STYLE;path.write_text(path.read_text().replace(studio.END,""));before=path.read_bytes()
        with self.assertRaises(ValueError):studio.apply(self.project,studio.default_config())
        self.assertEqual(before,path.read_bytes())
    def test_legacy_custom_template_inherits_classic_composition(self):
        studio.save_template(self.project,'legacy-style','Legacy')
        path=self.project/'slidev-templates/legacy-style.json';data=json.loads(path.read_text());data['defaults'].pop('composition');path.write_text(json.dumps(data))
        config=studio.default_config(self.project,template='legacy-style')
        self.assertEqual(config['settings']['composition'],'classic')
        studio.apply(self.project,config)
        self.assertTrue(studio.load_config(self.project)['template']=='legacy-style')
    def test_invalid_composition_cannot_modify_project(self):
        original=(self.project/'slides.md').read_bytes();config=studio.default_config();config['settings']['composition']='arbitrary-style'
        with self.assertRaises(ValueError):studio.apply(self.project,config)
        self.assertEqual(original,(self.project/'slides.md').read_bytes())
    def test_custom_template_roundtrip(self):
        config=studio.load_config(self.project);config["settings"]["accent"]="#123456"
        studio.save_template(self.project,"my-course","我的模板",config)
        selected=studio.default_config(self.project,template="my-course")
        self.assertEqual(selected["settings"]["accent"],"#123456")
        studio.apply(self.project,selected)
        self.assertEqual(studio.load_config(self.project)["template"],"my-course")
        with self.assertRaises(ValueError):studio.save_template(self.project,"my-course","duplicate")
    @unittest.skipIf(os.name == 'nt', 'Creating symlinks requires Windows developer privileges')
    def test_managed_symlink_escape_refused(self):
        outside=self.root/"outside.css";outside.write_text("keep me")
        path=self.project/studio.STYLE;path.unlink();path.symlink_to(outside)
        with self.assertRaises(ValueError):studio.apply(self.project,studio.default_config())
        self.assertEqual(outside.read_text(),"keep me")
    def test_alternate_style_entry_preserved(self):
        path=self.project/"styles/index.ts";path.write_text("import './custom.css'")
        with self.assertRaises(ValueError):studio.apply(self.project,studio.default_config())
        self.assertEqual(path.read_text(),"import './custom.css'")
    def test_preview_escapes_title(self):
        config=studio.default_config(title='<img src=x onerror=alert(1)>')
        content=studio.preview(config,"cover")
        self.assertIn('&lt;img',content)
        self.assertNotIn('<img src=x',content)
    def test_unknown_template_refused(self):
        with self.assertRaises(ValueError):studio.default_config(template="missing")
    def test_headmatter_does_not_touch_fences_or_notes(self):
        original='---\ntitle: Demo\nfonts:\n  sans: System\n---\n# One\n```yaml\n---\n```\n<!-- notes -->\n---\n# Two\n'
        updated=studio.update_headmatter(original,{"title":"Changed","aspectRatio":"4/3"})
        self.assertEqual(updated[updated.index('# One'):],original[original.index('# One'):])
        self.assertIn('  sans: System',updated)

if __name__=="__main__":unittest.main()
