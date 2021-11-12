import abc

from skimage.feature import ORB, match_descriptors
from skimage.measure import ransac
from skimage.transform import SimilarityTransform

from ijtransformer.imageCollection import ImageCollection
import typing as t_

Point2d = t_.Tuple[float, float]

class FeatureMatcher(abc.ABC):
    @abc.abstractmethod
    def match(self, im1: ImageCollection, im2: ImageCollection) -> t_.Tuple[t_.Sequence[Point2d], t_.Sequence[Point2d]]:
        pass


class ORBFeatureMatcher(FeatureMatcher):
    def __init__(self):
        self._orb1 = ORB()
        self._orb2 = ORB()

    def match(self, im1: ImageCollection, im2: ImageCollection) -> t_.Tuple[t_.Sequence[Point2d], t_.Sequence[Point2d]]:
        self._orb1.detect_and_extract(im1.getDisplayImage())
        self._orb2.detect_and_extract(im2.getDisplayImage())
        matches = match_descriptors(self._orb1.descriptors, self._orb2.descriptors)
        src = self._orb1.keypoints[matches[:, 0]]
        dst = self._orb2.keypoints[matches[:, 1]]

        src, dst = ransacPointSelection(src, dst)

        # Swap coords to account for the fact that they are originally (y,x) rather than (x,y)
        src = [(i[1], i[0]) for i in src]
        dst = [(i[1], i[0]) for i in dst]

        return src, dst

def ransacPointSelection(src: t_.Sequence[Point2d], dst: t_.Sequence[Point2d]) -> t_.Tuple[t_.Sequence[Point2d], t_.Sequence[Point2d]]:
    model_robust, inliers = ransac((src, dst), SimilarityTransform, min_samples=3,
                                   residual_threshold=2, max_trials=100)
    src = [i for i, inlier in zip(src, inliers) if inlier]
    dst = [i for i, inlier in zip(dst, inliers) if inlier]
    return src, dst