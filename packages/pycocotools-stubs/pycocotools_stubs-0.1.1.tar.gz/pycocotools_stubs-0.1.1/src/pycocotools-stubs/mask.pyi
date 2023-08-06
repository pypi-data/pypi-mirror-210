from typing import Any, overload

import numpy as np
import numpy.typing as npt

from .coco_types import _COCO_RLE

def iou(dt: npt.NDArray[np.uint32] | list[float] | list[_COCO_RLE],
        gt: npt.NDArray[np.uint32] | list[float] | list[_COCO_RLE],
        pyiscrowd: list[int] | npt.NDArray[np.uint8],
        ) -> list[Any] | npt.NDArray[np.float64]:
    """Compute intersection over union between masks."""
    ...

def merge(rleObjs: list[_COCO_RLE], intersect: int = ...) -> _COCO_RLE:
    """Compute union or intersection of COCO RLE masks."""
    ...

@overload
def frPyObjects(pyobj: npt.NDArray[np.uint32] | list[list[int]] | list[_COCO_RLE], h: int, w: int) -> list[_COCO_RLE]:
    """Convert polygon, bbox, or RLE to COCO RLE mask."""
    ...

@overload
def frPyObjects(pyobj: list[int] | _COCO_RLE, h: int, w: int) -> _COCO_RLE:
    ...

def encode(bimask: npt.NDArray[np.uint8]) -> _COCO_RLE:
    ...

def decode(rleObjs: _COCO_RLE) -> npt.NDArray[np.uint8]:
    ...

def area(rleObjs: _COCO_RLE) -> np.uint32:
    ...

def toBbox(rleObjs: _COCO_RLE) -> npt.NDArray[np.float64]:
    ...
