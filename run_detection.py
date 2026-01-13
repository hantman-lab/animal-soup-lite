import fastplotlib as fpl
from fastplotlib.ui import EdgeWindow
from imgui_bundle import imgui
# import numpy as np
# import cv2

figure = fpl.Figure(size=(1100, 900), names=["animal_id"])

figure.show()

figure[0, 0].axes.visible = False


class ImguiExample(EdgeWindow):
    def __init__(self, figure, size, location, title):
        super().__init__(figure=figure, size=size, location=location, title=title)

    def update(self):
        _changed_alpha, _new_alpha = imgui.slider_float(
            "alpha", v=0.5, v_min=0.0, v_max=1.0
        )

        # reset button
        if imgui.button("reset"):
            pass


# make GUI instance
gui = ImguiExample(
    figure,  # the figure this GUI instance should live inside
    size=275,  # width or height of the GUI window within the figure
    location="right",
    title="Behavior Detection",  # window title
)

# add it to the figure
figure.add_gui(gui)


if __name__ == "__main__":
    # TODO: parse command line args to get data dir
    fpl.loop.run()
