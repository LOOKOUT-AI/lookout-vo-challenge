#!/usr/bin/env python3
"""Infer timestamped trajectories from a public video/calibration package; never reads references."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
from public_dataset import (asset_path, load_manifest, load_timestamps, select_clips,
                            sha256, validate_prediction, write_json)
from tracking import track


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dataset', required=True, type=Path, help='public release_manifest.json')
    ap.add_argument('--split', default='val', help='train, val, test, comma-separated, or all')
    ap.add_argument('--clips', help='comma-separated anonymous IDs; overrides --split')
    ap.add_argument('--output', required=True, type=Path, help='new predictions run directory')
    ap.add_argument('--target-fps', type=float, default=8.0)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args(argv)
    if not np.isfinite(args.target_fps) or args.target_fps <= 0:
        ap.error('--target-fps must be positive and finite')
    try:
        manifest = load_manifest(args.dataset)
        selected = select_clips(manifest, args.split, args.clips)
    except (OSError, ValueError, KeyError) as exc:
        ap.error(str(exc))
    if args.output.exists() and any(args.output.iterdir()):
        ap.error('--output must be new or empty; choose a new directory for each run')
    pred_dir = args.output / 'predictions'
    pred_dir.mkdir(parents=True, exist_ok=True)
    root = args.dataset.resolve().parent
    records = []
    run = dict(dataset_sha256=sha256(args.dataset), target_fps=args.target_fps,
               seed=args.seed, clips=records)
    for clip in selected:
        key = clip['key']
        record = dict(key=key, split=clip['split'])
        try:
            video = asset_path(root, clip['video'])
            if not video.is_file():
                record['status'] = 'missing_video'
            else:
                frame_times = load_timestamps(root, clip)
                poses, indices, pre = track(str(video), clip['camera_mode'], args.target_fps,
                                           args.seed, calibration=clip['calibration'],
                                           frame_timestamps=frame_times)
                prediction = dict(key=key,
                    frame_indices=[pre.decoded_index(int(i)) for i in indices],
                    times=[float(pre.frame_time(int(i))) for i in indices],
                    positions=np.asarray(poses)[:, :3].tolist())
                validate_prediction(prediction, key, frame_times)
                write_json(pred_dir / f'{key}.json', prediction)
                record.update(status='predicted', n_poses=len(indices))
        except Exception as exc:
            record.update(status='tracking_failed', reason=str(exc)[:300])
        records.append(record)
        write_json(args.output / 'inference_manifest.json', run)
        print(f"{key}: {record['status']}", flush=True)
    predicted = sum(r['status'] == 'predicted' for r in records)
    print(f'INFERENCE_COMPLETE: {len(records)} attempted, {predicted} predicted')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
