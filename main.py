#!/usr/bin/env python
import time

import src.lumi as Lumi
import src.dimmer as Dimmer

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
