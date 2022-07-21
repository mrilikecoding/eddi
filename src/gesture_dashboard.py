import cv2
import numpy as np

from src import utils
from global_config import global_config


class GestureDashboard:
    def __init__(self):
        self.sequence_viewer_counter = 0
        self.mouse_pos = (None, None)
        self.gesture_comparer = None
        self.name = "Gesture Dashboard"

    def set_comparer_instance(self, gesture_comparer):
        self.gesture_comparer = gesture_comparer

    def display_dashboard(self):
        gc = self.gesture_comparer
        if len(gc.gesture_sequence_library) == 0:
            return

        max_len = global_config["gesture_heuristics"]["maximum_frame_count"]
        c = self.sequence_viewer_counter
        frames = []

        similar_gesture_detected = False
        if gc.most_similar_sequence_index:
            similar_gesture_detected = True
        # if we have ranked gesture similarities determine the index of most similar library gesture
        for i, seq in enumerate([gc.candidate_sequences] + gc.gesture_sequence_library):
            similarity_sequence = (
                similar_gesture_detected and gc.most_similar_sequence_index[0] == i - 1
            )

            out = None
            # TODO currently hacked for just one person (key 0) - fix
            mei = seq["MEI"]
            last_mhi = np.copy(seq["MHI"][-1])
            flattened_mhi = np.copy(seq["flattened_mhi"]).astype(np.uint8)
            gesture_energy = np.copy(seq["gesture_energy_matrix"]).astype(np.uint8)
            std = np.round(seq["meta"]["std"], 4)
            energy = np.round(seq["meta"]["energy"], 4)
            d, h, w = mei.shape
            info_window = np.zeros((200, w)).astype(np.uint8) + 100
            # if not looking at candidate sequence at first index
            if i > 0:
                # subtract 1 from i accessing stored variables to account for candidate seq in this list
                info_window = utils.put_text(
                    info_window, f"Weight: {np.round(gc.weights[i-1], 4)}", (15, 20)
                )
                info_window = utils.put_text(
                    info_window,
                    f"Current Gesture Sim: {np.round(gc.similarities[i-1], 4)}",
                    (15, 40),
                )
                if similarity_sequence:
                    info_window = utils.put_text(
                        info_window,
                        "CLOSEST SEQUENCE",
                        (int(w / 2), 170),
                    )
                    info_window = cv2.circle(
                        info_window,
                        (int(w / 2), 100),
                        radius=45,
                        color=255,
                        thickness=-1,
                    )
            else:
                info_window = utils.put_text(
                    info_window, "Candidate Sequence", (15, 20)
                )
                info_window = utils.put_text(
                    info_window,
                    f"Input Sequence: {gc.detected_gesture_count}",
                    (15, 40),
                )
            w_remainder = w % 3
            gesture_energy = cv2.resize(gesture_energy, (w // 3, w // 3))
            last_mhi = cv2.resize(last_mhi, (w // 3, w // 3))
            flattened_mhi = cv2.resize(flattened_mhi, (w // 3 + w_remainder, w // 3))
            energy_mhi = np.concatenate(
                [gesture_energy, last_mhi, flattened_mhi], axis=1
            )
            if c < len(mei):
                frame = mei[c]
            else:
                frame = mei[-1]
            frame = cv2.flip(frame, 1)
            out = np.concatenate([frame, energy_mhi, info_window], axis=0)
            out = utils.put_text(
                out,
                f"{i}:std-{std}, e-{energy}, len-{len(mei)}",
                (15, 20),
                color=(200, 200, 0),
                thickness=2,
            )
            # if we're on the candidate sequence
            # draw a rectangle to distingish
            if i == 0:
                h, w = out.shape
                out = cv2.rectangle(out, (4, 4), (w - 4, h - 4), 127, 4)
            elif similarity_sequence:
                h, w = out.shape
                out = cv2.rectangle(out, (4, 4), (w - 4, h - 4), 255, 4)

            frames.append(out)

        view = np.concatenate(frames, axis=1)
        if self.mouse_pos[0] and self.mouse_pos[1]:
            view = cv2.circle(view, self.mouse_pos, 15, 127, -1)
        utils.display_image(
            self.name,
            view,
            cv_event_handler=self.on_dashboard_event,
        )
        if self.sequence_viewer_counter == max_len:
            self.sequence_viewer_counter = 0
        else:
            self.sequence_viewer_counter += 1

    def on_dashboard_event(self, event, x, y, flag, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.mouse_pos = (x, y)
