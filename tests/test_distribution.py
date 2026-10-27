import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import install_agent
import release
import verify_install

class DistributionTests(unittest.TestCase):
    def test_hash_uses_posix_case_sensitive_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ['a.txt','Z.txt','b/n.txt']:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(name.encode())
            h=hashlib.sha256()
            for name in ['Z.txt','a.txt','b/n.txt']:
                h.update(name.encode()+b'\0'+hashlib.sha256(name.encode()).digest())
            self.assertEqual(release.tree_hash(root),h.hexdigest())
    def test_manifest_and_skill_versions_match(self):release.validate()
    def test_agent_install_contains_both_self_contained_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            for agent,folder in [('cursor','.cursor'),('claude','.claude'),('generic','.agents')]:
                project=Path(tmp)/agent;install_agent.install(project,agent)
                for skill in ['slidev','slidev-template-import']:
                    self.assertTrue((project/folder/'skills'/skill/'SKILL.md').is_file())
                receipt=json.loads((project/folder/'slidev-studio-install.json').read_text())
                self.assertEqual(receipt['version'],(ROOT/'VERSION').read_text().strip())
    def test_installed_helpers_and_catalog_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp);install_agent.install(project,'generic')
            result=verify_install.verify(project/'.agents/skills',project/'.agents/slidev-studio-install.json')
            self.assertTrue(result['verified']);self.assertEqual(result['presetCount'],8)
            (project/'.agents/skills/slidev/assets/studio/templates.json').write_text('[]')
            with self.assertRaises(ValueError):verify_install.verify(project/'.agents/skills')
    def test_stale_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp);install_agent.install(project,'cursor');receipt=project/'.cursor/slidev-studio-install.json'
            data=json.loads(receipt.read_text());data['version']='0.0.0';receipt.write_text(json.dumps(data))
            with self.assertRaises(ValueError):verify_install.verify(project/'.cursor/skills',receipt)
    def test_update_preserves_local_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp);install_agent.install(project,'generic');path=project/'.agents/skills/slidev/SKILL.md';path.write_text(path.read_text()+'\nlocal change\n');before=(project/'.agents/slidev-studio-install.json').read_bytes()
            with self.assertRaises(ValueError):install_agent.install(project,'generic')
            self.assertTrue(path.read_text().endswith('local change\n'));self.assertEqual(before,(project/'.agents/slidev-studio-install.json').read_bytes())
    def test_unrelated_skill_is_not_touched(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp);keep=project/'.cursor/skills/other/SKILL.md';keep.parent.mkdir(parents=True);keep.write_text('Keep')
            install_agent.install(project,'cursor');self.assertEqual(keep.read_text(),'Keep')

if __name__=='__main__':unittest.main()
