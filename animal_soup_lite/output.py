import pandas as pd
from datetime import datetime
from pathlib import Path

COLUMNS = ["trial_number", "frame_detected", "lift_ms"]


class DetectionLogger:
    def __init__(self, output_dir: Path | str, trials: list):
        self.output_dir = Path(output_dir)
        self.trials = trials
        self.df = pd.DataFrame(columns=COLUMNS)

        # initialize
        for t in self.trials:
            self.df.loc[len(self.df.index)] = [t, None, None]

    def log(self, trial: str, frame_detected: int):
        print("Saving frame detected for trial {}".format(trial))
        # convert frame to ms
        ms = int((frame_detected - 500) / 2)
        # get df ix of trial being detected
        ix = self.trials.index(trial)
        # update
        self.df.loc[ix, ["frame_detected", "lift_ms"]] = [frame_detected, ms]

    def save(self):
        """Save the dataframe to disk."""
        self.df.to_pickle(
            self.output_dir.joinpath(
                f"detect_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.pkl"
            )
        )
        print(self.df.head(n=8))
