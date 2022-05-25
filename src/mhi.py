import cv2
import numpy as np

from src.pipeline_node import PipelineNode


class MotionHistoryImager(PipelineNode):
    def __init__(self, min_max_dimensions):
        self.input_joint_list = []
        super().__init__(min_max_dimensions)

    def process_input_device_values(self, input_object_instance):
        try:
            if not self.input_joint_list:
                self.input_joint_list = input_object_instance.joint_list
        except Exception as e:
            print(f"Problem parsing input device data: {e}")
