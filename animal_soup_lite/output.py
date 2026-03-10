import pandas as pd
from pathlib import Path

from .utils import logger

COLUMNS = ["trial_number", "lift_frame", "lift_ms", "grab_frame", "grab_ms"]


class DetectionLogger:
    def __init__(self, output_dir: Path | str, trials: list, prefix: str):
        self.output_dir = Path(output_dir)
        self.trials = trials
        self.df = pd.DataFrame(columns=COLUMNS)
        self._prefix = prefix

        # initialize
        for t in self.trials:
            self.df.loc[len(self.df.index)] = [t, None, None, None, None]

    def log(self, trial: str, frame_detected, motif: str):
        # convert frame to ms
        ms = int((frame_detected - 500) * 2)
        # get df ix of trial being detected
        ix = self.trials.index(trial)

        # update
        if motif == "lift":
            self.df.loc[ix, ["lift_frame", "lift_ms"]] = [frame_detected, ms]
        elif motif == "grab":
            self.df.loc[ix, ["grab_frame", "grab_ms"]] = [frame_detected, ms]

    def save(self):
        """Save the dataframe to disk."""
        self.df.to_pickle(self.output_dir.joinpath(f"{self._prefix}_detect.pkl"))

    def print(self):
        output = list()
        output.append("\n")
        for _, r in self.df.iterrows():
            s = f"Trial: {r['trial_number']}, Lift Frame: {r['lift_frame']}, Grab Frame: {r['grab_frame']}"
            output.append(s)

        logger.info("\n".join(output))

    def load(self, previous_run: Path, video_dir: Path):
        self.df = pd.read_pickle(previous_run)

        if self.df.attrs["video_dir"] != video_dir:
            raise ValueError(
                f"Trying to load previous run for a different video dir. Expected video dir was {self.df.attr['video_dir']}, but got {video_dir}"
            )
