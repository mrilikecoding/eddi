import copy
import numpy as np

from global_config import global_config


class Director:
    """
    The purpose of this class is to gather information from various places
    in the system and use that information to broadly learn and make decisions
    that impact that output


    El Nasr - DigitalBeing: An Ambient Intelligence Interactive Dance Experience (2006)
    Some aesthetic research on "arousal" in terms of color when they build ELE, then ALVA
    Adaptive lighting engines

    The research found:
    1. Maintaining 70-100% light saturation for some time increases arousal
    2. Following high saturation with low saturation (100->10%) over a sequence decreases arousal
    3. Following low saturation with high saturation (10->100%) over a sequence increases arousal
    4. Following high brightness with low brightness (100->10%) over a sequence increases arousal
    5. Following low brightness with hight brightness (10->100%) over a sequence decreases arousal
    6. Following warm colors with cool colors (100% warmth to 10% warmth) over a sequence decreases arousal
    7. Following cool colors with warm colors (10% warmth to 100% warmth) over a sequence increases arousal
    8. Increasing brightness contrast over a sequence (more clearly defined brighter and darker spots) increases arousal
    9. Decreasing brightness contrast over a sequence (moving to more evenly distributed light) decreases arousal
    10. Increasing warm/cool contrast over a sequence (more clearly defined warm and cool spots) increases arousal
    11. Decreasing warm/cool contrast over a sequence (moving to more evenly distributed color) decreases arousal

    El Nasr (2006) "These patterns will be used...to reflect a decrease or increase in the dancer's arousal state
    based on the current lighting state"


    Other glossary terms:
    Distribution - where light is and how it works
    Direction - where does the light come from. Society dictates that lights simulate environments (that’s why lights are usually hung)
    Shape and size
    Quality of light - Clear versus diffused 1-10 (shadows versus no shadows)
    Character
        - smooth - very even lighting (sunlight)
        - uneven - bright spots, dark spots
        - pattern - specific patterns of lighting (tree shadows)
    Intensity - dim versus bright. Incandecent - warm versus flourescent (cool)
    Movement - how light moves -> sun moving over the course of the day
        - Special FX, follow spots
    Color - light is nearly opposite than pigment

    4 Functions of Stage Lighting:

    Visibility - what should and shouldn’t be seen
    Selective Focus - forcing audience to look at a certain place
    Modeling - being able to see people as if it were real light (e.g. light after sunset)
    Mood - what is the tone of the piece - warm versus cool?


    Properties
        Global light
            Variables
                * Character (smooth, uneven, pattern)
                * Quality (scale clear -> diffused)
                * Movement (temporal shift)
                * Focus (where is focus drawn on stage)
                * Modeling (achieving a specific look like sunset)
                * Mood (warm versus cool)
        For each fixture:
            Preset
                * Direction
            Variable (atomic representations)
                * Color
                * Intensity
    """

    def __init__(self, current_queue=None, current_queue_meta=None):
        # annealing stuff for experimenting
        self.epoch = 0
        self.temp = 10
        self.step_size = 0.1

        self.current_queue = current_queue
        self.current_queue_meta = current_queue_meta
        self.config = global_config
        self.network_properties = None
        # some vars for helping determing state / reward function
        self.eval = 0.0  # just naively establishing a reward var
        self.current_eval = None
        self.previous_eval = None
        # coining psychological stimulation so I don't have to write "arousal" over and over
        self.eval_max = 1.0
        self.eval_min = -1.0
        self.goal = "increase_ps"  # increase psychological stimulation
        # what vars to adjust for annealing
        self.reward_config = {
            "pattern_r": {
                "value": self.config["pattern_sequencer"]["director_control"][
                    "r_ratio"
                ],
                "min_max": (0, 1),
                "inc": 0.1,
            },
            "pattern_g": {
                "value": self.config["pattern_sequencer"]["director_control"][
                    "g_ratio"
                ],
                "min_max": (0, 1),
                "inc": 0.1,
            },
            "pattern_b": {
                "value": self.config["pattern_sequencer"]["director_control"][
                    "b_ratio"
                ],
                "min_max": (0, 1),
                "inc": 0.1,
            },
        }

    def update(self):
        self.update_current_eval()
        if self.current_eval == 1.0:
            self.goal = "decrease_ps"
        elif self.current_eval == -1.0:
            self.goal = "increase_ps"

        # self.run_annealing()
        self.run_not_real_annealing()
        self.epoch += 1

    def run_not_real_annealing(self):
        r = self.config["pattern_sequencer"]["director_control"]["r_ratio"]
        b = self.config["pattern_sequencer"]["director_control"]["b_ratio"]
        g = self.config["pattern_sequencer"]["director_control"]["g_ratio"]
        if self.reward_increasing():
            r += 0.002
            g -= 0.01
            b -= 0.02
        elif self.reward_decreasing():
            r -= 0.2
            g += 0.1
            b += 0.2

        self.config["pattern_sequencer"]["director_control"]["r_ratio"] = r
        self.config["pattern_sequencer"]["director_control"]["b_ratio"] = g
        self.config["pattern_sequencer"]["director_control"]["g_ratio"] = b

    def run_annealing(self):
        if self.epoch == 0:
            return
        # https://machinelearningmastery.com/simulated-annealing-from-scratch-in-python/
        # calculate temperature for current epoch
        candidate = self.current_eval + np.random.randint(10.0 * self.step_size)
        t = self.temp / float(self.epoch + 1)
        diff = self.current_eval - self.previous_eval

        metropolis = np.exp(-diff / t)

    def update_current_eval(self):
        if self.eval >= 1.0:
            self.eval = 1.0
        if self.eval <= -1.0:
            self.eval = -1.0
        self.previous_eval = copy.copy(self.current_eval)
        self.current_eval = self.eval

    def reward_increasing(self):
        if self.current_eval and self.previous_eval:
            if self.current_eval > self.previous_eval:
                return True
            else:
                return False
        return False

    def reward_decreasing(self):
        if self.current_eval and self.previous_eval:
            if self.current_eval > self.previous_eval:
                return False
            else:
                return True
        return False
