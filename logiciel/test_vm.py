import unittest
import vm_performance as app


class TestVm(unittest.TestCase):
    def test_demo_snapshot(self):
        demo = app.DemoBackend()
        reading = demo.read_snapshot()
        self.assertEqual(set(reading), {p[0] for p in app.FIELDS})
        self.assertGreater(reading['rpm'], 0)
        self.assertGreaterEqual(reading['speed'], 0)

    def test_fake_codes_label(self):
        demo = app.DemoBackend()
        self.assertTrue(all('FICTIF' in desc for _, desc in demo.read_codes()))

    def test_no_write_commands(self):
        import inspect
        source = inspect.getsource(app.OBDBackend)
        self.assertNotIn('CLEAR_DTC', source)
        self.assertNotIn('query(force=True)', source)
        self.assertNotIn('send(', source)


if __name__ == '__main__':
    unittest.main()
