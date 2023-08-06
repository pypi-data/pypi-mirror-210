"""Delta F over F calculations."""

import numpy as np
import pandas as pd


def compute_delta_f_over_f(
        movie: np.ndarray,
        baselines: pd.DataFrame,
        start_offset: int = 0,
        end_offset: int = 0,
        method: str = "mean",
        apply_limits: bool = True,
        absolute_limit: float = 10.0,
) -> np.ndarray:
    """Compute delta F over F movies based on baselines."""
    n_frames = movie.shape[0]
    n_baselines = baselines.shape[0]
    movie = movie.astype(np.float32)
    for i_row, row in baselines.iterrows():
        baseline_start = row["first_frame"] + start_offset
        baseline_end = row["last_frame"] + 1 + end_offset

        current_baseline = row["i_baseline"]
        next_baseline = current_baseline + 1
        is_next = baselines["i_baseline"] == next_baseline

        if current_baseline == 0:
            print("First baseline scales movie from beginning.")
            scale_start = 0
        else:
            scale_start = baseline_start
        if current_baseline == (n_baselines - 1):
            print("Last baseline scales movie until ending.")
            scale_end = n_frames
        else:
            scale_end = baselines.loc[is_next, "first_frame"].values[0]

        n_baseline = baseline_end - baseline_start
        n_scale = scale_end - scale_start

        baseline_movie = movie[baseline_start:baseline_end, :, :]
        scale_movie = movie[scale_start:scale_end]

        if method == "mean":
            baseline_image = np.mean(baseline_movie, axis=0)
        elif method == "median":
            baseline_image = np.median(baseline_movie, axis=0)
        else:
            raise ValueError(f"{method=} unknown")
        scale_movie = (scale_movie - baseline_image) / baseline_image

        if apply_limits:
            scale_movie[scale_movie < -absolute_limit] = -absolute_limit
            scale_movie[scale_movie > absolute_limit] = absolute_limit
        print(f"Baseline {current_baseline} {baseline_start}:{baseline_end} ({n_baseline}) scales {scale_start}:{scale_end} ({n_scale})")
        print(f"\tAfter scaling: from {np.nanmin(scale_movie):.1f} to {np.nanmax(scale_movie)} dF/F ({apply_limits=}, {absolute_limit=:.1f})")
        movie[scale_start:scale_end, :, :] = scale_movie
    return movie
