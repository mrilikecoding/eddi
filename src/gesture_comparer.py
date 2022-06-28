import numpy as np


class GestureComparer:
    def __init__(self, gesture_sequence_library=[]):
        self.gesture_sequence_library = gesture_sequence_library
        self.weights = np.array([1 for g in gesture_sequence_library]) / len(
            gesture_sequence_library
        )

    def ingest_sequences(self, sequences):
        pass

    def update_gesture_library(self, gesture_sequence_library):
        self.gesture_sequence_library = gesture_sequence_library

    def compute_similarity(self, gesture_sequence):
        pass

    def update_gesture_weights(self):
        pass
