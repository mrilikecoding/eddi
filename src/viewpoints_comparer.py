import numpy as np
import math

from src.gesture_comparer import GestureComparer
from src.viewpoints_gesture import ViewpointsGesture


class ViewpointsComparer(GestureComparer):
    def __init__(self, gesture_limit=3, director=None):
        self.director = director
        self.gesture_limit = self.director.config["gesture_limit"]
        self.viewpoints_gesture_limit = 6
        self.viewpoints_gestures = []
        self.viewpoints_gesture_map = {}
        self.similarities_computed_this_round = False
        super().__init__(gesture_limit=self.gesture_limit, director=director)

    def ingest_sequences(self, sequences):
        # TODO wary of increased memory usage with storing all gestures
        # will cross that bridge later...

        viewpoints_gesture = ViewpointsGesture(sequences_dict=sequences)
        index = len(self.viewpoints_gestures)
        sequences["meta"]["viewpoints_gesture_index"] = index
        self.viewpoints_gestures.append(viewpoints_gesture)
        self.similarities = self.compute_similarity(sequences)
        if len(self.similarities):
            # TODO this flag is a bit of a hack, just getting things working
            # refactor the class/subclass relationship here
            self.similarities_computed_this_round = True
            self.most_similar_idx = np.argmin(self.similarities)
        super().ingest_sequences(sequences)
        self.similarities_computed_this_round = False
        return True

    def compute_similarity(self, sequences):
        viewpoints_gesture = ViewpointsGesture(sequences_dict=sequences)
        # compute the viewpoints similarity to the incoming versus library
        viewpoints_library_gestures = [
            self.viewpoints_gestures[gs["meta"]["viewpoints_gesture_index"]]
            for gs in self.gesture_sequence_library
        ]

        similarities = [
            self.run_similarity_checks(viewpoints_gesture, s)
            for s in viewpoints_library_gestures
        ]
        return similarities

    def run_similarity_checks(self, sequence_a, sequence_b):
        sim_a = sequence_a.get_gesture_summary()
        sim_b = sequence_b.get_gesture_summary()
        return np.round(math.dist(sim_a, sim_b), 4)
