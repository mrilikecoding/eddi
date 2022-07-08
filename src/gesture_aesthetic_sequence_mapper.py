class GestureAestheticSequenceMapper:
    def __init__(self):
        self.output = []
        # TODO - again, grab this from a config
        self.spatial_categories = [
            "left",
            "right",
            "top",
            "bottom",
            "back",
            "front",
            "middle",
        ]

    def map_sequences_to_rgb(self, sequences):
        """
        params: 
        sequences = {
            'MEI' : nd.array shape = num_frames * h * w - eg (44, 278, 400)
            'MHI': nd.array shape = num_frames * h * w
            'energy_diff': nd.array shape = num_frames*h*w
            'meta': { 'at_frame': x, 'at_cycle': x, 'idxs' {0 : (s, e), 'energy': x, 'person_id': x}}
        }

        returns a list of spatially defined sequence frames
        [{
            "back": (r, g, b),
            "front": (r, g, b),
            "bottom": (r, g, b),
            "top": (r, g, b),
            "right": (r, g, b),
            "left": (r, g, b),
            "middle": (r, g, b),
        }, ...]
        """
        return []
