import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from global_config import global_config


class GestureAestheticSequenceMapper:
    def __init__(self):
        self.output = []
        # TODO - again, grab this from a config
        self.spatial_categories = [
            "left",
            "right",
            "top",
            "bottom",
            "back",
            "front",
            "middle",
        ]
        self.show_plots = global_config["view_light_sequence_plots"]

    def normalize_point(
        self, x, min_x, max_x, min_target, max_target, return_boundary=False
    ):
        # sometimes we may want to ignore extremes rather than
        # altering their value
        if return_boundary:
            if x > max_x:
                x = max_x
            if x < min_x:
                x = min_x

        x_norm = ((x - min_x) / (max_x - min_x)) * (max_target - min_target)
        return x_norm

    def slice_top(self, sequence, h):
        """Return top half of sequence"""
        return np.copy(sequence[:, : int(h / 2), :])

    def slice_bottom(self, sequence, h):
        """Return bottom half of sequence"""
        return np.copy(sequence[:, int(h / 2) :, :])

    def slice_left(self, sequence, w):
        """Return left half of sequence"""
        return np.copy(sequence[:, :, : int(w / 2)])

    def slice_right(self, sequence, w):
        """Return right half of sequence"""
        return np.copy(sequence[:, :, int(w / 2) :])

    def slice_middle(self, sequence, h):
        """Return middle vertical of sequence"""
        return np.copy(sequence[:, int(h / 3) : int(2 * (h / 3)), :])

    def compute_sequence_section_mean(self, sequence):
        return [np.mean(frame) for frame in sequence]

    def compute_sequence_section_std(self, sequence):
        return [np.std(frame) for frame in sequence]

    def map_sequences_to_rgb(self, sequences):
        """
        params:
        sequences = {
            'MEI' : nd.array shape = num_frames * h * w - eg (44, 278, 400)
            'MHI': nd.array shape = num_frames * h * w
            'energy_diff': nd.array shape = num_frames*h*w
            'meta': { 'at_frame': x, 'at_cycle': x, 'idxs' {0 : (s, e), 'energy': x, 'person_id': x}}
        }

        returns a list of spatially defined sequence frames
        [{
            "back": (r, g, b),
            "front": (r, g, b),
            "bottom": (r, g, b),
            "top": (r, g, b),
            "right": (r, g, b),
            "left": (r, g, b),
            "middle": (r, g, b),
        }, ...]
        """
        """
        slice each dimension top/bottom, left/right, middle
        - don't think I can do front back without some depth info in the volumes
        compute a dyanmic curve for each dimension
        maybe use the energymei
        """
        if not sequences:
            return

        frame_count, h, w = sequences["MEI"].shape
        energy_diff = sequences["energy_diff"]
        mhi = sequences["MHI"]
        mhi_top = self.slice_top(mhi, h)
        mhi_bottom = self.slice_bottom(mhi, h)
        mhi_left = self.slice_left(mhi, w)
        mhi_right = self.slice_right(mhi, w)
        mhi_middle = self.slice_middle(mhi, h)
        partitions = {
            "top": mhi_top,
            "bottom": mhi_bottom,
            "left": mhi_left,
            "right": mhi_right,
            "middle": mhi_middle,
        }

        if self.show_plots:
            self.plot_sequences(partitions)

        partition_mean_sequences = {
            key: self.compute_sequence_section_mean(partition)
            for key, partition in partitions.items()
        }

        spatial_sequence_frames = []
        for i in range(frame_count):
            spatial_sequence_frames.append(
                {
                    position: (
                        self.normalize_point(sequence[i], 0, 255, 0, 1),
                        0.01,
                        # self.normalize_point(sequence[i], 0, 255, 0, 1),
                        0.01
                        # self.normalize_point(sequence[i], 0, 255, 0, 1),
                    )
                    for position, sequence in partition_mean_sequences.items()
                }
            )
        # TODO what to do with RGB

        return spatial_sequence_frames

    def plot_sequences(self, partitions):
        sns.set_theme(style="darkgrid")
        plt.title("Sequence")
        partition_std_sequences = {
            key: self.compute_sequence_section_std(partition)
            for key, partition in partitions.items()
        }
        partition_mean_sequences = {
            key: self.compute_sequence_section_mean(partition)
            for key, partition in partitions.items()
        }

        sequence_data = pd.DataFrame(
            {
                # "middle_std": partition_std_sequences["middle"],
                # "top_std": partition_std_sequences["top"],
                # "bottom_std": partition_std_sequences["bottom"],
                "right_std": partition_std_sequences["right"],
                "left_std": partition_std_sequences["left"],
                # "middle_mean": partition_mean_sequences["middle"],
                # "top_mean": partition_mean_sequences["top"],
                # "bottom_mean": partition_mean_sequences["bottom"],
                "right_mean": partition_mean_sequences["right"],
                "left_mean": partition_mean_sequences["left"],
            }
        )

        sns.lineplot(data=sequence_data)
        plt.show()
