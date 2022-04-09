class DimmerInterface:
    def __init__(self, name=None):
        self.name = name
        self.channels = {}
        self.value = 0
        self.osc_addr_prefix = "/dmxout"

    def add_channel(self, name, value):
        self.channels[name] = value

    def remove_channel(self, name):
        del self.channels[name]

    def set_value(self, channel_name, value):
        self.channels[channel_name] = value

    def get_value(self):
        return self.value
