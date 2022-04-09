# starting

1) Set up lights
2) install QLC plus
3) Assign fixures in QLC+
4) In QLC+ visit inputs/outputs
5) Set the USB DMX interface be an Output device
6) Set OSC to be an input device on 127.0.0.1 send port 7700 for universe 0
7) You should see a joystick icon on the universe when sending an OSC message if it's working
8) In QLC+ create/assign all fixtures
9) Create a function for each fixture channel - create the func, add the fixture, select one of its channels, max it out and zero out /deactivate the others
10) Create a slider in the virtual console that uses the function
11) Auto-detect the OSC message to opereate this slider - choose a consistent naming convention
12) the address doesn't matter - it will accept a float 0-1 or int 0-255
13) see lumi.qxw

# Running Lumi
1) start kinect_osc.pde in processing (requires P5OSC and SimpleOpenNI)
2) run main.py