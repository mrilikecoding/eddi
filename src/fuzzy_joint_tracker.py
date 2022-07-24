from src.pipeline_node import PipelineNode
from global_config import global_config


class FuzzyJointTracker(PipelineNode):
    def __init__(
        self,
        min_max_dimensions,
    ):
        self.space_joint_to_track = "head"
        self.weight = global_config["output_weights"]["fuzzy_tracker"]
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
        output = {
            "back": (back, back, back),
            "front": (front, front, front),
            "bottom": (bottom, bottom, bottom),
            "top": (top, top, top),
            "right": (right, right, right),
            "left": (left, left, left),
            "middle": (middle, middle, middle),
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
