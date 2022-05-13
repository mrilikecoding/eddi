import cv2
import numpy as np


class MotionImager:
    def __init__(self, input_device):
        self.input_device = input_device
