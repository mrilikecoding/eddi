global_config = {
    "fuzzy_tracker": {
        "enabled": True,
        # "color_mode": "ocean",
        "color_mode": "lava",
        # "color_mode": "sunshine",
    },
    "pattern_sequencer": {
        "enabled": True,
        # "sequence_mode": "static",
        # "sequence_mode": "oscillator1", # THIS ONE IS BROKEN
        # "sequence_mode": "oscillator2",
        "sequence_mode": "perlin",
        "default_perline_range": (0.3, 0.7),
        # "color_mode": "default",
        "color_mode": "ocean",
        # "color_mode": "lava",
        # "color_mode": "sunshine",
    },
    # how much from 0-1 should this sequencer influence the lights when layering in other sequences
    # 0 means this output will not be present when competing with other sequencers
    # 1 means this outout will be out 1/(number of other sequences layered in)
    # these values will be added and normalized between 0-1
    # note - at the moment, these are only compared two at a time. So the logic is if two values are the same
    # then just take the average of the two. Otherwise, use the two values as percentages
    "output_weights": {
        "fuzzy_tracker": 0.01,
        "pattern_sequencer": 0.01,
        "gesture_pipeline": 0.99,
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
    "frame_decay": 3,  # how much to decay each frame in motion history
    "frame_window_length": 70,  # how many frames to keep in memory
    "display_gesture_matrices": False,  # visualize similarity / transition matrices from gesture segmenter
    "display_captured_gestures": False,  # display captured gestures when limit is reached
    "display_mhi_canvas": True,  # visualize similarity / transition matrices from gesture segmenter
    "gesture_limit": 3,  # max number of gestures to maintain for comparison
    "gesture_heuristics": {
        "gesture_sensitivity": 0.2,  # how much to smoothe out the transition matrices - bigger values mean looser transitions
        "minimum_frame_count": 30,  # min magnitude (frame count) of gesture
        "maximum_frame_count": 65,  # max magnitude (frame count) of gesture
        "min_std_threshold": 80.0,  # how much  variance should be in the gesture
        "min_energy_threshold": 2.0,  # how much energy should a gesture have
        "max_energy_threshold": 8.0,  # upper bound of gesture energy
    },
    "sequence_all_incoming_gestures": True,  # if there is no "most similar sequence", still output the latest sequence
    "repeated_gesture_similarity_threshold": 15.0,  # upper bound of similarity score when selected a repeated gesture
    "weight_increase_factor": 3.5,  # how much to scale up the weight of a repeated gesture
    "weight_pruning_threshold": 0.15,  # when to drop off a gesture from library if the weights have been lowered enough
    "load_saved_sequences_into_dashboard": False,  # load in a saved set of sequences from a gesture dashboard
    "load_saved_sequences_name": "sequences-1658942926.640728",  # sequences from gesture dashboard
    "saved_sequences_path": "saved_sequences/",  # path to sequence binaries
    "view_light_sequence_plots": False,  # plot the rgb curves when replaying a gesture
}
