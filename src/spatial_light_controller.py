import json
import simpful as sf
from src.controller import Controller


class SpatialLightController(Controller):
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

        # set up Fuzzy logic
        self.FS = sf.FuzzySystem()
        TLV = sf.AutoTriangle(
            3, terms=["low", "mid", "high"], universe_of_discourse=[0, 1]
        )
        # Sigmoid
        # S_1 = sf.InvSigmoidFuzzySet(c=0.5, a=0.2, term="low")
        # S_2 = sf.SigmoidFuzzySet(c=0.5, a=0.2, term="high")
        # sf.LinguisticVariable([S_1, S_2], universe_of_discourse=[0, 1])

        # TODO need to do multiple people additively - normalize?
        # inputs for x, y, z head position
        self.FS.add_linguistic_variable("x", TLV)
        self.FS.add_linguistic_variable("y", TLV)
        self.FS.add_linguistic_variable("z", TLV)
        # self.FS.add_linguistic_variable("x", S_1)
        # self.FS.add_linguistic_variable("x", S_2)
        # self.FS.add_linguistic_variable("y", S_1)
        # self.FS.add_linguistic_variable("y", S_2)
        # self.FS.add_linguistic_variable("z", S_1)
        # self.FS.add_linguistic_variable("z", S_2)

        # relative distance
        self.FS.set_crisp_output_value("low", 0.0)
        self.FS.set_crisp_output_value("mid", 0.5)
        self.FS.set_crisp_output_value("high", 1.0)

        self.FS.add_rules(
            [
                "IF (x IS low) THEN (left IS high)",
                "IF (x IS mid) THEN (left IS mid)",
                "IF (x IS high) THEN (left IS low)",
                "IF (x IS low) THEN (right IS low)",
                "IF (x IS mid) THEN (right IS mid)",
                "IF (x IS high) THEN (right IS high)",
                "IF (y IS low) THEN (bottom IS high)",
                "IF (y IS low) THEN (middle IS mid)",
                "IF (y IS mid) THEN (bottom IS mid)",
                "IF (y IS high) THEN (bottom IS low)",
                "IF (y IS mid) THEN (middle IS high)",
                "IF (y IS mid) THEN (top IS mid)",
                "IF (y IS low) THEN (top IS low)",
                "IF (y IS high) THEN (top IS high)",
                "IF (z IS low) THEN (front IS high)",
                "IF (z IS mid) THEN (front IS mid)",
                "IF (z IS high) THEN (front IS low)",
                "IF (z IS low) THEN (back IS low)",
                "IF (z IS mid) THEN (back IS mid)",
                "IF (z IS high) THEN (back IS high)",
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

                x, y, z = self.normalize_3d_point(x, y, z)
                fuzzy_spatial_map = self.get_fuzzy_output(person_id, x, y, z)
                self.set_spatial_map_values(fuzzy_spatial_map)
        self.send_update()

    def get_fuzzy_output(self, uid, x, y, z):
        self.FS.set_variable("x", x)
        self.FS.set_variable("y", y)
        self.FS.set_variable("z", z)

        fuzz_values = self.FS.inference()
        return fuzz_values

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
