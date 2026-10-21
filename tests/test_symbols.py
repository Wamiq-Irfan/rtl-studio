from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import schematic, synthesize
from symbols import gate_kind


class SymbolTests(unittest.TestCase):
    def test_synthesized_full_adder_has_real_gate_shapes(self):
        source = '''module full_adder(input a,b,cin, output sum,carry);
assign sum = a ^ b ^ cin;
assign carry = (a & b) | (cin & (a ^ b));
endmodule'''
        result = synthesize(source, 'full_adder')
        self.assertTrue(result['ok'], result['log'])
        root = ET.fromstring(schematic(result['netlist'], 'full_adder'))
        types = {node.attrib['data-symbol'] for node in root.iter() if 'data-symbol' in node.attrib}
        self.assertTrue({'AND', 'OR', 'XOR'} <= types)
        blocks = schematic(result['netlist'], 'full_adder', symbols=False)
        self.assertNotIn('data-symbol="AND"', blocks)
        self.assertIn('data-symbol="BLOCK"', blocks)

    def test_generic_inversion_and_unknown_cells(self):
        self.assertEqual(gate_kind('$_NAND_'), 'NAND')
        self.assertEqual(gate_kind('$_NOT_'), 'NOT')
        self.assertEqual(gate_kind('$_DFF_N_'), 'DFF')
        self.assertIsNone(gate_kind('$add'))
