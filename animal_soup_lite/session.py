from pathlib import Path
from tqdm import tqdm
import cv2

from animal_soup_lite.output import DetectionLogger
from animal_soup_lite.utils import LazyVideo
from .utils import logger, setup_log_file_handler


class Session:
    def __init__(self, video_dir: Path):
        """Class for managing all of the current sessions video data."""

        self._video_dir = video_dir
        self._output_dir = "./output"
        self._trials = self._compute_trials()

        self._current_trial = self._trials[0]
        self._current_video = self.get_trial(self._current_trial)

        self._detect_logger = DetectionLogger(self._output_dir, self._trials)

        # Apply some config
        logger.setLevel("INFO")
        setup_log_file_handler(Path("./logs"))
        logger.info("Starting animal-soup-lite application.")

        logger.info(self._detect_logger.df.head(n=8))

    @property
    def video_dir(self):
        return self._video_dir

    @property
    def detect_logger(self):
        return self._detect_logger

    @property
    def trials(self):
        return self._trials

    @property
    def current_trial(self):
        return self._current_trial

    @current_trial.setter
    def current_trial(self, index: int):
        self._current_trial = self._trials[index]
        logger.info("Changing video")
        self._current_video = self.get_trial(self._current_trial)

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
        trials.sort()
        return trials

    def get_trial(self, trial_no: str):
        """Returns an array representation of the video data for a particular trial."""
        trial_path = next(self.video_dir.glob(f"*_side_v{trial_no}*.avi"))
        video = LazyVideo(trial_path)
        return video

    def detect(self, crop):
        try:
            for i in tqdm(range(550, 900)):
                orig_frame = self.current_video[i]
                orig_frame = cv2.cvtColor(orig_frame, cv2.COLOR_RGB2GRAY)
                frame = orig_frame[crop[2] : crop[3], crop[0] : crop[1]]

                if (frame != 0).sum() >= 180:
                    logger.info("LIFT DETECTED")
                    self.detect_logger.log(self.current_trial, i, orig_frame)
                    break
        except Exception:
            logger.info(f"Could not detect for trial {self.current_trial}")

    def detect_all(self, crop):
        for t in tqdm(self._trials):
            try:
                video = self.get_trial(t)
                for i in tqdm(range(550, 900)):
                    orig_frame = video[i]
                    orig_frame = cv2.cvtColor(orig_frame, cv2.COLOR_RGB2GRAY)

                    frame = orig_frame[crop[2] : crop[3], crop[0] : crop[1]]

                    if (frame != 0).sum() >= 180:
                        self.detect_logger.log(t, i, orig_frame)
                        break
            except Exception:
                logger.info(f"Could not detect for trial {t}")

        self.detect_logger.save()
