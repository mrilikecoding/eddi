import pymunk
from src.pipeline_node import PipelineNode


class FuzzyJointTracker(PipelineNode):
    def __init__(
        self,
        min_max_dimensions,
        director=None,
    ):
        self.director = director
        self.space_joint_to_track = "head"
        self.color_mode = director.config["fuzzy_tracker"]["color_mode"]
        self.weight = director.config["output_weights"]["fuzzy_tracker"]
        self.name = "fuzzy_tracker"
        self.tracking = False
        # for normalizing fuzzy values against min / max dimensions
        # set the max bounds based on incoming data
        self.self_calibrate = False
        self.output = []  # note - make sure to overwrite this and not append to it

        # ### Physics ###
        # self.simulate_physics = False
        # self.space = pymunk.Space()
        # self.space.gravity = (0, 0)
        # self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        # # TODO can create multiple spaces based on spatial config if there are multiple navmesh spaces
        # self.shape = pymunk.Circle(self.body, 80)
        # self.shape.elasticity = 0.4
        # self.shape.friction = 0.5
        # self.space.add(self.body, self.shape)

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

    def update_config_values(self):
        self.min_max_dimensions = (self.director.config["space_min_max_dimensions"],)

    def process_input_device_values(self, input_object_instance):
        self.update_config_values()
        joint = self.space_joint_to_track
        # if self.simulate_physics == True:
        #     joint = "rightHand"
        output_map = {}
        for _, attrs in input_object_instance.people.items():
            if joint in attrs:
                x = attrs[joint]["x"]
                y = attrs[joint]["y"]
                z = attrs[joint]["z"]
                # if self.simulate_physics:
                #     print("origin", x, z)
                #     self.body.position = (x, z)
                #     x = self.shape.body.position.x
                #     z = self.shape.body.position.y
                #     print("pymunk", x, z)
                #     x, y, z = self.normalize_3d_point(x, y, z)
                #     print("normed", x, z)
                # else:
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
        if output_map and self.tracking:
            self.output = [output_map]
        else:
            self.output = []
        # self.space.step(1 / 50)

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
