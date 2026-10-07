# Maritime monocular VO: development quick start

**Development release v0.1 is available.** Download and verify the full video
package using the [README instructions](https://github.com/LOOKOUT-AI/lookout-vo-challenge#download-the-full-development-dataset).
The commands below run from this repository's root, with the downloaded package
extracted to `release/` beneath it. Use the repository's current `starter/` code,
not the older copy bundled in the dataset archive. Read
[RELEASE_STATUS.md](RELEASE_STATUS.md) for current validation and timing limitations.

The `release/` directory contains `release_manifest.json`, `videos/`, `timing/`
and `references/`. No LOOKOUT account or private research files are required.
Read `release/LICENSE.txt` for the
release terms and `RULES.md` for the task and score definition.

## Verify the download

```bash
(cd release && sha256sum --check CHECKSUMS.sha256)
```

The manifest describes each anonymous clip, its split, image geometry, and asset paths.
Calibration is nominal and FOV-derived; it is not measured per camera. Its `fx/fy/cx/cy`
are in the full-resolution **cropped active image**. `active_rect` is `[x,y,width,height]`
in encoded-video pixels. The starter applies that crop, halves the resolution and
trims the bottom/right to multiples of 16, scaling the calibration accordingly.

## CPU evaluation setup

Python 3.11 or 3.12 with NumPy is sufficient for evaluation; it imports neither DPVO
nor OpenCV:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install numpy==1.26.4
```

## DPVO inference setup

The recorded baseline used DPVO commit `859bbbfdac6c6185f345003b3c473901fcd13ace`,
PyTorch `2.5.1+cu121`, CUDA toolkit 12.1, and OpenCV `4.10.0.84`.
The CUDA extension must be built against the installed PyTorch/CUDA combination.
Follow the [installation instructions at the pinned upstream commit](https://github.com/princeton-vl/DPVO/tree/859bbbfdac6c6185f345003b3c473901fcd13ace#setup-and-installation)
for Eigen 3.4.0 and the upstream dependencies. The viewer is optional; this starter
runs with visualization disabled. With that environment activated:

```bash
git clone --recursive https://github.com/princeton-vl/DPVO.git
git -C DPVO checkout 859bbbfdac6c6185f345003b3c473901fcd13ace
git -C DPVO submodule update --init --recursive
# Install the pinned environment/dependencies and Eigen as described above, then:
python -m pip install --no-build-isolation ./DPVO
python -m pip install numpy==1.26.4 opencv-python==4.10.0.84
export DPVO_DIR="$PWD/DPVO"
```

Obtain `dpvo.pth` from the models link in the pinned upstream README, put it inside
`DPVO_DIR`, and verify its SHA-256 is
`30d02dc2b88a321cf99aad8e4ea1152a44d791b5b65bf95ad036922819c0ff12`.
The checkpoint is not included in the dataset. The CPU package tests do not establish
that a new GPU/CUDA installation reproduces the recorded baseline.

## One clip

Every release contains `clip_000`; its split is recorded in the manifest.

```bash
python starter/infer.py --dataset release/release_manifest.json --clips clip_000 --output runs/demo
python starter/evaluate.py --dataset release/release_manifest.json --clips clip_000 --predictions runs/demo
```

Inference reads only video, calibration and frame timing. References can be removed or
made inaccessible during inference. Each run needs a new/empty output directory, so
old predictions cannot silently survive a failed rerun.

## Validation split

```bash
python starter/infer.py --dataset release/release_manifest.json --split val --target-fps 8 --seed 0 --output runs/val-seed0
python starter/evaluate.py --dataset release/release_manifest.json --split val --predictions runs/val-seed0
```

Evaluation writes `results.json` (one outcome per expected clip), `summary.json`
(expected/scored/unscored counts and statistics over scored clips), and optional aligned
trajectories. Always report coverage alongside drift. v0.1 provides local development;
there is no official ranking or failure penalty yet.

## Diagnosing a failed inference run

`inference_manifest.json` records the requested target frame rate, seed, buffer
override and each clip's status and elapsed inference time. Successful clips also
record native/effective frame rates and stride. The default target is **8**, not
80: a target above the video's native frame rate processes every decoded frame,
without creating new frames, and can substantially increase runtime and tracker
memory use. Inference time is separate from the CPU evaluator's runtime.

Clip start/completion messages show progress. Failed clips write their full Python
traceback to `logs/<clip-id>.log`; the manifest retains a short reason and log path.
Keep this directory with the predictions when reporting an issue. A run can finish
with failures, so check the predicted/scored counts rather than only the exit code.
Non-finite predictions remain failures; do not replace them with fabricated poses
or remove the affected clips from evaluation.

For a focused retry, preserve the original run and select only the failed clips:

```bash
python starter/infer.py --dataset release/release_manifest.json --clips clip_037,clip_050 --target-fps 8 --seed 1 --output runs/retry-failed-fps8
python starter/evaluate.py --dataset release/release_manifest.json --clips clip_037,clip_050 --predictions runs/retry-failed-fps8
```

If a clip still fails specifically because DPVO's keyframe buffer is too small,
retry it in another new directory with `--dpvo-buffer-size 8192`. This overrides
`BUFFER_SIZE` after loading DPVO's configuration; upstream's `--opts` flag is not
accepted by this wrapper. A larger buffer consumes more GPU memory and is a
diagnostic option, not a guaranteed fix or a change to the baseline default.
Report any changed settings with the results. A selected-clip retry is not a
complete validation run or an official leaderboard submission.

## Prediction format

Write `predictions/<clip-id>.json`, using your estimator's own coordinate frame and scale:

```json
{
  "key": "clip_000",
  "frame_indices": [3, 7],
  "times": [0.1, 0.23333333333333334],
  "positions": [[0.0, 0.0, 0.0], [1.2, 0.1, 0.0]]
}
```

This is a format illustration, not a scoreable trajectory. Use the actual entries from
`timing/<clip-id>.json`: indices identify decoded source-video frames, and `times[i]`
must equal that frame's released PTS within one microsecond. All arrays must have the
same length, with increasing indices/times and finite Nx3 positions.
