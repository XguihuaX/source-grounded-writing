import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_release', ROOT / 'tools/build_release.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
SCRIPT = ROOT / 'skills/source-grounded-writing/scripts/init_library.py'


class LibraryTests(unittest.TestCase):
    def test_bundled_humanizer_snapshot_is_complete_and_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            for path in builder.build(folder):
                with zipfile.ZipFile(path) as archive:
                    prefix = 'source-grounded-writing/references/humanizer-zh/'
                    source = json.loads(archive.read(prefix + 'SOURCE.json'))
                    self.assertEqual(source['upstream'], 'https://github.com/op7418/Humanizer-zh')
                    self.assertEqual(set(source['sha256']), {'SKILL.md', 'README.md', 'LICENSE'})
                    for name, digest in source['sha256'].items():
                        data = archive.read(prefix + name)
                        self.assertEqual(hashlib.sha256(data).hexdigest(), digest)
                        self.assertEqual(data, (builder.SKILL / 'references/humanizer-zh' / name).read_bytes())

    def invoke(self, root, name, script=SCRIPT):
        return subprocess.run([sys.executable, str(script), '--root', str(root), '--project', name],
                              capture_output=True, text=True, encoding='utf-8')

    def test_existing_review_and_material_records_survive_reinitialization(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / '资料 库'
            self.assertEqual(self.invoke(root, '虚构项目甲').returncode, 0)
            overview = root / 'projects/虚构项目甲/overview.md'
            index = root / 'projects/虚构项目甲/material-index.json'
            overview.write_text('已确认的原有内容。', encoding='utf-8')
            index.write_text('{"project":"甲","materials":[{"id":"F01"}]}', encoding='utf-8')
            originals = (overview.read_bytes(), index.read_bytes())
            second = self.invoke(root, '虚构项目甲')
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(json.loads(second.stdout)['created'], [])
            self.assertEqual((overview.read_bytes(), index.read_bytes()), originals)
            self.assertEqual(self.invoke(root, '虚构项目乙').returncode, 0)
            self.assertEqual((overview.read_bytes(), index.read_bytes()), originals)

    def test_project_name_cannot_escape_workspace(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'work'
            for name in ('../outside', '/absolute', '..', 'a/b', 'a\\b', 'CON'):
                with self.subTest(name=name):
                    self.assertNotEqual(self.invoke(root, name).returncode, 0)
            self.assertFalse(root.exists())

    def test_project_symlink_outside_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'work'
            outside = Path(folder) / 'outside'
            outside.mkdir()
            (root / 'projects').mkdir(parents=True)
            try:
                (root / 'projects/link').symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Symlinks not available')
            self.assertNotEqual(self.invoke(root, 'link').returncode, 0)
            self.assertEqual(list(outside.iterdir()), [])

    def test_workbuddy_archive_runs_after_relocation(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            archives = builder.build(base / 'dist')
            path = next(p for p in archives if '-workbuddy-' in p.name)
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                self.assertTrue(all(n.startswith('source-grounded-writing/') for n in names))
                self.assertFalse(any('/Users/' in n or '__pycache__' in n for n in names))
                text = archive.read('source-grounded-writing/SKILL.md').decode('utf-8')
                front = text.split('---', 2)[1]
                metadata = {line.split(': ', 1)[0]: json.loads(line.split(': ', 1)[1])
                            for line in front.strip().splitlines()}
                for field in ('name', 'display_name', 'display_name_en', 'description',
                              'description_zh', 'description_en', 'version', 'author'):
                    self.assertTrue(metadata[field])
                source = (builder.SKILL / 'SKILL.md').read_text(encoding='utf-8')
                self.assertEqual(text.split('---', 2)[2], source.split('---', 2)[2])
                archive.extractall(base / '迁移到另一位置')
            relocated = base / '迁移到另一位置/source-grounded-writing/scripts/init_library.py'
            result = self.invoke(base / '新资料 库', '虚构示例', relocated)
            self.assertEqual(result.returncode, 0, result.stderr)
            index = json.loads((base / '新资料 库/projects/虚构示例/material-index.json').read_text(encoding='utf-8'))
            self.assertEqual(index['materials'], [])
            self.assertEqual(index['review']['status'], 'not_started')
            self.assertEqual(index['project'], '虚构示例')


if __name__ == '__main__':
    unittest.main()
