"""Build the visitor map from the supplied BCN/MMA archives and OSM snapshot.

Run with Python 3.12 and scripts/requirements-geo.txt. Input files stay in
data/raw; browser-ready, source-traceable EPSG:4326 outputs go to data/map.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import geopandas as gpd
from shapely.geometry import MultiPolygon, Point, Polygon
from clean_vector import clean_vector

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
OUT = ROOT / 'data/map'
UTM = 32719
NS = {'k': 'http://www.opengis.net/kml/2.2'}
SOURCES = {
    'comunas_bcn.zip': 'https://www.bcn.cl/obtienearchivo?id=repositorio/10221/10396/5/comunas_final.zip',
    'toponimos_bcn.zip': 'https://www.bcn.cl/obtienearchivo?id=repositorio/10221/10400/2/Toponimos.zip',
    'areas_protegidas_mma.zip': 'https://biodiversidadrm.mma.gob.cl/wp-content/uploads/2024/01/AP_descarga_kmz.zip',
    'localidades_osm.json': 'https://maps.mail.ru/osm/tools/overpass/api/interpreter',
}


def parse_coordinates(text: str) -> list[tuple[float, float]]:
    """Read KML lon,lat[,height] tuples without confusing axis order."""
    return [tuple(float(value) for value in token.split(',')[:2]) for token in text.split()]


def read_protected() -> gpd.GeoDataFrame:
    """Read polygons and holes from every KML inside the supplied nested KMZs."""
    records = []
    with ZipFile(RAW / 'areas_protegidas_mma.zip') as outer:
        for member in sorted(outer.namelist()):
            if not member.endswith('.kmz'):
                continue
            with ZipFile(BytesIO(outer.read(member))) as kmz:
                for name in kmz.namelist():
                    if not name.endswith('.kml'):
                        continue
                    root = ET.fromstring(kmz.read(name))
                    for index, placemark in enumerate(root.findall('.//k:Placemark', NS)):
                        polygons = []
                        for item in placemark.findall('.//k:Polygon', NS):
                            shell = item.findtext('k:outerBoundaryIs/k:LinearRing/k:coordinates', namespaces=NS)
                            if not shell:
                                raise ValueError('KML polygon without an outer ring')
                            holes = [parse_coordinates(ring.text or '') for ring in item.findall('k:innerBoundaryIs/k:LinearRing/k:coordinates', NS)]
                            polygons.append(Polygon(parse_coordinates(shell), holes))
                        if not polygons:
                            raise ValueError('Unexpected nonpolygon protected area')
                        description = placemark.findtext('k:description', default='', namespaces=NS)
                        cells = [html.unescape(re.sub('<[^>]*>', '', value)).strip() for value in re.findall(r'<td[^>]*>([^<]*)</td>', description)]
                        attrs = {cells[i]: cells[i+1] for i in range(len(cells)-1)}
                        group = 'snaspe' if member.startswith('SNASPE') else 'santuario'
                        records.append({
                            'id': f'{group}-{index}',
                            'name': placemark.findtext('k:name', default='', namespaces=NS).strip(),
                            'category': attrs.get('CATEGORIAS', group),
                            'group': group, 'edition': '2023' if group == 'snaspe' else '2024',
                            'decree': attrs.get('DECRETO', 'No informado'),
                            'source': 'MMA · Biodiversidad RM', 'source_file': member,
                            'source_url': SOURCES['areas_protegidas_mma.zip'],
                            'geometry': MultiPolygon(polygons),
                        })
    return gpd.GeoDataFrame(records, crs=4326)


def write_geojson(frame: gpd.GeoDataFrame, filename: str) -> dict:
    """Validate and serialize web coordinates, preserving Unicode and source IDs."""
    frame = frame.sort_values('id').to_crs(4326)
    assert frame.geometry.is_valid.all() and not frame.geometry.is_empty.any()
    data = json.loads(frame.to_json(drop_id=True))
    data['bbox'] = [round(float(x), 7) for x in frame.total_bounds]
    data['metadata'] = {'coordinate_reference_system': 'EPSG:4326', 'coordinate_order': 'longitude, latitude'}
    (OUT / filename).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    return {'features': len(frame), 'bbox': data['bbox'], 'bytes': (OUT / filename).stat().st_size}


def main() -> None:
    """Build boundary, locality and protection layers with an accounting manifest."""
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'sources': {}, 'layers': {}, 'rejected': []}
    for file, url in SOURCES.items():
        path = RAW / file
        report['sources'][file] = {'url': url, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'retrieved_at': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}

    communes = gpd.read_file(RAW / 'comunas_bcn.zip')
    selected = communes.loc[communes.cod_comuna == 13203].copy()
    assert len(selected) == 1, 'Expected exactly one commune for CUT 13203'
    boundary = clean_vector(selected, UTM)
    territory = boundary.geometry.iloc[0]
    report['boundary_input'] = {'national_features': len(communes), 'selected': 1, 'source_crs': str(communes.crs)}
    boundary = gpd.GeoDataFrame([{'id': '13203', 'name': 'San José de Maipo', 'source': 'Biblioteca del Congreso Nacional',
        'source_url': 'https://www.bcn.cl/siit/mapas_vectoriales', 'edition': 'BCN: ediciones referenciales 2014–2018',
        'geometry': territory.simplify(12, preserve_topology=True)}], crs=UTM)
    report['layers']['boundary'] = write_geojson(boundary, 'boundary.geojson')

    toponyms = gpd.read_file(RAW / 'toponimos_bcn.zip')
    osm = json.loads((RAW / 'localidades_osm.json').read_text(encoding='utf-8'))
    if osm.get('remark'):
        raise ValueError(f'OSM response incomplete: {osm["remark"]}')
    osm_index = {(item['type'], item['id']): item for item in osm['elements']}
    catalog = json.loads((ROOT / 'data/locality-catalog.json').read_text(encoding='utf-8'))
    records = []
    for number, entry in enumerate(catalog, 1):
        if entry['provider'] == 'osm':
            item = osm_index[(entry.get('osm_type', 'node'), entry['source_id'])]
            coord = item if 'lon' in item else item['center']
            point = Point(coord['lon'], coord['lat'])
            original_name = item['tags'].get('name', '')
            source = 'OpenStreetMap'
            source_url = f'https://www.openstreetmap.org/{item["type"]}/{item["id"]}'
        else:
            rows = toponyms.loc[toponyms.objectid == entry['source_id']].to_crs(4326)
            assert len(rows) == 1
            point = rows.geometry.iloc[0]
            original_name = rows.Nombre.iloc[0]
            source = 'BCN · Nombres geográficos'
            source_url = 'https://www.bcn.cl/siit/mapas_vectoriales'
        records.append({**entry, 'id': str(number), 'number': number, 'source': source, 'source_url': source_url,
            'original_name': original_name, 'geometry': point, 'access_status': 'Por confirmar'})
    points = clean_vector(gpd.GeoDataFrame(records, crs=4326), UTM)
    points['distance_outside_m'] = points.geometry.distance(territory).round(1)
    outside = points.loc[points.distance_outside_m > 0]
    report['outside_boundary'] = outside[['name','distance_outside_m']].to_dict('records')
    # Large mismatches require source review, not silent clipping or relocation.
    if (points.distance_outside_m > 500).any():
        raise ValueError('Locality more than 500 m outside BCN boundary: review source match')
    report['layers']['localities'] = write_geojson(points, 'localities.geojson')
    report['locality_catalog_count'] = len(catalog)

    protected = read_protected()
    report['protected_input'] = {'features': len(protected), 'categories': protected.category.value_counts().to_dict(), 'crs': str(protected.crs)}
    protected = clean_vector(protected, UTM)
    protected['overlap_ha'] = protected.geometry.intersection(territory).area / 10000
    keep = protected.overlap_ha > 1
    report['protected_excluded'] = protected.loc[~keep, ['name', 'overlap_ha']].to_dict('records')
    protected = protected.loc[keep].copy()
    # Retain whole protected-area geometries, including portions crossing commune boundaries.
    protected.geometry = protected.geometry.simplify(12, preserve_topology=True)
    protected['overlap_ha'] = protected.overlap_ha.round(1)
    report['layers']['protected'] = write_geojson(protected, 'protected.geojson')
    report['protected_selected'] = protected[['name','category','overlap_ha']].to_dict('records')
    report['display_crs'] = 'EPSG:3857'; report['analysis_crs'] = 'EPSG:32719'
    report['simplification_m'] = 12
    report['osm_snapshot'] = osm.get('osm3s', {}).get('timestamp_osm_base')
    (OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
