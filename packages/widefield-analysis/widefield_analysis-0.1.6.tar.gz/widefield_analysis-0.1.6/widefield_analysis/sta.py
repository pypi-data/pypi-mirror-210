"""Stimulus triggered averages."""

import numpy as np
import pandas as pd


def compute_stimulus_triggered_average(movie: np.ndarray, stim_periods: pd.DataFrame, start_offset: int = 0, end_offset: int = 0) -> np.ndarray:
    """Compute stimulus triggered average from stim periods."""
    repeat_movies = []
    for i_row, row in stim_periods.iterrows():
        start_index = row["first_frame"] + start_offset
        end_index = row["last_frame"] + 1 + end_offset
        single_repeat = movie[start_index:end_index, :, :]
        repeat_movies.append(single_repeat)
    min_length = np.min([single_movie.shape[0] for single_movie in repeat_movies])
    repeat_movies = [single_movie[:min_length, :, :] for single_movie in repeat_movies]
    repeat_tensor = np.stack(repeat_movies, axis=0)
    n_repeats = repeat_tensor.shape[0]
    print(f"Averaging over {n_repeats} repeats of {min_length} frames.")
    sta = np.mean(repeat_tensor, axis=0)
    return sta
