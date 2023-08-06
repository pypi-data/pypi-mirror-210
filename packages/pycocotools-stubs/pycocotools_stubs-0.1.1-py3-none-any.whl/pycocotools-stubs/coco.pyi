from collections.abc import Collection, Sequence
from pathlib import Path
from typing import Literal, overload

import numpy as np
import numpy.typing as npt
from typing_extensions import Self

from .coco_types import _Annotation, _AnnotationAny, _Category, _COCO_RLE, _Dataset, _Image, _RLE, _TPolygonSegmentation

class COCO:
    dataset: _Dataset
    anns: dict[int, _AnnotationAny]
    cats: dict[int, _Category]
    imgs: dict[int, _Image]
    imgToAnns: dict[int, list[_AnnotationAny]]
    catToImgs: dict[int, list[int]]

    def __init__(self: Self, annotation_file: str | Path | None = None) -> None:
        """Constructor of Microsoft COCO helper class for reading and visualizing annotations.

        Args:
            annotation_file: Location of annotation file
        """
        ...

    def createIndex(self: Self) -> None:
        ...

    def info(self: Self) -> None:
        """Print information about the annotation file."""
        ...

    def getAnnIds(self: Self, imgIds: Collection[int] | int = [], catIds: Collection[int] | int = [], areaRng: Sequence[float] = [], iscrowd: bool | None = None) -> list[int]:
        """Get ann ids that satisfy given filter conditions. default skips that filter.

        Args:
            imgIds: Get anns for given imgs.
            catIds: Get anns for given cats.
            areaRng: Get anns for given area range (e.g. [0 inf]).
            iscrowd: Get anns for given crowd label (False or True).

        Returns:
            Integer array of ann ids.
        """
        ...

    def getCatIds(self: Self, catNms: Collection[str] | str = [], supNms: Collection[str] | str = [], catIds: Sequence[int] | int = []) -> list[int]:
        """Get cat ids that satisfy given filter conditions. default skips that filter.

        Args:
            catNms: get cats for given cat names
            supNms get cats for given supercategory names
            catIds: get cats for given cat ids

        Returns:
            ids: integer array of cat ids
        """
        ...

    def getImgIds(self: Self, imgIds: Collection[int] | int = [], catIds: list[int] | int = []) -> list[int]:
        """Get img ids that satisfy given filter conditions.

        Args:
            imgIds: get imgs for given ids
            catIds : get imgs with all given cats

        Returns:
            ids: integer array of img ids
        """
        ...

    def loadAnns(self: Self, ids: Collection[int] | int = []) -> list[_AnnotationAny]:
        """Load anns with the specified ids.

        Args:
            ids: Integer ids specifying anns.

        Returns:
            anns: loaded ann objects
        """
        ...

    def loadCats(self: Self, ids: Collection[int] | int = []) -> list[_Category]:
        """Load cats with the specified ids.

        Args:
            ids: integer ids specifying cats.

        Returns:
            cats: loaded cat objects.
        """
        ...

    def loadImgs(self: Self, ids: Collection[int] | int = []) -> list[_Image]:
        """Load anns with the specified ids.

        Args:
            ids: integer ids specifying img

        Returns:
            imgs: loaded img objects
        """
        ...

    def showAnns(self: Self, anns: Sequence[_AnnotationAny], draw_bbox: bool = False) -> None:
        """Display the specified annotations.

        Args:
            anns: Annotations to display.
            draw_bbox: Wether to draw the bounding boxes or not.
        """
        ...

    def loadRes(self: Self, resFile: str) -> Self:
        """Load result file and return a result api object.

        Args:
            resFile: file name of result file

        Returns:
            res: result api object
        """
        ...

    def download(self: Self, tarDir: str | None = None, imgIds: Collection[int] = []) -> Literal[-1] | None:
        """Download COCO images from mscoco.org server.

        Args:
            tarDir: COCO results directory name
            imgIds: images to be downloaded
        """
        ...

    def loadNumpyAnnotations(self: Self, data: npt.NDArray[np.float64]) -> list[_AnnotationAny]:
        """Convert result data from a numpy array [Nx7] where each row contains {imageID,x1,y1,w,h,score,class}

        Args:
             data (numpy.ndarray)

        Returns:
            annotations (python nested list)
        """
        ...

    @overload
    def annToRLE(self: Self, ann: _Annotation[_RLE]) -> _RLE:
        """Convert polygons, RLE or COCO RLE annotation to COCO RLE."""
        ...

    @overload
    def annToRLE(self: Self, ann: _Annotation[_COCO_RLE]) -> _COCO_RLE:
        """Convert polygons, RLE or COCO RLE annotation to COCO RLE."""
        ...

    @overload
    def annToRLE(self: Self, ann: _Annotation[_TPolygonSegmentation]) -> _COCO_RLE:
        """Convert polygons, RLE or COCO RLE annotation to COCO RLE."""
        ...

    def annToMask(self: Self, ann: _AnnotationAny) -> npt.NDArray[np.uint8]:
        """Convert polygons, RLE or COCO RLE annotation to binary mask.

        Args:
            ann: The annotation whose mask shoulb be returned.

        Returns:
            binary mask (numpy 2D array)
        """
        ...
