global_config = {
    "pattern_sequencer": {
        "mode": "static",
        # "mode": "oscillator"
    },
    # how much from 0-1 should this sequencer influence the lights when layering in other sequences
    # 0 means this output will not be present when competing with other sequencers
    # 1 means this outout will be out 1/(number of other sequences layered in)
    # these values will be added and normalized between 0-1
    "output_weights": {
        "fuzzy_tracker": 0.5,
        "pattern_sequencer": 0.2,
        "gesture_pipeline": 1.0,
    },
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
    "miror_canvas_display": True,  # helpful if you're watching yourself
    "train_gesture_segmenter": True,
    "frame_decay": 3,  # how much to decay each frame in motion history
    "frame_window_length": 70,  # how many frames to keep in memory
    "display_gesture_matrices": False,  # visualize similarity / transition matrices from gesture segmenter
    "display_captured_gestures": False,  # display captured gestures when limit is reached
    "display_mhi_canvas": True,  # visualize similarity / transition matrices from gesture segmenter
    "gesture_limit": 3,  # max number of gestures to maintain for comparison
    "gesture_heuristics": {
        "gesture_sensitivity": 0.3,  # how much to smoothe out the transition matrices - bigger values mean looser transitions
        "minimum_frame_count": 30,  # min magnitude (frame count) of gesture
        "maximum_frame_count": 65,  # max magnitude (frame count) of gesture
        "min_std_threshold": 80.0,  # how much  variance should be in the gesture
        "min_energy_threshold": 2.0,  # how much energy should a gesture have
        "max_energy_threshold": 10.0,  # upper bound of gesture energy
    },
    "repeated_gesture_similarity_threshold": 7.0,  # upper bound of similarity score when selected a repeated gesture
    "weight_increase_factor": 2.5,  # how much to scale up the weight of a repeated gesture
    "weight_pruning_threshold": 0.18,  # when to drop off a gesture from library if the weights have been lowered enough
    "load_saved_sequences_into_dashboard": True,
    "load_saved_sequences_name": "sequences-1658782988.753462",
    "saved_sequences_path": "saved_sequences/",
    "view_light_sequence_plots": True,
}
