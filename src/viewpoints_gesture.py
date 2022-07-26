class ViewpointsGesture:
    def __init__(self, sequences_dict):
        self.sequence = sequences_dict
        self.set_tempo()
        self.set_repetition()
        self.set_kinesthetic_response()
        self.set_duration()
        self.set_shape()
        self.set_gesture()
        self.set_spatial_relationship()
        self.set_topography()
        self.set_architecture()

    def set_tempo(self):
        """
        How quickly is this happening? Characteristic energy, relative to...
        """
        pass

    def set_repetition(self):
        """
        Is this motion periodic? Is this an internal repetition
        Could distinguish between an self-repeating gesture. This relates
        to duration. A gesture repeating another similar gesture is also a different
        version of this viewpoint. This makes me think we want to define
        a gesture interaction network.
        """
        pass

    def set_kinesthetic_response(self):
        """Reactivity of this movement"""
        pass

    def set_duration(self):
        """How long this gesture will take"""
        pass

    def set_shape(self):
        """Overall shape of gesture, scale invariant"""
        pass

    def set_gesture(self):
        """Gesture Dynamics over time"""
        pass

    def set_spatial_relationship(self):
        """Location of this movement in space and relative to others"""
        pass

    def set_topography(self):
        """Floor pattern associated with this movement"""
        pass

    def set_architecture(self):
        """Space feature this gesture highlights"""
        pass

    def synthesize_new_sequence(self):
        """Output a variation of this gesture with shifted params"""
        pass
