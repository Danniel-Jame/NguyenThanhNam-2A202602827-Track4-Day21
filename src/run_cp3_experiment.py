"""CP3 Experiment Script: Evaluation of LiDAR-Camera Calibration Sensitivity under Yaw/Perturbation Sweeps.

This script executes a benchmark experiment sweeping through various perturbation levels (e.g., yaw rotation degrees),
evaluates metrics such as point projection count, percentage inside image, and point density/distribution,
saves the quantitative evaluation to `results/yaw_perturb_sweep.csv`, and outputs plot figures into `results/figures/`.
"""

import os
import random
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from starter.datasets import dataset_type, load_frame
from starter.projection import perturb_extrinsic, project_velo_to_image


def set_seed(seed: int = 42) -> None:
    """Set random seed across standard libraries for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)


def run_yaw_sweep_experiment(
    data_root: str = "data/kitti_mini",
    frame_id: str = "000011",
    yaw_degrees: list[float] = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0],
    seed: int = 42,
    csv_output_path: str = "results/yaw_perturb_sweep.csv",
    plot_output_path: str = "results/figures/yaw_perturb_sweep_plot.png"
) -> pd.DataFrame:
    """Executes a sweep over yaw perturbations and computes projection metrics."""
    set_seed(seed)

    # Ensure output directories exist
    Path(csv_output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(plot_output_path).parent.mkdir(parents=True, exist_ok=True)

    kwargs = {"use_ego_motion": True} if dataset_type(data_root) == "nuscenes" else {}
    frame_data = load_frame(data_root, frame_id, **kwargs)

    raw_points = frame_data["points"]
    calib_base = frame_data["calib"]
    img_shape = frame_data["image"].shape
    labels = frame_data["labels"]

    total_points = len(raw_points)
    results = []

    print(f"--- Running CP3 Sweep Experiment on frame '{frame_id}' ---")
    print(f"Total LiDAR Points: {total_points}")

    for yaw in yaw_degrees:
        # Apply yaw perturbation
        calib_perturbed = perturb_extrinsic(calib_base, yaw_deg=yaw)

        # Perform projection
        uv, depth, mask = project_velo_to_image(raw_points, calib_perturbed, img_shape)

        points_inside = int(mask.sum())
        ratio_inside = float(mask.mean())
        mean_depth = float(depth.mean()) if len(depth) > 0 else 0.0
        std_depth = float(depth.std()) if len(depth) > 0 else 0.0

        # Optional: Count points falling inside 2D bounding boxes of labels
        points_in_boxes = 0
        if len(uv) > 0 and len(labels) > 0:
            for obj in labels:
                x1, y1, x2, y2 = obj.bbox
                inside_box = (uv[:, 0] >= x1) & (uv[:, 0] <= x2) & (uv[:, 1] >= y1) & (uv[:, 1] <= y2)
                points_in_boxes += int(inside_box.sum())

        results.append({
            "frame_id": frame_id,
            "seed": seed,
            "yaw_deg": yaw,
            "total_points": total_points,
            "points_inside_image": points_inside,
            "pct_inside_image": ratio_inside * 100.0,
            "points_inside_2d_boxes": points_in_boxes,
            "mean_depth": mean_depth,
            "std_depth": std_depth
        })

        print(f"Yaw: {yaw:4.1f}° | Points Inside: {points_inside:6d} ({ratio_inside*100:5.2f}%) | In 2D BBoxes: {points_in_boxes}")

    # Convert results to DataFrame and export to CSV
    df = pd.DataFrame(results)
    df.to_csv(csv_output_path, index=False)
    print(f"\n[PASS] Saved metrics CSV to '{csv_output_path}'")

    # Generate and save evaluation plot
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(df["yaw_deg"], df["pct_inside_image"], marker='o', color='b', linewidth=2)
    plt.title("LiDAR Points Inside Image vs. Yaw Perturbation")
    plt.xlabel("Yaw Perturbation (degrees)")
    plt.ylabel("% Points Projected in Image")
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.subplot(1, 2, 2)
    plt.plot(df["yaw_deg"], df["points_inside_2d_boxes"], marker='s', color='r', linewidth=2)
    plt.title("Points Inside Bounding Boxes vs. Yaw Perturbation")
    plt.xlabel("Yaw Perturbation (degrees)")
    plt.ylabel("Point Count inside 2D BBoxes")
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig(plot_output_path, dpi=300)
    plt.close()
    print(f"[PASS] Saved plot figure to '{plot_output_path}'\n")

    return df


if __name__ == "__main__":
    # Run experiment with fixed random seed
    run_yaw_sweep_experiment(
        data_root="data/kitti_mini",
        frame_id="000011",
        yaw_degrees=[0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0],
        seed=42
    )