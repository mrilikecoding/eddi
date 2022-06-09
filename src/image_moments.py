import abc
import numpy as np
import cv2


class MotionImages(abc.ABC):
    @abc.abstractmethod
    # process takes the current input frame and returns a processed frame
    # process also takes a raw input frame for the cases where the subclass
    # is an intermediate step in a pipeline chain and some manipulation of
    # the original (beginning of the pipeline) needs to be done
    def process(current_input_frame, raw_input):
        pass

    def preprocess():
        pass

    def postprocess():
        pass


class ImageMoments(MotionImages):
    """
    Compute the Hu moments for a given image
    """

    def __init__(self, image):
        self.image = image

    def preprocess(self, image):
        """
        Given a color image
        Returns a grayscale average image
        """
        if image.ndim == 3:
            image = np.uint8(np.average(np.copy(image), axis=-1))
        image = np.float64(cv2.normalize(image, None, 0, 1, cv2.NORM_MINMAX))
        return image

    def postprocess(self, image):
        pass

    def process(self):
        image = self.preprocess(self.image)
        return self.compute_moments(image)

    def compute_moments(self, image):
        return self.hu_moments(image)

    def hu_moments(self, image):
        """
        Compute Hu moments
        """
        img = image
        m = self.moment
        m20 = m((2, 0), img)
        m02 = m((0, 2), img)
        m11 = m((1, 1), img)
        m30 = m((3, 0), img)
        m12 = m((1, 2), img)
        m21 = m((2, 1), img)
        m03 = m((0, 3), img)

        hu1 = m20 + m02
        hu2 = ((m20 - m02) ** 2) + (4 * (m11**2))
        hu3 = ((m30 - (3 * m12)) ** 2) + (((3 * m21) - m03) ** 2)
        hu4 = ((m30 + m12) ** 2) + ((m21 + m03) ** 2)
        hu5 = (
            (m30 - (3 * m12))
            * (m30 + m12)
            * (((m30 + m12) ** 2) - (3 * ((m21 + m03) ** 2)))
        ) + (
            (3 * m21 - m03)
            * (m21 + m03)
            * ((3 * ((m30 + m12) ** 2)) - ((m21 + m03) ** 2))
        )
        hu6 = ((m20 - m02) * (((m30 + m12) ** 2) - ((m21 + m03) ** 2))) + (
            (4 * m11 * (m30 + m12)) * (m21 + m03)
        )
        hu7 = -(
            (
                ((3 * m21) - m03)
                * (m30 + m12)
                * (((m30 + m12) ** 2) - (3 * ((m21 + m03) ** 2)))
            )
            - (
                (m30 - (3 * m12))
                * (m21 + m03)
                * ((3 * ((m30 + m12) ** 2)) - ((m21 + m03) ** 2))
            )
        )

        return [hu1, hu2, hu3, hu4, hu5, hu6, hu7]

    def moment(self, order, image):
        """
        order is a tuple of i, j powers (0,0)
        """
        normed_central_moment = self.normed_central_moment(order, image)
        return normed_central_moment

    def regular_moment(self, order, image):
        """
        Compute a regular image moment
        """
        rows, cols = image.shape
        i, j = order
        regular_moment = sum(
            [
                image[x, y] * (x**i) * (y**j)
                for x in range(rows)
                for y in range(cols)
            ]
        )
        return regular_moment

    def central_moment(self, order, image, x_mean, y_mean):
        """
        Compute a central/centroid moment by subtracting the means (order 0,0) of x and y
        """
        rows, cols = image.shape
        i, j = order
        central_moment = sum(
            [
                image[x, y] * ((x - x_mean) ** i) * ((y - y_mean) ** j)
                for x in range(rows)
                for y in range(cols)
            ]
        )
        return central_moment

    def normed_central_moment(self, order, image):
        """
        Compute a scale invariant central moment
        """
        rows, cols = image.shape
        i, j = order
        x_mean = self.regular_moment((1, 0), image) / self.regular_moment((0, 0), image)
        y_mean = self.regular_moment((0, 1), image) / self.regular_moment((0, 0), image)
        central_moment = self.central_moment(order, image, x_mean, y_mean)
        mean_central_moment = self.central_moment((0, 0), image, x_mean, y_mean)
        normed = central_moment / mean_central_moment ** (
            1 + ((order[0] + order[1]) / 2)
        )
        return normed
