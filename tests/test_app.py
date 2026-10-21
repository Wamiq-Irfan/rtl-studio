from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_editor_check_generate_and_stale_results(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
        self.assertFalse(app.exception)
        app.button[1].click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['analysis']['diagnostics'], '')
        app.button[0].click().run(timeout=60)
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state['analysis']['result']['ok'])
        app.text_area[0].set_value('module changed(input logic a, output logic y); assign y=a; endmodule').run()
        self.assertTrue(any('changed' in warning.value for warning in app.warning))
        app.radio[0].set_value('Upload files').run()
        self.assertFalse(app.exception)

