from fastplotlib.ui import EdgeWindow
from fastplotlib import RectangleSelector
from imgui_bundle import imgui
from .utils import logger, defaults

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

        # try to load from disk is possible
        defaults.load()

        self.current_lift_crop = defaults.CONFIG["LIFT"]
        self.current_grab_crop = defaults.CONFIG["GRAB"]

        self.rect_selector_lift = None
        self.rect_selector_grab = None

        self._figure.renderer.add_event_handler(self._key_modifiers, "key_up")

    def _center_label(self, text: str):
        """Helper function to create a centered label bounded above and below by a separator."""
        # first separator
        imgui.separator()
        # calculate where the centered text should be
        avail = imgui.get_content_region_avail().x
        text_w = imgui.calc_text_size(text).x
        # set render position for the text
        imgui.set_cursor_pos_x((avail - text_w) * 0.5)
        imgui.text(text)
        # second separator
        imgui.separator()

    def _key_modifiers(self, ev):
        global FRAME_NUM
        if "Shift" in ev.modifiers:
            match ev.key:
                case "ArrowRight":
                    self.current_index += 1
                    if self.current_index >= len(self.session.trials):
                        self.current_index = 0
                    self.session.current_trial = self.current_index
                    self._figure[0, 0]["frame"].data[:] = self.session.current_video[
                        FRAME_NUM
                    ]
                case "ArrowLeft":
                    self.current_index -= 1
                    if self.current_index < 0:
                        self.current_index = len(self.session.trials) - 1
                    self.session.current_trial = self.current_index
                    self._figure[0, 0]["frame"].data[:] = self.session.current_video[
                        FRAME_NUM
                    ]
                case "M":  # mark grab
                    self.session.detect_logger.log(
                        self.session.current_trial, FRAME_NUM, "grab"
                    )
                    self.session.detect_logger.save()
                case "S":  # save
                    self.session.detect_logger.save()
        else:
            match ev.key:
                case "ArrowRight":
                    FRAME_NUM += 3
                    if FRAME_NUM > self.current_video.shape[0] - 1:
                        FRAME_NUM = 0
                    self._figure[0, 0]["frame"].data[:] = self.session.current_video[
                        FRAME_NUM
                    ]
                    self._figure[0, 0].auto_scale()
                case "ArrowLeft":
                    FRAME_NUM -= 3
                    if FRAME_NUM < 0:
                        FRAME_NUM = self.current_video.shape[0] - 1
                    self._figure[0, 0]["frame"].data[:] = self.session.current_video[
                        FRAME_NUM
                    ]
                    self._figure[0, 0].auto_scale()
                case "m":  # mark lift
                    self.session.detect_logger.log(
                        self.session.current_trial, FRAME_NUM, "lift"
                    )
                    self.session.detect_logger.save()

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

        detection = self.session.get_detection_info()
        imgui.text(f"Lift: {detection['lift']}")
        imgui.text(f"Grab: {detection['grab']}")

        # section for lift
        self._center_label("Lift")

        # reset button
        if imgui.button("Detect##lift"):
            logger.info(f"Detecting for trial: {self.session.current_trial}")
            self.session.detect_lift(self.current_lift_crop)
            self.session.detect_logger.save()

        # reset button
        if imgui.button("View Crop##lift"):
            # check to see if rectangle selector already exists
            if self.rect_selector_lift is None:
                self.rect_selector_lift = RectangleSelector(
                    selection=self.current_lift_crop,
                    limits=(
                        0,
                        self.current_video[0].shape[1],
                        0,
                        self.current_video[0].shape[0],
                    ),
                    resizable=True,
                    edge_thickness=4,
                )
                self._figure[0, 0].add_graphic(self.rect_selector_lift, center=False)
            else:
                self.rect_selector_lift.selection = self.current_lift_crop

        imgui.same_line()

        # reset button
        if imgui.button("Select Crop##lift"):
            if self.rect_selector_lift is None:
                return
            logger.info("New lift crop")
            self.current_lift_crop = [int(_) for _ in self.rect_selector_lift.selection]

        imgui.same_line()

        if imgui.button("Reset Crop##lift"):
            if self.rect_selector_lift is None:
                return
            self.rect_selector_lift.selection = defaults.CONFIG["LIFT"]
            self.current_lift_crop = defaults.CONFIG["LIFT"]

        if imgui.button("Save Crop##lift"):
            if self.rect_selector_lift is not None:
                self.current_lift_crop = [
                    int(_) for _ in self.rect_selector_lift.selection
                ]
                defaults.CONFIG["LIFT"] = self.current_lift_crop
                defaults.save()

        if imgui.button("View Detection##lift"):
            frame_detected = self.session.detect_logger.df.loc[
                self.current_index, "lift_frame"
            ]
            if frame_detected is None:
                logger.info("No frame detected")
                return
            self._figure[0, 0]["frame"].data[:] = self.session.current_video[
                frame_detected
            ]
            FRAME_NUM = frame_detected

        imgui.text("Thresh:")
        imgui.same_line()
        changed, val = imgui.input_int("##Threshlift", self.session.lift_threshold)
        if changed:
            self.session.lift_threshold = val

        # section for grab
        self._center_label("Grab")

        # detect button
        if imgui.button("Detect##grab"):
            logger.info(f"Detecting for trial: {self.session.current_trial}")
            self.session.detect_grab(self.current_grab_crop)
            self.session.detect_logger.save()

        # reset button
        if imgui.button("View Crop##grab"):
            # check to see if rectangle selector already exists
            if self.rect_selector_grab is None:
                self.rect_selector_grab = RectangleSelector(
                    selection=self.current_grab_crop,
                    limits=(
                        0,
                        self.current_video[0].shape[1],
                        0,
                        self.current_video[0].shape[0],
                    ),
                    resizable=True,
                    edge_thickness=4,
                    edge_color=(0.5, 0.0, 0.0),
                    vertex_color=(0.7, 0.0, 0.0),
                )
                self._figure[0, 0].add_graphic(self.rect_selector_grab, center=False)
            else:
                self.rect_selector_grab.selection = self.current_grab_crop

        imgui.same_line()

        # reset button
        if imgui.button("Select Crop##grab"):
            if self.rect_selector_grab is None:
                return
            logger.info("New grab crop")
            self.current_grab_crop = [int(_) for _ in self.rect_selector_grab.selection]

        imgui.same_line()

        if imgui.button("Reset Crop##grab"):
            if self.rect_selector_grab is None:
                return
            self.rect_selector_grab.selection = defaults.CONFIG["GRAB"]
            self.current_grab_crop = defaults.CONFIG["GRAB"]

        if imgui.button("Save Crop##grab"):
            if self.rect_selector_grab is not None:
                self.current_grab_crop = [
                    int(_) for _ in self.rect_selector_grab.selection
                ]
                defaults.CONFIG["GRAB"] = self.current_grab_crop
                defaults.save()

        if imgui.button("View Detection##grab"):
            frame_detected = self.session.detect_logger.df.loc[
                self.current_index, "grab_frame"
            ]
            if frame_detected is None:
                logger.info("No frame detected")
                return
            self._figure[0, 0]["frame"].data[:] = self.session.current_video[
                frame_detected
            ]
            FRAME_NUM = frame_detected

        imgui.text("Thresh:")
        imgui.same_line()
        changed, val = imgui.input_int("##Threshgrab", self.session.grab_threshold)
        if changed:
            self.session.grab_threshold = val

        self._center_label("Miscellaneous")

        # reset button
        if imgui.button("Detect All"):
            logger.info("DETECTING ALL TRIALS")
            self.session.detect_all(self.current_lift_crop, self.current_grab_crop)

        if imgui.button("Save"):
            logger.info("SAVING")
            self.session.detect_logger.save()

        imgui.same_line()

        if imgui.button("Print"):
            self.session.detect_logger.print()

        if imgui.button("Clear crop"):
            if self.rect_selector_lift is not None:
                self._figure[0, 0].delete_graphic(self.rect_selector_lift)
                self.rect_selector_lift = None
            if self.rect_selector_grab is not None:
                self._figure[0, 0].delete_graphic(self.rect_selector_grab)
                self.rect_selector_grab = None


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
