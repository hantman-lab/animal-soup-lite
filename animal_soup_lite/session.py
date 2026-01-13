from pathlib import Path

from animal_soup_lite.utils import LazyVideo


class Session:
    def __init__(self, video_dir: Path):
        """Class for managing all of the current sessions video data."""

        self._video_dir = video_dir
        self._trials = self._compute_trials()

        self._current_trial = self._trials[0]
        self._current_video = self.get_trial(self._current_trial)

    @property
    def video_dir(self):
        return self._video_dir

    @property
    def trials(self):
        return self._trials

    @property
    def current_trial(self):
        return self._current_trial

    @current_trial.setter
    def current_trial(self, index: int):
        self._current_trial = self._trials[index]
        self._current_video = self.get_trial(self._current_trial)
        print(self._current_video.shape)

    @property
    def current_video(self):
        return self._current_video

    def _compute_trials(self):
        """Use `pathlib.Path.glob` to get the trials for this session."""
        # get trials by globbing
        trials = list()
        # only get the side trials
        for f in self.video_dir.glob("*_side_v*.avi"):
            trials.append(str(f)[-7:-4])
        return trials

    def get_trial(self, trial_no: str):
        """Returns an array representation of the video data for a particular trial."""
        trial_path = next(self.video_dir.glob(f"*_side_v{trial_no}*.avi"))
        video = LazyVideo(trial_path)
        return video
