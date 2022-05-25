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
        self.primary_axis = primary_axis

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

    def set_spatial_map_values(self, spatial_map_values):
        """
        The primary axis is a carrier and is modified by other axes
        """
        for location in self.primary_axis:
            for d in self.attr_indexed_output_devices[location]:
                value = spatial_map_values[location]
                r = self.output_devices[d].get_value("r")
                g = self.output_devices[d].get_value("g")
                b = self.output_devices[d].get_value("b")
                r = (r + value) / 2
                g = (g + value) / 2
                b = (b + value) / 2
                self.output_devices[d].set_value("r", r)
                self.output_devices[d].set_value("g", g)
                self.output_devices[d].set_value("b", b)

        for location in self.spatial_categories:
            if location in self.primary_axis:
                continue
            value = spatial_map_values[location]
            for d in self.attr_indexed_output_devices[location]:
                r = self.output_devices[d].get_value("r")
                g = self.output_devices[d].get_value("g")
                b = self.output_devices[d].get_value("b")
                r = r * value
                g = g * value
                b = b * value
                self.output_devices[d].set_value("r", r)
                self.output_devices[d].set_value("g", g)
                self.output_devices[d].set_value("b", b)

    def set_output_devices(self, output_devices):
        self.output_devices = output_devices

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

    def normalize_point(self, x, min_x, max_x, min_target, max_target):
        if x > max_x:
            x = max_x
        if x < min_x:
            x = min_x
        x_norm = ((x - min_x) / (max_x - min_x)) * (max_target - min_target)
        return x_norm
