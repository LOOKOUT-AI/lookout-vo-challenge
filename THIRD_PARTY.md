# Upstream dependencies

This repository contains the LOOKOUT challenge wrapper and evaluator. It does not
bundle the DPVO implementation, its CUDA extensions, Eigen or pretrained weights.

- DPVO: https://github.com/princeton-vl/DPVO, pinned revision
  `859bbbfdac6c6185f345003b3c473901fcd13ace` in the setup guide. Follow the license,
  notices and checkpoint terms provided by that upstream project.
- NumPy: https://numpy.org/ — installed separately for evaluation.
- OpenCV and PyTorch: installed separately for inference, following the pinned
  environment in QUICKSTART.md and their upstream terms.

Retain upstream notices when installing or redistributing dependencies. A license
for this starter does not relicense the upstream projects, weights or dataset.
