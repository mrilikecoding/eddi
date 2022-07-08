from collections import deque
from global_config import global_config
import copy


class Sequencer:
    def __init__(self, queue_length=500):
        # TODO not sure if we need this
        queue_length = global_config.get("max_sequence_queue_length") or queue_length
        self.queue_length = queue_length
        self.queue = deque([])

        # TODO Moving this spatial code from PipelineNode to here - exploring the sequencing flow...
        # will need to clean up here or there...

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
        self.init_frame = { k: (-1, -1, -1) for k in spatial_categories }

    def add_sequence_to_queue(self, sequence):
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
            [self.queue.append(copy.deepcopy(self.init_frame)) for _ in range(additional_slots)]

        # for each sequence frame check to see if there's an existing frame queued
        # if not, add queue slots to accomodate this sequence and set the slot to the sequence values
        # if there is a frame queued, average the new sequence with the existing sequence
        for i in range(len(sequence)):
            queued_frame = self.queue[i]
            sequence_frame = sequence[i]
            for position in self.spatial_categories:
                if queued_frame.get(position) and sequence_frame.get(position):
                    # average values together
                    if queued_frame[position][0] < 0:
                        r = sequence_frame[position][0]
                    else:
                        r = (queued_frame[position][0] + sequence_frame[position][0]) / 2
                    if queued_frame[position][1] < 0:
                        g = sequence_frame[position][1]
                    else:
                        g = (queued_frame[position][1] + sequence_frame[position][1]) / 2
                    if queued_frame[position][2] < 0:
                        b = sequence_frame[position][2]
                    else:
                        b = (queued_frame[position][2] + sequence_frame[position][2]) / 2
                    queued_frame[position] = (r, g, b)

    def get_next_values(self):
        if len(self.queue):
            return self.queue.popleft()
        else:
            return False
        
