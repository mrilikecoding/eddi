import json
import numpy as np


class SpatialLightController:
    def __init__(self, output_devices={}, send_channel_message=None, send_message=None):
        # define the default min/max x,y,z input values
        # these will be used to determine degree of membership
        # for fuzzy logic
        self.space_max_x = 400.0
        self.space_max_y = 150.0
        self.space_max_z = 1000.0
        self.space_min_x = 0.0
        self.space_min_y = 0.0
        self.space_min_z = 0.0
        self.self_calibrate = True  # set the max bounds based on incoming data

        # output devices are set from config file
        self.output_devices = output_devices

        # by default these will be handlers pass from lumi
        # send channel message should pass messages to a single instrument channel
        self.send_channel_message = send_channel_message
        # send message hould pass messages to all instrument channels
        self.send_message = send_message

        # from config file, map generic spatial assignments for each instrument
        # to a dictionary keyed off attribute
        self.attr_indexed_output_devices = {}
        self.spatial_categories = [
            "left",
            "right",
            "top",
            "bottom",
            "back",
            "front",
            "middle",
        ]
        try:
            f = open("spatial_device_configuration.json")
            device_config = json.load(f)
            f.close()
            self.device_config = device_config
        except Exception as e:
            print("No device config file found", e)

    def set_output_devices(self, output_devices):
        self.output_devices = output_devices
        if len(output_devices.items()):
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
        x_norm = (x - self.space_min_x) / (self.space_max_x - self.space_min_x)
        y_norm = (y - self.space_min_y) / (self.space_max_y - self.space_min_y)
        z_norm = (z - self.space_min_z) / (self.space_max_z - self.space_min_z)
        return x_norm, y_norm, z_norm

    def update_input(self, object_instance):
        for person, attrs in object_instance.people.items():
            if "head" in attrs:
                person_id = person
                x = attrs["head"]["x"]
                y = attrs["head"]["y"]
                z = attrs["head"]["z"]
                if self.self_calibrate:
                    self.calibrate_min_max(x, y, z)

                print("Non-normalized", person, x, y, z)
                x, y, z = self.normalize_3d_point(x, y, z)
                for device_name in self.output_devices.keys():
                    self.send_channel_message(device_name, "r", x)
                    self.send_channel_message(device_name, "g", y)
                    self.send_channel_message(device_name, "b", z)
                print("Normalized", person, x, y, z)
