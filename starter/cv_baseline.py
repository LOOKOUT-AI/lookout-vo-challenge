#!/usr/bin/env python3
"""Write a constant-velocity straight-line trajectory from frame timestamps only; reads no video or references."""
from __future__ import annotations
import argparse
from pathlib import Path
from public_dataset import load_manifest, load_timestamps, select_clips, sha256, validate_prediction, write_json


def predict(key, frame_times):
    # Unit speed along a fixed axis. The evaluator's Sim(3) fit supplies heading and scale.
    t0 = float(frame_times[0])
    return dict(key=key, frame_indices=list(range(len(frame_times))),
                times=[float(t) for t in frame_times],
                positions=[[float(t) - t0, 0.0, 0.0] for t in frame_times])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dataset', required=True, type=Path, help='public release_manifest.json')
    ap.add_argument('--split', default='val', help='train, val, test, comma-separated, or all')
    ap.add_argument('--clips', help='comma-separated anonymous IDs; overrides --split')
    ap.add_argument('--output', required=True, type=Path, help='new predictions run directory')
    args = ap.parse_args(argv)
    try:
        manifest = load_manifest(args.dataset)
        selected = select_clips(manifest, args.split, args.clips)
    except (OSError, ValueError, KeyError) as exc:
        ap.error(str(exc))
    if args.output.exists() and any(args.output.iterdir()):
        ap.error('--output must be new or empty; choose a new directory for each run')
    root = args.dataset.resolve().parent
    for clip in selected:
        frame_times = load_timestamps(root, clip)
        prediction = predict(clip['key'], frame_times)
        validate_prediction(prediction, clip['key'], frame_times)
        write_json(args.output / 'predictions' / f"{clip['key']}.json", prediction)
        print(f"{clip['key']}: {len(frame_times)} poses", flush=True)
    write_json(args.output / 'inference_manifest.json',
               dict(dataset_sha256=sha256(args.dataset), method='constant-velocity straight line',
                    inputs='frame timestamps only', clips=[c['key'] for c in selected]))
    print(f'CV_BASELINE_COMPLETE: {len(selected)} clips')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
