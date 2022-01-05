import abc
import enum

import numpy as np
import skimage.feature as feature
from skimage.measure import ransac
from skimage.transform import SimilarityTransform
import typing as t_

Point2d = t_.Tuple[float, float]


class FeatureMatcher(abc.ABC):
    """
    Abstract class for an object that can take two images as input and identify matching points on them.
    """
    @abc.abstractmethod
    def match(self, im1: np.ndarray, im2: np.ndarray) -> t_.Tuple[t_.Sequence[Point2d], t_.Sequence[Point2d]]:
        """

        Args:
            im1: A 2d image
            im2: Another 2d image

        Returns: Two sets of 2d points of the same length. each point between the two sets should correspond to the same feature in the two input
            images
        """
        pass


class ORBFeatureMatcher(FeatureMatcher):
    """
    A feature matcher that uses scikit-image's ORB algorithm
    """
    def __init__(self):
        self._orb1 = feature.ORB()
        self._orb2 = feature.ORB()

    def match(self, im1: np.ndarray, im2: np.ndarray) -> t_.Tuple[t_.Sequence[Point2d], t_.Sequence[Point2d]]:
        self._orb1.detect_and_extract(im1)
        self._orb2.detect_and_extract(im2)
        matches = feature.match_descriptors(self._orb1.descriptors, self._orb2.descriptors)
        src = self._orb1.keypoints[matches[:, 0]]
        dst = self._orb2.keypoints[matches[:, 1]]

        src, dst = ransacPointSelection(src, dst)

        # Swap coords to account for the fact that they are originally (y,x) rather than (x,y)
        src = [(i[1], i[0]) for i in src]
        dst = [(i[1], i[0]) for i in dst]

        return src, dst


class SIFTFeatureMatcher(FeatureMatcher):
    """
    A feature matcher that uses scikit-image's SIFT algorithm
    """
    def __init__(self):
        self._s1 = feature.SIFT()
        self._s2 = feature.SIFT()

    def match(self, im1: np.ndarray, im2: np.ndarray) -> t_.Tuple[t_.Sequence[Point2d], t_.Sequence[Point2d]]:
        self._s1.detect_and_extract(im1)
        self._s2.detect_and_extract(im2)
        matches = feature.match_descriptors(self._s1.descriptors, self._s2.descriptors)
        src = self._s1.keypoints[matches[:, 0]]
        dst = self._s2.keypoints[matches[:, 1]]

        src, dst = ransacPointSelection(src, dst)

        # Swap coords to account for the fact that they are originally (y,x) rather than (x,y)
        src = [(i[1], i[0]) for i in src]
        dst = [(i[1], i[0]) for i in dst]

        return src, dst


def ransacPointSelection(src: t_.Sequence[Point2d], dst: t_.Sequence[Point2d]) -> t_.Tuple[t_.Sequence[Point2d], t_.Sequence[Point2d]]:
    """
    Find which point pairs are outliers from the rest of the pairs using the RANSAC algorithm.

    Args:
        src: A sequence of 2d coordinates
        dst: A matching set of 2d coordinate to compare with `src`

    Returns:
        two sets of coordinates matching src and dst but with the outliers removed.
    """
    model_robust, inliers = ransac((src, dst), SimilarityTransform, min_samples=3,
                                   residual_threshold=2, max_trials=100)
    src = [i for i, inlier in zip(src, inliers) if inlier]
    dst = [i for i, inlier in zip(dst, inliers) if inlier]
    return src, dst


class MatcherFactory:
    """this object is responsible for producing instances of feature matchers"""
    class _Matchers(enum.Enum):
        ORB = enum.auto()
        SIFT = enum.auto()

    @staticmethod
    def getMatcherNames() -> t_.Tuple[str]:
        """
        Returns:
            The names of the feature matchers that are available.
        """
        return tuple(m.name for m in MatcherFactory._Matchers)

    @staticmethod
    def getMatcher(name: str) -> FeatureMatcher:
        """

        Args:
            name: The name of the feature matcher type to fetch

        Returns:
            A new instance of a feature matcher
        Raises:
            A valueerror if a featurematcher is not found for the input name.
        """
        if name == MatcherFactory._Matchers.ORB.name:
            return ORBFeatureMatcher()
        elif name == MatcherFactory._Matchers.SIFT.name:
            return SIFTFeatureMatcher()
        else:
            raise ValueError(f"No matching Matcher implementation was found for name: {name}")
