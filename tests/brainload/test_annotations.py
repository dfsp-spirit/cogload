import os
import pytest
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
import brainload.nitools as nit
import brainload.annotations as an

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(THIS_DIR, os.pardir, 'test_data')

# Respect the environment variable BRAINLOAD_TEST_DATA_DIR if it is set. If not, fall back to default.
TEST_DATA_DIR = os.getenv('BRAINLOAD_TEST_DATA_DIR', TEST_DATA_DIR)

FSAVERAGE_NUM_VERTS_PER_HEMISPHERE = 163842         # number of vertices of the 'fsaverage' subject from FreeSurfer 6.0
FSAVERAGE_NUM_FACES_PER_HEMISPHERE = 327680

SUBJECT1_SURF_LH_WHITE_NUM_VERTICES = 149244        # this number is quite arbitrary: the number of vertices is specific for this subject and surface.
SUBJECT1_SURF_LH_WHITE_NUM_FACES = 298484           # this number is quite arbitrary: the number of faces is specific for this subject and surface.

SUBJECT1_SURF_RH_WHITE_NUM_VERTICES = 153333        # this number is quite arbitrary: the number of vertices is specific for this subject and surface.
SUBJECT1_SURF_RH_WHITE_NUM_FACES = 306662           # this number is quite arbitrary: the number of faces is specific for this subject and surface.

SUBJECT1_SURF_LH_WHITE_APARC_ANNOT_NUM_LABELS = 36
SUBJECT1_SURF_RH_WHITE_APARC_ANNOT_NUM_LABELS = 36


def test_read_annotation_md_lh():
    annotation_file = os.path.join(TEST_DATA_DIR, 'subject1', 'label', 'lh.aparc.annot')
    labels, ctab, names, meta_data = an.read_annotation_md(annotation_file, 'lh', meta_data=None)
    assert len(meta_data) == 1
    assert meta_data['lh.annotation_file'] == annotation_file
    assert labels.shape == (SUBJECT1_SURF_LH_WHITE_NUM_VERTICES, )
    assert ctab.shape == (SUBJECT1_SURF_LH_WHITE_APARC_ANNOT_NUM_LABELS, 5)
    assert len(names) == SUBJECT1_SURF_LH_WHITE_APARC_ANNOT_NUM_LABELS
    assert names[0] == "unknown"    # The first label is known to be 'unknown'. This also tests whether the object really is a string, i.e., whether the bytes have been coverted to string properly for Python 3. This is the real goal.


def test_read_annotation_md_rh():
    annotation_file = os.path.join(TEST_DATA_DIR, 'subject1', 'label', 'rh.aparc.annot')
    labels, ctab, names, meta_data = an.read_annotation_md(annotation_file, 'rh', meta_data=None)
    assert len(meta_data) == 1
    assert meta_data['rh.annotation_file'] == annotation_file
    assert labels.shape == (SUBJECT1_SURF_RH_WHITE_NUM_VERTICES, )
    assert ctab.shape == (SUBJECT1_SURF_RH_WHITE_APARC_ANNOT_NUM_LABELS, 5)
    assert len(names) == SUBJECT1_SURF_RH_WHITE_APARC_ANNOT_NUM_LABELS
    assert names[0] == "unknown"    # The first label is known to be 'unknown'. This also tests whether the object really is a string, i.e., whether the bytes have been coverted to string properly for Python 3. This is the real goal.


def test_read_annotation_md_raises_on_invalid_hemisphere_label():
    annotation_file = os.path.join(TEST_DATA_DIR, 'subject1', 'label', 'rh.aparc.annot')
    with pytest.raises(ValueError) as exc_info:
        labels, ctab, names, meta_data = an.read_annotation_md(annotation_file, 'invalid_hemisphere_label', meta_data=None)
    assert 'hemisphere_label must be one of' in str(exc_info.value)
    assert 'invalid_hemisphere_label' in str(exc_info.value)
