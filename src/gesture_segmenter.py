import math
import cv2
import numpy as np
import scipy.signal


class GestureSegmenter:
    def __init__(self, mei_mhi_volume_diffs, display=True):
        self.display = display
        self.volumes = mei_mhi_volume_diffs
        self.similarity_matrices = {}
        for key, volume in self.volumes.items():
            self.similarity_matrices[key] = self.compute_similarity_matrix(volume)

        if display:
            self.display_similarity_matrices()

    def compute_similarity_matrix(self, volume):
        similarity_matrix = np.zeros((self.tau, self.tau))
        if self.tau == len(volume):
            for i in range(self.tau):
                for j in range(self.tau):
                    similarity_matrix[i, j] = math.dist(volume[i], volume[j])
        return similarity_matrix

    def display_similarity_matrices(self):
        for volume in self.similarity_matrices.values():
            volume = np.copy(volume)
            cv2.normalize(volume, volume, 0, 255, cv2.NORM_MINMAX)
        diff_similarity_matrices = np.concatenate(
            self.similarity_matrices.values(), axis=1
        )
        # for cv2 imshow, waitkey is set in caller, so don't put here, otherwise
        # this will be blocking
        cv2.imshow("MEI/MHI Diff Similarity Matrices", diff_similarity_matrices)

    def synthesize_sequence(volume, start, end):
        """Pull out the given loop from the input video volume.

        Parameters
        ----------
        video_volume : np.ndarray
            A (time, height, width, 3) array, as created by your videoVolume
            function.

        start : int
            The index of the starting frame.

        end : int
            The index of the ending frame.

        Returns
        -------
        list
            A list of arrays of size (height, width, 3) and dtype np.uint8,
            similar to the original input to the videoVolume function.
        """
        frames = volume[start : end + 1, ...].astype("uint8")
        return frames

    def binomial_filter_5(self):
        """
        Return a binomial filter of length 5.
        -------
        numpy.ndarray(dtype: np.float)
            A 5x1 numpy array representing a binomial filter.
        """
        return np.array([1 / 16.0, 1 / 4.0, 3 / 8.0, 1 / 4.0, 1 / 16.0], dtype=float)

    def transitionDifference(self, similarity):
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
        diff_matrix = scipy.signal.convolve2d(
            similarity.astype(np.float64), binomial, mode="valid"
        )
        return diff_matrix


# def runTexture(img_list, alpha):
#     """This function administrates the extraction of a video texture from the
#     given frames, and generates the three viewable difference matrices.
#     """
#     video_volume = textures.videoVolume(img_list)
#     try:
#         ssd_diff = np.load("ssd_diff.npy")
#     except:
#         ssd_diff = textures.computeSimilarityMetric(video_volume)
#         np.save("ssd_diff.npy", ssd_diff)

#     transition_diff = textures.transitionDifference(ssd_diff)
#     alphas = np.r_[0.003:0.02:1001j]
#     candidate_idxs = []
#     candidate_alphas = []
#     idxs = (0, 0)
#     if alpha == 0:
#         for a in alphas:
#             print("Testing alpha: {}".format(a))
#             biggestLoop = textures.findBiggestLoop(transition_diff, a)
#             if biggestLoop not in candidate_idxs:
#                 candidate_idxs.append(biggestLoop)
#                 candidate_alphas.append(a)
#         print("Candidate Alphas: {}".format(candidate_alphas))
#         print("Candidate Indexes: {}".format(candidate_idxs))
#     else:
#         biggestLoop = textures.findBiggestLoop(transition_diff, alpha)

#     idxs = biggestLoop
#     print("Loop bounds: {}".format(idxs))

#     diff3 = np.zeros(transition_diff.shape, float)

#     for i in range(transition_diff.shape[0]):
#         for j in range(transition_diff.shape[1]):
#             diff3[i, j] = alpha * (j - i) - transition_diff[j, i]
#     diff3 = cv2.circle(vizDifference(diff3), (idxs[1], idxs[0]), 3, (0), 1)

#     return (
#         vizDifference(ssd_diff),
#         vizDifference(transition_diff),
#         vizDifference(diff3),
#         textures.synthesizeLoop(video_volume, idxs[0], idxs[1]),
#     )
