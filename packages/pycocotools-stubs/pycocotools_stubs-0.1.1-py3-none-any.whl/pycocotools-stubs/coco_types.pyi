from typing import Generic, Literal, TypeAlias, TypedDict, TypeVar

import numpy as np
import numpy.typing as npt

class _Image(TypedDict):
    id: int
    width: int
    height: int
    file_name: str


_TPolygonSegmentation: TypeAlias = list[list[float]]


class _RLE(TypedDict):
    size: list[int]
    counts: list[int]


class _COCO_RLE(TypedDict):
    size: list[int]
    counts: str | bytes


_T_Seg = TypeVar("_T_Seg", _TPolygonSegmentation, _RLE, _COCO_RLE, _TPolygonSegmentation | _RLE | _COCO_RLE)


class _Annotation(TypedDict, Generic[_T_Seg]):
    id: int
    image_id: int
    category_id: int
    # Segmentation can be a polygon, RLE or COCO RLE.
    # Exemple of polygon: "segmentation": [[510.66,423.01,511.72,420.03,...,510.45,423.01]]
    # Exemple of RLE: "segmentation": {"size": [40, 40], "counts": [245, 5, 35, 5, 35, 5, 35, 5, 35, 5, 1190]}
    # Exemple of COCO RLE: "segmentation": {"size": [480, 640], "counts": "aUh2b0X...BgRU4"}
    segmentation: _T_Seg
    area: float
    # The COCO bounding box format is [top left x position, top left y position, width, height].
    # bbox exemple:  "bbox": [473.07,395.93,38.65,28.67]
    bbox: list[float]
    iscrowd: Literal[0] | Literal[1]


_AnnotationAny: TypeAlias = _Annotation[_TPolygonSegmentation | _RLE | _COCO_RLE]


class _Category(TypedDict):
    id: int
    name: str
    supercategory: str


class _ImageEvaluationResult(TypedDict):
    image_id: int
    category_id: int
    aRng: list[int]
    maxDet: int
    dtIds: list[int]
    gtIds: list[int]
    dtMatches: npt.NDArray[np.float64]
    gtMatches: npt.NDArray[np.float64]
    dtScores: list[float]
    gtIgnore: npt.NDArray[np.float64]
    dtIgnore: npt.NDArray[np.float64]


class _Dataset(TypedDict):
    images: list[_Image]
    annotations: list[_AnnotationAny]
    categories: list[_Category]
