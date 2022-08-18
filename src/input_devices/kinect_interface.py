class KinectInterface:
    """
    Input via OSC - specify the address prefix of messages from this device
    This class keeps track of kinect position state for up to 6 people (according to kinect v1 spec)
    Written assuming joint position coordinates (x, y, z) are send via osc messages
    """

    def __init__(self):
        # TODO make an interface here since this is also going to be
        # used to parse the skel data for MHIs
        self.name = "kinect"
        self.osc_addr_prefix = "/kinect"
        self.people = {}  # track individual people
        self.tracking = {}
        # what skeleton positions / joints are we interested in?
        self.joint_list = [
            "head",
            "neck",
            "leftShoulder",
            "leftElbow",
            "leftHand",
            "rightShoulder",
            "rightElbow",
            "rightHand",
            "torso",
            "leftHip",
            "rightHip",
            # "leftKnee",
            # "rightKnee",
            # "leftFoot",
            # "rightFoot",
        ]

    def update_from_osc(self, unused_addr, *obj):
        """
        Must conform to message handler signature
        unused_addr, *args

        This parses message received via osc and stores head x y z in a user key
        """
        try:
            if "tracking" in obj:
                user_id = obj[1]
                self.tracking[user_id] = True
                print(f"Kinect - Tracking user {user_id}")
            elif "lost" in obj:
                user_id = obj[1]
                self.tracking[user_id] = False
                print(f"Kinect - Lost user {user_id}")
            else:
                user_id, joint, x, y, z = obj
                if joint not in self.joint_list:
                    return
                if user_id not in self.people:
                    self.people[user_id] = {}
                person = self.people[user_id]

                # update position coordinates
                person[joint] = {"x": x, "y": y, "z": z}
        except Exception as e:
            print("Unable to parse OSC message for Kinect", e)
