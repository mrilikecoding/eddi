import numpy as np
import cv2
import time

from src.gesture_segmenter import GestureSegmenter
from src.gesture_comparer import GestureComparer
from src.gesture_aesthetic_sequence_mapper import GestureAestheticSequenceMapper
from src import utils
from global_config import global_config


class GesturePipelineRunner:
    def __init__(
        self,
        display_gesture_matrices=False,
        display_captured_gestures=False,
        gesture_limit=5,
        gesture_heuristics={},
        frame_window_length=75,
        display_info=False,
    ):
        self.display_capture_gestures = display_captured_gestures
        self.energy_diff_gesture_sequences = {}
        self.MEI_gesture_sequences = {}
        self.MHI_gesture_sequences = {}
        self.global_gesture_sequences = []
        self.gesture_limit = gesture_limit
        self.gesture_limit_reached = False
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

        self.out_params = {}

        self.display_info = display_info
        self.info_window = np.zeros((200, 500))

        self.sequence_viewer_counter = 0

        # initialize the interface for comparing new gestures with stored gestures
        self.gesture_comparer = GestureComparer(gesture_limit=self.gesture_limit)
        self.gesture_sequence_mapper = GestureAestheticSequenceMapper()
        # where to store a cycle's output sequence (accessed by #run_cycle caller)
        self.output = []

    def run_gesture_subcycles(
        self, energy_moment_delta_volumes, mei_volumes, mhi_volumes
    ):
        """
        Here we're creating 3 concurrent cycles phased 1/3 from each other
        Gestures are extracted from each subcycle and voted upon

        This is so that the same gesture isn't selected over and over from the same
        adjacent frames and also to account for gestures that may overlap cycles.
        Hopefully a gesture that is extracted partially from one cycle that overlaps
        into another will be reselected "wholly" if it occurs fully within another
        subcycle and be voted better than the previously selected partial.

        If each subcycle has selected gestures, vote on and return the best one,
        otherwise return None
        """
        sequences = None
        valid_volumes = (
            all([energy_moment_delta_volumes and mei_volumes and mhi_volumes])
        ) and len(list(energy_moment_delta_volumes.values())[0]) > 0
        cycle_interval = self.frame_window_length // 3
        if self.current_frame == 0:
            self.current_cycle += 1
            if valid_volumes:
                # primary sequence
                p_sequences = self.segment_gestures(
                    energy_moment_delta_volumes,
                    mei_volumes,
                    mhi_volumes,
                    self.current_cycle,
                    cycle_name="primary",
                )
                self.current_cycle_sequence_1 = p_sequences
        if self.current_frame == cycle_interval:
            self.alt_cycle_1 += 1
            if valid_volumes:
                # alt 1 sequence
                a1_sequences = self.segment_gestures(
                    energy_moment_delta_volumes,
                    mei_volumes,
                    mhi_volumes,
                    self.alt_cycle_1,
                    cycle_name="alt_cycle_1",
                )
                self.current_cycle_sequence_2 = a1_sequences
        if self.current_frame == cycle_interval * 2:
            self.alt_cycle_2 += 1
            if valid_volumes:
                # alt 2 sequence
                a2_sequences = self.segment_gestures(
                    energy_moment_delta_volumes,
                    mei_volumes,
                    mhi_volumes,
                    self.alt_cycle_2,
                    cycle_name="alt_cycle_2",
                )
                self.current_cycle_sequence_3 = a2_sequences

        if (
            self.current_cycle_sequence_1
            and self.current_cycle_sequence_2
            and self.current_cycle_sequence_3
        ):
            for person, _ in self.current_cycle_sequence_1.items():
                candidates = [
                    self.current_cycle_sequence_1[person],
                    self.current_cycle_sequence_2[person],
                    self.current_cycle_sequence_3[person],
                ]
            sequences = self.gesture_comparer.compute_best_sequences(candidates)

        # if we have stored and voted between 3 cycle sequences, reset them
        # return sequences
        if sequences:
            self.current_cycle_sequence_1 = None
            self.current_cycle_sequence_2 = None
            self.current_cycle_sequence_3 = None
            return sequences

    def run_cycle(self, energy_moment_delta_volumes, mei_volumes, mhi_volumes):
        sequences = None
        # empty the ouput sequence for this upcoming cycle
        self.output = []
        if len(self.global_gesture_sequences) == self.gesture_limit:
            self.gesture_limit_reached = True
        else:
            self.gesture_limit_reached = False
        # update the frame position within the frame window
        # this is useful for not selecting the same gesture
        # over and over again within a window
        self.current_frame = self.current_frame % self.frame_window_length

        # run 3 phased subcycles - will be None or dict of sequences
        # TODO this will need adjusting for multiple people
        sequences = self.run_gesture_subcycles(
            energy_moment_delta_volumes, mei_volumes, mhi_volumes
        )

        self.current_frame += 1

        # if we have a valid gesture sequence
        self.global_gesture_sequences = self.gesture_comparer.gesture_sequence_library
        if sequences is not None:
            print("Gesture Detected")

            # TODO make work for multiple people
            # self.global_gesture_sequences.append(sequences[0])
            self.gesture_comparer.ingest_sequences(sequences=sequences)
            # if global_config["train_gesture_segmenter"]:
            #     self.display_gesture_explorer(sequences)
            # allow the outputs to react to this gesture
            # right now it'll just use the last sequence in the dict
            # but that's prob ok for experimenting with just me at the moment
            # prob want to make this output a person dict and then layer it
            # further down the road
            # TODO - adjust this to work with multiple people
            self.output = self.gesture_sequence_mapper.map_sequences_to_rgb(
                self.gesture_comparer.best_output
            )
            # TODO when ingesting sequences, we want to get back
            # a sequence from the comparer that is the most similar
            # sequence within a threshold and reweight the library
            # then send that sequence to the sequence mapper and
            # set the output
        self.gesture_comparer.process_cycle()

    def display_gesture_explorer(self, sequences):
        gesture_energy_matrix = sequences["gesture_energy_matrix"]
        energy = sequences["meta"]["energy"]
        start, end = sequences["meta"]["idxs"]
        mei_sequence = sequences["MEI"]
        if global_config["train_gesture_segmenter"]:
            utils.display_image(
                "Energy Matrix",
                gesture_energy_matrix,
                normalize=True,
                input_range=(
                    np.min(gesture_energy_matrix),
                    np.max(gesture_energy_matrix),
                ),
                resize=(300, 300),
                text=f"e={np.round(energy, 4)} l={end-start}, c={self.current_cycle}",
                text_params={"pos": (20, 20), "color": 0},
                event_func=gesture_explorer_handler,
                event_params={
                    "sequence": mei_sequence,
                    "energy_matrix": gesture_energy_matrix,
                },
                wait=0,
            )

    def segment_gestures(
        self, energy_moment_delta_volumes, mei_volumes, mhi_volumes, cycle, cycle_name
    ):
        """
        Outputs updated gesture sequences based on the
        computed best sequence in the passed volumes
        NOTE - this class initializes with the current list of sequences
        then with "segment gestures" method, the newly found gesture is appended
        to the list of sequences - it may eventually make sense to init this once
        but for now initializing a new segmenter each time - this will allow
        params to be adjusted in realtime if needed
        """
        gs = GestureSegmenter(
            energy_diff_gesture_sequences=self.energy_diff_gesture_sequences,
            MEI_gesture_sequences=self.MEI_gesture_sequences,
            MHI_gesture_sequences=self.MHI_gesture_sequences,
            global_gesture_sequences=self.global_gesture_sequences,
            gesture_limit_reached=self.gesture_limit_reached,
            energy_moment_delta_volumes=energy_moment_delta_volumes,
            frame_window_length=self.frame_window_length,
            current_frame=self.current_frame,
            current_cycle=cycle,
            cycle_name=cycle_name,
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

    def display_captured_gestures_window(self):
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
                utils.display_image("Gesture", frame, top=True, wait=0)


# for now putting this outside class to make event handler stuff easier
def gesture_explorer_handler(params):
    def view_gesture(params):
        sequence = params["sequence"]
        for i, s in enumerate(sequence):
            s = np.copy(s)
            display_frame = utils.put_text(s, f"{i}/{len(sequence)}", (15, 15))
            cv2.imshow("Sequence", display_frame)
            cv2.waitKey(50)

    sequence = params["sequence"]
    display_frame = utils.put_text(
        np.copy(sequence[0]), f"{0}/{len(sequence)}", (15, 15)
    )
    cv2.imshow("Sequence", display_frame)
    k = cv2.waitKey(0)
    if k == ord("c"):
        view_gesture(params)
    elif k == ord("q"):
        cv2.destroyAllWindows()
    elif k == ord("n"):
        id = time.time()
        print("Negative")
        cv2.imwrite(f"training/negative/neg_energy-{id}.jpg", params["energy_matrix"])
        with open(f"training/negative/pos_mhi_sequence-{id}.npy", "wb") as f:
            np.save(f, sequence)
    elif k == ord("p"):
        id = time.time()
        print("Positive")
        cv2.imwrite(f"training/positive/pos_energy-{id}.jpg", params["energy_matrix"])
        with open(f"training/positive/neg_mhi_sequence-{id}.npy", "wb") as f:
            np.save(f, sequence)

    print("Viewing gesture")
    return True
