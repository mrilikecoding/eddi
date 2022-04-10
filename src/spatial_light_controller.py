# from house perspective
# TODO store in separate config file
SPATIAL_DEVICE_CONFIGURATION = {
    "d01": {
        "right": False,
        "left": True,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d02": {
        "right": False,
        "left": True,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d03": {
        "right": False,
        "left": True,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d04": {
        "right": False,
        "left": True,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d05": {
        "right": False,
        "left": True,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d06": {
        "right": False,
        "left": True,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d07": {
        "right": False,
        "left": True,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d08": {
        "right": False,
        "left": True,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d09": {
        "right": True,
        "left": False,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d10": {
        "right": True,
        "left": False,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d11": {
        "right": True,
        "left": False,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d12": {
        "right": True,
        "left": False,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d13": {
        "right": True,
        "left": False,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d14": {
        "right": True,
        "left": False,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d15": {
        "right": True,
        "left": False,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "d16": {
        "right": True,
        "left": False,
        "back": False,
        "front": False,
        "top": True,
        "middle": False,
        "bottom": False,
    },
    "s1": {
        "right": True,
        "left": False,
        "back": False,
        "front": False,
        "top": False,
        "middle": True,
        "bottom": False,
    },
    "s2": {
        "right": False,
        "left": True,
        "back": False,
        "front": False,
        "top": False,
        "middle": True,
        "bottom": False,
    },
    "f1": {
        "right": True,
        "left": False,
        "back": False,
        "front": True,
        "top": False,
        "middle": False,
        "bottom": True,
    },
    "f2": {
        "right": True,
        "left": False,
        "back": True,
        "front": False,
        "top": False,
        "middle": False,
        "bottom": True,
    },
    "f3": {
        "right": False,
        "left": True,
        "back": True,
        "front": False,
        "top": False,
        "middle": False,
        "bottom": True,
    },
    "f4": {
        "right": False,
        "left": True,
        "back": False,
        "front": True,
        "top": False,
        "middle": False,
        "bottom": True,
    },
}


class SpatialLightController:
    def __init__(self, output_devices={}):
        self.output_devices = output_devices
        self.attr_indexed_output_devices = {}
        self.device_config = SPATIAL_DEVICE_CONFIGURATION

    def set_output_devices(self, output_devices):
        self.output_devices = output_devices
        if len(output_devices.items()):
            self.index_output_devices_by_config_attribute()

    def index_output_devices_by_config_attribute(self):
        for device in self.output_devices.keys():
            config = self.device_config[device]
            for k, v in config.items():
                if k in self.attr_indexed_output_devices:
                    if v == True:
                        self.attr_indexed_output_devices[k].append(device)
                else:
                    if v == True:
                        self.attr_indexed_output_devices[k] = [device]

    def light_coordinates(self, object_instance):
        for person, attrs in object_instance.people.items():
            if "head" in attrs:
                person_id = person
                x = attrs["head"]["x"]
                y = attrs["head"]["y"]
                z = attrs["head"]["z"]
                print(person_id, x, y, z)
