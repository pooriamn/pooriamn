"""Regression tests for energy and charge integration from synthetic traces."""
import importlib.util
from pathlib import Path
import unittest

from electrochem_toolkit import pipeline as toolkit_pipeline


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "standalone_experiment_pipeline",
    ROOT / "projects" / "experimental-pipeline" / "pipeline.py",
)
standalone_pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(standalone_pipeline)


class ChargeAccountingTests(unittest.TestCase):
    def assert_both_implementations(self, data, expected):
        for module in (toolkit_pipeline, standalone_pipeline):
            with self.subTest(implementation=module.__name__):
                result = module.summarise(data)
                for key, value in expected.items():
                    self.assertAlmostEqual(result[key], value, places=12)
                self.assertEqual(result["sample_count"], data.count(b"\n") - 1)
                self.assertEqual(len(result["source_sha256"]), 64)

    def test_constant_current(self):
        self.assert_both_implementations(
            b"time_s,voltage_V,current_A\n0,2,3\n3600,2,3\n",
            {"energy_Wh": 6.0, "charge_Ah": 3.0,
             "mean_current_A": 3.0, "mean_power_W": 6.0},
        )

    def test_irregular_sampling(self):
        # 0-900 s: 0.5 Ah; 900-3600 s: 2.25 Ah.
        self.assert_both_implementations(
            b"time_s,voltage_V,current_A\n0,2,0\n900,2,4\n3600,2,2\n",
            {"energy_Wh": 5.5, "charge_Ah": 2.75,
             "mean_current_A": 2.75, "duration_s": 3600.0},
        )

    def test_charge_is_independent_of_voltage(self):
        # End-point powers are 0 and 6 W: 3 Wh by the power trapezoid.
        self.assert_both_implementations(
            b"time_s,voltage_V,current_A\n0,0,1\n3600,2,3\n",
            {"energy_Wh": 3.0, "charge_Ah": 2.0,
             "mean_current_A": 2.0},
        )

    def test_zero_current(self):
        self.assert_both_implementations(
            b"time_s,voltage_V,current_A\n0,2,0\n3600,2,0\n",
            {"energy_Wh": 0.0, "charge_Ah": 0.0,
             "mean_current_A": 0.0},
        )

    def test_negative_current_still_rejected(self):
        data = b"time_s,voltage_V,current_A\n0,2,-1\n3600,2,1\n"
        for module in (toolkit_pipeline, standalone_pipeline):
            with self.subTest(implementation=module.__name__):
                with self.assertRaises(ValueError):
                    module.summarise(data)


if __name__ == "__main__":
    unittest.main()
