import time

from src.controller import Controller
from src.fuzzy_joint_tracker import FuzzyJointTracker


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

        # Processing pipeline classes
        self.fuzzy_tracker = FuzzyJointTracker(
            self.space_min_max_dimensions,
        )
        self.processing_pipeline = [self.fuzzy_tracker]

    def set_output_devices(self, output_devices):
        """
        This is called by the client when it is started
        Done this way to separate the initialization and starting
        steps
        """
        self.output_devices = output_devices
        for node in self.processing_pipeline:
            node.set_output_devices(self.output_devices)
            node.index_output_devices_by_config_attribute()

    def process_input_device_values(self, input_object_instance):
        for node in self.processing_pipeline:
            # TODO enforce an interface for pipeline
            node.process_input_device_values(input_object_instance)
