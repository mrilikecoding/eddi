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
        self.name = "pattern_sequencer"
        self.modulator_value = 100
        self.sequence_mode = global_config["pattern_sequencer"]["sequence_mode"]
        if self.sequence_mode == "oscillator1":
            self.samples = np.linspace(
                0.25, 0.75, int(self.modulator_value), endpoint=False
            )
        if self.sequence_mode == "oscillator2":
            self.samples = np.linspace(
                -1.0, 1.0, int(self.modulator_value), endpoint=False
            )
        self.color_mode = global_config["pattern_sequencer"]["color_mode"]

    def process_input_device_values(self, input_device_instance=None):
        out_value = 0
        if self.sequence_mode == "static":
            constant = 0.2
            front = constant
            back = constant
            middle = constant
            top = constant
            bottom = constant
            left = constant
            right = constant
        elif self.sequence_mode == "oscillator1":
            out_value = self.samples[int(self.counter % self.modulator_value)]
            out_value = self.constrain(out_value)
            back = out_value
            front = out_value
            bottom = out_value
            top = out_value
            right = out_value
            left = out_value
            middle = out_value
        elif self.sequence_mode == "oscillator2":
            out_value = 1 - np.abs(
                self.samples[int(self.counter % self.modulator_value)]
            )
            out_value2 = np.abs(self.samples[int(self.counter % self.modulator_value)])
            if out_value < 0:
                out_value = 0.0
            if out_value < 1.0:
                out_value = 1.0

            back = out_value
            front = out_value2
            bottom = out_value
            top = out_value2
            right = out_value
            left = out_value2
            middle = out_value
        output = {
            "back": (self.mod_r(back), self.mod_g(back), self.mod_b(back)),
            "front": (self.mod_r(front), self.mod_g(front), self.mod_b(front)),
            "bottom": (self.mod_r(bottom), self.mod_g(bottom), self.mod_b(bottom)),
            "top": (self.mod_r(top), self.mod_g(top), self.mod_b(top)),
            "right": (self.mod_r(right), self.mod_g(right), self.mod_b(right)),
            "left": (self.mod_r(left), self.mod_g(left), self.mod_b(left)),
            "middle": (self.mod_r(middle), self.mod_g(middle), self.mod_b(middle)),
        }
        self.output = [output]
        self.counter += 1

    def mod_r(self, value):
        out = value
        if self.color_mode == "ocean":
            out = value * 0.05
        elif self.color_mode == "lava":
            out = value * 1
        else:
            out = value
        return self.constrain(out)

    def mod_g(self, value):
        out = value
        if self.color_mode == "ocean":
            out = value * 0.8
        elif self.color_mode == "lava":
            out = value * 0.01
        else:
            out = value
        return self.constrain(out)

    def mod_b(self, value):
        out = value
        if self.color_mode == "ocean":
            out = value * 0.95
        elif self.color_mode == "lava":
            out = value * 0.30
        else:
            return self.constrain(value)
        return self.constrain(out)

    def constrain(self, value):
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value
