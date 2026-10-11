import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'starter'))
from public_dataset import validate_prediction, validate_times


class ConstantVelocityBaselineTests(unittest.TestCase):
    def test_writes_valid_prediction_at_every_frame_without_references(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'example'
            subprocess.run([sys.executable, str(ROOT / 'examples/make_synthetic_example.py'),
                            '--output', str(root)], check=True, capture_output=True)
            for ref in (root / 'references').glob('*.json'):
                ref.unlink()
            run = Path(temp) / 'cv'
            subprocess.run([sys.executable, str(ROOT / 'starter/cv_baseline.py'),
                            '--dataset', str(root / 'release_manifest.json'),
                            '--split', 'val', '--output', str(run)],
                           check=True, capture_output=True, text=True)
            timing = json.loads((root / 'timing/clip_000.json').read_text())
            pred = json.loads((run / 'predictions/clip_000.json').read_text())
            validate_prediction(pred, 'clip_000', validate_times(timing['times']))
            self.assertEqual(pred['times'], timing['times'])
            self.assertEqual(pred['frame_indices'], list(range(len(timing['times']))))
            t0 = timing['times'][0]
            self.assertEqual(pred['positions'], [[t - t0, 0.0, 0.0] for t in timing['times']])

    def test_refuses_non_empty_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'example'
            subprocess.run([sys.executable, str(ROOT / 'examples/make_synthetic_example.py'),
                            '--output', str(root)], check=True, capture_output=True)
            result = subprocess.run([sys.executable, str(ROOT / 'starter/cv_baseline.py'),
                                     '--dataset', str(root / 'release_manifest.json'),
                                     '--output', str(root / 'run')], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / 'run/inference_manifest.json').exists())


if __name__ == '__main__':
    unittest.main()
