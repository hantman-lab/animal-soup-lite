from fastplotlib.ui import EdgeWindow
from imgui_bundle import imgui


class ImguiBehavior(EdgeWindow):
    def __init__(self, figure, size, location, title, session):
        super().__init__(figure=figure, size=size, location=location, title=title)

        self.session = session
        self.current_index = 0
        self.current_video = self.session.get_trial(
            self.session.trials[self.current_index]
        )

        self._figure[0, 0].add_image(self.current_video[0], cmap="gray", name="frame")

    def update(self):
        data_options = self.session.trials

        imgui.text("Trial")
        imgui.same_line()
        selected, index = imgui.combo("##Trial", self.current_index, data_options, 10)

        if selected:
            self.current_index = index
            self.session.current_trial = index

        # reset button
        if imgui.button("Detect"):
            pass

        imgui.same_line()

        # reset button
        if imgui.button("Detect All"):
            pass

        # reset button
        if imgui.button("View Crop"):
            pass

        imgui.same_line()

        # reset button
        if imgui.button("Select Crop"):
            pass

        imgui.same_line()

        if imgui.button("Reset Crop"):
            pass

        if imgui.button("View Detection"):
            pass


class ImguiSlider(EdgeWindow):
    def __init__(self, figure, size, location, title, session):
        super().__init__(figure=figure, size=size, location=location, title=title)

        self.session = session

    def update(self):
        imgui.text("Frame")
        imgui.same_line()
        changed_index, new_index = imgui.slider_int(
            "##Frame", v=0, v_min=0, v_max=self.session.current_video.shape[0] - 1
        )

        if changed_index:
            self._figure[0, 0]["frame"].data = self.session.current_video[new_index]
