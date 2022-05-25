import cv2
import numpy as np

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

        self.init_canvas = np.zeros((self.w, self.h))
        self.MHI_canvases = {}  # will store a canvas for each person

        # how fast will history decay per frame?
        # i.e. 0.9 = 90% of previous pixel value this frame
        self.decay_rate = 0.95
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
            if person not in self.MHI_canvases:
                self.MHI_canvases[person] = np.copy(self.init_canvas)
            self.MHI_canvases[person] = self.MHI_canvases[person] * self.decay_rate
            canvas = self.MHI_canvases[person]

            # create offset for centering skel on canvas
            center_joint_x = self.normalize_point(
                attrs[self.center_joint]["x"], self.min_x, self.max_x, 0, self.w
            )
            center_joint_y = self.normalize_point(
                attrs[self.center_joint]["y"], self.min_y, self.max_y, 0, self.h
            )
            offset_x = center_joint_x - self.canvas_center[0]
            offset_y = center_joint_y - self.canvas_center[1]

            for joint in self.input_joint_list:
                if joint in attrs:
                    x = int(
                        self.normalize_point(
                            attrs[joint]["x"], self.min_x, self.max_x + 1, 0, self.w
                        )
                        - offset_x
                    )
                    y = int(
                        self.normalize_point(
                            attrs[joint]["y"], self.min_y, self.max_y + 1, 0, self.h
                        )
                        - offset_y
                    )
                    z = int(
                        self.normalize_point(
                            attrs[joint]["z"], self.min_z, self.max_z + 1, 0, 255
                        )
                    )
                    # offsets may push some coords out of bounds
                    # if so, skip this joint
                    if (x >= self.w) or (x <= 0) or (y >= self.h) or (y <= 0):
                        continue
                    canvas[x, y] = z

    def display_canvases(self):
        try:
            canvases = self.init_canvas
            if self.MHI_canvases:
                canvases = np.concatenate(list(self.MHI_canvases.values()), axis=0)
            out = cv2.rotate(canvases, cv2.ROTATE_90_CLOCKWISE)
            cv2.imshow("MHI Canvas", out)
            cv2.waitKey(1)
        except Exception as e:
            print(f"Problem rendering MHI data: {e}")
