Set up lights
install QLC plus
Assign fixures in QLC+
In QLC+ visit inputs/outputs
Set the USB DMX interface be an Output device
Set OSC to be an input device on 127.0.0.1 send port 7700 for universe 0
You should see a joystick icon on the universe when sending an OSC message if it's working
In QLC+ create/assign all fixtures
Create a function for each fixture channel - create the func, add the fixture, select one of its channels, max it out and zero out /deactivate the others
Create a slider in the virtual console that uses the function
Auto-detect the OSC message to opereate this slider - choose a consistent naming convention
the address doesn't matter - it will accept a float 0-1 or int 0-255
see lumi.qxw
