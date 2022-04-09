#!/usr/bin/env python
import time

from src.lumi import Lumi
from src.dimmer import DimmerInterface
from src.kinect_interface import KinectInterface

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
        d = DimmerInterface(dimmer["name"])
        [d.add_channel(c, 0) for c in dimmer["channels"]]
        lumi.register_output_device(d)

    kinect = KinectInterface()
    lumi.register_input_device(kinect, kinect.update_people_data)
    lumi.listen()

    # test send
    for d in dimmers:
        lumi.send_message(d["name"], 0.2)
    time.sleep(2)
    lumi.blackout()
