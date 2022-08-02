from collections import deque
import copy
import numpy as np


class Sequencer:
    def __init__(self, queue_length=500, director=None):
        # TODO not sure if we need this
        self.director = director
        queue_length = (
            self.director.config.get("max_sequence_queue_length") or queue_length
        )
        self.queue_length = queue_length
        self.queue = deque([])
        self.queue_meta = deque([])

        # assume we have some discrete spatial areas and at least one binary primary axis
        # TODO can probably abstract this from config file
        # making this more abstract will enable different kinds of space partitioning
        # TODO pass these in
        spatial_categories = [
            "left",
            "right",
            "top",
            "bottom",
            "back",
            "front",
            "middle",
        ]

        # TODO there can be a multi-space hierarchy that defines
        # categories for each space and their primary axes
        self.spatial_categories = spatial_categories
        # init an RGB frame for placeholders in the queue -
        # -1 indicates an invalid value that can be replaced, otherwise new values will average in
        self.init_frame = {k: (-1, -1, -1) for k in spatial_categories}

        # exposing some internal vars for testing
        self.current_sequence_weights = None
        self.current_sequences = None
        self.currnet_sequence_origins = None
        self.unmerged_queue = None

    def add_output_sequences_to_queue(self, outputs=[]):
        """
        the sequence should be shaped like this...
        [{
            "back": (r, g, b),
            "front": (r, g, b),
            "bottom": (r, g, b),
            "top": (r, g, b),
            "right": (r, g, b),
            "left": (r, g, b),
            # "middle": (r, g, b),
        }, ...]
        """
        if not len(outputs):
            return

        # vars exposed for testing
        self.current_sequence_weights = None
        self.current_sequences = None
        self.current_sequence_origins = None
        self.unmerged_queue = None

        eps = 1e-10  # for preventing divide by zero errors normalizing
        origin_weights = {o["origin"]: o["weight"] for o in outputs}
        sequence_weights = np.array([o["weight"] for o in outputs])
        sequence_weights = sequence_weights / (np.sum(sequence_weights) + eps)
        sequences = [o["sequence"] for o in outputs]
        sequence_origins = [o["origin"] for o in outputs]

        # vars exposed for testing
        self.current_sequence_weights = sequence_weights
        self.current_sequences = sequences
        self.current_sequence_origins = sequence_origins

        # determine how many spots to open in queue
        max_sequence_len = 0
        for seq in sequences:
            if len(seq) > max_sequence_len:
                max_sequence_len = len(seq)

        if len(self.queue) < max_sequence_len:
            # open up empty queue slots to accomodate sequence
            additional_slots = max_sequence_len - len(self.queue)
            [
                self.queue.append(copy.deepcopy(self.init_frame))
                for _ in range(additional_slots)
            ]
            [self.queue_meta.append({}) for _ in range(additional_slots)]

        # layer in each output sequence frame into a column of unmerged values
        # for each queue position
        self.unmerged_queue = []
        for i, _ in enumerate(self.queue):
            frame_layers = []
            for j, sequence in enumerate(sequences):
                # if the incoming sequence overlaps with this queue position
                if i < len(sequence):
                    # add the corresponding sequence weight/origin to the data
                    sequence[i]["weight"] = sequence_weights[j]
                    sequence[i]["origin"] = sequence_origins[j]
                    # add the sequence frame to this queue column
                    frame_layers.append(sequence[i])
            # TODO prob can refactor this
            # do a second pass normalizing the weights, since sequences will have different lengths
            layer_weights = []
            for layer in frame_layers:
                layer_weights.append(layer["weight"])
            layer_weights = np.array(layer_weights) / (np.sum(layer_weights) + eps)
            for i, layer in enumerate(frame_layers):
                frame_layers[i]["weight"] = layer_weights[i]

            self.unmerged_queue.append(frame_layers)

        for i, frame_layers in enumerate(self.unmerged_queue):
            r, g, b = (-1, -1, -1)  # default, matching init frame
            existing_weights = self.queue_meta[i].get("origins")
            for position in self.spatial_categories:
                if position in self.queue[i]:
                    r = self.queue[i][position][0]
                    g = self.queue[i][position][1]
                    b = self.queue[i][position][2]
                frame_composition = []  # track where these values originated
                for j, sequence_frame in enumerate(frame_layers):
                    frame_composition.append(sequence_frame["origin"])
                    if position in sequence_frame:

                        weighted_r = (
                            sequence_frame[position][0] * sequence_frame["weight"]
                        )
                        weighted_g = (
                            sequence_frame[position][1] * sequence_frame["weight"]
                        )
                        weighted_b = (
                            sequence_frame[position][2] * sequence_frame["weight"]
                        )
                        if all([ch >= 0 for ch in [r, g, b]]):
                            # TODO might be another edge case in here but maybe rarer
                            # does this logic track?
                            # if we have two overlapping sequences from the same source, average their values together
                            if existing_weights is not None:
                                current_origin = sequence_frame["origin"]
                                if current_origin in existing_weights:
                                    r = (r + weighted_r) / 2
                                    g = (g + weighted_g) / 2
                                    b = (b + weighted_b) / 2
                            # otherwise add into existing sequence
                            else:
                                r += weighted_r
                                g += weighted_g
                                b += weighted_b
                        else:
                            r = weighted_r
                            g = weighted_g
                            b = weighted_b
                        self.queue[i][position] = tuple(np.round((r, g, b), 3))
                    else:
                        # if there is no position value, remove the placeholder entry for position
                        if position in self.queue[i]:
                            del self.queue[i][position]
            self.queue_meta[i]["origins"] = {
                o: w for o, w in origin_weights.items() if o in frame_composition
            }

        # update director with latest queue / queue meta
        # NB: this is by reference
        self.director.current_queue = self.queue
        self.director.current_queue_meta = self.queue_meta
        return

    def get_next_values(self):
        if len(self.queue):
            # popleft on director queue will affect sequencer queue by reference
            # this is by design right now - getting into trouble copying values over
            # however, this function will return a copy of next value
            next_values = copy.copy(self.director.current_queue.popleft())
            next_meta = copy.copy(self.director.current_queue_meta.popleft())
            return next_values
        else:
            return False
