# LOOKOUT: Maritime Monocular Visual Odometry

Estimate a boat-mounted camera's trajectory from RGB or thermal video, calibration
and frame timestamps. Water reflections, waves, changing visibility and distant
shorelines make this a challenging setting for visual odometry.

**Public development preview — 18 September 2026.** The starter, prediction format,
local evaluator and a synthetic example are available now. Real dataset downloads,
a reproduced public-data baseline and participation dates are coming next.

[Challenge page](https://macvi.org/workshop/macvi27/challenges/lookout) ·
[Development rules](RULES.md) · [DPVO quick start](QUICKSTART.md) ·
[Release progress](RELEASE_STATUS.md)

## Try the evaluator now

Python 3.11 or 3.12 is sufficient. The synthetic example needs no GPU, video,
checkpoint, account or private data:

```bash
git clone https://github.com/LOOKOUT-AI/lookout-vo-challenge.git
cd lookout-vo-challenge
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-eval.txt
python examples/make_synthetic_example.py --output runs/synthetic
python starter/evaluate.py --dataset runs/synthetic/release_manifest.json --predictions runs/synthetic/run --split val
```

Inspect `runs/synthetic/run/predictions/clip_000.json` for the prediction format and
`runs/synthetic/run/summary.json` for the score and coverage counts. To try your own
trajectory writer, emit the same format and rerun the evaluator. Use a new output
directory when regenerating the example.

This is an artificial trajectory for testing the interface. It has no video and
cannot be used for inference, model training or a real-world performance claim.

## Prepare for the dataset

The planned development selection has 75 training and 20 validation clips, split
by recording boat, with RGB and thermal imagery. The released manifest will define
the final selection and camera coverage. Each sequence will have anonymous IDs,
video, decoded frame timestamps, nominal calibration and separate local-position
references. Test data remains withheld.

The inference wrapper uses DPVO; [QUICKSTART.md](QUICKSTART.md) records the pinned
upstream revision, environment and checkpoint checksum. You can prepare that
environment now. Running inference requires the forthcoming video package.

Allowed inference inputs are monocular video, calibration and frame timestamps.
GPS, IMU, AIS, speed and heading are not inference inputs. Read [RULES.md](RULES.md)
for training rules and the provisional local evaluation metric. Always report
coverage with scores. Online submissions and a competitive leaderboard will follow.

## Follow updates and contribute

Watch this repository's releases for dataset announcements. Use
[GitHub issues](https://github.com/LOOKOUT-AI/lookout-vo-challenge/issues) for starter
questions, interface feedback or reproducible bugs, and the
[MaCVi community](https://macvi.org/discord) for discussion.

The starter is developed by Harin Nallaguntla and LOOKOUT contributors. DPVO is a
separate upstream dependency; its code and pretrained weights are not redistributed
here. See [THIRD_PARTY.md](THIRD_PARTY.md).

## Terms

The code license is being finalized for this preview. No dataset license or rights
to recordings are granted by publication of this source. Dataset terms will accompany
the download. Upstream dependency and checkpoint terms apply separately.
