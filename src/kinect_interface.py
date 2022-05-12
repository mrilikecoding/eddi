class KinectInterface:
    """
    Input via OSC - specify the address prefix of messages from this device
    """

    def __init__(self, update_callback=lambda x: None):
        self.name = "kinect"
        self.osc_addr_prefix = "/kinect"
        self.people = {}  # track individual people
        self.update_callback = update_callback

    def set_update_callback(self, cb):
        self.update_callback = cb

    def osc_update(self, unused_addr, *obj):
        """
        Must conform to message handler signature
        unused_addr, *args

        This parses message received via osc and stores head x y z in a user key
        """
        try:
            user_id, position, x, y, z = obj
            if user_id not in self.people:
                self.people[user_id] = {}
            person = self.people[user_id]
            if id not in self.people:
                self.people[id] = {}

            # update head
            person[position] = {"x": x, "y": y, "z": z}
        except Exception as e:
            print("Unable to parse OSC message for Kinect", e)

        self.update_callback(self)
