"""Guard the positioning contract between custom pins and MapLibre."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MarkerStyleTests(unittest.TestCase):
    """Prevent normal-flow offsets from being added to map projections."""

    def test_pins_use_map_origin_without_overriding_projection(self) -> None:
        css = (ROOT / 'territory-map.css').read_text(encoding='utf-8')
        rule = re.search(r'\.locality-pin\.maplibregl-marker\s*\{([^}]+)\}', css)
        self.assertIsNotNone(rule, 'A scoped rule must preserve MapLibre positioning')
        declarations = dict(re.findall(r'([\w-]+)\s*:\s*([^;]+)', rule.group(1)))
        for key, expected in {'position': 'absolute', 'top': '0', 'left': '0', 'margin': '0'}.items():
            self.assertEqual(declarations.get(key), expected, key)
        self.assertNotIn('transform', declarations, 'MapLibre owns the projected transform')


if __name__ == '__main__':
    unittest.main()
