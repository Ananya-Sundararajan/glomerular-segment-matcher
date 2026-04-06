from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = tuple[DataType, dict, str]

import os
from napari.qt.threading import thread_worker
import tifffile as tiff
import numpy as np

def write_single_image(path: str, data: Any, meta: dict = None):
    base_path, ext = os.path.splitext(str(path)) # because it must be a directory
    if base_path.endswith(".zip"):
        base_path = base_path[:-4]
    try:
        actual_pixels = data[0][0] if isinstance(data, list) else data
    except (IndexError, TypeError):
        actual_pixels = data

    layer_dir_pth = base_path
    os.makedirs(base_path, exist_ok=True)

    @thread_worker
    def write_tiffs():
        out_files = []
        for i in range(actual_pixels.shape[0]):
            tiff_nme = f"{i}_mask.tif"
            tiff_pth = os.path.join(layer_dir_pth, tiff_nme)
            
            img_slice = np.asarray(actual_pixels[i])
            
            tiff.imwrite(tiff_pth, img_slice, compression='zlib')
            out_files.append(tiff_pth)
            
        return out_files

    worker = write_tiffs()
    worker.returned.connect(lambda res: print(f"Successfully saved {len(res)} images to {layer_dir_pth}"))
    worker.start()

    return [layer_dir_pth]
