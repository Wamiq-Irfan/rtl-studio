from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import lint, module_names, schematic, synthesize

EXAMPLES = Path(__file__).resolve().parents[1] / 'examples'


class EngineTests(unittest.TestCase):
    def test_counter_real_netlist(self):
        result = synthesize((EXAMPLES / 'counter.sv').read_text(), 'counter')
        self.assertTrue(result['ok'], result['log'])
        kinds = [c['type'] for c in result['netlist']['modules']['counter']['cells'].values()]
        self.assertTrue(any('dff' in kind.lower() for kind in kinds))
        self.assertIn('$add', kinds)
        ET.fromstring(schematic(result['netlist'], 'counter'))

    def test_mux_connectivity(self):
        result = synthesize((EXAMPLES / 'mux.sv').read_text(), 'mux2')
        self.assertTrue(result['ok'], result['log'])
        svg = schematic(result['netlist'], 'mux2')
        self.assertIn('$mux', svg)
        self.assertIn('connected bit(s)', svg)
        self.assertIn('A;', svg)
        ET.fromstring(svg)

    def test_invalid_syntax_diagnostics(self):
        self.assertIn('error', lint('module bad(input logic a) assign = ; endmodule').lower())

    def test_latch_rejected_in_always_comb(self):
        result = synthesize((EXAMPLES / 'broken.sv').read_text(), 'broken')
        self.assertFalse(result['ok'])
        self.assertIn('latch', result['log'].lower())

    def test_gate_mapping(self):
        result = synthesize((EXAMPLES / 'mux.sv').read_text(), 'mux2', gates=True)
        self.assertTrue(result['ok'], result['log'])
        kinds = [c['type'] for c in result['netlist']['modules']['mux2']['cells'].values()]
        self.assertIn('$_MUX_', kinds)

    def test_bad_top_rejected(self):
        with self.assertRaises(ValueError):
            synthesize('module a; endmodule', 'a; shell')

    def test_names_ignore_comments(self):
        self.assertEqual(module_names('// module fake;\n module real; endmodule'), ['real'])


if __name__ == '__main__':
    unittest.main()
