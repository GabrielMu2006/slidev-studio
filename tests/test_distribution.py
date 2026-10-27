import hashlib
import shutil
import tarfile
from unittest.mock import patch
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
                self.assertEqual(receipt['installationType'],'skills-compatibility');self.assertFalse(receipt['nativePluginRegistered'])
    def test_installed_helpers_and_catalog_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp);install_agent.install(project,'generic')
            result=verify_install.verify(project/'.agents/skills',project/'.agents/slidev-studio-install.json')
            self.assertTrue(result['verified']);self.assertEqual(result['presetCount'],8)
            self.assertEqual(result['installationType'],'skills-compatibility');self.assertFalse(result['hostRegistrationVerified'])
            (project/'.agents/skills/slidev/assets/studio/templates.json').write_text('[]')
            with self.assertRaises(ValueError):verify_install.verify(project/'.agents/skills')
    def test_stale_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp);install_agent.install(project,'cursor');receipt=project/'.cursor/slidev-studio-install.json'
            data=json.loads(receipt.read_text());data['version']='0.0.0';receipt.write_text(json.dumps(data))
            with self.assertRaises(ValueError):verify_install.verify(project/'.cursor/skills',receipt)
    def test_skill_copy_is_not_accepted_as_plugin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(release.PLUGIN/'skills',root/'skills',ignore=shutil.ignore_patterns('__pycache__'))
            with self.assertRaisesRegex(ValueError,'No plugin manifest'):verify_install.verify_plugin(root)
    def test_plugin_package_does_not_claim_host_registration(self):
        result=verify_install.verify_plugin(release.PLUGIN)
        self.assertEqual(result['installationType'],'plugin-package');self.assertFalse(result['hostRegistrationVerified'])
        self.assertIn('.zcode-plugin/plugin.json',result['manifests'])
    def test_zcode_marketplace_resolves_flat_skills(self):
        marketplace=json.loads((ROOT/'marketplace.json').read_text());entry=marketplace['plugins'][0]
        plugin=ROOT/entry['source'];manifest=json.loads((plugin/'.zcode-plugin/plugin.json').read_text())
        self.assertEqual(entry['version'],manifest['version'])
        self.assertEqual(sorted(p.parent.name for p in (plugin/manifest['skills']).glob('*/SKILL.md')),['slidev','slidev-template-import'])
    def test_zcode_version_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','dist','node_modules','__pycache__'))
            for relative,message in [('plugins/slidev-studio/.zcode-plugin/plugin.json','Version mismatch'),('marketplace.json','Marketplace version/source mismatch')]:
                path=root/relative;original=path.read_text();data=json.loads(original)
                if relative=='marketplace.json':data['plugins'][0]['version']='0.0.0'
                else:data['version']='0.0.0'
                path.write_text(json.dumps(data))
                with patch.object(release,'ROOT',root),patch.object(release,'PLUGIN',root/'plugins/slidev-studio'):
                    with self.assertRaisesRegex(ValueError,message):release.validate()
                path.write_text(original)
    def test_dsh_release_contains_native_bundle_and_both_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            one=Path(tmp)/'one';two=Path(tmp)/'two';release.build(one);release.build(two)
            version=(ROOT/'VERSION').read_text().strip();name='slidev-studio-dsh-'+version+'.tgz'
            self.assertEqual((one/name).read_bytes(),(two/name).read_bytes())
            with tarfile.open(one/name) as archive:
                package=json.load(archive.extractfile('package/package.json'))
                self.assertEqual(package['version'],version);self.assertIn('bundle',package['dsh'])
                for path in ['adapters/dsh/index.mjs','adapters/dsh/cordis.patch.yml','plugins/slidev-studio/skills/slidev/scripts/studio.py','plugins/slidev-studio/skills/slidev-template-import/scripts/template_bundle.py']:
                    self.assertIsNotNone(archive.getmember('package/'+path))
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
