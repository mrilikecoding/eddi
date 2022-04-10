import json

class SpatialLightController:
    def __init__(self, output_devices={}):
        self.output_devices = output_devices
        self.attr_indexed_output_devices = {}
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
