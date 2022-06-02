from src.pipeline_node import PipelineNode


class FuzzyJointTracker(PipelineNode):
    def __init__(
        self,
        min_max_dimensions,
    ):
        self.space_joint_to_track = "head"
        # for normalizing fuzzy values against min / max dimensions
        # set the max bounds based on incoming data
        self.self_calibrate = False

        # init pipeline parent
        super().__init__(min_max_dimensions)

    def fuzzy_log(self, x):
        # assume 0-1
        if x < 0:
            x = 0
        if x > 1:
            x = 1
        return x**3

    def get_fuzzy_output(self, x, y, z):
        # TODO just running a crude fuzzy pattern for now
        # will try another lib or just define simple DOM funcs
        # since these are relatively simple mappings...
        right = round(self.fuzzy_log(x), 2)
        left = 1.0 - right
        bottom = round(self.fuzzy_log(y), 2)
        top = 1.0 - bottom
        back = round(self.fuzzy_log(z), 2)
        front = 1.0 - back
        middle = (top + bottom) / 2
        output = {
            "back": back,
            "front": front,
            "bottom": bottom,
            "top": top,
            "right": right,
            "left": left,
            "middle": middle,
        }
        return output

    def process_input_device_values(self, input_object_instance):
        joint = self.space_joint_to_track
        for person, attrs in input_object_instance.people.items():
            if joint in attrs:
                x = attrs[joint]["x"]
                y = attrs[joint]["y"]
                z = attrs[joint]["z"]
                x, y, z = self.normalize_3d_point(x, y, z)
                fuzzy_spatial_map = self.get_fuzzy_output(x, y, z)
                self.set_spatial_map_values(fuzzy_spatial_map)
