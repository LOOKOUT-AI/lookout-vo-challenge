# Development release v0.1

Published 23 September 2026.

The [full development dataset](https://macvi.org/downloads/lookout/v0.1/lookout-vo-dev-v0.1.tar)
is available without an account: **92 clips, 68 training and 24 validation**.
It includes all development videos, anonymous sequence IDs, frame timestamps,
nominal calibration, local reference trajectories, rules and the public starter.
Test clips remain withheld. The dataset is CC BY-NC 4.0 and the starter is MIT.

## Validation and limitations

- The source archive and every packaged file passed SHA-256 checks. All 92 clips
  passed public manifest/timing/reference validation, image-dimension checks and
  initial video decoding.
- The starter handles inaccurate container frame-count metadata and checks the
  actual decoded frame count against the released timing array. This matters for
  `clip_042`, whose container declares two more frames than are decoded.
- Released timing arrays include small monotonicity repairs. Nine clips contain
  intervals of approximately one microsecond: `clip_015`, `clip_032`, `clip_042`,
  `clip_046`, `clip_048`, `clip_049`, `clip_056`, `clip_069`, `clip_089`.
  Use the released times for prediction/scoring consistency. Timing quality and
  reference alignment remain development limitations; corrections will be versioned.
- Calibration is nominal and FOV-derived. References are local positions in metres
  with zero vertical coordinate; the evaluator scores position after global
  similarity alignment, not absolute scale or orientation.
- The maintainer has reported GPU baseline runs, but an independent run on the
  exact public package has not been completed. We do not publish an official
  baseline score or claim GPU reproduction from CPU checks. DPVO results vary
  between runs; report seeds, temporal coverage, scored/failed counts and spread.

## What follows

Participants can download the full package, run their own methods and evaluate
locally now. Online submissions, the leaderboard, final ranking/coverage rules and
competition dates will be announced separately. The development interface and
reference data may receive documented corrections.

Watch releases, report issues in this repository, or join the
[MaCVi community](https://macvi.org/discord) for updates.
