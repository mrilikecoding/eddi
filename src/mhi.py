import cv2
import numpy as np


import OpenGL
import OpenGL.GL
import OpenGL.GLUT
import OpenGL.GLU

from src.pipeline_node import PipelineNode


class MotionHistoryImager(PipelineNode):
    def __init__(self, min_max_dimensions):
        self.input_joint_list = []
        super().__init__(min_max_dimensions)

    def process_input_device_values(self, input_object_instance):
        try:
            if not self.input_joint_list:
                self.input_joint_list = input_object_instance.joint_list

            self.draw_skeleton(input_object_instance)

        except Exception as e:
            print(f"Problem parsing input device data: {e}")

    def draw_skeleton(self, input_object_instance):
        for person, attrs in input_object_instance.people.items():
            for joint in self.input_joint_list:
                x = attrs[joint]["x"]
                y = attrs[joint]["y"]
                z = attrs[joint]["z"]
                x, y, z = self.normalize_3d_point(x, y, z)
