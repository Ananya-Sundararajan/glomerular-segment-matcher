
import os
import numpy as np
import pytest
import tifffile
from pathlib import Path
from glomerular_segment_matcher._writer import write_single_image

@pytest.fixture
def dummy_layer_data():
    """Simulates the [(data, meta, type)] format napari sends to writers."""
    data = np.zeros((3, 10, 10), dtype=np.uint16)
    data[0, 0, 0] = 1
    meta = {"name": "test_layer"}
    layer_type = "labels"
    return [(data, meta, layer_type)]

def test_write_single_image_directory_creation(tmp_path, dummy_layer_data, qtbot):
    """Test that the writer creates the directory and the correct number of files."""
    save_path = tmp_path / "my_experiment"
    
    returned_paths = write_single_image(str(save_path), dummy_layer_data)
    
    assert str(save_path) in returned_paths[0]
    last_file = save_path / "2_mask.tif"
    
    qtbot.waitUntil(lambda: last_file.exists(), timeout=5000)
    
    files = list(save_path.glob("*.tif"))
    assert len(files) == 3
    
    written_data = tifffile.imread(str(save_path / "0_mask.tif"))
    assert written_data[0, 0] == 1
    assert written_data.shape == (10, 10)

def test_write_single_image_cleans_extension(tmp_path, dummy_layer_data, qtbot):
    """Test that .tiff or .zip extensions are stripped to create a directory."""

    save_path_with_ext = tmp_path / "my_results.tiff"
    expected_dir = tmp_path / "my_results"
    
    write_single_image(str(save_path_with_ext), dummy_layer_data)
 
    qtbot.waitUntil(lambda: (expected_dir / "0_mask.tif").exists(), timeout=5000)
    
    assert expected_dir.is_dir()
    assert not save_path_with_ext.is_file() 

def test_write_single_image_handles_raw_array(tmp_path, qtbot):
    """Test that the writer handles a raw numpy array instead of a napari list."""
    save_path = tmp_path / "raw_data_test"
    raw_data = np.zeros((2, 5, 5), dtype=np.uint8)
    
    write_single_image(str(save_path), raw_data)
    
    sentinel = save_path / "1_mask.tif"
    qtbot.waitUntil(lambda: sentinel.exists(), timeout=5000)
    
    assert len(list(save_path.glob("*.tif"))) == 2

def test_write_single_image_zip_stripping(tmp_path, dummy_layer_data, qtbot):
    """Test the specific logic for stripping .zip from the path."""
    save_path = tmp_path / "archive.zip"
    expected_dir = tmp_path / "archive"
    
    write_single_image(str(save_path), dummy_layer_data)
    
    qtbot.waitUntil(lambda: (expected_dir / "0_mask.tif").exists(), timeout=5000)
    assert expected_dir.is_dir()