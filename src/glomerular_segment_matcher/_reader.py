import os
from pathlib import Path

import dask
import dask.array as da
import imageio.v3 as iio
import numpy as np
import tifffile as tiff
from napari.utils import progress
from natsort import natsorted

IMAGE_FOLDER_NAME = 'images'
MASK_FOLDER_NAME = 'masks'
RECON_FOLDER_NAME = 'reconstructed'


def napari_get_reader(path):
    """
    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a directory of two folders of images and masks in format
        .tif or .png, return a function that accepts the same path or list of paths,
        and returns a list of layer data tuples.
    """

    path = Path(path)
    if path.is_dir():
        return reader_function
    return None


def reader_function(path):
    """
    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type)
            data: numpy array,
            metadata: dict,
            layer_type: string
    """

    path = Path(path)
    all_layer_data = []

    # method to read in images (works for both tifs and pngs)
    @dask.delayed
    def read_image(im_path):
        img = iio.imread(im_path)
        img = np.asarray(img)
        img = np.squeeze(img)

        if im_path.endswith('.tif') and img.ndim == 3:
            # channel-last
            if img.shape[-1] in (3, 4):
                img = img[..., 0]
            # channel-first
            elif img.shape[0] in (3, 4):
                img = img[0, ...]

        if img.ndim < 2:
            raise ValueError(
                f'{path.name} has unsupported shape {img.shape}. '
                'Only 2D or RGB images are supported.'
            )
        return img

    # Find all directories starting with 'reconstructed'
    recon_dirs = [
        d
        for d in path.iterdir()
        if d.is_dir() and d.name.startswith(RECON_FOLDER_NAME)
    ]  # Added logic to find all matching folders
    num_recon = 0  # Initialize counter to support validation later

    for (
        recon_dir
    ) in recon_dirs:  # added loop to process multiple recon folders
        recon_file_names = natsorted(os.listdir(recon_dir))
        recon_file_paths = [
            os.path.join(recon_dir, f)
            for f in recon_file_names
            if f.endswith(('.tif', '.png'))
        ]

        num_recon = len(recon_file_paths)
        # read in one reconstructed mask to get data type and shape
        recon_shape = None
        recon_dtype = None
        if recon_file_names[0].endswith('.tif'):
            recon = tiff.imread(recon_file_paths[0])
            recon_shape = recon.shape
            recon_dtype = recon.dtype
        else:
            recon = iio.imread(recon_file_paths[0])
            recon_shape = recon.shape
            recon_dtype = recon.dtype

        recon_stack = [
            da.zeros(shape=recon_shape, dtype=recon_dtype)
            for _ in range(num_recon)
        ]

        # create the stack with appropriate data for reconstructed masks
        for i in progress(range(len(recon_file_paths))):
            recon_path = recon_file_paths[i]
            recon = da.from_delayed(
                read_image(recon_path), shape=recon_shape, dtype=recon_dtype
            )
            recon_stack[i] = recon

        recon_layer_data = da.stack(recon_stack)
        recon_layer_type = 'labels'
        recon_layer_name = (
            recon_dir.name
        )  # changed to use the specific folder name for the layer
        recon_add_kwargs = {'name': recon_layer_name}

        all_layer_data.append(
            (recon_layer_data, recon_add_kwargs, recon_layer_type)
        )

    # load in image file paths
    image_dir = path / IMAGE_FOLDER_NAME
    if not image_dir.exists():
        raise ValueError('Valid image directory is not given.')
    image_file_names = natsorted(os.listdir(image_dir))
    image_file_paths = [
        os.path.join(image_dir, f)
        for f in image_file_names
        if f.endswith(('.tif', '.png'))
    ]

    num_images = len(image_file_paths)

    # read in one image to get data type and shape
    im_shape = None
    im_dtype = None
    if image_file_names[0].endswith('.tif'):
        im = tiff.imread(image_file_paths[0])
        im_shape = im.shape
        im_dtype = im.dtype
    else:
        im = iio.imread(image_file_paths[0])
        im_shape = im.shape
        im_dtype = im.dtype

    # read in mask file paths
    mask_dir = path / MASK_FOLDER_NAME
    if not mask_dir.exists():
        raise ValueError('No mask directory has been given.')
    mask_file_names = natsorted(os.listdir(mask_dir))
    mask_file_paths = [
        os.path.join(mask_dir, f)
        for f in mask_file_names
        if f.endswith(('.tif', '.png'))
    ]

    num_masks = len(mask_file_paths)
    # read in one mask to get data type and shape
    mask_shape = None
    mask_dtype = None
    if mask_file_names[0].endswith('.tif'):
        mask = tiff.imread(mask_file_paths[0])
        mask_shape = mask.shape
        mask_dtype = mask.dtype
    else:
        mask = iio.imread(mask_file_paths[0])
        mask_shape = mask.shape
        mask_dtype = mask.dtype

    # if mask shape and image shape are not the same then raise error
    if num_masks != num_images:
        raise ValueError(
            f'{num_images} images found, but {num_masks} masks found.'
        )
    if (
        len(recon_dirs) > 0 and num_recon != num_images
    ):  # Updated to check if recons exist before comparing
        raise ValueError(
            f'{num_recon} reconstructed masks found, but {num_images} masks found.'
        )

    # initialize stack size
    image_stack = [
        da.zeros(shape=im_shape, dtype=im_dtype) for _ in range(num_images)
    ]
    mask_stack = [
        da.zeros(shape=mask_shape, dtype=mask_dtype) for _ in range(num_masks)
    ]

    # create the stack with appropriate data for images
    for i in progress(range(len(image_file_paths))):
        image_path = image_file_paths[i]
        image = da.from_delayed(
            read_image(image_path), shape=im_shape, dtype=im_dtype
        )
        image_stack[i] = image

    image_layer_data = da.stack(image_stack)
    image_layer_type = 'image'
    image_layer_name = IMAGE_FOLDER_NAME
    image_add_kwargs = {'name': image_layer_name}

    # create the stack with appropriate data for masks
    for i in progress(range(len(mask_file_paths))):
        mask_path = mask_file_paths[i]
        mask = da.from_delayed(
            read_image(mask_path), shape=mask_shape, dtype=mask_dtype
        )
        mask_stack[i] = mask

    mask_layer_data = da.stack(mask_stack)
    mask_layer_type = 'labels'
    mask_layer_name = MASK_FOLDER_NAME
    mask_add_kwargs = {'name': mask_layer_name}

    # append both image layer and mask layer
    all_layer_data.append(
        (image_layer_data, image_add_kwargs, image_layer_type)
    )
    all_layer_data.append((mask_layer_data, mask_add_kwargs, mask_layer_type))

    return all_layer_data
