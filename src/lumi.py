import asyncio
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc.osc_server import AsyncIOOSCUDPServer

from src.spatial_light_controller import SpatialLightController

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
        self.light_controller = SpatialLightController(
            send_channel_message=self.send_channel_message,
            send_message=self.send_message,
        )

    def register_output_device(self, device):
        self.output_registry[device.name] = device

    def generic_handler(self, unused_addr, *args):
        print(unused_addr, args)

    def input_update_handler(self, input_device_instance):
        self.light_controller.update_input(input_device_instance)

    def register_input_device(self, device_instance):
        self.input_registry[device_instance.name] = device_instance
        self.input_dispatcher.map(
            device_instance.osc_addr_prefix, device_instance.osc_update
        )
        device_instance.set_update_callback(self.input_update_handler)

    def blackout(self):
        for device_name in self.output_registry.keys():
            self.send_message(device_name, 0)

    def send_message(self, device_name, value):
        """
        send the same value to every channel on a device
        """
        device = self.output_registry[device_name]
        try:
            for channel_name in self.output_registry[device.name].channels.keys():
                self.client.send_message(
                    device.osc_addr_prefix + "/" + device.name + channel_name, value
                )
                self.output_registry[device.name].set_value(channel_name, value)
                # print(f"Sent {device.name + channel_name} val {value}.")
        except Exception as e:
            print(f"Couldn't send message to {device.name}...")
            print(e)

    def send_channel_message(self, device_name, channel_name, value):
        """
        send value to channel on a device
        """
        device = self.output_registry[device_name]
        try:
            self.client.send_message(
                device.osc_addr_prefix + "/" + device.name + channel_name, value
            )
            self.output_registry[device.name].set_value(channel_name, value)
            # print(f"Sent {device.name + channel_name} val {value}.")
        except Exception as e:
            print(f"Couldn't send message to {device.name}...")
            print(e)

    def start(self, listener_port=12000, listener_server="127.0.0.1"):
        self.light_controller.set_output_devices(self.output_registry)
        asyncio.run(self.init_main(listener_port, listener_server))

    async def loop(self):
        while True:
            # TODO find something useful put here, like keys for quitting
            self.update()  # if we want to do other stuff...
            await asyncio.sleep(1 / 60)  # FPS

    async def init_main(self, port, ip):
        dispatcher = self.input_dispatcher
        server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
        (
            transport,
            protocol,
        ) = await server.create_serve_endpoint()

        print(f"Lumi is listening on {ip}:{port}")
        await self.loop()  # Enter main loop of program

        self.blackout()  # let's turn off the lights on the way out
        transport.close()  # Clean up serve endpoint

    def update(self):
        pass
