import asyncio
import time
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
        self.FPS = 30  # how many updates / frames per sec?
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

    def register_input_device(self, device_instance):
        self.input_registry[device_instance.name] = device_instance
        self.input_dispatcher.map(
            device_instance.osc_addr_prefix, device_instance.update_from_osc
        )

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
            await asyncio.sleep(1 / self.FPS)  # FPS

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

    def update_output_devices(self):
        for _, device in self.input_registry.items():
            # TODO this is the entrypoint for any logic - does this make sense?
            self.light_controller.process_input_device_values(device)
            # TODO figure out how this

        for _, device in self.output_registry.items():
            r = device.get_value("r")
            g = device.get_value("g")
            b = device.get_value("b")
            self.send_channel_message(device.name, "r", r)
            self.send_channel_message(device.name, "g", g)
            self.send_channel_message(device.name, "b", b)

    def update(self):
        self.update_output_devices()
