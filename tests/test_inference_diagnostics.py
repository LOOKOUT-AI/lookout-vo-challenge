import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'starter'))
import infer
import tracking


class InferenceDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dataset = self.root / 'release_manifest.json'
        self.dataset.write_text('{}', encoding='utf-8')
        self.output = self.root / 'run'
        self.clips = [dict(key=f'clip_{i:03}', split='val', video=f'{i}.mp4',
                           camera_mode='wide', calibration={}) for i in range(2)]
        for clip in self.clips:
            (self.root / clip['video']).touch()
        self.pre = SimpleNamespace(decoded_index=int, frame_time=float,
                                   native_fps=30.0, stride=4, effective_fps=7.5)
        self.success = (np.zeros((2, 7)), np.arange(2), self.pre)

    def run_inference(self, outcomes, extra=()):
        stdout = io.StringIO()
        with patch.object(infer, 'load_manifest', return_value={'clips': self.clips}), \
             patch.object(infer, 'load_timestamps', return_value=np.array([0., 1.])), \
             patch.object(infer, 'track', side_effect=outcomes) as tracker, \
             contextlib.redirect_stdout(stdout):
            result = infer.main(['--dataset', str(self.dataset), '--output',
                                 str(self.output), *extra])
        self.assertEqual(result, 0)
        manifest = json.loads((self.output / 'inference_manifest.json').read_text())
        return manifest, stdout.getvalue(), tracker

    def test_full_error_log_survives_reason_truncation_and_next_clip_runs(self):
        error = 'x' * 400 + ' important trailing detail'
        run, stdout, tracker = self.run_inference(
            [RuntimeError(error), self.success], ['--dpvo-buffer-size', '8192'])
        first, second = run['clips']
        self.assertEqual(first['status'], 'tracking_failed')
        self.assertEqual(len(first['reason']), 300)
        log = (self.output / first['error_log']).read_text()
        self.assertIn('Traceback', log)
        self.assertIn(error, log)
        self.assertFalse((self.output / 'predictions/clip_000.json').exists())
        self.assertEqual(second['status'], 'predicted')
        self.assertEqual((second['native_fps'], second['stride'], second['effective_fps']),
                         (30., 4, 7.5))
        self.assertTrue(all(r['elapsed_seconds'] >= 0 for r in run['clips']))
        self.assertEqual(run['target_fps'], 8.)
        self.assertEqual(run['dpvo_buffer_size'], 8192)
        self.assertEqual(tracker.call_args.kwargs['dpvo_buffer_size'], 8192)
        self.assertIn('[1/2] clip_000: starting inference', stdout)
        self.assertIn('[2/2] clip_001: predicted', stdout)

    def test_non_finite_prediction_remains_failed_and_is_not_written(self):
        poses = np.zeros((2, 7))
        poses[1, 0] = np.nan
        run, _, _ = self.run_inference([(poses, np.arange(2), self.pre), self.success])
        self.assertEqual(run['clips'][0]['status'], 'tracking_failed')
        self.assertIn('non-finite', run['clips'][0]['reason'])
        self.assertIn('FloatingPointError',
                      (self.output / run['clips'][0]['error_log']).read_text())
        self.assertFalse((self.output / 'predictions/clip_000.json').exists())

    def test_requested_fps_and_seed_are_preserved(self):
        run, stdout, tracker = self.run_inference(
            [self.success, self.success], ['--target-fps', '80', '--seed', '1'])
        self.assertEqual((run['target_fps'], run['seed'], run['dpvo_buffer_size']),
                         (80., 1, None))
        self.assertEqual(tracker.call_args.args[2:4], (80., 1))
        self.assertIn('target_fps=80.0', stdout)

    def test_missing_video_still_records_progress_and_duration(self):
        (self.root / self.clips[0]['video']).unlink()
        run, stdout, tracker = self.run_inference([self.success])
        self.assertEqual(run['clips'][0]['status'], 'missing_video')
        self.assertIn('elapsed_seconds', run['clips'][0])
        self.assertIn('clip_000: missing_video', stdout)
        self.assertEqual(tracker.call_count, 1)

    def test_invalid_buffer_rejected_before_creating_output(self):
        for value in ('0', '-1', '1.5'):
            with self.subTest(value=value), contextlib.redirect_stderr(io.StringIO()), \
                 self.assertRaises(SystemExit) as failure:
                infer.main(['--dataset', str(self.dataset), '--output', str(self.output),
                            '--dpvo-buffer-size', value])
            self.assertEqual(failure.exception.code, 2)
        self.assertFalse(self.output.exists())


class TrackingConfigurationTests(unittest.TestCase):
    def test_buffer_override_is_applied_after_yaml_without_mutating_shared_config(self):
        shared = Mock(BUFFER_SIZE=4096)
        configured = Mock(BUFFER_SIZE=4096)
        shared.clone.return_value = configured
        configured.merge_from_file.side_effect = lambda _: setattr(configured, 'BUFFER_SIZE', 4096)
        torch = SimpleNamespace(manual_seed=Mock(), no_grad=contextlib.nullcontext,
                                cuda=SimpleNamespace(empty_cache=Mock()))
        stream = Mock()
        stream.__iter__ = Mock(return_value=iter(()))
        modules = {'torch': torch, 'dpvo.config': SimpleNamespace(cfg=shared),
                   'dpvo.dpvo': SimpleNamespace(DPVO=Mock())}
        with patch.dict(sys.modules, modules), \
             patch.object(sys, 'path', list(sys.path)), \
             patch.object(tracking, 'DPVO_DIR', 'fake-dpvo'), \
             patch.object(tracking, 'ClipPreprocessor'), \
             patch.object(tracking, 'ClipStream', return_value=stream):
            with self.assertRaisesRegex(RuntimeError, 'no frames decoded'):
                tracking.track('unused.mp4', 'wide', 8, 1, dpvo_buffer_size=8192)
        self.assertEqual(shared.BUFFER_SIZE, 4096)
        self.assertEqual(configured.BUFFER_SIZE, 8192)
        configured.merge_from_file.assert_called_once()
        stream.close.assert_called_once()
        torch.cuda.empty_cache.assert_called_once()


if __name__ == '__main__':
    unittest.main()
