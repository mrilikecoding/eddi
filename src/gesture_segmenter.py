import math
import cv2
import numpy as np
import scipy.signal


class GestureSegmenter:
    """
    Analyzing energy diff similarity matrices inspired by
    Schödl, Arno, et al. "Video textures." Proceedings of the 27th annual conference on Computer graphics and interactive techniques. 2000.
    """

    def __init__(self, mei_mhi_volume_diffs, tau, display=True):
        self.display = display
        self.tau = tau  # max number of frame windows / volume size
        self.volumes = mei_mhi_volume_diffs
        # Alpha is a scaling factor.
        # The size of the loop and the transition cost are likely to be in very different units,
        # so introduce a new parameter to make them comparable.
        # Manipulate alpha to control the tradeoff between loop size and smoothness.
        # Large alphas prefer large loop sizes,
        # and small alphas bias towards short loop sizes.
        # You are looking for an alpha between these extremes (the goldilocks alpha).
        # Your findBiggestLoop function has to compute this score for every choice of start and end,
        # and return the start and end frame numbers that corresponds to the largest score.
        self.display = display
        self.alpha = 0.50
        self.similarity_matrices = {}
        self.transition_matrices = {}
        self.current_best_sequence = {}
        for key, volume in self.volumes.items():
            if len(volume):
                self.similarity_matrices[key] = self.compute_similarity_matrix(volume)
                self.transition_matrices[key] = self.compute_transition_matrix(
                    self.similarity_matrices[key]
                )
                self.current_best_sequence[key] = self.find_motion(
                    transition_matrix=self.transition_matrices[key], alpha=self.alpha
                )

        if self.display and self.similarity_matrices and self.transition_matrices:
            self.display_similarity_matrices()
            self.display_transition_matrices()
            # TODO when finding the best similarity loop, pick the top 3 rather than the best
            # do a heirarchy and see what the results are

    def find_motion(self, transition_matrix, alpha=0.5):
        candidate_idxs = []
        candidate_alphas = []
        idxs = (0, 0)
        # alphas = np.r_[0.003:0.02:1001j]
        # if alpha == 0:
        #     for a in alphas:
        #         print("Testing alpha: {}".format(a))
        #         biggestLoop = self.find_motion_sequences(transition_matrix, a)
        #     if biggestLoop not in candidate_idxs:
        #         candidate_idxs.append(biggestLoop)
        #         candidate_alphas.append(a)
        #         print("Candidate Alphas: {}".format(candidate_alphas))
        #         print("Candidate Indexes: {}".format(candidate_idxs))
        # else:
        #     biggestLoop = self.find_motion_sequences(transition_matrix, alpha)
        best_sequence_idxs = self.find_motion_sequences(transition_matrix, alpha)
        return best_sequence_idxs

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
        cv2.imshow("MEI/MHI Diff Similarity Matrices", diff_similarity_matrices)

    def display_transition_matrices(self):
        for volume in self.transition_matrices.values():
            volume = np.copy(volume)
            cv2.normalize(volume, volume, 0, 255, cv2.NORM_MINMAX)
        transition_matrices = np.concatenate(
            list(self.transition_matrices.values()), axis=1
        )
        # for cv2 imshow, waitkey is set in caller, so don't put here, otherwise
        # this will be blocking
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontscale = 0.55
        transition_matrices = np.copy(transition_matrices).astype(np.float32)
        transition_matrices = cv2.resize(transition_matrices, (300, 300))
        color = (255, 0, 255)
        transition_matrices = cv2.cvtColor(transition_matrices, cv2.COLOR_BGR2RGB)
        transition_matrices = cv2.putText(
            transition_matrices,
            str(self.current_best_sequence),
            (10, 100),
            fontFace=font,
            fontScale=fontscale,
            color=color,
            thickness=2,
        )
        cv2.imshow("Transition Matrices", transition_matrices)

    def synthesize_sequence(volume, start, end):
        """
        Pull out sequence by index from the given volume.
        """

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

        Hint: There is an efficient way to do this with 2d convolution. Think about
            the coordinates you are using as you consider the preceding and
            following frame pairings.

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

    def find_motion_sequences(self, transition_matrix, alpha):
        """Find the longest and smoothest loop for the given difference matrix.

        For each cell (i, j) in the transition differences matrix, find the
        maximum score according to the following metric:

            score = alpha * (j - i) - transition_diff[j, i]

        The pair i, j correspond to the start and end indices of the longest loop.

        **************************************************************************
        NOTE: Remember to correct the indices from the transition difference
            matrix to account for the rows and columns dropped from the edges
                        when the binomial filter was applied.
        **************************************************************************

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
