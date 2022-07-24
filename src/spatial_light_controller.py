import json
import numpy as np

from global_config import global_config
from src.controller import Controller
from src.fuzzy_joint_tracker import FuzzyJointTracker
from src.mhi import MotionHistoryImager
from src.gesture_pipeline_runner import GesturePipelineRunner
from src.pattern_sequence_mapper import PatternSequenceMapper
from src.sequencer import Sequencer


class SpatialLightController(Controller):
    def __init__(self, send_channel_message, output_devices={}):

        # TODO this is repeated a few places - DRY up
        self.spatial_categories = [
            "left",
            "right",
            "top",
            "bottom",
            "back",
            "front",
            "middle",
        ]
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

        # Init processing pipeline node instances
        self.fuzzy_tracker = FuzzyJointTracker(
            min_max_dimensions=global_config["space_min_max_dimensions"],
        )

        # Sequencer Initialization
        self.send_channel_message = send_channel_message
        self.sequencer = Sequencer()

        # Generic Pattern Sequence Mapper (for background textures etc)
        self.pattern_sequence_mapper = PatternSequenceMapper()

        # Gesture Pipeline Initialization
        # track global gesture state in this class
        self.gesture_pipeline = GesturePipelineRunner(
            frame_window_length=global_config["frame_window_length"],
            display_gesture_matrices=global_config["display_gesture_matrices"],
            display_captured_gestures=global_config["display_captured_gestures"],
            gesture_limit=global_config["gesture_limit"],
            gesture_heuristics=global_config["gesture_heuristics"],
        )

        # Motion Imaging Initialization
        # track global input image state in this class
        self.motion_history_imager = MotionHistoryImager(
            min_max_dimensions=global_config["space_min_max_dimensions"],
            frame_window_length=global_config["frame_window_length"],
            frame_decay=global_config["frame_decay"],
            display_canvas=global_config["display_mhi_canvas"],
        )

        self.input_processing_pipeline = [
            self.pattern_sequence_mapper,
            self.fuzzy_tracker,
            self.motion_history_imager,
        ]

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
        for node in self.input_processing_pipeline:
            node.process_input_device_values(input_object_instance)
            if len(node.output):
                outputs.append((node.output, node.weight))

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
            outputs.append((self.gesture_pipeline.output, self.gesture_pipeline.weight))

        # weight each output sequence value according to its weight and number of competing sequences
        weights = [output[1] for output in outputs]
        eps = 1e-10
        normalizer = np.sum(weights) + eps
        for i, output in enumerate(outputs):
            seq = output[0]
            for j, frame in enumerate(seq):
                for k, v in frame.items():
                    outputs[i][0][j][k] = tuple(
                        [x * (weights[i] / normalizer) for x in v]
                    )

        for output in outputs:
            self.sequencer.add_sequence_to_queue(output[0])

    def send_next_frame_values_to_devices(self):
        # get the next column of values in queue
        # average all corresponding outputs
        # send message
        spatial_map_values = self.sequencer.get_next_values()
        if not spatial_map_values:
            return
        self.set_spatial_map_values(spatial_map_values)
        for _, device in self.output_devices.items():
            r = device.get_value("r")
            g = device.get_value("g")
            b = device.get_value("b")
            # TODO figure out other channels
            self.send_channel_message(device.name, "r", r)
            self.send_channel_message(device.name, "g", g)
            self.send_channel_message(device.name, "b", b)

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

    def set_spatial_map_values(self, spatial_map_values):
        """
        The primary axis is a carrier and is modified by other axes
        """
        if not spatial_map_values:
            return

        for location in self.primary_axis:
            for d in self.attr_indexed_output_devices[location]:
                value = spatial_map_values[location]
                self.output_devices[d].set_value("r", value[0])
                self.output_devices[d].set_value("g", value[1])
                self.output_devices[d].set_value("b", value[2])

        for location in self.spatial_categories:
            if location in self.primary_axis:
                continue
            value = spatial_map_values[location]
            for d in self.attr_indexed_output_devices[location]:
                r = self.output_devices[d].get_value("r")
                g = self.output_devices[d].get_value("g")
                b = self.output_devices[d].get_value("b")
                r = r * value[0]
                g = g * value[1]
                b = b * value[2]
                self.output_devices[d].set_value("r", r)
                self.output_devices[d].set_value("g", g)
                self.output_devices[d].set_value("b", b)
