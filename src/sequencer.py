from collections import deque
import copy


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

    def add_sequence_to_queue(self, sequence, sequence_weight=1.0, origin="default"):
        """
        sequence should be shaped like this...
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
        if not sequence:
            return

        if len(self.queue) < len(sequence):
            # open up empty queue slots to accomodate sequence
            additional_slots = len(sequence) - len(self.queue)
            [
                self.queue.append(copy.deepcopy(self.init_frame))
                for _ in range(additional_slots)
            ]
            [
                self.queue_meta.append({"origin": origin, "weight": sequence_weight})
                for _ in range(additional_slots)
            ]

        # for each sequence frame check to see if there's an existing frame queued
        # if not, add queue slots to accomodate this sequence and set the slot to the sequence values
        # if there is a frame queued, average the new sequence with the existing sequence
        for i in range(len(sequence)):
            eps = 1e-10  # for preventing divide by zero errors normalizing
            queued_frame = self.queue[i]
            sequence_frame = sequence[i]
            queued_frame_weight = self.queue_meta[i]["weight"]
            normalizer = queued_frame_weight + sequence_weight + eps
            for position in self.spatial_categories:
                if queued_frame.get(position) and sequence_frame.get(position):
                    # average values together
                    rgb = [None, None, None]
                    channel_value = 0
                    for ch in range(3):
                        if queued_frame[position][ch] < 0:
                            # if this frame has no competetion from other sequence, use its default value
                            channel_value = sequence_frame[position][ch]
                        else:
                            # if weghts are equal, just take the normal average
                            if sequence_weight == queued_frame_weight:
                                channel_value = (
                                    queued_frame[position][ch]
                                    + sequence_frame[position][ch]
                                ) / 2
                            else:
                                # otherwise, give the weighted average of sum of sequence frames
                                # where "output_weights" are defined in configuration
                                channel_value = (
                                    (queued_frame[position][ch] * queued_frame_weight)
                                    + (sequence_frame[position][ch] * sequence_weight)
                                ) / (2 * normalizer)
                        rgb[ch] = channel_value

                    queued_frame[position] = tuple(rgb)
        # send the latest queued output to the Director class instance for
        # final stage transformations
        self.director.set_current_queue(
            copy.copy(self.queue), copy.copy(self.queue_meta)
        )

    def get_next_values(self):
        queue = copy.copy(self.director.get_current_queue())
        if len(queue):
            self.queue.popleft()
            return queue.popleft()
        else:
            return False
