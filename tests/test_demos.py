import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

eis = load("impedance", "projects/electrochemical-analysis/impedance.py")
stack = load("stack", "projects/electrolyser-calculator/stack.py")
pipeline = load("pipeline", "projects/experimental-pipeline/pipeline.py")

class ImpedanceTests(unittest.TestCase):
    def test_limits(self):
        self.assertAlmostEqual(eis.impedance(1e-9, .2, 1.5, .01).real, 1.7)
        self.assertAlmostEqual(eis.impedance(1e9, .2, 1.5, .01).real, .2)
    def test_recover_known_parameters(self):
        f = [0.1, 1, 10, 100, 1000]
        z = [eis.impedance(x, .2, 1.5, .01) for x in f]
        params, error = eis.fit_grid(f, z, [.1,.2], [1,1.5], [.01,.02])
        self.assertEqual(params, (.2, 1.5, .01))
        self.assertAlmostEqual(error, 0)
    def test_invalid_frequency(self):
        with self.assertRaises(ValueError):
            eis.impedance(0, .2, 1.5, .01)

class StackTests(unittest.TestCase):
    def test_series_balance(self):
        result = stack.calculate(10, 100, .3, 1.8)
        self.assertEqual(result["current_A"], 30)
        self.assertAlmostEqual(result["dc_power_kW"], .54)
        self.assertAlmostEqual(result["dc_specific_energy_kWh_kg"], 47.862637, places=3)
    def test_efficiency(self):
        self.assertAlmostEqual(stack.calculate(10,100,.3,1.8,.5)["hydrogen_kg_h"],
                               stack.calculate(10,100,.3,1.8)["hydrogen_kg_h"]/2)
    def test_invalid(self):
        for args in [(0,100,.3,1.8), (10,100,.3,1.8,1.1)]:
            with self.assertRaises(ValueError):
                stack.calculate(*args)

class PipelineTests(unittest.TestCase):
    def test_constant_power(self):
        result = pipeline.summarise(b"time_s,voltage_V,current_A\n0,2,3\n3600,2,3\n")
        self.assertEqual(result["energy_Wh"], 6)
    def test_reject_invalid(self):
        for raw in [b"time_s,voltage_V,current_A\n0,2,3\n0,2,3\n",
                    b"time_s,voltage_V,current_A\n0,nan,3\n1,2,3\n",
                    b"time_s,voltage_V,current_A\n0,2,3,extra\n1,2,3\n"]:
            with self.assertRaises(ValueError):
                pipeline.summarise(raw)
    def test_deterministic_and_preserves_previous_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory)/"data.csv", Path(directory)/"report.json"
            source.write_bytes(b"time_s,voltage_V,current_A\n0,2,3\n1,2,3\n")
            pipeline.publish(source, output)
            original = output.read_bytes()
            pipeline.publish(source, output)
            self.assertEqual(output.read_bytes(), original)
            source.write_text("invalid")
            with self.assertRaises(ValueError):
                pipeline.publish(source, output)
            self.assertEqual(output.read_bytes(), original)

if __name__ == "__main__":
    unittest.main()
