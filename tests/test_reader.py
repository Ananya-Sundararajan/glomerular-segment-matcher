import numpy as np
import pytest
import tifffile as tiff
import imageio.v3 as iio

from glomerular_segment_matcher._reader import napari_get_reader, reader_function

@pytest.fixture
def temp_napari_dir(tmp_path):
    """Creates a temporary valid directory structure with dummy images."""
    img_dir = tmp_path / "images"
    mask_dir = tmp_path / "masks"
    recon_dir = tmp_path / "reconstructed"
    
    for d in [img_dir, mask_dir, recon_dir]:
        d.mkdir()

    data = np.zeros((10, 10), dtype=np.uint16)
    for i in range(3):
        tiff.imwrite(img_dir / f"img_{i}.tif", data)
        tiff.imwrite(mask_dir / f"mask_{i}.tif", data)
        tiff.imwrite(recon_dir / f"recon_{i}.tif", data)
        
    return tmp_path

def test_get_reader_valid_dir(temp_napari_dir):
    reader = napari_get_reader(temp_napari_dir)
    assert callable(reader)

def test_get_reader_invalid_path(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello")
    assert napari_get_reader(str(file_path)) is None

def test_reader_function_full_load(temp_napari_dir):
    layer_data = reader_function(str(temp_napari_dir))
    
    assert len(layer_data) == 3
    
    for data, kwargs, layer_type in layer_data:
        assert hasattr(data, "compute") 
        assert data.shape == (3, 10, 10)
        
        if kwargs["name"] == "images":
            assert layer_type == "image"
        else:
            assert layer_type == "labels"

def test_mismatched_counts(temp_napari_dir):
    tiff.imwrite(temp_napari_dir / "images" / "extra.tif", np.zeros((10, 10)))
    
    with pytest.raises(ValueError, match="images found, but 3 masks found"):
        reader_function(str(temp_napari_dir))