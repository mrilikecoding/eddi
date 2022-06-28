global_config = {
    # The default min/max x,y,z input values
    # TODO if the space is partitioned differently or hierarchically,
    # these will need to be set in spatial device config - prob makes sense to do that
    # there anyway - can be overridden by "self callibrate" flag
    "space_min_max_dimensions": {
        "max_x": 500.0,
        "min_x": 100.0,
        "max_y": 378.0,
        "min_y": 100.0,
        "max_z": 2950.0,
        "min_z": 1400,
    },
    "frame_decay": 3,  # how much to decay each frame in motion history
    "frame_window_length": 50,  # how many frames to keep in memory
    "display_gesture_matrices": True,  # visualize similarity / transition matrices from gesture segmenter
    "gesture_limit": 5,  # max number of gestures to maintain for comparison
    "gesture_sensitivity": 0.5,  # aka alpha in gesture segmenter
    "gesture_heuristics": {
        "gesture_sensitivity": 0.3,
        "minimum_frame_count": 20,  # min magnitude of gesture
        "maximum_frame_count": 40,  # max magnitude of gesture
        "energy_threshold": 5.0,  # how much energy should a gesture have
    },
}
