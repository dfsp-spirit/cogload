import os
import pytest
import numpy as np
import brainload as bl
import brainload.meshexport as me

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(THIS_DIR, os.pardir, 'test_data')

# Respect the environment variable BRAINLOAD_TEST_DATA_DIR if it is set. If not, fall back to default.
TEST_DATA_DIR = os.getenv('BRAINLOAD_TEST_DATA_DIR', TEST_DATA_DIR)


def test_ply_header_no_color():
    header = me._ply_header(100, 150)
    expected_header = """ply
format ascii 1.0
comment Generated by Brainload
element vertex 100
property float x
property float y
property float z
element face 150
property list uchar int vertex_indices
end_header
"""
    assert header == expected_header


def test_ply_header_color():
    header = me._ply_header(100, 150, use_vertex_colors=True)
    expected_header = """ply
format ascii 1.0
comment Generated by Brainload
element vertex 100
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
property uchar alpha
element face 150
property list uchar int vertex_indices
end_header
"""
    assert header == expected_header


def test_ply_verts_no_color():
    verts = np.array([[1.5, 1.5, 1.5], [2.5, 2.5, 2.5], [3.5, 3.5, 3.5]])
    vert_rep = me._ply_verts(verts)
    expected = "1.500000 1.500000 1.500000\n2.500000 2.500000 2.500000\n3.500000 3.500000 3.500000\n"
    assert vert_rep == expected


def test_ply_verts_empty():
    verts = np.array([])
    vert_rep = me._ply_verts(verts)
    expected = ""
    assert vert_rep == expected


def test_ply_verts_color():
    verts = np.array([[1.5, 1.5, 1.5], [2.5, 2.5, 2.5], [3.5, 3.5, 3.5]])
    colors = np.array([[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]])
    vert_rep = me._ply_verts(verts, vertex_colors=colors)
    expected = "1.500000 1.500000 1.500000 255 0 0 255\n2.500000 2.500000 2.500000 0 255 0 255\n3.500000 3.500000 3.500000 0 0 255 255\n"
    assert vert_rep == expected


def test_ply_faces():
    faces = np.array([[0, 1, 2], [2, 3, 4], [4, 5, 6]])
    face_rep = me._ply_faces(faces)
    expected = "3 0 1 2\n3 2 3 4\n3 4 5 6\n"
    assert face_rep == expected


def test_ply_faces_empty():
    faces = np.array([])
    face_rep = me._ply_faces(faces)
    expected = ""
    assert face_rep == expected


def test_mesh_to_ply_with_vcolors():
    verts = np.array([[1.5, 1.5, 1.5], [2.5, 2.5, 2.5], [3.5, 3.5, 3.5]])
    faces = np.array([[0, 1, 2], [2, 3, 4], [4, 5, 6]])
    colors = np.array([[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]])
    ply = me.mesh_to_ply(verts, faces, vertex_colors=colors)
    expected = """ply
format ascii 1.0
comment Generated by Brainload
element vertex 3
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
property uchar alpha
element face 3
property list uchar int vertex_indices
end_header
1.500000 1.500000 1.500000 255 0 0 255
2.500000 2.500000 2.500000 0 255 0 255
3.500000 3.500000 3.500000 0 0 255 255
3 0 1 2
3 2 3 4
3 4 5 6
"""
    assert ply == expected


def test_mesh_to_ply_no_vcolors():
    verts = np.array([[1.5, 1.5, 1.5], [2.5, 2.5, 2.5], [3.5, 3.5, 3.5]])
    faces = np.array([[0, 1, 2], [2, 3, 4], [4, 5, 6]])
    ply = me.mesh_to_ply(verts, faces)
    expected = """ply
format ascii 1.0
comment Generated by Brainload
element vertex 3
property float x
property float y
property float z
element face 3
property list uchar int vertex_indices
end_header
1.500000 1.500000 1.500000
2.500000 2.500000 2.500000
3.500000 3.500000 3.500000
3 0 1 2
3 2 3 4
3 4 5 6
"""
    assert ply == expected


def test_normalize_to_range_zero_one_nonconstant():
    values = np.array([1.5, 15.7, 37.5])
    values_norm = me._normalize_to_range_zero_one(values)
    assert np.min(values_norm) == pytest.approx(0., 0.0001)
    assert np.max(values_norm) == pytest.approx(1., 0.0001)


def test_normalize_to_range_zero_one_constant():
    values = np.array([1.5, 1.5, 1.5])
    values_norm = me._normalize_to_range_zero_one(values)
    assert np.min(values_norm) == pytest.approx(1., 0.0001)
    assert np.max(values_norm) == pytest.approx(1., 0.0001)


def test_scalars_to_colors_clist_even():
    scalars = np.arange(10.0)
    clist = np.array([[255, 0, 0, 255], [255, 0, 0, 235], [255, 0, 0, 215], [255, 0, 0, 195], [255, 0, 0, 175]])
    vertex_colors = me.scalars_to_colors_clist(scalars, clist)
    assert vertex_colors.shape[0] == scalars.shape[0]     # one color for each value
    assert vertex_colors.shape[1] == 4     # RGBA
    assert np.array_equal(vertex_colors[0][:], np.array([255, 0, 0, 255]))
    assert np.array_equal(vertex_colors[1][:], np.array([255, 0, 0, 255]))
    assert np.array_equal(vertex_colors[2][:], np.array([255, 0, 0, 235]))
    assert np.array_equal(vertex_colors[3][:], np.array([255, 0, 0, 235]))
    assert np.array_equal(vertex_colors[4][:], np.array([255, 0, 0, 215]))
    assert np.array_equal(vertex_colors[5][:], np.array([255, 0, 0, 215]))
    assert np.array_equal(vertex_colors[6][:], np.array([255, 0, 0, 195]))
    assert np.array_equal(vertex_colors[7][:], np.array([255, 0, 0, 195]))
    assert np.array_equal(vertex_colors[8][:], np.array([255, 0, 0, 175]))
    assert np.array_equal(vertex_colors[9][:], np.array([255, 0, 0, 175]))


def test_scalars_to_colors_clist_all_except_one_first_color():
    scalars = np.array([.0, .010, .002, 0.013, 10.])
    clist = np.array([[255, 0, 0, 255], [255, 0, 0, 235], [255, 0, 0, 215], [255, 0, 0, 195], [255, 0, 0, 175]])
    vertex_colors = me.scalars_to_colors_clist(scalars, clist)
    assert vertex_colors.shape[0] == scalars.shape[0]     # one color for each value
    assert vertex_colors.shape[1] == 4     # RGBA
    assert np.array_equal(vertex_colors[0][:], np.array([255, 0, 0, 255]))
    assert np.array_equal(vertex_colors[1][:], np.array([255, 0, 0, 255]))
    assert np.array_equal(vertex_colors[2][:], np.array([255, 0, 0, 255]))
    assert np.array_equal(vertex_colors[3][:], np.array([255, 0, 0, 255]))
    assert np.array_equal(vertex_colors[4][:], np.array([255, 0, 0, 175]))


def test_scalars_to_colors_matplotlib_linear():
    try:
        import matplotlib.cm as mpl_cm
        import matplotlib.colors as mpl_colors
    except:
        pytest.skip("Please install matplotlib to test this function.")
    scalars = np.array([.0, .010, .002, 0.013, 10.])
    colors = me.scalars_to_colors_matplotlib(scalars, 'Spectral')
    assert colors.shape[0] == scalars.shape[0]


def test_scalars_to_colors_matplotlib_custom_cmap():
    try:
        import matplotlib.cm as mpl_cm
        import matplotlib.colors as mpl_colors
    except:
        pytest.skip("Please install matplotlib to test this function.")
    scalars = np.array([.0, .010, .002, 0.013, 10.])
    cmap = mpl_cm.get_cmap(name='viridis')
    colors = me.scalars_to_colors_matplotlib(scalars, 'A greenish cmap', custom_cmap=cmap)
    assert colors.shape[0] == scalars.shape[0]


def test_scalars_to_colors_matplotlib_log():
    try:
        import matplotlib.cm as mpl_cm
        import matplotlib.colors as mpl_colors
    except:
        pytest.skip("Please install matplotlib to test this function.")
    scalars = np.array([.05, .010, .002, 0.013, 10.])    # values must be  > 0.0 for log, of course
    colors = me.scalars_to_colors_matplotlib(scalars, 'Spectral', data_normalization='log')
    assert colors.shape[0] == scalars.shape[0]


def test_scalars_to_colors_matplotlib_raises_on_invalid_data_normalization():
    try:
        import matplotlib.cm as mpl_cm
        import matplotlib.colors as mpl_colors
    except:
        pytest.skip("Please install matplotlib to test this function.")
    scalars = np.array([.0, .010, .002, 0.013, 10.])
    with pytest.raises(ValueError) as exc_info:
        colors = me.scalars_to_colors_matplotlib(scalars, 'Spectral', data_normalization='invalid_data_normalization')
    assert 'data_normalization must be one of' in str(exc_info.value)
    assert 'invalid_data_normalization' in str(exc_info.value)


def test_get_example_colorlist():
    colorlist = me._get_example_colorlist(300)
    assert colorlist.shape == (300, 4)


def test_color_index_from_clist_within_range_start():
    color_index = me._color_index_from_clist(0.01, 10)
    assert color_index == 0     # For a value range of 0.0 to 1.0, the value 0.01 should result in the first color being selected.


def test_color_index_from_clist_within_range_end():
    color_index = me._color_index_from_clist(0.99, 10)
    assert color_index == 9


def test_color_index_from_clist_below_range():
    color_index = me._color_index_from_clist(-0.1, 10)  # Out of range value smaller than lowest value in range should be mapped to first color
    assert color_index == 0


def test_color_index_from_clist_above_range():
    color_index = me._color_index_from_clist(1.5, 10)  # Out of range value larger than highest value in range should be mapped to last color
    assert color_index == 9


def test_obj_verts():
    verts = np.array([[1.5, 1.5, 1.5], [2.5, 2.5, 2.5], [3.5, 3.5, 3.5]])
    vert_rep = me._obj_verts(verts)
    expected = "v 1.500000 1.500000 1.500000\nv 2.500000 2.500000 2.500000\nv 3.500000 3.500000 3.500000\n"
    assert vert_rep == expected


def test_obj_verts_empty():
    verts = np.array([])
    vert_rep = me._obj_verts(verts)
    expected = ""
    assert vert_rep == expected


def test_obj_faces():
    faces = np.array([[0, 1, 2], [2, 3, 4], [4, 5, 6]])
    face_rep = me._obj_faces(faces)
    expected = "f 1 2 3\nf 3 4 5\nf 5 6 7\n"
    assert face_rep == expected


def test_obj_faces_empty():
    faces = np.array([])
    face_rep = me._obj_faces(faces)
    expected = ""
    assert face_rep == expected


def test_mesh_to_obj():
    verts = np.array([[1.5, 1.5, 1.5], [2.5, 2.5, 2.5], [3.5, 3.5, 3.5]])
    faces = np.array([[0, 1, 2], [2, 3, 4], [4, 5, 6]])
    obj = bl.mesh_to_obj(verts, faces)
    expected = """# Generated by Brainload
v 1.500000 1.500000 1.500000
v 2.500000 2.500000 2.500000
v 3.500000 3.500000 3.500000
f 1 2 3
f 3 4 5
f 5 6 7
"""
    assert obj == expected
