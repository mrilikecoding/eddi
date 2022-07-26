import cv2
import numpy as np
import time

from src import utils
from global_config import global_config


class GestureDashboard:
    def __init__(self):
        self.sequence_viewer_counter = 0
        self.mouse_pos = (None, None)
        self.gesture_comparer = None
        self.name = "Gesture Dashboard"
        self.sequence_card_coord_map = {}
        self.mouse_down = None  # mac os x is weird with open cv / double click - using this var to debounce
        self.override_data_load = False
        self.loaded_data = None

    def set_comparer_instance(self, gesture_comparer):
        self.gesture_comparer = gesture_comparer

    def display_dashboard(self):
        """
        this method takes each sequence in the sequence library and loops through the sequence
        to visualize them in a loop. additinally it shows the current candidate sequence that would
        be compared against each sequence library sequence. If the sequence library is not yet full
        they will be populated as the library is updated.

        additionally, the current set of sequences can be locked by double clicking a specified region

        if sequences are locked, double clicking the sequence area will send the sequence to the best output
        to be picked up by the sequence - this is helpful for manually triggering lights based on gestures

        TODO additionally, sequence sets can be saved and loaded
        """
        ###
        # For each sequence in the sequence library, display the sequence along with
        # mhi/mei composites and gesture energy reperesentation
        ## Also append an "info window for additional context"
        # if we have ranked gesture similarities determine the index of most similar library gesture
        gc = None
        dashboard_sequences = None
        c = self.sequence_viewer_counter
        frames = []
        max_len = None
        if (
            global_config["load_saved_sequences_into_dashboard"]
            and not self.override_data_load
        ):
            similar_gesture_detected = False
            # reset the best output here, since we may manually update this when clicking
            # saved gestures - TODO make this a little more intuitive
            self.gesture_comparer.best_output = None
            saved_data_path = global_config["saved_sequences_path"]
            saved_data_name = global_config["load_saved_sequences_name"]
            max_len = 65  # todo compute this from data or save into data meta
            try:
                data = utils.read_data(saved_data_path, saved_data_name)
                self.loaded_data = data
                gc = data["gesture_comparer_instance"]
                dashboard_sequences = data["sequences"]
                self.gesture_comparer.gestures_locked = True
            except:
                print("Could not load sequences from data...")
                gc = self.gesture_comparer
                dashboard_sequences = [
                    gc.candidate_sequences
                ] + gc.gesture_sequence_library
        else:
            gc = self.gesture_comparer
            if len(gc.gesture_sequence_library) == 0:
                return

            max_len = global_config["gesture_heuristics"]["maximum_frame_count"]

            similar_gesture_detected = False
            if gc.most_similar_sequence_index:
                similar_gesture_detected = True
            dashboard_sequences = [gc.candidate_sequences] + gc.gesture_sequence_library
        for i, seq in enumerate(dashboard_sequences):

            # flag if this sequence is the most similar sequence to the candidate sequence
            # note, we substract 1 because we've appended the sequences to the candidate sequence
            # subtract 1 to line back up with the indices of the sequence library
            similarity_sequence = (
                similar_gesture_detected and gc.most_similar_sequence_index[0] == i - 1
            )

            out = None
            # TODO currently hacked for just one person (key 0) - fix
            ## compile vars for display
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
                # if this sequence is tracked as the most similar sequence
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
                # for the candidate sequence...
                info_window = utils.put_text(
                    info_window, "Candidate Sequence", (15, 20)
                )
                info_window = utils.put_text(
                    info_window,
                    f"Input Sequence: {gc.detected_gesture_count}",
                    (15, 40),
                )
            w_remainder = (
                w % 3
            )  # we are splitting three views below the sequence replay
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
            h, w = out.shape
            if i == 0:
                out = cv2.rectangle(out, (4, 4), (w - 4, h - 4), 127, 4)
            elif similarity_sequence:
                out = cv2.rectangle(out, (4, 4), (w - 4, h - 4), 255, 4)

            # top left (x, y), top right, bottom left, bottom right
            self.sequence_card_coord_map[i] = {
                "top_left": (i * w, 0),
                "top_right": ((i * w) + w, 0),
                "bottom_left": (i * w, h),
                "bottom_right": ((i * w) + w, h),
            }
            frames.append(out)

        view = np.concatenate(frames, axis=1)
        h, w = view.shape
        ## render a "Lock/unlock gestures button"
        button_height = 75
        button_width = 150
        lock_text = None
        lock_color = None
        if self.gesture_comparer.gestures_locked:
            lock_text = "Unlock Gestures"
            lock_color = 0
        else:
            lock_text = "Lock Gestures"
            lock_color = 50
        self.lock_button_coords = [(0, h), (button_width, h - button_height)]

        view = cv2.rectangle(
            view, self.lock_button_coords[0], self.lock_button_coords[1], lock_color, -1
        )
        view = utils.put_text(view, lock_text, (5, h - 30), 255)

        ## render a "Save Sequence Set" button
        self.save_button_coords = [
            (0, h - button_height),
            (button_width, h - (2 * button_height)),
        ]
        save_text = "Save Sequences"
        save_color = 200
        view = cv2.rectangle(
            view, self.save_button_coords[0], self.save_button_coords[1], save_color, -1
        )
        view = utils.put_text(view, save_text, (5, h - 110), 255)

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

    def mouse_over_sequence(self):
        x, y = self.mouse_pos
        for seq, coords in self.sequence_card_coord_map.items():
            if (
                x is not None
                and y is not None
                and (
                    x >= coords["top_left"][0]
                    and x <= coords["top_right"][0]
                    and y >= coords["top_left"][1]
                    and y <= coords["bottom_left"][1]
                )
            ):
                return seq

    def mouse_over_lock_sequence_button(self):
        x, y = self.mouse_pos
        if (
            x is not None
            and y is not None
            and x >= self.lock_button_coords[0][0]
            and x <= self.lock_button_coords[1][0]
            and y <= self.lock_button_coords[0][1]
            and y >= self.lock_button_coords[1][1]
        ):
            return True
        else:
            return False

    def mouse_over_save_sequence_button(self):
        x, y = self.mouse_pos
        if (
            x is not None
            and y is not None
            and x >= self.save_button_coords[0][0]
            and x <= self.save_button_coords[1][0]
            and y <= self.save_button_coords[0][1]
            and y >= self.save_button_coords[1][1]
        ):
            return True
        else:
            return False

    def on_dashboard_event(self, event, x, y, flag, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.mouse_pos = (x, y)
        if event == 1:  # EVENT_LBUTTONDOWN is 1
            """
            Click / Double click handling is behaving strangely.
            However double clicks work on the regular mouse down event, but send events twice
            So here's hack to debounce
            """
            if self.mouse_down is not None and time.time() - self.mouse_down < 100:
                self.mouse_down = None
                """
                Do stuff here
                """
                # Lock / unlock the lock sequences button
                if self.mouse_over_lock_sequence_button():
                    if self.gesture_comparer.gestures_locked:
                        self.gesture_comparer.gestures_locked = False
                        # if we unlock gestures from loaded data, we want to
                        # no longer load data - however, we'll set our current
                        # comparer instance to the loaded data so we continue
                        # seamlessly
                        if global_config["load_saved_sequences_into_dashboard"]:
                            self.gesture_comparer = self.loaded_data[
                                "gesture_comparer_instance"
                            ]
                            self.override_data_load = True
                    else:
                        self.gesture_comparer.gestures_locked = True
                # Set the "best output" to the double-clicked sequence if gestures are locked
                # Lock / unlock the lock sequences button
                if self.mouse_over_save_sequence_button():
                    gc = self.gesture_comparer
                    sequences = [gc.candidate_sequences] + gc.gesture_sequence_library
                    data = {"gesture_comparer_instance": gc, "sequences": sequences}
                    utils.write_data(
                        global_config["saved_sequences_path"],
                        data,
                        f"sequences-{time.time()}",
                    )
                # Set the "best output" to the double-clicked sequence if gestures are locked
                if self.mouse_over_sequence() >= 0:
                    seq = self.mouse_over_sequence()
                    if global_config["load_saved_sequences_into_dashboard"]:
                        gc = self.loaded_data["gesture_comparer_instance"]
                    else:
                        gc = self.gesture_comparer
                    if self.gesture_comparer.gestures_locked:
                        if seq == 0:
                            print(f"Lighting candidate sequence")
                            self.gesture_comparer.best_output = gc.candidate_sequences
                        else:
                            print(f"Lighting library sequence {seq-1}")
                            self.gesture_comparer.best_output = (
                                gc.gesture_sequence_library[seq - 1]
                            )

            else:
                self.mouse_down = time.time()
