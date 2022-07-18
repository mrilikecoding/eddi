import numpy as np
import cv2

from global_config import global_config
from src import utils


class GestureComparer:
    def __init__(self, gesture_sequence_library=[], gesture_limit=5):
        self.gesture_limit = gesture_limit
        self.gesture_sequence_library = gesture_sequence_library
        self.weights = np.array([1 for g in gesture_sequence_library]) / len(
            gesture_sequence_library
        )
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
        else:
            # TODO do stuff, then update this
            self.best_output = sequences

    def compute_similarity(self, gesture_sequence):
        # for the passed sequences,
        # how similar are they to sequences in lib
        # if there is a match within threshold
        # adjust weights - double the weight of match and renormalize
        # if any of the weights are signficantly lower than the others
        # then let's relinquish the sequence and add a new gesture
        # to the library
        pass

    def update_gesture_weights(self):
        pass

    def compute_best_sequences(self, candidates):
        """
        TODO - could also try the biggest standard deviation
        """
        if all(
            c["meta"]["energy"] == candidates[0]["meta"]["energy"] for c in candidates
        ):
            return candidates[0]
        else:
            energies = [c["meta"]["energy"] for c in candidates]
            best_energy = np.argmax(energies)
            return candidates[best_energy]

    def loop_global_gesture_dashboard(self):
        if len(self.gesture_sequence_library) == 0:
            return

        max_len = 50  # TODO set this to the max gesture size
        c = self.sequence_viewer_counter
        frames = []
        for i, seq in enumerate(self.gesture_sequence_library):
            out = None
            # TODO currently hacked for just one person (key 0) - fix
            mei = seq["MEI"]
            energy = seq["meta"]["energy"]
            gesture_energy = seq["gesture_energy_matrix"]
            d, h, w = mei.shape
            gesture_energy = cv2.resize(gesture_energy, (w, w))
            if c < len(mei):
                frame = mei[c]
            else:
                frame = mei[-1]
            out = np.concatenate([frame, gesture_energy], axis=0)
            out = utils.put_text(
                out,
                f"{i}:e-{np.round(energy, 4)}, l-{len(mei)}",
                (15, 15),
                color=200,
                thickness=1,
            )
            frames.append(out)

        view = np.concatenate(frames, axis=1)
        utils.display_image("Captured Gestures", view)
        if self.sequence_viewer_counter == max_len:
            self.sequence_viewer_counter = 0
        else:
            self.sequence_viewer_counter += 1
