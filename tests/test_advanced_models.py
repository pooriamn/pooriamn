import unittest
try:
    import numpy as np
    from electrochem_toolkit import inverse as inv, electrothermal as et
    AVAILABLE=True
except ImportError:
    AVAILABLE=False

@unittest.skipUnless(AVAILABLE,"Install the advanced extra")
class AdvancedTests(unittest.TestCase):
    def test_analytic_jacobian(self):
        f=np.logspace(-2,4,31)
        t=np.r_[np.log([.12,.8,.025]),.82]
        _,J=inv._model("RQ",f,t)
        for k in range(4):
            d=np.zeros(4);d[k]=1e-6
            numeric=(inv._model("RQ",f,t+d)[0]-inv._model("RQ",f,t-d)[0])/(2e-6)
            np.testing.assert_allclose(J[:,k],numeric,rtol=2e-5,atol=1e-8)
    def test_nested_model(self):
        f=np.logspace(-3,5,50)
        np.testing.assert_allclose(inv.response("RC",f,.12,.8,.025),
                                   inv.response("RQ",f,.12,.8,.025,1))
    def test_recover_noisy_rq_and_select_model(self):
        f=np.logspace(-2,4,60);rng=np.random.default_rng(7)
        z=inv.response("RQ",f,.12,.8,.025,.82)
        s=.002*np.ones(len(f));z+=s*(rng.normal(size=len(f))+1j*rng.normal(size=len(f)))
        spec=inv.Spectrum(f,z,s)
        rq=inv.fit(spec,"RQ",starts=6);rc=inv.fit(spec,"RC",starts=6)
        self.assertLess(rq.aicc,rc.aicc)
        self.assertAlmostEqual(rq.parameters["alpha"],.82,delta=.025)
        self.assertAlmostEqual(rq.parameters["R_ohm"],.8,delta=.03)
        self.assertEqual(rq.rank,4)
        self.assertIsNotNone(rq.standard_errors)
    def test_invalid_spectrum(self):
        with self.assertRaises(ValueError):
            inv.Spectrum(np.ones(10),np.ones(10),.1)
        with self.assertRaises(ValueError):
            inv.Spectrum(np.arange(1,11),np.ones(10),0)
    def test_reference_reversible_and_thermoneutral(self):
        p=et.operating_point(et.Stack(),0,298.15)
        self.assertAlmostEqual(p["E_rev_V"],1.229,delta=.002)
        self.assertAlmostEqual(p["E_tn_V"],1.481,delta=.002)
        self.assertEqual(p["dc_power_W"],0)
    def test_pressure_and_temperature(self):
        a=et.operating_point(et.Stack(),.3,298.15)
        b=et.operating_point(et.Stack(hydrogen_bar=10),.3,298.15)
        self.assertAlmostEqual(b["E_rev_V"]-a["E_rev_V"],et.R*298.15/(2*et.F)*np.log(10))
        c=et.operating_point(et.Stack(),.3,333.15)
        self.assertLess(c["eta_ohmic_V"],a["eta_ohmic_V"])
    def test_adiabatic_conservation(self):
        s=et.Stack(UA_W_K=0)
        rows=et.simulate(s,[(120,.4,0),(180,.7,50)],sample_s=10)
        self.assertEqual(rows[-1]["time_s"],300)
        self.assertLess(abs(rows[-1]["balance_residual_J"]),1e-5)
        self.assertEqual(len(set(row["time_s"] for row in rows)),len(rows))
    def test_passive_cooling(self):
        s=et.Stack()
        out=et.simulate(s,[(300,0,0)],initial_K=333.15,sample_s=30)[-1]
        exact=s.ambient_K+(333.15-s.ambient_K)*np.exp(-s.UA_W_K*300/s.heat_capacity_J_K)
        self.assertAlmostEqual(out["temperature_K"],exact,places=5)
    def test_domain_exit(self):
        with self.assertRaises(ValueError):
            et.simulate(et.Stack(UA_W_K=0),[(100,0,1e6)],initial_K=372)
