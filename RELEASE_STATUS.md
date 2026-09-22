# Development release progress

Updated 22 September 2026.

| Available now | Next release | Later |
| --- | --- | --- |
| Task, development rules and MIT-licensed starter code | The complete development dataset | Full competitive submission rules |
| DPVO inference wrapper and pinned setup guide | Video, timing, calibration and reference downloads | Online submission service |
| CPU evaluator and prediction format | Real RGB/thermal reproduction and public validation result | Leaderboard |
| Synthetic evaluator example | Final data coverage and release terms | Competition dates |

The synthetic example verifies the input/output workflow only. Real recordings are
not available in this repository, and no score is claimed as a reproduced result on
the forthcoming public dataset. Development rules and interfaces may evolve; changes
will be recorded here and in releases.

The current development selection is planned to contain 68 training and 24
validation clips. A thermal recording boat has been moved into validation, and
three clips with invalid frame timestamps have been removed. The published
manifest will define the final selection and RGB/thermal coverage.

The complete development package has been built and its maintainer reports
successful checksum, inference and scoring checks. The package handoff and an
independent check remain pending before public downloads are enabled. The next
dataset release will include the full development selection. Test data remains
withheld; online submissions and the leaderboard can follow separately.

The DPVO baseline varies between runs. The release should report all five existing
validation runs, their aggregate median and observed range, and scored/failed clip
and temporal coverage. The results will be published with the validation evidence.

Watch releases or join the [MaCVi community](https://macvi.org/discord) for updates.
