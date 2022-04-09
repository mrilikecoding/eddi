from pythonosc import udp_client
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder

# Set up a mapping of OSC addresses to QLC+ virtual console sliders which are themselves mapped to functions controlling dmx channels
class Lumi:
    def __init__(
        self, send_server="127.0.0.1", send_port=7700, osc_message_prefix="/dmxout/"
    ):
        self.client = udp_client.SimpleUDPClient(send_server, send_port)
        self.osc_message_prefix = osc_message_prefix
        self.registry = {}

    def register_device(self, device):
        self.registry[device.name] = device

    def blackout(self):
        for device_name in self.registry.keys():
            self.send_message(device_name, 0)

    def send_message(self, device_name, value):
        """
        send the same value to every channel on a device
        """
        try:
            for channel_name in self.registry[device_name].channels.keys():
                self.client.send_message(
                    self.osc_message_prefix + device_name + channel_name, value
                )
                self.registry[device_name].set_value(channel_name, value)
                print(f"Sent {device_name + channel_name} val {value}.")
        except Exception as e:
            print(f"Couldn't send message to {device_name}...")
            print(e)

    def send_channel_message(self, device_name, channel_name, value):
        """
        send value to channel on a device
        """
        try:
            self.client.send_message(
                self.osc_message_prefix + device_name + channel_name, value
            )
            self.registry[device_name][channel_name] = value
            print(f"Sent {device_name + channel_name} val {value}.")
        except Exception as e:
            print(f"Couldn't send message to {device_name}...")
            print(e)
