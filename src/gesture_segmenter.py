import math
import time
import cv2
import numpy as np
import scipy.signal
from src import utils
from global_config import global_config


class GestureSegmenter:
    """
    Analyzing energy diff similarity matrices inspired by
    Schödl, Arno, et al. "Video textures." Proceedings of the 27th annual conference on Computer graphics and interactive techniques. 2000.
    """

    def __init__(
        self,
        energy_moment_delta_volumes={},
        MEI_gesture_sequences={},
        MHI_gesture_sequences={},
        energy_diff_gesture_sequences={},
        global_gesture_sequences=[],
        frame_window_length=75,
        current_frame=0,
        current_cycle=0,
        alpha=0.5,
        display=True,
        gesture_heuristics={},
    ):
        self.display = display
        # max number of frame windows / volume size
        self.tau = frame_window_length
        self.current_frame = current_frame
        self.current_cycle = current_cycle
        self.volumes = energy_moment_delta_volumes
        # Alpha is a scaling factor.
        # The size of the loop and the transition cost are likely to be in very different units,
        # so introduce a new parameter to make them comparable.
        # Manipulate alpha to control the tradeoff between loop size and smoothness.
        # Large alphas prefer large loop sizes,
        # and small alphas bias towards short loop sizes.
        # Best alpha is between these extremes (the goldilocks alpha).
        self.gesture_heuristics = gesture_heuristics
        self.display = display
        self.alpha = alpha
        self.similarity_matrices = {}
        self.transition_matrices = {}
        self.current_best_sequence = {}
        # NOTE for output - these sequences are passed in, appended to, and returned
        self.global_gesture_sequences = global_gesture_sequences
        self.MEI_gesture_sequences = MEI_gesture_sequences
        self.MHI_gesture_sequences = MHI_gesture_sequences
        self.energy_diff_gesture_sequences = energy_diff_gesture_sequences

        for key, volume in self.volumes.items():
            if len(volume):
                self.similarity_matrices[key] = self.compute_similarity_matrix(volume)
                self.transition_matrices[key] = self.compute_transition_matrix(
                    self.similarity_matrices[key]
                )
                sequence_idxs = self.find_motion_sequences(
                    transition_matrix=self.transition_matrices[key],
                    alpha=self.alpha,
                )
                if sequence_idxs is not None:
                    self.current_best_sequence[key] = sequence_idxs

        if self.display and self.similarity_matrices and self.transition_matrices:
            # self.display_similarity_matrices()
            self.display_transition_matrices()

    def run_validations(self, sequence_idxs, energy):
        if (
            self.valid_gesture_cycle()
            and self.valid_magnitude(sequence_idxs)
            and self.valid_energy(energy)
            and self.valid_unique_energy(energy)
        ):
            return True
        return False

    def valid_energy(self, energy):
        return (
            self.gesture_heuristics["min_energy_threshold"]
            < energy
            < self.gesture_heuristics["max_energy_threshold"]
        )
    
    def valid_unique_energy(self, energy):
        """
        return false if the energy exactly matches any stored sequences
        """
        return not any([
            stored_sequences["meta"]["energy"] == energy
            for stored_sequences in self.global_gesture_sequences
        ])

    def valid_magnitude(self, idxs):
        """
        return whether passed indices are within a desireable magnitude range
        """
        magnitude = np.abs(idxs[0] - idxs[1])
        min_mag = self.gesture_heuristics["minimum_frame_count"]
        max_mag = self.gesture_heuristics["maximum_frame_count"]
        return min_mag <= magnitude <= max_mag

    def valid_gesture_cycle(self):
        """
        return false if any previously stored gestures have come from this cycle
        """
        return not any(
            [
                sequence["meta"]["at_cycle"] == self.current_cycle
                for sequence in self.global_gesture_sequences
            ]
        )

    def compute_similarity_matrix(self, volume):
        similarity_matrix = np.zeros((self.tau, self.tau))
        if self.tau == len(volume):
            for i in range(self.tau):
                for j in range(self.tau):
                    # TODO could explore a different similarity metric
                    similarity_matrix[i, j] = math.dist(volume[i], volume[j])
        return similarity_matrix

    def display_similarity_matrices(self):
        for volume in self.similarity_matrices.values():
            volume = np.copy(volume)
            cv2.normalize(volume, volume, 0, 255, cv2.NORM_MINMAX)
        diff_similarity_matrices = np.concatenate(
            list(self.similarity_matrices.values()), axis=1
        )
        # for cv2 imshow, waitkey is set in caller, so don't put here, otherwise
        # this will b5e blocking
        diff_similarity_matrices = np.copy(diff_similarity_matrices)
        diff_similarity_matrices = cv2.resize(diff_similarity_matrices, (300, 300))
        utils.display_image(
            "MEI/MHI Diff Similarity Matrices", diff_similarity_matrices
        )

    def display_transition_matrices(self):
        matrices = []
        for key, matrix in self.transition_matrices.items():
            matrix = np.copy(matrix).astype(np.float32)
            matrix = cv2.cvtColor(matrix, cv2.COLOR_BGR2RGB)
            cv2.normalize(matrix, matrix, 0, 255, cv2.NORM_MINMAX)
            if key in self.current_best_sequence:
                sequence_indices = self.current_best_sequence[key]
                matrix = cv2.circle(
                    matrix,
                    (sequence_indices[0], sequence_indices[0]),
                    2,
                    (255, 0, 0),
                    -1,
                )
                matrix = cv2.circle(
                    matrix,
                    (sequence_indices[1], sequence_indices[1]),
                    2,
                    (255, 0, 0),
                    -1,
                )
            matrices.append(matrix)
        transition_matrices = np.concatenate(matrices, axis=1)
        # for cv2 imshow, waitkey is set in caller, so don't put here, otherwise
        # this will be blocking
        transition_matrices = cv2.resize(transition_matrices, (300, 300))
        transition_matrices = utils.put_text(
            transition_matrices,
            str(self.current_best_sequence),
            (10, 100),
            (255, 0, 255),
        )
        utils.display_image("Transition Matrices", transition_matrices)

    def extract_frame_sequence(self, volume, start_end_idxs):
        volume = np.copy(volume)
        frame_sequence = volume[start_end_idxs[0] : start_end_idxs[1] + 1, ...].astype(
            "uint8"
        )
        return frame_sequence

    def binomial_filter_5(self):
        """
        Return a binomial filter of length 5.
        -------
        numpy.ndarray(dtype: np.float)
            A 5x1 numpy array representing a binomial filter.
        """
        return np.array([1 / 16.0, 1 / 4.0, 3 / 8.0, 1 / 4.0, 1 / 16.0], dtype=float)

    def compute_transition_matrix(self, similarity):
        """Compute the transition costs between frames accounting for dynamics.

        Iterate through each cell (i, j) of the similarity matrix (skipping the
        first two and last two rows and columns).  For each cell, calculate the
        weighted sum:

            diff = sum ( binomial * similarity[i + k, j + k]) for k = -2...2
        Note - can do this with 2d colvolution using a filter

        Parameters
        ----------
        similarity : numpy.ndarray
            A similarity matrix as produced by your similarity metric function.

        Returns
        -------
        numpy.ndarray
            A difference matrix that takes preceding and following frames into
            account. The output difference matrix should have the same dtype as
            the input, but be 4 rows and columns smaller, corresponding to only
            the frames that have valid dynamics.
        """
        binomial = np.diag(self.binomial_filter_5())
        # note - this will output the non-padded input
        # so in essence it will shrink by 2 each direction
        transition_matrix = scipy.signal.convolve2d(
            similarity.astype(np.float32), binomial, mode="valid"
        )
        return transition_matrix

    def find_motion_sequences(self, transition_matrix, alpha=0.5):
        """Find the longest and smoothest loop for the given difference matrix.

        For each cell (i, j) in the transition differences matrix, find the
        maximum score according to the following metric:

        score = alpha * (j - i) - transition_diff[j, i]

        The pair i, j correspond to the start and end indices of the longest loop.

        Correct the indices from the transition difference matrix to account for the rows and columns dropped from the edges
                        when the binomial filter was applied.

        Parameters
        ----------
        transition_diff : np.ndarray
            A square 2d numpy array where each cell contains the cost of
            transitioning from frame i to frame j in the input video as returned
            by the transitionDifference function.

        alpha : float
            A parameter for how heavily you should weigh the size of the loop
            relative to the transition cost of the loop. Larger alphas favor
            longer loops, but may have rough transitions. Smaller alphas give
            shorter loops, down to no loop at all in the limit.

        Returns
        -------
        int, int
            The pair of (start, end) indices of the longest loop after correcting
            for the rows and columns lost due to the binomial filter.
        """

        rows, cols = transition_matrix.shape
        scores = np.zeros((rows - 4, cols - 4), dtype=np.float32)
        r, c = scores.shape
        for i in range(r):
            for j in range(c):
                score = np.float32(alpha) * (j - i) - np.float32(
                    transition_matrix[j + 2, i + 2]
                )
                scores[i, j] = score
        biggest_motion_sequence = np.unravel_index(
            np.argmax(scores, axis=None), scores.shape
        )
        sequence_indices = (biggest_motion_sequence[0], biggest_motion_sequence[1])
        return sequence_indices

    def compute_total_energy_change(self, gesture_transition_matrix):
        """
        computes the sum of the mhi - mei sequence values
        this will inevitably be very large (millions)
        let's reduce the size since precision isn't that important
        will multiply by 0.000000
        """
        # TODO there's probably some refining to do here
        # need some better tooling to analyze this
        # not sure if it makes sense to use energy diff sequence
        total_energy_change = np.sum(gesture_transition_matrix)
        total_energy_change = total_energy_change * 1e-6
        return total_energy_change

    def segment_gestures(
        self,
        energy_moment_delta_volumes,
        mei_volumes,
        mhi_volumes,
    ):
        """
        if the current best sequence is None, just return.
        This will be the case if the best gesture does not meet
        heuristic requirements (like gesture magnitude)
        Otherwise, if we have sequence indices, return the sequence as applied to the
        passed volumes
        """
        sequences = {}
        # make sure we've established our full event cycle before extracting gesture
        if self.current_cycle == 0 or self.current_best_sequence is None:
            return
        best_person_frame_sequence_idxs = self.current_best_sequence
        for person, sequence_idxs in best_person_frame_sequence_idxs.items():
            if not person in self.MEI_gesture_sequences:
                self.MEI_gesture_sequences[person] = []
                self.MHI_gesture_sequences[person] = []
                self.energy_diff_gesture_sequences[person] = []
            energy_diff_sequence = self.extract_frame_sequence(
                np.copy(energy_moment_delta_volumes[person]), sequence_idxs
            )
            mei_sequence = self.extract_frame_sequence(
                np.copy(mei_volumes[person]), sequence_idxs
            )
            mhi_sequence = self.extract_frame_sequence(
                np.copy(mhi_volumes[person]), sequence_idxs
            )
            start, end = self.current_best_sequence[person]
            gesture_energy_matrix = self.transition_matrices[person][
                start:end, start:end
            ]
            gesture_energy_matrix = (255 - gesture_energy_matrix).astype(np.uint8)
            energy = self.compute_total_energy_change(gesture_energy_matrix)
            if not self.run_validations(sequence_idxs, energy):
                return
            if global_config["train_gesture_segmenter"]:
                utils.display_image(
                    "Energy Matrix",
                    gesture_energy_matrix,
                    normalize=True,
                    input_range=(
                        np.min(gesture_energy_matrix),
                        np.max(gesture_energy_matrix),
                    ),
                    resize=(300, 300),
                    text=f"e={np.round(energy, 4)} l={end-start}, c={self.current_cycle}",
                    text_params={"pos": (20, 20), "color": 0},
                    event_func=gesture_explorer_handler,
                    event_params={
                        "sequence": mei_sequence,
                        "energy_matrix": gesture_energy_matrix,
                    },
                    wait=0,
                )
            sequences = {
                "MEI": mei_sequence,
                "MHI": mhi_sequence,
                "energy_diff": energy_diff_sequence,
                "gesture_energy_matrix": gesture_energy_matrix,
                "meta": {
                    "at_frame": self.current_frame,
                    "at_cycle": self.current_cycle,
                    "idxs": self.current_best_sequence[person],
                    "energy": energy,
                    "person_id": person,
                },
            }
            print("Gesture detected!")

        # if we have sequences, return them, otherwise return None
        if sequences:
            # TODO will this work
            return sequences


# for now putting this outside class to make event handler stuff easier
def gesture_explorer_handler(params):
    print("Viewing gesture")
    sequence = params["sequence"]
    for i, s in enumerate(sequence):
        s = np.copy(s)
        display_frame = utils.put_text(s, f"{i}/{len(sequence)}", (15, 15))
        cv2.imshow("Sequence", display_frame)
        k = cv2.waitKey(0)
        training_path = "training/"
        if k == ord("n"):
            id = time.time()
            print("Negative")
            cv2.imwrite(
                f"training/negative/neg_energy-{id}.jpg", params["energy_matrix"]
            )
            with open(f"training/negative/pos_mhi_sequence-{id}.npy", "wb") as f:
                np.save(f, sequence)

        if k == ord("p"):
            id = time.time()
            print("Positive")
            cv2.imwrite(
                f"training/positive/pos_energy-{id}.jpg", params["energy_matrix"]
            )
            with open(f"training/positive/neg_mhi_sequence-{id}.npy", "wb") as f:
                np.save(f, sequence)
    return True
