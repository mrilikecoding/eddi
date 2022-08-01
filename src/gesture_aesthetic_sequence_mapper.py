import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import cv2
from scipy.stats import skew
from src import utils


class GestureAestheticSequenceMapper:
    def __init__(self, director=None):
        self.director = director
        self.output = []
        # TODO - again, grab this from a config
        self.smoothing_factor = 5
        self.spatial_categories = [
            "left",
            "right",
            "top",
            "bottom",
            "back",
            "front",
            "middle",
        ]
        self.show_plots = self.director.config["view_light_sequence_plots"]

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

    def compute_sequence_section_mean(self, sequence):
        return [np.mean(frame) for frame in sequence]

    def compute_sequence_section_std(self, sequence):
        return [np.std(frame) for frame in sequence]

    def compute_sequence_section_skew(self, sequence):
        return [skew(frame, axis=None) for frame in sequence]

    def map_sequences_to_rgb(self, sequences):
        """
        params:
        sequences = {
            'MEI' : nd.array shape = num_frames * h * w - eg (44, 278, 400)
            'MHI': nd.array shape = num_frames * h * w
            'energy_diff': nd.array shape = num_frames*h*w
            'meta': { 'at_frame': x, 'at_cycle': x, 'idxs' {0 : (s, e), 'energy': x, 'person_id': x, ...}}
        }

        returns a list of spatially defined sequence frames
        NOTE - normalize r g b to values between 0-1
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
        partitions = {
            "top": mhi_top,
            "bottom": mhi_bottom,
            "left": mhi_left,
            "right": mhi_right,
        }

        # TODO - so the section values are not smooth between regions. Intensity maybe, but not hue or saturation. Need to make smooth curves somehow...
        partition_sequences = {
            key: self.compute_sequence_section_values(partition, sequences["meta"])
            for key, partition in partitions.items()
        }

        if self.show_plots:
            self.plot_data(
                {
                    "sequences": sequences,
                    "partitions": partitions,
                    "partition_sequences": partition_sequences,
                }
            )

        # normalize 0-1
        normalized_partition_sequences = {
            position: {
                "r": (sequence["r"] - np.min(sequence["r"])) / 255.0,
                "g": (sequence["g"] - np.min(sequence["g"])) / 255.0,
                "b": (sequence["b"] - np.min(sequence["b"])) / 255.0,
            }
            for position, sequence in partition_sequences.items()
        }
        # restructure as list
        spatial_sequence_frames = []
        for i in range(frame_count):
            spatial_sequence_frames.append(
                {
                    position: (
                        sequence["r"][i],
                        sequence["g"][i],
                        sequence["b"][i],
                    )
                    for position, sequence in normalized_partition_sequences.items()
                }
            )

        return spatial_sequence_frames

    def compute_sequence_section_values(self, partition, meta):
        """
        Here's goes some funky stuff - relatively arbitrary aesthetic choices based on statistical properties
        of the mhi images partitioned by region
        """
        weight = meta.get("weight") or 1.0
        energy = meta.get("energy") or 3.0
        # intepolate values in lab space
        # L: 0 to 100, a: -127 to 128, b: -128 to 127.
        skew_values = self.compute_sequence_section_skew(partition)
        std_values = self.compute_sequence_section_std(partition)
        mean_values = self.compute_sequence_section_mean(partition)
        # To start, let's try
        # ch1 Lab L (lightness) or HSV Hue as a min max interpolation of the regional skew
        # ch2 Lab A(red->green pole) or HSV Saturation as a min max interpolation of the regional mean
        # ch3 Lab B(yellow->blue pole) or HSV Value as a min max interpolation of the regional std
        # or we can try HSV - OPENCV HSV is [0-180, 0-255, 0-255]
        # print("Energy", meta.get("energy"))
        # print("Weight", meta.get("weight"))
        min_energy = self.director.config["gesture_heuristics"]["min_energy_threshold"]
        max_energy = self.director.config["gesture_heuristics"]["max_energy_threshold"]
        hue = int(
            self.normalize_point(
                energy, min_energy, max_energy, 0, 180, return_boundary=True
            )
        )
        saturation = int(
            self.normalize_point(weight, 0, 1, 0, 255, return_boundary=True)
        )
        value_scalar = 1.0
        saturation_value_scalar = 2.0
        saturation = saturation * saturation_value_scalar
        ch1 = np.array(
            [
                # self.normalize_point(
                #     value, np.min(mean_values), np.max(mean_values), 0, 180
                # )
                int(hue)
                for value in mean_values
            ]
        ).astype(np.uint8)
        ch2 = np.array(
            [
                # self.normalize_point(
                #     value, np.min(mean_values), np.max(mean_values), 0, 255
                # )
                saturation
                for value in mean_values
            ]
        ).astype(np.uint8)
        ch3 = self.smooth(
            np.array(
                [
                    self.normalize_point(
                        value * value_scalar,
                        np.min(mean_values),
                        np.max(mean_values),
                        0,
                        255,
                        return_boundary=True,
                    )
                    for value in mean_values
                ]
            ).astype(np.uint8),
            self.smoothing_factor,
        )
        # then convert to rgb
        values = np.array(
            [
                cv2.cvtColor(
                    np.array([[[ch1[i], ch2[i], ch3[i]]]]).astype(np.uint8),
                    cv2.COLOR_HSV2RGB,
                ).flatten()
                for i in range(len(ch1))
            ]
        )

        return {
            "r": values[:, 0],
            "g": values[:, 1],
            "b": values[:, 2],
        }

    def smooth(self, y, box_pts):
        # https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
        box = np.ones(box_pts) / box_pts
        y_smooth = np.convolve(y, box, mode="same")
        return y_smooth.astype(np.uint8)

    def plot_data(self, data):
        sequences = data["sequences"]
        partitions = data["partitions"]
        partition_sequences = data["partition_sequences"]
        sns.set_theme(style="darkgrid")
        # plt.title("Values")

        plt.title("Sequence Regions RGB")
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
                "top_r": partition_sequences["top"]["r"],
                "top_g": partition_sequences["top"]["g"],
                "top_b": partition_sequences["top"]["b"],
                "bottom_r": partition_sequences["bottom"]["r"],
                "bottom_g": partition_sequences["bottom"]["g"],
                "bottom_b": partition_sequences["bottom"]["b"],
                "left_r": partition_sequences["left"]["r"],
                "left_g": partition_sequences["left"]["g"],
                "left_b": partition_sequences["left"]["b"],
                "right_r": partition_sequences["right"]["r"],
                "right_b": partition_sequences["right"]["b"],
                "right_g": partition_sequences["right"]["g"],
                # "top_std": partition_std_sequences["top"],
                # "bottom_std": partition_std_sequences["bottom"],
                "right_mean": partition_mean_sequences["right"],
                "left_mean": partition_mean_sequences["left"],
                # "right_std": partition_std_sequences["right"],
                # "left_std": partition_std_sequences["left"],
                "top_mean": partition_mean_sequences["top"],
                "bottom_mean": partition_mean_sequences["bottom"],
            }
        )

        sns.lineplot(data=sequence_data["top_r"], color="red", linestyle="--")
        sns.lineplot(data=sequence_data["top_g"], color="green", linestyle="--")
        sns.lineplot(data=sequence_data["top_b"], color="blue", linestyle="--")
        sns.lineplot(data=sequence_data["bottom_r"], color="red", linestyle=":")
        sns.lineplot(data=sequence_data["bottom_g"], color="green", linestyle=":")
        sns.lineplot(data=sequence_data["bottom_b"], color="blue", linestyle=":")
        sns.lineplot(data=sequence_data["left_r"], color="red", linestyle="-")
        sns.lineplot(data=sequence_data["left_g"], color="green", linestyle="-")
        sns.lineplot(data=sequence_data["left_b"], color="blue", linestyle="-")
        sns.lineplot(data=sequence_data["right_r"], color="red", linestyle="-.")
        sns.lineplot(data=sequence_data["right_g"], color="green", linestyle="-.")
        sns.lineplot(data=sequence_data["right_b"], color="blue", linestyle="-.")
        # sns.lineplot(data=sequence_data["right_mean"], color="purple", linestyle=":")
        # sns.lineplot(data=sequence_data["left_mean"], color="orange", linestyle=":")
        # sns.lineplot(data=sequence_data["top_mean"], color="yellow", linestyle=":")
        # sns.lineplot(data=sequence_data["bottom_mean"], color="pink", linestyle=":")
        plt.legend(
            labels=[
                "T r",
                "T g",
                "T b",
                "B r",
                "B g",
                "B b",
                "L r",
                "L g",
                "L b",
                "R r",
                "R g",
                "R b",
                # "right mean",
                # "left mean",
                # "top mean",
                # "bottom mean",
            ],
            title="Channel Values",
        )
        plt.show()
        return sequence_data
