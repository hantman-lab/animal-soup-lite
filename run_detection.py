import fastplotlib as fpl

import argparse
from pathlib import Path
import numpy as np

from animal_soup_lite import Session, ImguiBehavior, ImguiSlider

figure = fpl.Figure(size=(1100, 900))

figure.show()

figure[0, 0].axes.visible = False
figure[0, 0].title = "Behavior Detection"


figure.show()


if __name__ == "__main__":
    # parse the command line args to get the video dir
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "video_dir",
        type=str,
        help="Path to video directory (i.e. /reaganbullins2/ProjectionProjection/rb50/20250125/videos/)",
    )
    parser.add_argument("output_dir", type=str, help="Path to output directory")

    args = parser.parse_args()

    # check if video dir exists
    video_dir = Path(args.video_dir)
    if not video_dir.is_dir():
        raise FileNotFoundError(f"Video directory {video_dir} not found")

    output_dir = Path(args.output_dir)
    if not video_dir.is_dir():
        raise FileNotFoundError(f"Video directory {video_dir} not found")

    session = Session(video_dir, output_dir)

    # make GUI instance
    gui = ImguiBehavior(
        figure,  # the figure this GUI instance should live inside
        size=275,  # width or height of the GUI window within the figure
        location="right",
        title="Behavior Detection",  # window title
        session=session,
    )

    gui2 = ImguiSlider(
        figure,  # the figure this GUI instance should live inside
        size=75,  # width or height of the GUI window within the figure
        location="bottom",
        title=" ",  # window title
        session=session,
    )

    # add it to the figure
    figure.add_gui(gui)
    figure.add_gui(gui2)

    figure[0, 0].auto_scale()
    figure[0, 0].camera.set_state({"scale": np.array([1, -1, 1])})

    fpl.loop.run()
