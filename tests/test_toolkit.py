import math
import unittest
from electrochem_toolkit import impedance,stack,battery,polarisation,pipeline

class ToolkitTests(unittest.TestCase):
    def test_bode(self):
        mag, phase = impedance.bode([1/(2*math.pi*1.5*.01)],.2,1.5,.01)[0]
        self.assertAlmostEqual(mag,abs(complex(.95,-.75)))
        self.assertLess(phase,0)
    def test_fit(self):
        fs=[.1,1,10,100]
        zs=[impedance.impedance(f,.2,1.5,.01) for f in fs]
        self.assertEqual(impedance.fit_grid(fs,zs,[.2],[1.5],[.01]),((.2,1.5,.01),0))
    def test_stack(self):
        x=stack.calculate(10,100,.3,1.8)
        self.assertAlmostEqual(x["dc_specific_energy_kWh_kg"],47.862637,places=5)
        self.assertAlmostEqual(x["dc_power_kW"],.54)
    def test_battery_charge_discharge(self):
        out=battery.throughput([0,3600,7200],[2,2,-2])
        self.assertAlmostEqual(out["charge_Ah"],2.5)
        self.assertAlmostEqual(out["discharge_Ah"],.5)
        self.assertAlmostEqual(out["net_Ah"],2)
    def test_battery_constant_discharge(self):
        self.assertEqual(battery.throughput([0,3600],[-2,-2])["discharge_Ah"],2)
    def test_battery_invalid(self):
        for t,i in [([0,0],[1,2]),([0,1],[1,float("nan")]),([0],[1])]:
            with self.assertRaises(ValueError):
                battery.throughput(t,i)
    def test_tafel(self):
        out=polarisation.tafel([.001,.01,.1],[.1,.16,.22])
        self.assertAlmostEqual(out["slope_V_dec"],.06)
        self.assertAlmostEqual(out["r_squared"],1)
        self.assertAlmostEqual(out["rmse_V"],0)
    def test_tafel_invalid(self):
        for j,e in [([0,1,2],[1,2,3]),([1,1,1],[1,2,3])]:
            with self.assertRaises(ValueError):
                polarisation.tafel(j,e)
    def test_report(self):
        out=pipeline.summarise(b"time_s,voltage_V,current_A\n0,2,3\n3600,2,3\n")
        self.assertEqual(out["energy_Wh"],6)
        self.assertEqual(len(out["source_sha256"]),64)
