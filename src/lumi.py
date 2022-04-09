from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server

# Set up a mapping of OSC addresses to QLC+ virtual console sliders which are themselves mapped to functions controlling dmx channels
class Lumi:
    def __init__(
        self, send_server="127.0.0.1", send_port=7700, osc_message_prefix="/dmxout/"
    ):
        self.client = udp_client.SimpleUDPClient(send_server, send_port)
        self.osc_message_prefix = osc_message_prefix
        self.output_registry = {}
        self.input_registry = {}
        self.input_dispatcher = dispatcher.Dispatcher()

    def register_output_device(self, device):
        self.output_registry[device.name] = device

    def generic_handler(self, unused_addr, *args):
        print(unused_addr, args)

    def register_input_device(self, device, handler=None):
        handler = self.generic_handler if handler == None else handler
        self.input_registry[device.name] = device
        self.input_dispatcher.map(device.osc_addr_prefix, handler)

    def blackout(self):
        for device_name in self.output_registry.keys():
            self.send_message(device_name, 0)

    def send_message(self, device, value):
        """
        send the same value to every channel on a device
        """
        try:
            for channel_name in self.output_registry[device.name].channels.keys():
                self.client.send_message(
                    device.osc_addr_prefix + "/" + device.name + channel_name, value
                )
                self.registry[device.name].set_value(channel_name, value)
                print(f"Sent {device.name + channel_name} val {value}.")
        except Exception as e:
            print(f"Couldn't send message to {device.name}...")
            print(e)

    def send_channel_message(self, device, channel_name, value):
        """
        send value to channel on a device
        """
        try:
            self.client.send_message(
                device.osc_addr_prefix + "/" + device.name + channel_name, value
            )
            self.output_registry[device.name][channel_name] = value
            print(f"Sent {device.name + channel_name} val {value}.")
        except Exception as e:
            print(f"Couldn't send message to {device.name}...")
            print(e)

    def listen(self, listener_port=12000, listener_server="127.0.0.1"):
        dispatcher = self.input_dispatcher
        server = osc_server.ThreadingOSCUDPServer(
            (listener_server, listener_port), dispatcher
        )
        print(f"Lumi is listening on {server.server_address}")
        server.serve_forever()
