import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


verifier = module('verifier', ROOT / 'tools/verify_backup.py')
sync = module('source_sync', ROOT / '备份与交接/source_sync.py')


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'docs').mkdir()
        (self.root / 'a.txt').write_text('content')
        self.manifest = self.root / 'docs/源码文件校验清单.json'
        self.manifest.write_text(json.dumps({'a.txt': hashlib.sha256(b'content').hexdigest()}))

    def test_valid_and_corrupted_restore(self):
        self.assertEqual(verifier.verify(self.root), 1)
        (self.root / 'a.txt').write_text('changed')
        with self.assertRaises(ValueError):
            verifier.verify(self.root)

    def test_traversal_rejected(self):
        self.manifest.write_text(json.dumps({'../outside': 'fake'}))
        with self.assertRaises(ValueError):
            verifier.verify(self.root)

    def test_private_directory_rejected(self):
        (self.root / 'local-private').mkdir()
        with self.assertRaises(ValueError):
            verifier.verify(self.root)

    def test_secret_file_rejected(self):
        (self.root / '.env').write_text('EXAMPLE_ONLY=1')
        with self.assertRaises(ValueError):
            verifier.verify(self.root)

    def test_sync_private_and_runtime_exclusions(self):
        for name in ['local-private', '.git', 'node_modules', '.codex']:
            self.assertTrue(sync.skip_directory(self.root / name, Path(name)))
        self.assertTrue(sync.excluded(self.root / '.env', Path('.env')))
        self.assertTrue(sync.excluded(self.root / 'a.key', Path('a.key')))
        self.assertFalse(sync.excluded(self.root / '.env.example', Path('.env.example')))
        self.assertFalse(sync.excluded(self.root / 'scene.blend', Path('scene.blend')))


if __name__ == '__main__':
    unittest.main()
