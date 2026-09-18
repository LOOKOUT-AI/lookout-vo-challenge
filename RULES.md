# MaCVi maritime monocular VO — v0.1 development rules

## Task and allowed inputs

Estimate a camera trajectory from **monocular video, camera calibration, and video frame
timestamps**. GPS, IMU, AIS, speed, heading, attitude and other clip-specific navigation
signals are not inference inputs. The train/validation reference files are evaluation
labels, separate from the inputs. Test clips and references are withheld from this
development release.

Train on the provided training split. External pretraining is allowed and must be
disclosed. Use validation references for development/evaluation; do not train on the
validation or test splits, including self-supervised training on their videos. These
development rules do not establish final competition dates or submission rules.

## Data and predictions

The public manifest uses anonymous `clip_NNN` IDs. It contains video/timing/reference
paths and full calibration, without source device identifiers or storage paths. The
coordinate and prediction formats are specified in `QUICKSTART.md`.

Reference trajectories contain only `key`, `times`, and local three-dimensional
`positions` in metres. East and north come from the cleaned navigation reference;
up is zero because this is a horizontal position reference. The first reference position
is zero and no geographic origin is distributed. Reference times use the same seconds
clock as the released video PTS, including the organizer's reviewed clock offset.

Predictions need not share reference axes, origin or scale. Submit a self-consistent
timestamped trajectory and its decoded source-frame indices. Orientation is not scored.

## Metric

For each clip, interpolate the prediction onto reference times in their overlapping
window. Fit one global similarity transform (rotation, translation and scale). For
each reference path length in `{100,200,...,800}` metres and each start index sampled
at stride 10 on that reference window, find the first endpoint reaching that length.
The segment must span at least three reference-index intervals. Compute

`100 * ||(E[j]-E[i]) - (G[j]-G[i])|| / segment_length`.

Drift is the mean over eligible segments. There is no per-segment alignment. This is
a **position-only, globally scale-aligned relative-displacement metric** inspired by
KITTI; it is not the full KITTI pose metric and does not measure recovered metric scale.
ATE is also reported. `starter/metrics.py` is the implementation.

## Coverage and failure reporting

Choose the expected split or explicit clip list independently of prediction files.
The evaluator emits one record for every expected clip:

| Status | Meaning |
|---|---|
| `scored` | Valid trajectory with an eligible drift metric |
| `missing_prediction` | No prediction file for an expected clip |
| `invalid_prediction` | Invalid JSON, dimensions, indices or timestamps |
| `non_finite_estimate` | Non-finite position values |
| `no_overlap` | Fewer than ten reference samples in the shared time window |
| `degenerate_estimate` | Global alignment cannot be computed |
| `no_eligible_segment` | No eligible 100–800 m segment |
| `missing_gt` | A manifest declares withheld test references |
| `invalid_dataset` | Required dataset timing/reference file is missing or invalid |

Inference records tracking/decode failures separately and does not emit a prediction for
them. The evaluator consequently records those expected clips as missing predictions.
Unexpected prediction IDs are listed in the summary and excluded from scoring.

The summary reports expected/scored/unscored counts and mean/median drift **over scored
clips only**. Per-clip temporal coverage and maximum prediction-time gap are recorded.
Shortened trajectories are evaluated over their shared window, so coverage must accompany
scores. v0.1 defines no official ranking, coverage threshold or failure penalty; these
must be settled before a competitive leaderboard. A low drift over a small selected
subset must not be presented as full-dataset performance.

## Release scope and terms

This version supports local development/evaluation. The submission server, competition
dates and final leaderboard policy will follow separately. Consult the supplied
`LICENSE.txt` for the approved release terms and retain upstream notices for dependencies.
