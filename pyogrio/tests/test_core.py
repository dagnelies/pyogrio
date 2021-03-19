from numpy import array_equal
import pytest

from pyogrio import (
    list_layers,
    read_info,
    set_gdal_config_options,
    get_gdal_config_option,
)


def test_list_layers(naturalearth_lowres, naturalearth_lowres_vsi, test_fgdb_vsi):
    assert array_equal(
        list_layers(naturalearth_lowres), [["naturalearth_lowres", "Polygon"]]
    )

    assert array_equal(
        list_layers(naturalearth_lowres_vsi), [["naturalearth_lowres", "Polygon"]]
    )

    # Measured 3D is downgraded to 2.5D during read
    # Make sure this warning is raised
    with pytest.warns(
        UserWarning, match=r"Measured \(M\) geometry types are not supported"
    ):
        fgdb_layers = list_layers(test_fgdb_vsi)
        assert len(fgdb_layers) == 7

        # Make sure that nonspatial layer has None for geometry
        assert array_equal(fgdb_layers[0], ["basetable_2", None])

        # Confirm that measured 3D is downgraded to 2.5D during read
        assert array_equal(fgdb_layers[3], ["test_lines", "2.5D MultiLineString"])
        assert array_equal(fgdb_layers[6], ["test_areas", "2.5D MultiPolygon"])


def test_read_info(naturalearth_lowres):
    meta = read_info(naturalearth_lowres)

    assert meta["crs"] == "EPSG:4326"
    assert meta["geometry_type"] == "Polygon"
    assert meta["encoding"] == "UTF-8"
    assert meta["fields"].shape == (5,)
    assert meta["features"] == 177


@pytest.mark.parametrize(
    "name,value,expected",
    [
        ("CPL_DEBUG", "ON", True),
        ("CPL_DEBUG", True, True),
        ("CPL_DEBUG", "OFF", False),
        ("CPL_DEBUG", False, False),
    ],
)
def test_set_config_options(name, value, expected):
    set_gdal_config_options({name: value})
    actual = get_gdal_config_option(name)
    assert actual == expected


def test_reset_config_options():
    set_gdal_config_options({"foo": "bar"})
    assert get_gdal_config_option("foo") == b"bar"

    set_gdal_config_options({"foo": None})
    assert get_gdal_config_option("foo") is None
