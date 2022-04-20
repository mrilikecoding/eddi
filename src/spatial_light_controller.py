import json
from src.controller import Controller


class SpatialLightController(Controller):
    def __init__(self, output_devices={}, send_channel_message=None, send_message=None):
        # define the default min/max x,y,z input values
        # these will be used to determine degree of membership
        # for fuzzy logic
        self.space_max_x = 625.0
        self.space_max_y = 300.0
        self.space_max_z = 2700.0
        self.space_min_x = 120.0
        self.space_min_y = 130.0
        self.space_min_z = 1500.0
        self.self_calibrate = False  # set the max bounds based on incoming data

        self.output_devices = output_devices

        # by default these will be handlers pass from lumi
        # send channel message should pass messages to a single instrument channel
        self.send_channel_message = send_channel_message
        # send message hould pass messages to all instrument channels
        self.send_message = send_message

        # from config file, map generic spatial assignments for each instrument
        # to a dictionary keyed off attribute
        self.attr_indexed_output_devices = {}
        # TODO can probably abstract this from config file
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

    def update_input(self, object_instance):
        for person, attrs in object_instance.people.items():
            if "head" in attrs:
                x = attrs["head"]["x"]
                y = attrs["head"]["y"]
                z = attrs["head"]["z"]
                # print(x, y, z)
                if self.self_calibrate:
                    self.calibrate_min_max(x, y, z)
                x, y, z = self.normalize_3d_point(x, y, z)
                fuzzy_spatial_map = self.get_fuzzy_output(x, y, z)
                self.set_spatial_map_values(fuzzy_spatial_map)
        self.send_update()

    def fuzzy_log(self, x):
        # assume 0-1
        if x < 0:
            x = 0
        if x > 1:
            x = 1
        return x**3

    def get_fuzzy_output(self, x, y, z):
        # TODO just running a crude fuzzy pattern for now
        # will try another lib or just define simple DOM funcs
        # since these are relatively simple mappings...
        right = round(self.fuzzy_log(x), 2)
        left = 1.0 - right
        bottom = round(self.fuzzy_log(y), 2)
        top = 1.0 - bottom
        back = round(self.fuzzy_log(z), 2)
        front = 1.0 - back
        middle = (top + bottom) / 2
        output = {
            "back": back,
            "front": front,
            "bottom": bottom,
            "top": top,
            "right": right,
            "left": left,
            "middle": middle,
        }
        return output

    def set_spatial_map_values(self, spatial_map_values):
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

    def send_update(self):
        for d in self.output_devices.keys():
            r = self.output_devices[d].get_value("r")
            g = self.output_devices[d].get_value("g")
            b = self.output_devices[d].get_value("b")
            self.send_channel_message(d, "r", r)
            self.send_channel_message(d, "g", g)
            self.send_channel_message(d, "b", b)
