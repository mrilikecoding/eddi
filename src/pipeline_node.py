import json


class PipelineNode:
    def __init__(self, min_max_dimensions):
        self.space_min_x = min_max_dimensions["min_x"]
        self.space_min_y = min_max_dimensions["min_y"]
        self.space_min_z = min_max_dimensions["min_z"]
        self.space_max_x = min_max_dimensions["max_x"]
        self.space_max_y = min_max_dimensions["max_y"]
        self.space_max_z = min_max_dimensions["max_z"]

        # assume we have some discrete spatial areas and at least one binary primary axis
        # TODO can probably abstract this from config file
        # making this more abstract will enable different kinds of space partitioning
        spatial_categories = [
            "left",
            "right",
            "top",
            "bottom",
            "back",
            "front",
            "middle",
        ]
        primary_axis = ["left", "right"]

        # TODO there can be a multi-space hierarchy that defines
        # categories for each space and their primary axes
        self.spatial_categories = spatial_categories

        # Initializing an output sequence - this can be any length
        # sequence of length 1 is like tracking realtime
        # sequence > length 1 will be layered into an output stream
        self.output = []

    def process_input_device_values(self, input_device_instance=None):
        """
        Make sure to implement this function in any subclass

        If this pipeline node should update output device values,
        then this method should call self.set_spatial_map_values with
        a dictionary keyed off each spatial category and values
        between 0 and 1

        Example:
            spatial_map_values = {
                "back": 0.1,
                "front": 1.0,
                "bottom": 1.0,
                "top": 0.4,
                "right": 1.0,
                "left": 0.1,
                "middle": 0.0,
            }
            self.set_spatial_map_values(spatial_map_values)
        """
        raise NotImplementedError

    def set_space_boundaries(self, min_max_dimensions):
        self.space_min_x = min_max_dimensions["min_x"]
        self.space_min_y = min_max_dimensions["min_y"]
        self.space_min_z = min_max_dimensions["min_z"]
        self.space_max_x = min_max_dimensions["max_x"]
        self.space_max_y = min_max_dimensions["max_y"]
        self.space_max_z = min_max_dimensions["max_z"]

    def calibrate_min_max(self, x, y, z):
        if x > self.space_max_x:
            self.space_max_x = x
        if y > self.space_max_y:
            self.space_max_y = y
        if z > self.space_max_z:
            self.space_max_z = z
        if x < self.space_min_x:
            self.space_min_x = x
        if y < self.space_min_y:
            self.space_min_y = y
        if z < self.space_min_z:
            self.space_min_z = z

    def normalize_3d_point(self, x, y, z):
        if x > self.space_max_x:
            x = self.space_max_x
        if y > self.space_max_y:
            y = self.space_max_y
        if z > self.space_max_z:
            z = self.space_max_z
        if x < self.space_min_x:
            x = self.space_min_x
        if y < self.space_min_y:
            y = self.space_min_y
        if z < self.space_min_z:
            z = self.space_min_z
        x_norm = (x - self.space_min_x) / (self.space_max_x - self.space_min_x)
        y_norm = (y - self.space_min_y) / (self.space_max_y - self.space_min_y)
        z_norm = (z - self.space_min_z) / (self.space_max_z - self.space_min_z)
        return x_norm, y_norm, z_norm

    def normalize_point(
        self, x, min_x, max_x, min_target, max_target, return_boundary=False
    ):
        # sometimes we may want to ignore extremes rather than
        # altering their value
        if return_boundary:
            if x > max_x:
                x = max_x
            if x < min_x:
                x = min_x

        x_norm = ((x - min_x) / (max_x - min_x)) * (max_target - min_target)
        return x_norm
