import json
import simpful as sf
import matplotlib.pyplot as plt
from src.controller import Controller


class SpatialLightController(Controller):
    def __init__(self, output_devices={}, send_channel_message=None, send_message=None):
        # define the default min/max x,y,z input values
        # these will be used to determine degree of membership
        # for fuzzy logic
        self.space_max_x = 600.0
        self.space_max_y = 400.0
        self.space_max_z = 2700.0
        self.space_min_x = 200.0
        self.space_min_y = 150.0
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
        try:
            f = open("spatial_device_configuration.json")
            device_config = json.load(f)
            f.close()
            self.device_config = device_config
        except Exception as e:
            print("No device config file found", e)

        # TODO this takes too long - seems to take between 0.16 and 0.25 s to complete
        # set up Fuzzy logic
        self.FS = sf.FuzzySystem()
        D1 = sf.FuzzySet(points=[[0.0, 1.0], [0.5, 0.0]], term="low")
        D2 = sf.FuzzySet(points=[[0.0, 0.0], [0.5, 1.0], [1.0, 0.0]], term="mid")
        D3 = sf.FuzzySet(points=[[0.0, 0.0], [0.5, 0.0], [1.0, 1.0]], term="high")
        for d in ["x", "y", "z"]:
            self.FS.add_linguistic_variable(
                d,
                sf.LinguisticVariable(
                    [D1, D2, D3],
                    concept=f"Where {d} falls in defined min/max range",
                    universe_of_discourse=[0, 1],
                ),
            )

        I1 = sf.FuzzySet(points=[[0.0, 1.0], [0.5, 0.0]], term="zero")
        I2 = sf.FuzzySet(points=[[0.0, 0.0], [0.5, 1.0], [1.0, 0.0]], term="half")
        I3 = sf.FuzzySet(points=[[0.0, 0.0], [0.5, 0.0], [1.0, 1.0]], term="full")
        for spatial_category in self.spatial_categories:
            self.FS.add_linguistic_variable(
                spatial_category,
                sf.LinguisticVariable(
                    [I1, I2, I3],
                    concept=f"Intensity value for {spatial_category}",
                    universe_of_discourse=[0, 1],
                ),
            )

        self.FS.add_rules(
            [
                "IF (x IS low) THEN (left IS full)",
                "IF (x IS high) THEN (left IS zero)",
                "IF (x IS mid) THEN (left IS half)",
                "IF (x IS mid) THEN (right IS half)",
                "IF (x IS low) THEN (right IS zero)",
                "IF (x IS high) THEN (right IS full)",
                # "IF (x IS mid) THEN (right IS mid)",
                # "IF (y IS low) THEN (bottom IS high)",
                # "IF (y IS low) THEN (middle IS mid)",
                # "IF (y IS mid) THEN (bottom IS mid)",
                # "IF (y IS high) THEN (bottom IS low)",
                # "IF (y IS mid) THEN (middle IS high)",
                # "IF (y IS mid) THEN (top IS mid)",
                # "IF (y IS low) THEN (top IS low)",
                # "IF (y IS high) THEN (top IS high)",
                # "IF (z IS low) THEN (front IS high)",
                # "IF (z IS mid) THEN (front IS mid)",
                # "IF (z IS high) THEN (front IS low)",
                # "IF (z IS low) THEN (back IS low)",
                # "IF (z IS mid) THEN (back IS mid)",
                # "IF (z IS high) THEN (back IS high)",
            ]
        )

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
                person_id = person
                x = attrs["head"]["x"]
                y = attrs["head"]["y"]
                z = attrs["head"]["z"]
                # print(x, y, z)
                if self.self_calibrate:
                    self.calibrate_min_max(x, y, z)
                x, y, z = self.normalize_3d_point(x, y, z)
                fuzzy_spatial_map = self.get_fuzzy_output(person_id, x, y, z)
                self.set_spatial_map_values(fuzzy_spatial_map)
        self.send_update()

    def get_fuzzy_output(self, uid, x, y, z):
        # self.FS.set_variable("x", x)
        # self.FS.set_variable("x", y)
        # self.FS.set_variable("x", z)

        # fuzz_values = self.FS.inference()
        # return fuzz_values
        # TODO just running a crude fuzzy pattern for now
        # will try another lib or just define simple DOM funcs
        # since these are relatively simple mappings...
        return {
            "back": z,
            "front": 1 - z,
            "top": 1 - y,
            "bottom": y,
            "right": 1 - x,
            "left": x,
        }

    def set_spatial_map_values(self, spatial_map_values):
        for space, value in spatial_map_values.items():
            devices = self.attr_indexed_output_devices[space]
            for d in devices:
                r = self.output_devices[d].get_value("r")
                g = self.output_devices[d].get_value("g")
                b = self.output_devices[d].get_value("b")
                r = r + value / 2
                g = g + value / 2
                b = b + value / 2
                self.output_devices[d].set_value("r", value)
                self.output_devices[d].set_value("g", value)
                self.output_devices[d].set_value("b", value)

    def send_update(self):
        for d, device in self.output_devices.items():
            r = self.output_devices[d].get_value("r")
            g = self.output_devices[d].get_value("g")
            b = self.output_devices[d].get_value("b")
            self.send_channel_message(d, "r", r)
            self.send_channel_message(d, "g", g)
            self.send_channel_message(d, "b", b)
