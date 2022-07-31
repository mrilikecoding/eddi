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
            # "middle",
        ]

        # TODO there can be a multi-space hierarchy that defines
        # categories for each space and their primary axes
        self.spatial_categories = spatial_categories
        # init an RGB frame for placeholders in the queue -
        # -1 indicates an invalid value that can be replaced, otherwise new values will average in
        self.init_frame = {k: (-1, -1, -1) for k in spatial_categories}

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

        eps = 1e-10  # for preventing divide by zero errors normalizing
        sequence_weights = np.array([o["weight"] for o in outputs])
        sequence_weights = sequence_weights / (np.sum(sequence_weights) + eps)
        sequences = [o["sequence"] for o in outputs]

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

        # layer in each output sequence frame into a column of unmerged values
        # for each queue position
        # TODO something is making the values rather small still, but the sequencing is working
        unmerged_queue = []
        unmerged_queue_frame_weights = []
        for i, _ in enumerate(self.queue):
            frame_layers = []
            frame_layer_weights = []
            for j, sequence in enumerate(sequences):
                # if the incoming sequence overlaps with this queue position
                if i < len(sequence):
                    # add the sequence frame to this queue column
                    frame_layers.append(sequence[i])
                    # add the corresponding sequence weight
                    frame_layer_weights.append(sequence_weights[j])
            unmerged_queue.append(frame_layers)
            unmerged_queue_frame_weights.append(frame_layer_weights)

        for i, frame_layers in enumerate(unmerged_queue):
            r, g, b = (None, None, None)
            for position in self.spatial_categories:
                r = self.queue[i][position][0]
                g = self.queue[i][position][1]
                b = self.queue[i][position][2]
                # print(r, g, b)
                for j, sequence_frame in enumerate(frame_layers):
                    if position in sequence_frame:
                        weighted_r = sequence_frame[position][0] * sequence_weights[j]
                        weighted_g = sequence_frame[position][1] * sequence_weights[j]
                        weighted_b = sequence_frame[position][2] * sequence_weights[j]
                        if all([ch >= 0 for ch in [r, g, b]]):
                            r += weighted_r
                            g += weighted_g
                            b += weighted_b
                        else:
                            r = weighted_r
                            g = weighted_g
                            b = weighted_b
                self.queue[i][position] = (r, g, b)
        self.director.set_current_queue(
            copy.copy(self.queue), copy.copy(self.queue_meta)
        )
        return

    def get_next_values(self):
        queue = copy.copy(self.director.get_current_queue())
        if queue and len(queue):
            self.queue.popleft()
            # self.queue_meta.popleft()
            next_values = queue.popleft()
            return next_values
        else:
            return False
