"""Inspect supplied geospatial sources without modifying them."""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
NS = {'k': 'http://www.opengis.net/kml/2.2'}

if __name__ == '__main__':
    boundary = gpd.read_file(ROOT / 'data/raw/comunas_bcn.zip')
    print('BOUNDARY', boundary.crs, boundary.columns.tolist())
    selected = boundary[boundary.astype(str).apply(lambda col: col.str.contains('San Jos', case=False)).any(axis=1)]
    print(selected.drop(columns='geometry').to_string(index=False))
    print('BOUNDS', selected.to_crs(4326).total_bounds)
    places = gpd.read_file(ROOT / 'data/raw/toponimos_bcn.zip')
    print('PLACES', places.crs, places.columns.tolist(), len(places))
    local = places[(places.cod_comuna == 13203) & (~places.fc.isin(['T', 'H']))].to_crs(4326)
    print(local.drop(columns='geometry').to_string(index=False))
    print('CANDIDATE COORDS', [(ascii(r.Nombre), r.objectid, round(r.geometry.x,6), round(r.geometry.y,6)) for _, r in local.iterrows()])
    with ZipFile(ROOT / 'data/raw/areas_protegidas_mma.zip') as archive:
        for member in archive.namelist():
            with ZipFile(BytesIO(archive.read(member))) as kmz:
                for name in kmz.namelist():
                    if name.lower().endswith('.kml'):
                        doc = ET.fromstring(kmz.read(name))
                        print('KML', member, len(doc.findall('.//k:Placemark', NS)))
                        for feature in doc.findall('.//k:Placemark', NS):
                            print(feature.findtext('k:name', default='', namespaces=NS))
