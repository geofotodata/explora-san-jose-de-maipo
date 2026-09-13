"""Regression checks for generated pages and the locality/map contract."""
import json
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from build_site import ROOT, build, slug


class Document(HTMLParser):
    """Collect local references and semantic headings without a browser."""
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[str] = []
        self.h1 = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if 'id' in values:
            self.ids.append(values['id'])
        if tag == 'h1':
            self.h1 += 1
        for attr in ('href', 'src'):
            if values.get(attr):
                self.links.append(values[attr])


class SiteTests(unittest.TestCase):
    """Validate every generated page and stable territorial link."""
    @classmethod
    def setUpClass(cls) -> None:
        build()
        cls.pages = list(ROOT.glob('*.html')) + list((ROOT / 'localidades').glob('*.html'))

    def test_all_local_links_and_fragments(self) -> None:
        for path in self.pages:
            doc = Document()
            doc.feed(path.read_text(encoding='utf-8'))
            self.assertEqual(doc.h1, 1, path.name)
            self.assertEqual(len(doc.ids), len(set(doc.ids)), path.name)
            for link in doc.links:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.exists(), f'{path.name}: {link}')
                if url.fragment and target.suffix == '.html':
                    other = Document()
                    other.feed(target.read_text(encoding='utf-8'))
                    self.assertIn(unquote(url.fragment), other.ids, f'{path.name}: {link}')

    def test_catalog_has_one_detail_per_feature(self) -> None:
        data = json.loads((ROOT / 'data/map/localities.geojson').read_text(encoding='utf-8'))
        self.assertEqual(len(list((ROOT / 'localidades').glob('*.html'))), len(data['features']))
        for feature in data['features']:
            p = feature['properties']
            content = (ROOT / 'localidades' / f'{slug(p["name"])}.html').read_text(encoding='utf-8')
            self.assertIn(f'mapa.html?localidad={p["id"]}', content)
            self.assertIn('Sin información verificada', content)
            self.assertIn(p['source_url'], content)

    def test_slug_accents_and_punctuation(self) -> None:
        self.assertEqual(slug('San José de Maipo'), 'san-jose-de-maipo')
        self.assertEqual(slug('El Morado (acceso)'), 'el-morado-acceso')

    def test_build_is_repeatable(self) -> None:
        before = {p: p.read_bytes() for p in self.pages}
        build()
        self.assertEqual(before, {p: p.read_bytes() for p in self.pages})


if __name__ == '__main__':
    unittest.main()
