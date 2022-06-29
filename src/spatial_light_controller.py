from global_config import global_config
from src.controller import Controller
from src.fuzzy_joint_tracker import FuzzyJointTracker
from src.mhi import MotionHistoryImager
from src.gesture_pipeline_runner import GesturePipelineRunner


# TODO rename this class - maybe something like IOPipeline
class SpatialLightController(Controller):
    def __init__(self, output_devices={}):

        self.output_devices = output_devices

        # Init processing pipeline node instances
        self.fuzzy_tracker = FuzzyJointTracker(
            min_max_dimensions=global_config["space_min_max_dimensions"],
        )

        # self.display_gesture_matrices = True
        self.MEI_gesture_sequences = {}
        self.MHI_gesture_sequences = {}
        self.energy_diff_gesture_sequences = {}
        self.global_gesture_sequences = []

        # Motion Imaging Initialization
        # track global input image state in this class
        self.motion_history_imager = MotionHistoryImager(
            min_max_dimensions=global_config["space_min_max_dimensions"],
            frame_window_length=global_config["frame_window_length"],
            frame_decay=global_config["frame_decay"],
        )

        # Gesture Pipeline Initialization
        # track global gesture state in this class
        self.gesture_pipeline = GesturePipelineRunner(
            frame_window_length=global_config["frame_window_length"],
            display_gesture_matrices=global_config["display_gesture_matrices"],
            gesture_limit=global_config["gesture_limit"],
            gesture_heuristics=global_config["gesture_heuristics"],
        )

        self.input_processing_pipeline = [
            self.fuzzy_tracker,
            self.motion_history_imager,
        ]

    def process_input_device_values(self, input_object_instance):
        """
        This is the main event loop function
        """
        for node in self.input_processing_pipeline:
            node.process_input_device_values(input_object_instance)

        # motion history imager processes volume of mei and mhi images as well as their diff
        # NOTE - these volumes operate as a FIFO array of images of length frame_window_length
        # each loop, the latest frame is added to the front and the oldest is pushed out
        energy_moment_delta_volumes = (
            self.motion_history_imager.energy_moment_delta_volumes
        )
        mei_volumes = self.motion_history_imager.MEI_volumes
        mhi_volumes = self.motion_history_imager.MHI_volumes
        if energy_moment_delta_volumes and mei_volumes and mhi_volumes:
            self.gesture_pipeline.run_cycle(
                energy_moment_delta_volumes,
                mei_volumes,
                mhi_volumes,
            )

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
