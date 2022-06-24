import cv2
from src.controller import Controller
from src.fuzzy_joint_tracker import FuzzyJointTracker
from src.mhi import MotionHistoryImager
from src.gesture_segmenter import GestureSegmenter


class SpatialLightController(Controller):
    def __init__(self, output_devices={}):
        # define the default min/max x,y,z input values
        # TODO if the space is partitioned differently or hierarchically,
        # these will need to be set in config - prob makes sense to do that
        # there anyway - can be overridden by "self callibrate" flag
        self.space_max_x = 500.0
        self.space_min_x = 100.0
        self.space_max_y = 378.0
        self.space_min_y = 100.0
        self.space_max_z = 2950.0
        self.space_min_z = 1400.0
        self.space_min_max_dimensions = {
            "max_x": self.space_max_x,
            "min_x": self.space_min_x,
            "max_y": self.space_max_y,
            "min_y": self.space_min_y,
            "max_z": self.space_max_z,
            "min_z": self.space_min_z,
        }

        self.output_devices = output_devices

        # Init processing pipeline node instances
        self.fuzzy_tracker = FuzzyJointTracker(
            self.space_min_max_dimensions,
        )

        # TODO - put this in global config
        # computed per person sequences
        # as MHI, MEI, and their diff (they'll correspond)
        self.gesture_limit = 5
        self.frame_window_length = 50
        self.maximum_gesture_frame_count = 40
        self.minimum_gesture_frame_count = 20
        self.gesture_energy_threshold = 1200  # TODO find good way to determine this
        self.MEI_gesture_sequences = {}
        self.MHI_gesture_sequences = {}
        self.energy_diff_gesture_sequences = {}
        self.global_gesture_sequences = []
        self.gesture_heuristics = {
            "maximum_frame_count": self.maximum_gesture_frame_count,  # max magnitude of gesture
            "minimum_frame_count": self.minimum_gesture_frame_count,  # min magnitude of gesture
            "energy_threshold": self.gesture_energy_threshold,  # how much energy should a gesture have
        }
        self.current_frame = 0
        self.current_cycle = 0  # number of iterations over frame window
        self.frame_decay = 3  # how much to decay values per frame in MHI
        self.motion_history_imager = MotionHistoryImager(
            self.space_min_max_dimensions,
            frame_window_length=self.frame_window_length,
            frame_decay=self.frame_decay,
        )
        self.input_processing_pipeline = [
            self.fuzzy_tracker,
            self.motion_history_imager,
        ]

    def set_output_devices(self, output_devices):
        """
        This is called by the client when it is started
        Done this way to separate the initialization and starting
        steps

        For each Pipeline node, register all the output devices
        This is for pipeline nodes that will directly need to alter
        output values (see Fuzzy Tracker as an example).

        Output values will be sent to physical devices at the end of each
        processing loop
        """
        self.output_devices = output_devices
        for node in self.input_processing_pipeline:
            node.set_output_devices(self.output_devices)
            node.index_output_devices_by_config_attribute()

    ### SEGMENT GESTURES ###
    def segment_gestures(self, energy_moment_delta_volumes, mei_volumes, mhi_volumes):
        if not energy_moment_delta_volumes:
            return
        # outputs an updated dictionary of gesture sequences based on the
        # previously computed best sequence of the current volumes
        if len(self.global_gesture_sequences) < self.gesture_limit:
            # init a new gesture segmenter that computes the best frame start/end
            # for the passed volume
            gs = GestureSegmenter(
                energy_moment_delta_volumes,
                self.energy_diff_gesture_sequences,
                self.MEI_gesture_sequences,
                self.MHI_gesture_sequences,
                self.global_gesture_sequences,
                frame_window_length=self.frame_window_length,
                current_frame=self.current_frame,
                current_cycle=self.current_cycle,
                alpha=0.5,
                display=True,
                gesture_heuristics=self.gesture_heuristics,
            )
            sequences = gs.segment_gestures(
                energy_moment_delta_volumes, mei_volumes, mhi_volumes
            )
            if sequences is not None:
                (
                    self.energy_diff_gesture_sequences,
                    self.MEI_gesture_sequences,
                    self.MHI_gesture_sequences,
                    self.global_gesture_sequences,
                ) = sequences
        else:
            # TODO remove at some point - this is for testing
            # NOTE - this call is in the loop, so it'll
            # repeat every capture gesture by holding a key
            self.display_captured_gestures()
        # update the frame position within the frame window
        # this is useful for not selecting the same gesture
        # over and over again within a window
        self.current_frame = (self.current_frame + 1) % self.frame_window_length
        # track the number of cycles - this will help make sure
        # we don't tag the same gesture within the same cycle
        if self.current_frame == 0:
            self.current_cycle += 1

    def display_captured_gestures(self):
        # TODO add a conditional flag for this display
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontscale = 0.55
        color = (255, 0, 255)

        for sequence_count, sequence in enumerate(self.global_gesture_sequences):
            sequence_length = len(sequence["MEI"])
            for frame_count, frame in enumerate(sequence["MEI"]):
                info = f"Seq: {sequence_count}, Frame: {frame_count}/{sequence_length}"
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.putText(
                    frame,
                    info,
                    (10, 10),
                    fontFace=font,
                    fontScale=fontscale,
                    color=color,
                    thickness=2,
                )
                cv2.imshow("Gesture", frame)
                cv2.waitKey(0)

    def process_input_device_values(self, input_object_instance):
        for node in self.input_processing_pipeline:
            node.process_input_device_values(input_object_instance)

        # motion history imager processes volume of mei and mhi images as well as their diff
        energy_moment_delta_volumes = (
            self.motion_history_imager.energy_moment_delta_volumes
        )
        mei_volumes = self.motion_history_imager.MEI_volume
        mhi_volumes = self.motion_history_imager.MHI_volume
        if energy_moment_delta_volumes and mei_volumes and mhi_volumes:
            self.segment_gestures(energy_moment_delta_volumes, mei_volumes, mhi_volumes)
