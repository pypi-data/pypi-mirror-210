from typing import Literal, TypeAlias, TypedDict

import numpy as np
import numpy.typing as npt
from typing_extensions import Self

from .coco import COCO
from .coco_types import _ImageEvaluationResult

_T_IOU: TypeAlias = Literal["segm", "bbox", "keypoints"]


class COCOeval:
    cocoGt: COCO
    cocoDt: COCO
    evalImgs: list[_ImageEvaluationResult]
    eval: _EvaluationResult
    params: Params
    stats: npt.NDArray[np.float64]
    ious: dict[tuple[int, int],  list[float]]

    def __init__(self: Self, cocoGt: COCO | None = None, cocoDt: COCO | None = None, iouType: _T_IOU = "segm") -> None:
        """Initialize CocoEval using coco APIs for gt and dt

        Args:
            cocoGt: coco object with ground truth annotations
            cocoDt: coco object with detection results
        """
        ...

    def evaluate(self: Self) -> None:
        """Run per image evaluation on given images and store results (a list of dict) in self.evalImgs"""
        ...

    def computeIoU(self: Self, imgId: int, catId: int) -> list[float]:
        ...

    def computeOks(self: Self, imgId: int, catId: int) -> npt.NDArray[np.float64]:
        ...

    def evaluateImg(self: Self, imgId: int, catId: int, aRng: list[int], maxDet: int) -> _ImageEvaluationResult:
        """Perform evaluation for single category and image.

        Returns:
            dict (single image results)
        """
        ...

    def accumulate(self: Self, p: Params | None = None) -> None:
        """Accumulate per image evaluation results and store the result in self.eval

        Args:
            p: input params for evaluation
        """
        ...

    def summarize(self: Self) -> None:
        """Compute and display summary metrics for evaluation results.

        Note this functin can *only* be applied on the default parameter setting
        """
        ...

    def __str__(self: Self) -> str:
        ...


class Params:
    """Params for coco evaluation api"""
    imgIds: list[int]
    catIds: list[int]
    iouThrs: npt.NDArray[np.float64]
    recThrs: npt.NDArray[np.float64]
    maxDets: list[int]
    areaRng: list[float]
    areaRngLbl: list[str]
    useCats: int
    kpt_oks_sigmas: npt.NDArray[np.float64]
    iouType: _T_IOU
    useSegm: int | None

    def __init__(self: Self, iouType: _T_IOU = "segm") -> None:
        ...

    def setDetParams(self: Self) -> None:
        ...

    def setKpParams(self: Self) -> None:
        ...


class _EvaluationResult(TypedDict):
    params: Params
    counts: list[int]
    date: str
    precision: npt.NDArray[np.float64]
    recall: npt.NDArray[np.float64]
    scores: npt.NDArray[np.float64]
