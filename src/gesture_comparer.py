import numpy as np


class GestureComparer:
    def __init__(self, gesture_sequence_library={}, gesture_limit=5):
        self.gesture_limit = gesture_limit
        self.gesture_sequence_library = gesture_sequence_library
        self.weights = np.array([1 for g in gesture_sequence_library]) / len(
            gesture_sequence_library
        )
        self.similarity_threshold = 0.5  # just a placeholder val

    def ingest_sequences(self, sequences):
        # for the passed sequences,
        # how similar are they to sequences in lib
        # if there is a match within threshold
        # adjust weights - double the weight of match and renormalize
        # if any of the weights are signficantly lower than the others
        # then let's relinquish the sequence and add a new gesture
        # to the library
        self.compute_similarity(sequences["energy_moment_diff_sequence"])

    def update_gesture_library(self, gesture_sequence_library):
        self.gesture_sequence_library = gesture_sequence_library

    def compute_similarity(self, gesture_sequence):
        pass

    def update_gesture_weights(self):
        pass
