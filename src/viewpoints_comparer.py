from src.gesture_comparer import GestureComparer
from src.viewpoints_gesture import ViewpointsGesture


class ViewpointsComparer(GestureComparer):
    def __init__(self, gesture_limit=3, director=None):
        self.director = director
        self.gesture_limit = self.director.config["gesture_limit"]
        self.viewpoints_gestures = []
        super().__init__(gesture_limit=self.gesture_limit, director=director)

    def ingest_sequences(self, sequences):
        if self.gestures_locked or sequences is None:
            return
        if len(self.gesture_sequence_library) < self.gesture_limit:
            viewpoints_gesture = ViewpointsGesture(sequences_dict=sequences)
            self.viewpoints_gestures.append(viewpoints_gesture)

        return super().ingest_sequences(sequences)

    def compute_similarity(self, sequences):
        return super().compute_similarity(sequences)
