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
        self.frame_window_length = 75
        self.frame_decay = 3
        self.motion_history_imager = MotionHistoryImager(
            self.space_min_max_dimensions,
            frame_window_length=self.frame_window_length,
            frame_decay=self.frame_decay,
        )
        self.input_processing_pipeline = [
            self.fuzzy_tracker,
            self.motion_history_imager,
        ]

        # computed per person sequences
        # as MHI, MEI, and their diff (they'll correspond)
        self.MEI_gesture_sequences = {}
        self.MHI_gesture_sequences = {}
        self.energy_diff_gesture_sequences = {}

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

        gs = GestureSegmenter(
            energy_moment_delta_volumes,
            self.energy_diff_gesture_sequences,
            self.MEI_gesture_sequences,
            self.MHI_gesture_sequences,
            frame_window_length=self.frame_window_length,
            alpha=0.5,
            display=True,
        )
        (
            self.energy_diff_gesture_sequences,
            self.MEI_gesture_sequences,
            self.MHI_gesture_sequences,
        ) = gs.segment_gestures(energy_moment_delta_volumes, mei_volumes, mhi_volumes)

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
