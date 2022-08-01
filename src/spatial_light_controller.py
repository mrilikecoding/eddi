import json
import numpy as np

from src.controller import Controller
from src.fuzzy_joint_tracker import FuzzyJointTracker
from src.mhi import MotionHistoryImager
from src.gesture_pipeline_runner import GesturePipelineRunner
from src.pattern_sequence_mapper import PatternSequenceMapper
from src.sequencer import Sequencer


class SpatialLightController(Controller):
    def __init__(self, send_channel_message, output_devices={}, director=None):

        # TODO this is repeated a few places - DRY up
        # spatial properties
        self.spatial_categories = [
            "left",
            "right",
            "top",
            "bottom",
            "back",
            "front",
            "middle",
        ]
        # TODO prob remove this? ... don't think we need the primary axis anymore
        self.primary_axis = ["left", "right"]

        self.output_devices = output_devices
        # from config file, map generic spatial assignments for each instrument
        # to a dictionary keyed off attribute
        self.attr_indexed_output_devices = {}
        try:
            f = open("spatial_device_configuration.json")
            device_config = json.load(f)
            f.close()
            self.device_config = device_config
        except Exception as e:
            print("No device config file found", e)

        # instantiate global director that will be passed into nodes
        self.director = director

        # Init processing pipeline node instances
        self.fuzzy_tracker = FuzzyJointTracker(
            min_max_dimensions=self.director.config["space_min_max_dimensions"],
            director=self.director,
        )

        # Sequencer Initialization
        self.send_channel_message = send_channel_message
        self.sequencer = Sequencer(director=self.director)

        # Generic Pattern Sequence Mapper (for background textures etc)
        self.pattern_sequence_mapper = PatternSequenceMapper(director=self.director)

        # Gesture Pipeline Initialization
        # track global gesture state in this class
        self.gesture_pipeline = GesturePipelineRunner(
            frame_window_length=self.director.config["frame_window_length"],
            display_gesture_matrices=self.director.config["display_gesture_matrices"],
            display_captured_gestures=self.director.config["display_captured_gestures"],
            gesture_limit=self.director.config["gesture_limit"],
            gesture_heuristics=self.director.config["gesture_heuristics"],
            director=self.director,
        )

        # Motion Imaging Initialization
        # track global input image state in this class
        self.motion_history_imager = MotionHistoryImager(
            min_max_dimensions=self.director.config["space_min_max_dimensions"],
            frame_window_length=self.director.config["frame_window_length"],
            frame_decay=self.director.config["frame_decay"],
            display_canvas=self.director.config["display_mhi_canvas"],
            director=self.director,
        )

        self.input_processing_pipeline = []
        if self.director.config["pattern_sequencer"]["enabled"]:
            self.input_processing_pipeline.append(self.pattern_sequence_mapper)
        if self.director.config["fuzzy_tracker"]["enabled"]:
            self.input_processing_pipeline.append(self.fuzzy_tracker)
        self.input_processing_pipeline.append(self.motion_history_imager)

    def process_input_device_values(self, input_object_instance):
        """
        This is the main event loop function
        All inputs are processed here via defined pipelines
        And input or processing node instance that needs to
        affect the output should keep an output array that will
        be sent to the sequencer. This function is called by the client
        to start the process. Then the client calls the #send_next_frame_values_to_devices
        to pull values off the sequencer and send to the output devices
        """
        outputs = []
        tracking_user = any(input_object_instance.tracking.values())
        self.fuzzy_tracker.tracking = tracking_user
        for node in self.input_processing_pipeline:
            node.process_input_device_values(input_object_instance)
            if len(node.output):
                outputs.append(
                    {
                        "sequence": node.output,
                        "weight": node.weight,
                        "origin": node.name,
                    }
                )

        # motion history imager processes volume of mei and mhi images as well as their diff
        # NOTE - these volumes operate as a FIFO array of images of length frame_window_length
        # each loop, the latest frame is added to the front and the oldest is pushed out
        energy_moment_delta_volumes = (
            self.motion_history_imager.energy_moment_delta_volumes
        )
        mei_volumes = self.motion_history_imager.MEI_volumes
        mhi_volumes = self.motion_history_imager.MHI_volumes
        self.gesture_pipeline.run_cycle(
            energy_moment_delta_volumes,
            mei_volumes,
            mhi_volumes,
        )
        if self.gesture_pipeline.output and len(self.gesture_pipeline.output):
            outputs.append(
                {
                    "sequence": self.gesture_pipeline.output,
                    "weight": self.gesture_pipeline.weight,
                    "origin": self.gesture_pipeline.name,
                }
            )

        if len(outputs):
            self.sequencer.add_output_sequences_to_queue(outputs)

    def send_next_frame_values_to_devices(self):
        # get the next column of values in queue
        # average all corresponding outputs
        # send message
        spatial_map_values = self.sequencer.get_next_values()
        if not spatial_map_values:
            return False
        r = len(self.spatial_categories)
        c = len(self.output_devices.keys())

        output_matrix = np.empty((r, c, 3), dtype=np.float)
        output_matrix[:, :, :] = np.nan
        for i, location in enumerate(self.spatial_categories):
            for j, device_name in enumerate(self.output_devices.keys()):
                r, g, b = [0, 0, 0]
                if location in spatial_map_values:
                    r, g, b = spatial_map_values[location]
                    if r == -1 and g == -1 and b == -1:
                        r = np.nan
                        g = np.nan
                        b = np.nan
                if device_name in self.attr_indexed_output_devices[location]:
                    output_matrix[i, j, :] = [r, g, b]
        output = np.nanmean(output_matrix, axis=0)
        for i, device in enumerate(self.output_devices):
            device_instance = self.output_devices[device]
            r, g, b = output[i]
            device_instance.set_value("r", r)
            device_instance.set_value("g", g)
            device_instance.set_value("b", b)
            self.send_channel_message(device_instance.name, "r", r)
            self.send_channel_message(device_instance.name, "g", g)
            self.send_channel_message(device_instance.name, "b", b)
        return True

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
        self.index_output_devices_by_config_attribute()

    def index_output_devices_by_config_attribute(self):
        for device in self.output_devices.keys():
            config = self.device_config[device]
            for k, v in config.items():
                if (
                    k in self.spatial_categories
                    and k in self.attr_indexed_output_devices
                ):
                    if v == True:
                        self.attr_indexed_output_devices[k].append(device)
                else:
                    if v == True:
                        self.attr_indexed_output_devices[k] = [device]
