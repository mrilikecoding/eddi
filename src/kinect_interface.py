class KinectInterface:
    """
    Input via OSC - specify the address prefix of messages from this device
    """

    def __init__(self):
        self.name = "kinect"
        self.osc_addr_prefix = "/kinect"
        self.people = {}

    def update_people_data(self, unused_addr, *obj):
        """
        Must conform to message handler signature
        unused_addr, *args

        This parses message received via osc and stores head x y z in a user key
        """
        id = obj[0]
        head_x = obj[1]
        head_y = obj[2]
        head_z = obj[3]
        if id not in self.people:
            self.people[id] = {}

        # update head
        self.people[id]["head"] = {
            "x": head_x,
            "y": head_y,
            "z": head_z,
        }
        print(self.people)
