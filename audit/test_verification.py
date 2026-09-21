"""Ensure corrupt certificates and changed provenance cannot pass the archive gate."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ArchiveGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'audit', self.root / 'audit', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(ROOT / 'results/chain-first-annealer', self.root / 'results/chain-first-annealer')

    def check(self):
        return subprocess.run([sys.executable, str(self.root/'audit/verify_all.py'), '--check'],
                              capture_output=True, text=True)

    def test_changed_timing_requires_manifest_update(self):
        path=self.root/'results/chain-first-annealer/s2_k3_v2/summary.json'
        data=json.loads(path.read_text());data['elapsed_s']+=1
        path.write_text(json.dumps(data))
        result=self.check()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Manifest differs',result.stderr)

    def test_corrupt_facet_is_rejected(self):
        path=self.root/'results/chain-first-annealer/s2_k3_v2/cover.txt'
        original=path.read_text()
        self.assertIn('(0,0)',original)
        path.write_text(original.replace('(0,0)','(99,99)',1))
        result=self.check()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('facet table mismatch',result.stderr)


if __name__=='__main__':
    unittest.main()
