from src.gesture_segmenter import GestureSegmenter
from src.gesture_comparer import GestureComparer
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
        self.gesture_limit_reached = False
        self.display_gesture_matrices = display_gesture_matrices
        self.frame_window_length = frame_window_length
        self.gesture_sensitivity = self.gesture_heuristics["gesture_sensitivity"]

        # initialize the interface for comparing new gestures with stored gestures
        self.gesture_comparer = GestureComparer()

    def run_cycle(self, energy_moment_delta_volumes, mei_volumes, mhi_volumes):
        # from passed volumes, cut out the best determined sequence
        sequences = self.segment_gestures(
            energy_moment_delta_volumes,
            mei_volumes,
            mhi_volumes,
        )
        if sequences is not None:
            if len(self.global_gesture_sequences) < self.gesture_limit:
                (
                    self.energy_diff_gesture_sequences,
                    self.MEI_gesture_sequences,
                    self.MHI_gesture_sequences,
                    self.global_gesture_sequences,
                ) = sequences
            else:
                if self.display_captured_gestures:
                    self.display_captured_gestures()
                self.gesture_comparer.ingest_sequences(sequences)

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
            global_gesture_sequences=self.global_gesture_sequences,
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

        # update the frame position within the frame window
        # this is useful for not selecting the same gesture
        # over and over again within a window
        self.current_frame = (self.current_frame + 1) % self.frame_window_length
        # track the number of cycles - this will help make sure
        # we don't tag the same gesture within the same cycle
        self.current_cycle += 1

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
