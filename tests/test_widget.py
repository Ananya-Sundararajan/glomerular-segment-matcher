'''
@pytest.fixture
def segment_matcher_viewer(make_napari_viewer):
    """Fixture to set up a viewer with required layers."""
    viewer = make_napari_viewer()

    img_stack = np.random.random((5, 10, 10)).astype(np.float32)
    mask_stack = np.zeros((5, 10, 10), dtype=np.uint16)

    viewer.add_image(img_stack, name='images')
    viewer.add_labels(mask_stack, name='masks')

    return viewer
'''
