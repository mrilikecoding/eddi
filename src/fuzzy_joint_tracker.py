from src.pipeline_node import PipelineNode
from global_config import global_config


class FuzzyJointTracker(PipelineNode):
    def __init__(
        self,
        min_max_dimensions,
    ):
        self.space_joint_to_track = "head"
        self.color_mode = global_config["fuzzy_tracker"]["color_mode"]
        self.weight = global_config["output_weights"]["fuzzy_tracker"]
        self.name = "fuzzy_tracker"
        self.tracking = False
        # for normalizing fuzzy values against min / max dimensions
        # set the max bounds based on incoming data
        self.self_calibrate = False
        self.output = []  # note - make sure to overwrite this and not append to it

        # init pipeline parent
        super().__init__(min_max_dimensions)

    def fuzzy_log(self, x):
        # TODO - pulled out the lib that was performing poorly
        # ideally this is some kind of a sigmoid funcion but x**3 will
        # be fine for now
        # Range 0-1
        if x < 0:
            x = 0
        if x > 1:
            x = 1
        return x**3

    def get_fuzzy_output(self, x, y, z):
        # TODO just running a crude fuzzy pattern for now
        # will try another lib or just define simple DOM funcs
        # since these are relatively simple mappings...
        # NOTE - all rgb values are the same for this tracker
        right = round(self.fuzzy_log(x), 2)
        left = 1.0 - right
        bottom = round(self.fuzzy_log(y), 2)
        top = 1.0 - bottom
        back = round(self.fuzzy_log(z), 2)
        front = 1.0 - back
        middle = (top + bottom) / 2
        # output is dict keyed off positions with value (r, g, b)
        if not self.tracking:
            back = 0
            front = 0
            left = 0
            right = 0
            top = 0
            bottom = 0
            middle = 0
        output = {
            "back": (self.mod_r(back), self.mod_g(back), self.mod_b(back)),
            "front": (self.mod_r(front), self.mod_g(front), self.mod_b(front)),
            "bottom": (self.mod_r(bottom), self.mod_g(bottom), self.mod_b(bottom)),
            "top": (self.mod_r(top), self.mod_g(top), self.mod_b(top)),
            "right": (self.mod_r(right), self.mod_g(right), self.mod_b(right)),
            "left": (self.mod_r(left), self.mod_g(left), self.mod_b(left)),
            "middle": (self.mod_r(middle), self.mod_g(middle), self.mod_b(middle)),
        }
        return output

    def process_input_device_values(self, input_object_instance):
        joint = self.space_joint_to_track
        output_map = {}
        for _, attrs in input_object_instance.people.items():
            if joint in attrs:
                x = attrs[joint]["x"]
                y = attrs[joint]["y"]
                z = attrs[joint]["z"]
                x, y, z = self.normalize_3d_point(x, y, z)
                fuzzy_spatial_map = self.get_fuzzy_output(x, y, z)
                # NOTE: This fuzzy tracker is a real time tracker,
                # so it doesn't output a sequence, but rather a single value
                # however, will follow a convention of returning a list of values
                # as generally these Pipeline Nodes will output sequences that will go
                # into a FIFO queue
                # self.set_spatial_map_values(fuzzy_spatial_map)

                # average the values for each tracked person
                for position, value in fuzzy_spatial_map.items():
                    if output_map.get(position):
                        output_map[position] = (output_map[position] + value) / 2
                    else:
                        output_map[position] = value
            else:
                return
        # can return a sequence, but this is a simple mapper module, so just one frame
        if output_map:
            self.output = [output_map]

    def mod_r(self, value):
        out = value
        if self.color_mode == "ocean":
            out = value * 0.05
        elif self.color_mode == "lava":
            out = value * 1
        elif self.color_mode == "sunshine":
            out = value * 0.9
        else:
            out = value
        return self.constrain(out)

    def mod_g(self, value):
        out = value
        if self.color_mode == "ocean":
            out = value * 0.8
        elif self.color_mode == "lava":
            out = value * 0.10
        elif self.color_mode == "sunshine":
            out = value * 0.9
        else:
            out = value
        return self.constrain(out)

    def mod_b(self, value):
        out = value
        if self.color_mode == "ocean":
            out = value * 0.95
        elif self.color_mode == "lava":
            out = value * 0.05
        elif self.color_mode == "sunshine":
            out = value * 0.10
        else:
            return self.constrain(value)
        return self.constrain(out)

    def constrain(self, value, min=0.0, max=1.0):
        if value < min:
            return min
        if value > max:
            return max
        return value
