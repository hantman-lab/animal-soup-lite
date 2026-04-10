from pathlib import Path
from tqdm import tqdm
import cv2
import sys

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

        self._detect_logger = DetectionLogger(
            self._output_dir, self._trials, self._prefix
        )

        self._lift_threshold = 180
        self._grab_threshold = 150

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
    def lift_threshold(self):
        return self._lift_threshold

    @lift_threshold.setter
    def lift_threshold(self, value: int):
        self._lift_threshold = value

    @property
    def grab_threshold(self):
        return self._grab_threshold

    @grab_threshold.setter
    def grab_threshold(self, value: int):
        self._grab_threshold = value

    @property
    def current_video(self):
        return self._current_video

    def _compute_trials(self):
        """Use `pathlib.Path.glob` to get the trials for this session."""
        # get trials by globbing
        trials = list()
        # only get the side trials
        videos = list(self.video_dir.glob("*_side_v*.avi"))
        if len(videos) == 0:
            logger.info("No video files found. Exiting.")
            sys.exit(0)
        for f in videos:
            trials.append(str(f)[-7:-4])
        self._prefix = Path(f).stem.split("_s")[0]
        trials.sort()
        return trials

    def get_trial(self, trial_no: str):
        """Returns an array representation of the video data for a particular trial."""
        trial_path = next(self.video_dir.glob(f"*_side_v{trial_no}*.avi"))
        video = LazyVideo(trial_path)
        return video

    def detect_lift(self, crop):
        try:
            for i in tqdm(range(550, 900)):
                orig_frame = self.current_video[i]
                orig_frame = cv2.cvtColor(orig_frame, cv2.COLOR_RGB2GRAY)
                frame = orig_frame[crop[2] : crop[3], crop[0] : crop[1]]

                if (frame != 0).sum() >= self.lift_threshold:
                    logger.info("LIFT DETECTED")
                    self.detect_logger.log(self.current_trial, i, "lift")
                    self.detect_logger.save()
                    break
        except Exception:
            logger.info(f"Could not detect lift for trial {self.current_trial}")

    def detect_grab(self, crop):
        try:
            for i in tqdm(range(600, 1000)):
                orig_frame = self.current_video[i]
                orig_frame = cv2.cvtColor(orig_frame, cv2.COLOR_RGB2GRAY)
                frame = orig_frame[crop[2] : crop[3], crop[0] : crop[1]]

                if (frame != 0).sum() >= self.grab_threshold:
                    logger.info("GRAB DETECTED")
                    self.detect_logger.log(self.current_trial, i + 6, "grab")
                    self.detect_logger.save()
                    break
        except Exception:
            logger.info(f"Could not detect grab for trial {self.current_trial}")

    def detect_all(self, lift_crop, grab_crop):
        for t in tqdm(self._trials):
            try:
                video = self.get_trial(t)
                lift = 600
                for i in range(550, 900):
                    orig_frame = video[i]
                    orig_frame = cv2.cvtColor(orig_frame, cv2.COLOR_RGB2GRAY)
                    frame = orig_frame[
                        lift_crop[2] : lift_crop[3], lift_crop[0] : lift_crop[1]
                    ]

                    if (frame != 0).sum() >= 180:
                        self.detect_logger.log(t, i, "lift")
                        lift = i
                        break

                for i in range(lift, 1000):
                    orig_frame = video[i]
                    orig_frame = cv2.cvtColor(orig_frame, cv2.COLOR_RGB2GRAY)
                    frame = orig_frame[
                        grab_crop[2] : grab_crop[3], grab_crop[0] : grab_crop[1]
                    ]

                    if (frame != 0).sum() >= 150:
                        self.detect_logger.log(t, i + 6, "grab")
                        break
            except Exception:
                logger.info(f"Could not detect for trial {t}")

        logger.info(self.detect_logger.print())
        self.detect_logger.save()

    def get_detection_info(self):
        ix = self._trials.index(self.current_trial)
        detection = self.detect_logger.df.loc[ix, ["lift_frame", "grab_frame"]]
        return {"lift": detection["lift_frame"], "grab": detection["grab_frame"]}
