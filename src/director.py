import copy
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

    def __init__(self, current_queue=None):
        self.currrent_queue = current_queue
        self.config = global_config

    def set_current_queue(self, queue, queue_meta):
        self.currrent_queue = queue

    def get_current_queue(self):
        return copy.copy(self.currrent_queue)
