import os
import sys
import pytest
import numpy as np
from numpy.testing import assert_raises, assert_array_equal, assert_allclose
import brainload.brainwrite as bw
import brainload.freesurferdata as fsd
import brainload as bl
import nibabel as nib
import tempfile

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(THIS_DIR, os.pardir, 'test_data')

# Respect the environment variable BRAINLOAD_TEST_DATA_DIR if it is set. If not, fall back to default.
TEST_DATA_DIR = os.getenv('BRAINLOAD_TEST_DATA_DIR', TEST_DATA_DIR)

def test_get_volume_data_with_custom_marks():
    voxel_mark_list = [(np.array([[1, 1, 1], [2, 2, 2]], dtype=int), 40), (np.array([[0, 1, 2], [0, 2, 2]], dtype=int), 160)]
    vol_data = bw.get_volume_data_with_custom_marks(voxel_mark_list, background_voxel_value=0, shape=(3, 3, 3))
    assert vol_data.shape == (3, 3, 3)
    assert vol_data.dtype == np.uint8
    assert vol_data[0, 0, 0] == 0
    assert vol_data[0, 0, 1] == 0
    assert vol_data[0, 0, 2] == 0
    assert vol_data[0, 2, 0] == 0
    assert vol_data[0, 2, 1] == 0
    assert vol_data[0, 1, 0] == 0
    assert vol_data[0, 1, 1] == 0
    assert vol_data[1, 1, 1] == 40
    assert vol_data[2, 2, 2] == 40
    assert vol_data[0, 1, 2] == 160
    assert vol_data[0, 2, 2] == 160
    assert vol_data[1, 2, 2] == 0


def test_get_volume_data_with_custom_marks_no_shape_given_custom_background_value():
    voxel_mark_list = [(np.array([[1, 1, 1], [2, 2, 2]], dtype=int), 40), (np.array([[0, 1, 2], [0, 2, 2]], dtype=int), 160)]
    vol_data = bw.get_volume_data_with_custom_marks(voxel_mark_list, background_voxel_value=10, dtype=np.int16)
    assert vol_data.shape == (256, 256, 256)
    assert vol_data.dtype == np.int16
    assert vol_data[0, 0, 0] == 10
    assert vol_data[0, 0, 1] == 10
    assert vol_data[0, 0, 2] == 10
    assert vol_data[0, 2, 0] == 10
    assert vol_data[0, 2, 1] == 10
    assert vol_data[0, 1, 0] == 10
    assert vol_data[0, 1, 1] == 10
    assert vol_data[1, 1, 1] == 40
    assert vol_data[2, 2, 2] == 40
    assert vol_data[0, 1, 2] == 160
    assert vol_data[0, 2, 2] == 160
    assert vol_data[1, 2, 2] == 10


def test_get_surface_vertices_overlay_volume_data():
    num_verts = 10
    vertex_mark_list = [(np.array([0, 2, 4], dtype=int), [20, 20, 20]), (np.array([1, 3, 5, 7], dtype=int), [40, 40, 40])]
    vol_data = bw.get_surface_vertices_overlay_volume_data(num_verts, vertex_mark_list, background_rgb=[200, 200, 200])
    assert vol_data.shape == (10, 3, 1)
    assert_array_equal(vol_data[0,:,0], [20, 20, 20])
    assert_array_equal(vol_data[2,:,0], [20, 20, 20])
    assert_array_equal(vol_data[4,:,0], [20, 20, 20])
    assert_array_equal(vol_data[1,:,0], [40, 40, 40])
    assert_array_equal(vol_data[3,:,0], [40, 40, 40])
    assert_array_equal(vol_data[5,:,0], [40, 40, 40])
    assert_array_equal(vol_data[7,:,0], [40, 40, 40])
    assert_array_equal(vol_data[6,:,0], [200, 200, 200])
    assert_array_equal(vol_data[8,:,0], [200, 200, 200])
    assert_array_equal(vol_data[9,:,0], [200, 200, 200])


def test_get_surface_vertices_overlay_text_file_lines():
    num_verts = 10
    vertex_mark_list = [(np.array([0, 2, 4], dtype=int), [20, 20, 20]), (np.array([1, 3, 5, 7], dtype=int), [40, 40, 40])]
    overlay_lines = bw.get_surface_vertices_overlay_text_file_lines(num_verts, vertex_mark_list)
    assert len(overlay_lines) == 10
    assert overlay_lines[0] == "20, 20, 20"
    assert overlay_lines[2] == "20, 20, 20"
    assert overlay_lines[4] == "20, 20, 20"
    assert overlay_lines[1] == "40, 40, 40"
    assert overlay_lines[7] == "40, 40, 40"
    assert overlay_lines[6] == "200, 200, 200"


def test_get_surface_vertices_overlay_volume_data_1color():
    num_verts = 10
    vertex_mark_list = [(np.array([0, 2, 4], dtype=int), 20), (np.array([1, 3, 5, 7], dtype=int), 40)]
    vol_data = bw.get_surface_vertices_overlay_volume_data_1color(num_verts, vertex_mark_list, background_value=0)
    assert vol_data.shape == (10, 1, 1)
    assert vol_data[0,0,0] == 20
    assert vol_data[2,0,0] == 20
    assert vol_data[4,0,0] == 20
    assert vol_data[1,0,0] == 40
    assert vol_data[7,0,0] == 40
    assert vol_data[6,0,0] == 0


def test_write_voldata_to_nifti_file():
    # This test currently assumes that the working directory is writable (and writes a file to it).
    if sys.version_info.major < 3:
        pytest.skip("Skipping: python 2 has no support for tempfile.TemporaryDirectory")
    with tempfile.TemporaryDirectory() as tmpdirname:
        vol_data = np.zeros((10, 10, 10), dtype=int)
        vol_data[0,0,1] = 20
        vol_data[0,0,2] = 40
        vol_data[3,3,3] = 60
        nifti_file_name = os.path.join(tmpdirname, 'test.nii')
        bw.write_voldata_to_nifti_file(nifti_file_name, vol_data)
        assert os.path.isfile(nifti_file_name)
        img = nib.load(nifti_file_name)
        nifti_data = img.get_data()
        assert nifti_data.shape == (10, 10, 10)
        assert nifti_data[0,0,0] == 0
        assert nifti_data[0,0,1] == 20
        assert nifti_data[0,0,2] == 40
        assert nifti_data[3,3,3] == 60


def test_write_voldata_to_mgh_file():
    if sys.version_info.major < 3:
        pytest.skip("Skipping: python 2 has no support for tempfile.TemporaryDirectory")
    with tempfile.TemporaryDirectory() as tmpdirname:
        vol_data = np.zeros((10, 10, 10), dtype=int)
        vol_data[0,0,1] = 20
        vol_data[0,0,2] = 40
        vol_data[3,3,3] = 60
        mgh_file_name = os.path.join(tmpdirname, 'test.mgh')
        bw.write_voldata_to_mgh_file(mgh_file_name, vol_data)
        assert os.path.isfile(mgh_file_name)
        mgh_data, mgh_meta_data = fsd.read_mgh_file(mgh_file_name)
        assert mgh_data.shape == (10, 10, 10)
        assert mgh_data[0,0,0] == 0
        assert mgh_data[0,0,1] == 20
        assert mgh_data[0,0,2] == 40
        assert mgh_data[3,3,3] == 60
