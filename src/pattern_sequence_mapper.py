from asyncio import constants
import numpy as np
from global_config import global_config
from src.pipeline_node import PipelineNode


class PatternSequenceMapper(PipelineNode):
    """
    This is a generic pattern sequence mapper class that provides
    the "Fundamental frequency" so to speak for the lights.
    The patterns loaded here will be the baseline lights that run.
    Other sequence patterns will be added on top of the patterns that
    run here.

    TODO - currently a simple oscillation is programmed, but
    we could load in really specific world looks here that are
    dynamic or static.

    TODO - additionally, this class is where event triggered "scenes"
    can be specified / triggered via midi or osc or whatever
    """

    def __init__(self):
        self.counter = 0
        self.weight = global_config["output_weights"]["pattern_sequencer"]
        self.modulator_value = 100
        # self.samples = np.linspace(-1.0, 1.0, int(self.modulator_value), endpoint=False)
        self.samples = np.linspace(
            0.25, 0.75, int(self.modulator_value), endpoint=False
        )
        self.mode = global_config["pattern_sequencer"]["mode"]

    def process_input_device_values(self, input_device_instance=None):
        if self.mode == "static":
            constant = 0.4
            front = constant
            back = constant
            middle = constant
            top = constant
            bottom = constant
            left = constant
            right = constant
        elif self.mode == "oscillator":
            out_value = 1 - np.abs(
                self.samples[int(self.counter % self.modulator_value)]
            )
            out_value2 = np.abs(self.samples[int(self.counter % self.modulator_value)])
            back = out_value
            front = out_value2
            bottom = out_value
            top = out_value2
            right = out_value
            left = out_value2
            middle = out_value
        output = {
            "back": (back, back, back),
            "front": (front, front, front),
            "bottom": (bottom, bottom, bottom),
            "top": (top, top, top),
            "right": (right, right, right),
            "left": (left, left, left),
            "middle": (middle, middle, middle),
        }
        self.output = [output]
        self.counter += 1
