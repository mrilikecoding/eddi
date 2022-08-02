import numpy as np
from src import utils


class ViewpointsGesture:
    def __init__(self, sequences_dict):
        self.sequence = sequences_dict
        self.tempo = None
        self.repetition = None
        self.kr = None
        self.duration = None
        self.shape = None
        self.gesture = None
        self.spatial_relationship = None
        self.topography = None
        self.architecture = None
        self.set_duration()
        self.set_tempo()
        self.set_repetition()
        self.set_kinesthetic_response()
        self.set_shape()
        self.set_gesture()
        self.set_spatial_relationship()
        self.set_topography()
        self.set_architecture()

    def get_gesture_summary(self):
        summary = [
            self.tempo,
            self.repetition,
            self.kr,
            self.duration,
            self.shape,
            self.gesture,
        ]
        # make values similar scale
        return [float(utils.safe_log10(float(x))) for x in summary]

    def set_tempo(self):
        """
        How quickly is this happening? Characteristic energy, relative to...
        """
        MEI = self.sequence["MEI"]
        MHI = self.sequence["MHI"]
        diff = MEI - MHI
        diff_mean = [np.mean(frame) for frame in diff]
        self.tempo = np.mean(
            [diff_mean[i] - diff_mean[i - 1] for i in range(1, len(diff_mean))]
        )

    def set_repetition(self):
        """
        How many times has this gesture been repeated?
        """
        self.repetition = 0

    def set_kinesthetic_response(self):
        """
        Reactivity of this movement
        KR is more a statement about how things react to this stimulus
        So to start, maybe this can be tempo * repetition * 1/duration or something
        So this would mean higher reactivity for higher tempo, repeated, shorter gestures
        """
        self.kr = self.tempo * (self.repetition + 1) * (1 / self.duration)

    def set_duration(self):
        """How long this gesture will take - length of sequence"""
        self.duration = len(self.sequence["MEI"])

    def set_shape(self):
        """Overall shape of gesture, scale invariant - Hu Moments of final MHI frame"""
        # for now just making some quick and dirty choices
        self.shape = np.sum(self.sequence["meta"]["last_mhi_hu_moments"][:2])

    def set_gesture(self):
        """Gesture Dynamics over time"""
        # for now using standard deviation
        self.gesture = self.sequence["meta"]["std"]

    def set_spatial_relationship(self):
        """Location of this movement in space and relative to others"""
        # won't do this until multiple people working
        pass

    def set_topography(self):
        """Floor pattern associated with this movement"""
        # won't do this until multiple people working
        pass

    def set_architecture(self):
        """Space feature this gesture highlights"""
        # won't do this until there are other spatial features
        pass

    def synthesize_new_sequence(self):
        """Output a variation of this gesture with shifted params"""
        pass
