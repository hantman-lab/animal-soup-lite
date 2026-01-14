from fastplotlib.ui import EdgeWindow
from fastplotlib import RectangleSelector
from imgui_bundle import imgui
from animal_soup_lite.utils import DefaultCrops

FRAME_NUM = 0


class ImguiBehavior(EdgeWindow):
    def __init__(self, figure, size, location, title, session):
        super().__init__(figure=figure, size=size, location=location, title=title)

        self.session = session
        self.current_index = 0
        self.current_video = self.session.get_trial(
            self.session.trials[self.current_index]
        )

        self._figure[0, 0].add_image(self.current_video[0], cmap="gray", name="frame")

        self.current_crop = DefaultCrops.LIFT.value

        self.rect_selector = None

    def update(self):
        global FRAME_NUM
        data_options = self.session.trials

        imgui.text("Trial")
        imgui.same_line()
        selected, index = imgui.combo("##Trial", self.current_index, data_options, 10)

        if selected:
            self.current_index = index
            self.session.current_trial = index
            FRAME_NUM = 0
            self._figure[0, 0]["frame"].data[:] = self.session.current_video[FRAME_NUM]

        # reset button
        if imgui.button("Detect"):
            print(f"Detecting for trial: {self.session.current_trial}")
            self.session.detect(self.current_crop)

        imgui.same_line()

        # reset button
        if imgui.button("Detect All"):
            print("DETECTING ALL TRIALS")
            self.session.detect_all(self.current_crop)

        # reset button
        if imgui.button("View Crop"):
            # check to see if rectangle selector already exists
            if self.rect_selector is None:
                self.rect_selector = RectangleSelector(
                    selection=self.current_crop,
                    limits=(
                        0,
                        self.current_video[0].shape[1],
                        0,
                        self.current_video[0].shape[0],
                    ),
                    resizable=False,
                )
                self._figure[0, 0].add_graphic(self.rect_selector, center=False)
            else:
                self.rect_selector.selection = self.current_crop

        imgui.same_line()

        # reset button
        if imgui.button("Select Crop"):
            if self.rect_selector is None:
                return
            print("new crop")
            self.current_crop = [int(_) for _ in self.rect_selector.selection]

        imgui.same_line()

        if imgui.button("Reset Crop"):
            if self.rect_selector is None:
                return
            self.rect_selector.selection = DefaultCrops.LIFT.value
            self.current_crop = DefaultCrops.LIFT.value

        if imgui.button("View Detection"):
            frame_detected = self.session.detect_logger.df.loc[
                self.current_index, "frame_detected"
            ]
            if frame_detected is None:
                print("No frame detected")
                return
            FRAME_NUM = frame_detected
            self._figure[0, 0]["frame"].data[:] = self.session.current_video[
                frame_detected
            ]

        if imgui.button("Save"):
            print("SAVING")
            self.session.detect_logger.save()


class ImguiSlider(EdgeWindow):
    def __init__(self, figure, size, location, title, session):
        super().__init__(figure=figure, size=size, location=location, title=title)

        self.session = session

    def update(self):
        global FRAME_NUM
        imgui.text("Frame")
        imgui.same_line()
        changed_index, new_index = imgui.slider_int(
            "##Frame",
            v=FRAME_NUM,
            v_min=0,
            v_max=self.session.current_video.shape[0] - 1,
        )

        if changed_index:
            self._figure[0, 0]["frame"].data[:] = self.session.current_video[new_index]
            self._figure[0, 0].auto_scale()
            FRAME_NUM = new_index
