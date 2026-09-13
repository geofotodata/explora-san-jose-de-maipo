"""Data contract checks: run python -m unittest discover -s scripts -p 'test_*.py'."""
import json
import unittest
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point, Polygon
from build_map_data import parse_coordinates
from clean_vector import clean_vector

ROOT = Path(__file__).resolve().parents[1]


class MapDataTests(unittest.TestCase):
    def test_kml_axis_order_and_altitude(self) -> None:
        self.assertEqual(parse_coordinates('-70.35,-33.64,1200 -70.34,-33.65,0'), [(-70.35,-33.64),(-70.34,-33.65)])

    def test_hygiene_requires_crs(self) -> None:
        with self.assertRaises(ValueError):
            clean_vector(gpd.GeoDataFrame(geometry=[Point(-70,-33)]), 32719)

    def test_repair_and_exact_deduplication(self) -> None:
        bow = Polygon([(0,0),(2,2),(0,2),(2,0),(0,0)])
        data = gpd.GeoDataFrame({'name':['same','same','different']}, geometry=[bow,bow,Point(1,1)], crs=32719)
        result = clean_vector(data,32719)
        self.assertEqual(len(result),2)
        self.assertTrue(result.geometry.is_valid.all())

    def test_all_municipal_entries_present(self) -> None:
        catalog = json.loads((ROOT/'data/locality-catalog.json').read_text(encoding='utf-8'))
        expected = {'La Obra','Las Vertientes','El Canelo','El Manzano','Los Maitenes','El Guayacán','San José de Maipo','Lagunillas','El Toyo','El Melocotón','San Alfonso','El Ingenio','Bollenar','San Gabriel','El Romeral','Embalse El Yeso','Los Queltehues','Las Melosas','El Volcán','Baños Morales','El Morado','Lo Valdés','Baños Colina'}
        self.assertEqual({x.get('municipal_name',x['name']) for x in catalog if x['municipal']},expected)

    def test_spatial_invariants(self) -> None:
        boundary = gpd.read_file(ROOT/'data/map/boundary.geojson').to_crs(32719)
        points = gpd.read_file(ROOT/'data/map/localities.geojson').to_crs(32719)
        protected = gpd.read_file(ROOT/'data/map/protected.geojson').to_crs(32719)
        self.assertEqual(len(boundary),1); self.assertEqual(len(points),25)
        for frame in [boundary,points,protected]:
            self.assertTrue(frame.geometry.is_valid.all())
            self.assertFalse(frame.geometry.is_empty.any())
            self.assertEqual(frame.id.nunique(),len(frame))
        self.assertTrue(points.geometry.covered_by(boundary.geometry.iloc[0]).all())
        self.assertEqual(set(protected.group),{'snaspe','santuario'})
        self.assertGreater(len(protected[protected.group=='snaspe']),0)

    def test_three_coordinates_match_osm_snapshot(self) -> None:
        osm = json.loads((ROOT/'data/raw/localidades_osm.json').read_text(encoding='utf-8'))
        sources = {x['id']:x for x in osm['elements'] if x['type']=='node'}
        points = json.loads((ROOT/'data/map/localities.geojson').read_text(encoding='utf-8'))['features']
        for source_id in [214180495,214212998,418990982]:
            point = next(x for x in points if x['properties']['source_id']==source_id)
            self.assertAlmostEqual(point['geometry']['coordinates'][0],sources[source_id]['lon'],places=7)
            self.assertAlmostEqual(point['geometry']['coordinates'][1],sources[source_id]['lat'],places=7)


if __name__ == '__main__':
    unittest.main()
