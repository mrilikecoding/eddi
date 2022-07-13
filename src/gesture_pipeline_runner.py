import numpy as np

from src.gesture_segmenter import GestureSegmenter
from src.gesture_comparer import GestureComparer
from src.gesture_aesthetic_sequence_mapper import GestureAestheticSequenceMapper
from src import utils


class GesturePipelineRunner:
    def __init__(
        self,
        display_gesture_matrices=False,
        display_captured_gestures=False,
        gesture_limit=5,
        gesture_heuristics={},
        frame_window_length=75,
    ):
        self.display_capture_gestures = display_captured_gestures
        self.energy_diff_gesture_sequences = {}
        self.MEI_gesture_sequences = {}
        self.MHI_gesture_sequences = {}
        self.global_gesture_sequences = []
        self.gesture_limit = gesture_limit
        self.gesture_heuristics = gesture_heuristics
        self.current_frame = 0
        self.current_cycle = 0
        self.alt_cycle_1 = 0
        self.alt_cycle_2 = 0
        self.gesture_limit_reached = False
        self.display_gesture_matrices = display_gesture_matrices
        self.frame_window_length = frame_window_length
        self.gesture_sensitivity = self.gesture_heuristics["gesture_sensitivity"]
        # keeping 3 sequences within proximity of each other to vote on
        self.current_cycle_sequence_1 = None
        self.current_cycle_sequence_2 = None
        self.current_cycle_sequence_3 = None

        # initialize the interface for comparing new gestures with stored gestures
        self.gesture_comparer = GestureComparer(gesture_limit=self.gesture_limit)
        self.gesture_sequence_mapper = GestureAestheticSequenceMapper()
        # where to store a cycle's output sequence (accessed by #run_cycle caller)
        self.output = []

    def run_cycle(self, energy_moment_delta_volumes, mei_volumes, mhi_volumes):
        # TODO may want to use this output variable to loop sequences by not
        # resetting the variable - but would need to figure out length of sequence
        # in relation to the frame position so we're not layering the sequence on
        # top of itself
        self.output = []  # reset the output
        # from passed volumes, cut out the best determined sequence
        if (
            len(list(energy_moment_delta_volumes.values())[0])
            < self.frame_window_length
        ):
            return
        sequences = self.segment_gestures(
            energy_moment_delta_volumes,
            mei_volumes,
            mhi_volumes,
        )

        # TODO - try investigating diff in standard deviation
        # [(np.std(s['MEI']), np.std(s['MHI'])) for s in self.global_gesture_sequences]
        # For example:
        # (74.2569363682991, 101.03913215004903) - Better gesture
        # (62.647375294280025, 92.60295603239565) - Better gesture
        # (69.97907209297676, 77.4157758742946) - Bad gesture
        # (60.72376924833079, 101.06151798739978) - Better gesture
        # (68.41915553867938, 86.2812660323224) - Bad gesture

        # update the frame position within the frame window
        # this is useful for not selecting the same gesture
        # over and over again within a window
        self.current_frame = (self.current_frame + 1) % self.frame_window_length
        # track the number of cycles - this will help make sure
        # we don't tag the same gesture within the same cycle
        if self.current_frame == 0:
            print("subcycle 1")
            self.current_cycle_sequence_1 = sequences
            self.current_cycle += 1
        if self.current_frame // 3 == 0:
            print("subcycle 2")
            self.current_cycle_sequence_2 = sequences
            self.alt_cycle_1 += 1
        if (self.current_frame // 3) * 2 == 0:
            print("subcycle 3")
            self.current_cycle_sequence_3 = sequences
            self.alt_cycle_2 += 1

        if (
            self.current_cycle_sequence_1
            and self.current_cycle_sequence_2
            and self.current_cycle_sequence_3
        ):
            sequences = self.compute_best_sequences()
        else:
            return

        # if we have a valid gesture sequence
        if sequences is not None and not any(
            [
                stored_sequences["meta"]["energy"] == sequences["meta"]["energy"]
                for stored_sequences in self.global_gesture_sequences
            ]
        ):
            self.current_cycle_sequence_1 = None
            self.current_cycle_sequence_2 = None
            self.current_cycle_sequence_3 = None
            if len(self.global_gesture_sequences) < self.gesture_limit:
                # if True:
                self.global_gesture_sequences.append(sequences)
                # update our library of stored gestures
                self.gesture_comparer.update_gesture_library(
                    self.global_gesture_sequences
                )
                # allow the outputs to react to this gesture
                self.output = self.gesture_sequence_mapper.map_sequences_to_rgb(
                    sequences
                )
            else:
                if self.display_captured_gestures:
                    self.display_captured_gestures()
            # self.gesture_comparer.ingest_sequences(
            #     {
            #         "energy_moment_diff_sequence": sequences[0],
            #         "mei_sequence": sequences[1],
            #         "mhi_sequence": sequences[2],
            #         "global_sequence": sequences[3],
            #     }
            # )
            # TODO when ingesting sequences, we want to get back
            # a sequence from the comparer that is the most similar
            # sequence within a threshold and reweight the library
            # then send that sequence to the sequence mapper and
            # set the output

    def compute_best_sequences(self):
        if (
            self.current_cycle_sequence_1["meta"]["energy"]
            == self.current_cycle_sequence_2["meta"]["energy"]
            == self.current_cycle_sequence_3["meta"]["energy"]
        ):
            return self.current_cycle_sequence_1
        else:
            candidates = [
                self.current_cycle_sequence_1["meta"]["energy"],
                self.current_cycle_sequence_2["meta"]["energy"],
                self.current_cycle_sequence_3["meta"]["energy"],
            ]
            best_energy = np.argmax(candidates)
            return candidates[best_energy]

    def segment_gestures(
        self,
        energy_moment_delta_volumes,
        mei_volumes,
        mhi_volumes,
    ):
        """
        Outputs updated gesture sequences based on the
        computed best sequence in the passed volumes
        NOTE - this class initializes with the current list of sequences
        then with "segment gestures" method, the newly found gesture is appended
        to the list of sequences - it may eventually make sense to init this once
        but for now initializing a new segmenter each time
        """
        gs = GestureSegmenter(
            energy_diff_gesture_sequences=self.energy_diff_gesture_sequences,
            MEI_gesture_sequences=self.MEI_gesture_sequences,
            MHI_gesture_sequences=self.MHI_gesture_sequences,
            global_gesture_sequences=self.global_gesture_sequences,  # TODO prob don't need this
            energy_moment_delta_volumes=energy_moment_delta_volumes,
            frame_window_length=self.frame_window_length,
            current_frame=self.current_frame,
            current_cycle=self.current_cycle,
            alpha=self.gesture_sensitivity,
            display=self.display_gesture_matrices,
            gesture_heuristics=self.gesture_heuristics,
        )
        sequences = gs.segment_gestures(
            energy_moment_delta_volumes,
            mei_volumes,
            mhi_volumes,
        )

        return sequences

    def display_captured_gestures(self):
        # TODO add a conditional flag for this display
        for sequence_count, sequence in enumerate(self.global_gesture_sequences):
            sequence_length = len(sequence["MEI"])
            for frame_count, frame in enumerate(sequence["MEI"]):
                info1 = (
                    f"Seq: {sequence_count + 1}, Frame: {frame_count}/{sequence_length}"
                )
                info2 = f"Cycle: {sequence['meta']['at_cycle']} Energy: {sequence['meta']['energy']}"
                frame = utils.put_text(
                    frame,
                    info1,
                    position=(10, 10),
                    color=(255, 0, 255),
                    convert_image_color=True,
                )
                frame = utils.put_text(
                    frame,
                    info2,
                    position=(10, 30),
                    color=(255, 0, 255),
                    convert_image_color=True,
                )
                utils.display_image("Gesture", frame, top=True, wait=True)
