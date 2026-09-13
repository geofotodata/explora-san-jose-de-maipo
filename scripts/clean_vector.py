"""Vector hygiene adapted from geo-data-engineering's standard clean_vector.

Keeps explicit accounting, repairs invalid geometries and never guesses CRS.
"""
import geopandas as gpd
from pyproj import CRS
from shapely import make_valid


def clean_vector(gdf: gpd.GeoDataFrame, target_epsg: int) -> gpd.GeoDataFrame:
    """Return valid, nonempty, exactly deduplicated data in a projected CRS."""
    if gdf.crs is None or not CRS.from_epsg(target_epsg).is_projected:
        raise ValueError('Known input CRS and projected target CRS are required')
    initial = len(gdf)
    result = gdf.loc[~(gdf.geometry.isna() | gdf.geometry.is_empty)].copy()
    missing = initial - len(result)
    invalid = ~result.geometry.is_valid
    repaired = int(invalid.sum())
    result.loc[invalid, result.geometry.name] = result.loc[invalid].geometry.apply(make_valid)
    if not result.geometry.is_valid.all():
        raise ValueError('Invalid geometry after repair')
    result = result.loc[~result.geometry.is_empty].copy()
    before = len(result)
    result = result.drop_duplicates().to_crs(target_epsg)
    print(f'Hygiene {initial} -> {len(result)}; missing={missing}; repaired={repaired}; duplicates={before-len(result)}; EPSG:{target_epsg}')
    return result
