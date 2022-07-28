import numpy as np
import math

from src.gesture_dashboard import GestureDashboard


class GestureComparer:
    def __init__(self, gesture_sequence_library=[], gesture_limit=5, director=None):
        self.director = director
        self.gesture_limit = gesture_limit
        self.gesture_sequence_library = gesture_sequence_library
        self.weights = np.array([1 for g in gesture_sequence_library]) / len(
            gesture_sequence_library
        )
        self.similarities = [0 for _ in range(self.gesture_limit)]
        self.similarities_meta = [{} for _ in range(self.gesture_limit)]
        self.gesture_classifier = None
        self.similarity_threshold = 0.5  # just a placeholder val
        self.best_output = None
        self.candidate_sequences = None
        self.most_similar_sequence_index = None
        self.detected_gesture_count = 0
        self.gestures_locked = False

        self.dashboard = GestureDashboard(director=self.director)

    def process_cycle(self):
        # loop captured gestures
        self.dashboard.set_comparer_instance(gesture_comparer=self)
        self.dashboard.display_dashboard()

    def ingest_sequences(self, sequences):
        if self.gestures_locked or sequences is None:
            return
        self.candidate_sequences = sequences
        self.detected_gesture_count += 1
        if len(self.gesture_sequence_library) < self.gesture_limit:
            self.most_similar_sequence_index = None
            self.gesture_sequence_library.append(sequences)
            self.best_output = sequences
            if len(self.weights) == 0:
                self.set_gesture_weights()
            else:
                self.weights = np.append(
                    self.weights, 1 / len(self.gesture_sequence_library)
                )
                self.normalize_weights()
            self.set_similarities()
        else:
            self.similarities = self.compute_similarity(sequences)
            # Update best output based on similarity scores
            most_similar_idx = np.argmin(self.similarities)

            if (
                self.similarities[most_similar_idx]
                < self.director.config["repeated_gesture_similarity_threshold"]
            ):
                self.most_similar_sequence_index = (
                    most_similar_idx,
                    self.similarities[most_similar_idx],
                )
                self.update_gesture_weights(most_similar_idx)
                # store the current weight on in the output meta
                self.gesture_sequence_library[most_similar_idx]["meta"][
                    "weight"
                ] = self.weights[most_similar_idx]
                self.best_output = self.gesture_sequence_library[most_similar_idx]
            elif self.director.config["sequence_all_incoming_gestures"] == True:
                self.most_similar_sequence_index = None
                self.best_output = sequences
            else:
                self.most_similar_sequence_index = None
                self.best_output = None
        self.prune_low_weights()
        # Store latest weights in sequence meta
        for i, s in enumerate(self.gesture_sequence_library):
            s["meta"]["weight"] = self.weights[i]

    def compute_similarity(self, sequences):
        """
        for the passed sequences,
        how similar are they to sequences in lib
        if there is a match within threshold
        adjust weights - double the weight of match and renormalize
        if any of the weights are signficantly lower than the others
        then let's relinquish the sequence and add a new gesture
        # to the library
        Sequences are shaped like this:
        {
            "MEI": mei_sequence,
            "MHI": mhi_sequence,
            "energy_diff": energy_diff_sequence,
            "gesture_energy_matrix": gesture_energy_matrix,
            "flattened_mhi": flattened_mhi,
            "meta": {
                "at_frame": self.current_frame,
                "at_cycle": self.current_cycle,
                "cycle_name": self.cycle_name,
                "idxs": self.current_best_sequence[person],
                "energy": energy,
                "std": std,
                "person_id": person,
                "last_mhi_hu_moments": last_mhi_hu_moments,
                "flattened_mhi_hu_moments": flattened_mhi_hu_moments,
            },
        }
        """
        similarities = [
            self.run_similarity_checks(sequences, s)
            for s in self.gesture_sequence_library
        ]

        return similarities

    def run_similarity_checks(self, sequence_a, sequence_b):
        meta_a = sequence_a["meta"]
        meta_b = sequence_b["meta"]
        sim_a = np.concatenate(
            [
                meta_a["last_mhi_hu_moments"][:-1],
                # meta_a["flattened_mhi_hu_moments"],
                [meta_a["energy"]],
                [meta_a["std"]],
            ],
        )

        sim_b = np.concatenate(
            [
                meta_b["last_mhi_hu_moments"][:-1],
                # meta_b["flattened_mhi_hu_moments"],
                [meta_b["energy"]],
                [meta_b["std"]],
            ],
        )

        return np.round(math.dist(sim_a, sim_b), 4)

    def set_similarities(self):
        self.similarities = [0 for g in self.gesture_sequence_library]

    def set_gesture_weights(self):
        self.weights = np.array([1 for g in self.gesture_sequence_library]) / len(
            self.gesture_sequence_library
        )

    def normalize_weights(self):
        self.weights = self.weights / np.sum(self.weights)

    def update_gesture_weights(self, boost_idx):
        self.weights[boost_idx] = (
            self.weights[boost_idx] * self.director.config["weight_increase_factor"]
        )
        self.normalize_weights()

    def prune_low_weights(self):
        """
        this looks for sequences with corresponding weights below a certain threshold
        as defined in global config. If sequence weight is low, prune it and remove
        corresponding entries so a new gesture can take its place
        """
        prune_list = np.array(
            [w < self.director.config["weight_pruning_threshold"] for w in self.weights]
        )
        if not len(self.similarities):
            return
        for i, p in enumerate(prune_list):
            if p:
                self.gesture_sequence_library[i] = None
                self.weights[i] = None
        self.gesture_sequence_library = list(
            filter(lambda v: v != None, self.gesture_sequence_library)
        )
        self.weights = np.array(list(filter(lambda v: v == v, self.weights)))

    def compute_best_sequences(self, candidates):
        """
        Called to choose the greatest standard deviation from a list of passed sequences
        """
        if all(c["meta"]["std"] == candidates[0]["meta"]["std"] for c in candidates):
            return candidates[0]
        else:
            stds = [c["meta"]["std"] for c in candidates]
            best_stds = np.argmax(stds)
            return candidates[best_stds]
