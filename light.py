# Set up lights
# install QLC plus via brew
# Assign fixures in QLC+
# In QLC+ visit inputs/outputs
# Set the USB DMX interface be an Output device
# Set OSC to be an input device on 127.0.0.1 send port 7700 for universe 0
# Map fixures to OSC here
# In QLC+ create/assign all fixtures
# for each fixture channel, create a function assigned to the fixture channel
# then for each function, create a virtual slider - configure it to receive an osc message
# the address doesn't matter - it will accept a float 0-1 or int 0-255
# see example.qxw

"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
from mimetypes import init
import random
from re import T
import time

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


class Dimmer:
    def __init__(self, name=None):
        self.name = name
        self.channels = {}
        self.value = 0

    def add_channel(self, name, value):
        self.channels[name] = value

    def remove_channel(self, name):
        del self.channels[name]

    def set_value(self, channel_name, value):
        self.channels[channel_name] = value

    def get_value(self):
        return self.value


if __name__ == "__main__":
    dimmers = [
        {"name": "d01", "channels": ["r", "g", "b"]},
        {"name": "d02", "channels": ["r", "g", "b"]},
        {"name": "d03", "channels": ["r", "g", "b"]},
        {"name": "d04", "channels": ["r", "g", "b"]},
        {"name": "d05", "channels": ["r", "g", "b"]},
        {"name": "d06", "channels": ["r", "g", "b"]},
        {"name": "d07", "channels": ["r", "g", "b"]},
        {"name": "d08", "channels": ["r", "g", "b"]},
        {"name": "d09", "channels": ["r", "g", "b"]},
        {"name": "d10", "channels": ["r", "g", "b"]},
        {"name": "d11", "channels": ["r", "g", "b"]},
        {"name": "d12", "channels": ["r", "g", "b"]},
        {"name": "d13", "channels": ["r", "g", "b"]},
        {"name": "d14", "channels": ["r", "g", "b"]},
        {"name": "d15", "channels": ["r", "g", "b"]},
        {"name": "d16", "channels": ["r", "g", "b"]},
        {"name": "s1", "channels": ["r", "g", "b", "a"]},
        {"name": "s2", "channels": ["r", "g", "b", "a"]},
        {"name": "f1", "channels": ["r", "g", "b", "u"]},
        {"name": "f2", "channels": ["r", "g", "b", "u"]},
        {"name": "f3", "channels": ["r", "g", "b", "u"]},
        {"name": "f4", "channels": ["r", "g", "b", "u"]},
    ]

    lumi = Lumi()
    for dimmer in dimmers:
        d = Dimmer(dimmer["name"])
        [d.add_channel(c, 0) for c in dimmer["channels"]]
        lumi.register_device(d)

    for d in dimmers:
        lumi.send_message(d["name"], 0.2)
    time.sleep(2)
    lumi.blackout()

    # bundle = osc_bundle_builder.OscBundleBuilder(
    #   osc_bundle_builder.IMMEDIATELY)
    # msg = osc_message_builder.OscMessageBuilder(address="/SYNC")
    # msg.add_arg(4.0)
    # # Add 4 messages in the bundle, each with more arguments.
    # bundle.add_content(msg.build())
    # msg.add_arg(2)
    # bundle.add_content(msg.build())
    # msg.add_arg("value")
    # bundle.add_content(msg.build())
    # msg.add_arg(b"\x01\x02\x03")
    # bundle.add_content(msg.build())

    # sub_bundle = bundle.build()
    # # Now add the same bundle inside itself.
    # bundle.add_content(sub_bundle)
    # # The bundle has 5 elements in total now.
    # bundle = bundle.build()
