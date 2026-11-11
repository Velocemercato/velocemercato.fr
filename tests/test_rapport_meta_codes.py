import ast
import re
import unittest
from pathlib import Path

class DeliveryError(Exception):
    pass

source = (Path(__file__).resolve().parents[1] / "tools" / "rapport_meta_du_jour.py").read_text()
tree = ast.parse(source)
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "safe_error")
scope = {"re": re, "DeliveryError": DeliveryError}
exec(compile(ast.Module(body=[function], type_ignores=[]), "<safe_error>", "exec"), scope)

class DiagnosticTests(unittest.TestCase):
    def test_only_numeric_codes_are_disclosed(self):
        error = DeliveryError("Meta a refusé (400, code 190) : secret=EAA_PRIVATE_TOKEN email=private@example.com")
        self.assertEqual(scope["safe_error"](error), "Meta HTTP=400 code=190")

    def test_unexpected_errors_never_disclose_their_message(self):
        for error in (ValueError("secret"), DeliveryError("https://service/?access_token=secret")):
            self.assertEqual(scope["safe_error"](error), "erreur de contrôle")

    def test_unknown_provider_code_is_safe(self):
        self.assertEqual(scope["safe_error"](DeliveryError("Meta a refusé (403, code ?) : secret")), "Meta HTTP=403 code=?")

    def test_report_is_read_only(self):
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                self.assertNotEqual(n.func.attr, "save")
                if n.func.attr == "call":
                    self.assertIsInstance(n.args[0], ast.Constant)
                    self.assertEqual(n.args[0].value, "GET")

if __name__ == "__main__":
    unittest.main()
