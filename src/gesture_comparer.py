import numpy as np
import cv2
import math

from global_config import global_config
from src import utils


class GestureComparer:
    def __init__(self, gesture_sequence_library=[], gesture_limit=5):
        self.gesture_limit = gesture_limit
        self.gesture_sequence_library = gesture_sequence_library
        self.weights = np.array([1 for g in gesture_sequence_library]) / len(
            gesture_sequence_library
        )
        self.similarities = [0 for _ in range(self.gesture_limit)]
        self.similarities_meta = [{} for _ in range(self.gesture_limit)]
        self.train_gesture_classifier = global_config["train_gesture_segmenter"]
        self.gesture_classifier = None
        self.similarity_threshold = 0.5  # just a placeholder val
        self.best_output = None
        self.sequence_viewer_counter = 0

    def process_cycle(self):
        # loop captured gestures
        self.loop_global_gesture_dashboard()

    def ingest_sequences(self, sequences):
        if len(self.gesture_sequence_library) < self.gesture_limit:
            self.gesture_sequence_library.append(sequences)
            self.best_output = sequences
            self.set_gesture_weights()
        else:
            self.similarities = self.compute_similarity(sequences)
            ranks = np.array(self.similarities).argsort()
            for i, s in enumerate(self.similarities_meta):
                s["rank"] = ranks[i]

            # Update best output based on similarity scores
            most_similar_idx = None
            if all(
                [("rank" in s and s.get("rank") >= 0) for s in self.similarities_meta]
            ):
                most_similar_idx = np.argmin(
                    [s["rank"] for s in self.similarities_meta]
                )
                if (
                    self.similarities[most_similar_idx]
                    < global_config["repeated_gesture_similarity_threshold"]
                ):
                    self.update_gesture_weights(most_similar_idx)
                    self.prune_low_weights()
                    self.best_output = self.gesture_sequence_library[most_similar_idx]
            else:
                self.best_output = None

    def compute_similarity(self, sequences):
        """
        for the passed sequences,
        how similar are they to sequences in lib
        if there is a match within threshold
        adjust weights - double the weight of match and renormalize
        if any of the weights are signficantly lower than the others
        then let's relinquish the sequence and add a new gesture
        # to the library
        Sequences are shaped like this:
        {
            "MEI": mei_sequence,
            "MHI": mhi_sequence,
            "energy_diff": energy_diff_sequence,
            "gesture_energy_matrix": gesture_energy_matrix,
            "flattened_mhi": flattened_mhi,
            "meta": {
                "at_frame": self.current_frame,
                "at_cycle": self.current_cycle,
                "cycle_name": self.cycle_name,
                "idxs": self.current_best_sequence[person],
                "energy": energy,
                "std": std,
                "person_id": person,
                "last_mhi_hu_moments": last_mhi_hu_moments,
                "flattened_mhi_hu_moments": flattened_mhi_hu_moments,
            },
        }
        """
        similarities = [
            self.run_similarity_checks(sequences, s)
            for s in self.gesture_sequence_library
        ]

        return similarities

    def run_similarity_checks(self, sequence_a, sequence_b):
        meta_a = sequence_a["meta"]
        meta_b = sequence_b["meta"]
        sim_a = np.concatenate(
            [
                meta_a["last_mhi_hu_moments"][:-1],
                # meta_a["flattened_mhi_hu_moments"],
                [meta_a["energy"]],
                [meta_a["std"]],
            ],
        )

        sim_b = np.concatenate(
            [
                meta_b["last_mhi_hu_moments"][:-1],
                # meta_b["flattened_mhi_hu_moments"],
                [meta_b["energy"]],
                [meta_b["std"]],
            ],
        )

        return np.round(math.dist(sim_a, sim_b), 4)

    def set_gesture_weights(self):
        self.weights = np.array([1 for g in self.gesture_sequence_library]) / len(
            self.gesture_sequence_library
        )

    def update_gesture_weights(self, boost_idx):
        self.weights[boost_idx] = (
            self.weights[boost_idx] * global_config["weight_increase_factor"]
        )
        self.weights = self.weights / np.sum(self.weights)

    def prune_low_weights(self):
        prune_list = np.array(
            [w < global_config["weight_pruning_threshold"] for w in self.weights]
        )
        # TODO - fix this
        if not len(self.similarities):
            return
        for i, p in enumerate(prune_list):
            if p:
                del self.similarities[i]
                del self.similarities_meta[i]
                del self.gesture_sequence_library[i]
                np.delete(prune_list, i)
                if len(self.similarities):
                    self.prune_low_weights()

    def compute_best_sequences(self, candidates):
        """
        Called to choose the greatest standard deviation from a list of passed sequences
        """
        if all(c["meta"]["std"] == candidates[0]["meta"]["std"] for c in candidates):
            return candidates[0]
        else:
            stds = [c["meta"]["std"] for c in candidates]
            best_stds = np.argmax(stds)
            return candidates[best_stds]

    def loop_global_gesture_dashboard(self):
        if len(self.gesture_sequence_library) == 0:
            return

        max_len = 50  # TODO set this to the max gesture size
        c = self.sequence_viewer_counter
        frames = []

        most_similar_idx = None
        similar_gesture_detected = False
        if all([("rank" in s and s.get("rank") >= 0) for s in self.similarities_meta]):
            most_similar_idx = np.argmin([s["rank"] for s in self.similarities_meta])
            similar_gesture_detected = (
                self.similarities[most_similar_idx]
                < global_config["repeated_gesture_similarity_threshold"]
            )
        for i, seq in enumerate(self.gesture_sequence_library):
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
            info_window = utils.put_text(
                info_window, f"Weight: {np.round(self.weights[i], 4)}", (15, 20)
            )
            info_window = utils.put_text(
                info_window,
                f"Current Gesture Sim: {np.round(self.similarities[i], 4)}",
                (15, 40),
            )
            if similar_gesture_detected and most_similar_idx == i:
                info_window = utils.put_text(
                    info_window,
                    f"Sim Rank: {self.similarities_meta[i]['rank']}",
                    (15, 60),
                )
                info_window = cv2.circle(
                    info_window,
                    (int(w / 2), 100),
                    radius=45,
                    color=255,
                    thickness=-1,
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
                (15, 15),
                color=(200, 200, 0),
                thickness=2,
            )
            frames.append(out)

        view = np.concatenate(frames, axis=1)
        utils.display_image("Captured Gestures", view)
        if self.sequence_viewer_counter == max_len:
            self.sequence_viewer_counter = 0
        else:
            self.sequence_viewer_counter += 1
