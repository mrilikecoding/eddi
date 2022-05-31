import cv2
import numpy as np
from skimage.draw import line

from src.pipeline_node import PipelineNode


class MotionHistoryImager(PipelineNode):
    def __init__(self, min_max_dimensions):
        self.input_joint_list = []
        # for normalizing constants
        self.min_x = min_max_dimensions["min_x"]
        self.max_x = min_max_dimensions["max_x"]
        self.min_y = min_max_dimensions["min_y"]
        self.max_y = min_max_dimensions["max_y"]
        self.min_z = min_max_dimensions["min_z"]
        self.max_z = min_max_dimensions["max_z"]

        # set each MHI canvas's dimensions
        self.w = int(min_max_dimensions["max_x"] - min_max_dimensions["min_x"])
        self.h = int(min_max_dimensions["max_y"] - min_max_dimensions["min_y"])

        self.canvas_center = (self.w / 2, self.h / 2)
        self.center_joint = "torso"  # name of joint to center MHI on

        self.init_canvas = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        self.MHI_canvases = {}  # will store a canvas for each person

        # joint position tracking
        self.joint_position_indices = {}
        # Should be a DAG
        self.joint_connections = {
            "head": ["neck"],
            "neck": ["leftShoulder", "rightShoulder", "torso"],
            "leftShoulder": ["leftElbow", "torso"],
            "leftElbow": ["leftHand"],
            "leftHand": [],
            "rightShoulder": ["rightElbow", "torso"],
            "rightElbow": ["rightHand"],
            "rightHand": [],
            "torso": ["leftHip", "rightHip"],
            "leftHip": ["leftKnee", "rightHip"],
            "rightHip": ["rightKnee"],
            "leftKnee": ["leftFoot"],
            "rightKnee": ["rightFoot"],
            "leftFoot": [],
            "rightFoot": [],
        }

        # how fast will history decay per frame?
        # i.e. 0.9 = 90% of previous pixel value this frame
        self.decay_rate = 0.85
        super().__init__(min_max_dimensions)

    def process_input_device_values(self, input_object_instance):
        try:
            if not self.input_joint_list:
                self.input_joint_list = input_object_instance.joint_list

            self.draw_skeleton(input_object_instance)
            self.display_canvases()

        except Exception as e:
            print(f"Problem parsing input device data: {e}")

    def draw_skeleton(self, input_object_instance):
        if not input_object_instance.people.items():
            return
        for person, attrs in input_object_instance.people.items():
            # instantiate a canvas and joint lookup map for each person
            if person not in self.MHI_canvases:
                self.MHI_canvases[person] = np.copy(self.init_canvas)
            if person not in self.joint_position_indices:
                self.joint_position_indices[person] = {}

            # update energy values with decay rate
            canvas = self.MHI_canvases[person]
            canvas[:, :, :] = canvas[:, :, :] * self.decay_rate

            joint_positions = self.joint_position_indices[person]

            # create offset for centering skel on canvas (torso is good choice)
            center_joint_x = self.normalize_point(
                attrs[self.center_joint]["x"], self.min_x, self.max_x, 0, self.w
            )
            center_joint_y = self.normalize_point(
                attrs[self.center_joint]["y"], self.min_y, self.max_y, 0, self.h
            )
            offset_x = int(center_joint_x - self.canvas_center[0])
            offset_y = int(center_joint_y - self.canvas_center[1])

            for joint in self.input_joint_list:
                if joint in attrs:
                    x = int(
                        self.normalize_point(
                            attrs[joint]["x"], self.min_x, self.max_x, 0, self.w
                        )
                    )
                    y = int(
                        self.normalize_point(
                            attrs[joint]["y"], self.min_y, self.max_y, 0, self.h
                        )
                    )
                    z = int(
                        self.normalize_point(
                            attrs[joint]["z"], self.min_z, self.max_z, 0, 179, True
                        )
                    )

                    # offsets may push some coords out of bounds
                    # if so, skip this joint
                    x_prime = x - offset_x
                    y_prime = y - offset_y
                    joint_out_of_bounds = (
                        (x_prime >= self.w)
                        or (x_prime <= 0)
                        or (y_prime >= self.h)
                        or (y_prime <= 0)
                    )
                    if joint_out_of_bounds:
                        continue

                    joint_positions[joint] = (x_prime, y_prime)
                    canvas[y_prime, x_prime] = [
                        z,
                        255,
                        255,
                    ]  # numpy array dim 0 is y dim 1 is x
            self.connect_skel_joints(person)

    def connect_skel_joints(self, person):
        canvas = self.MHI_canvases[person]
        for joint, connections in self.joint_connections.items():
            if joint in self.joint_position_indices[person]:
                x1, y1 = self.joint_position_indices[person][joint]
                for connection in connections:
                    if connection in self.joint_position_indices[person]:
                        x2, y2 = self.joint_position_indices[person][connection]
                        rr, cc = line(x1, y1, x2, y2)
                        z1 = canvas[y1, x1, 0]
                        z2 = canvas[y2, x2, 0]
                        depth_interpolated_values = np.linspace(
                            z1, z2, num=len(rr)
                        ).astype("uint8")

                        canvas[cc, rr, 0] = depth_interpolated_values
                        canvas[cc, rr, 1:] = 255

    def display_canvases(self):
        try:
            canvases = self.init_canvas
            if self.MHI_canvases:
                canvases = np.concatenate(list(self.MHI_canvases.values()), axis=1)
            canvases = cv2.resize(canvases, (self.w * 2, self.h * 2))
            canvases = cv2.cvtColor(canvases, cv2.COLOR_BGR2HSV)
            canvases = cv2.medianBlur(canvases, 5)
            cv2.imshow("MHI Canvas", canvases)
            cv2.waitKey(1)
        except Exception as e:
            print(f"Problem rendering MHI data: {e}")
