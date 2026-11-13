"""Complex nonlinear least squares for two explicitly defined EIS models.

Optional NumPy/SciPy dependencies. Sigma is the standard deviation of each
independent real/imaginary observation, in ohms; not a modulus weight.
"""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import least_squares

@dataclass(frozen=True)
class Spectrum:
    frequency_hz: np.ndarray
    impedance_ohm: np.ndarray
    sigma_ohm: np.ndarray

    def __post_init__(self):
        freq=np.asarray(self.frequency_hz,dtype=float).copy()
        z=np.asarray(self.impedance_ohm,dtype=complex).copy()
        sigma=np.broadcast_to(np.asarray(self.sigma_ohm,dtype=float),freq.shape).copy()
        if freq.ndim!=1 or len(freq)<8 or z.shape!=freq.shape:
            raise ValueError("At least eight aligned frequency and impedance samples required")
        if not np.all(np.isfinite(freq)&(freq>0)) or len(np.unique(freq))!=len(freq):
            raise ValueError("Frequencies must be unique, finite and positive")
        if not np.all(np.isfinite(z)) or not np.all(np.isfinite(sigma)&(sigma>0)):
            raise ValueError("Finite impedance and positive finite sigma required")
        for name,value in [("frequency_hz",freq),("impedance_ohm",z),("sigma_ohm",sigma)]:
            value.setflags(write=False)
            object.__setattr__(self,name,value)

def _model(model, freq, theta):
    """Evaluate model and analytic Jacobian with respect to transformed parameters.

    RQ: Rs + R/(1 + R Q (j omega)^alpha).
    RC is the nested alpha=1 model; Q then equals C.
    """
    if model not in ("RC","RQ"):
        raise ValueError("model must be RC or RQ")
    rs,r,q=np.exp(theta[:3])
    alpha=theta[3] if model=="RQ" else 1.0
    logjw=np.log(2*np.pi*freq)+1j*np.pi/2
    y=r*q*np.exp(alpha*logjw)
    den=1+y
    z=rs+r/den
    cols=[np.full_like(z,rs),r/den**2,-r*y/den**2]
    if model=="RQ":
        cols.append(-r*y*logjw/den**2)
    return z,np.column_stack(cols)

def response(model, frequency_hz, rs, r, q, alpha=1.0):
    freq=np.asarray(frequency_hz,dtype=float)
    if not np.all(np.isfinite(freq)&(freq>0)):
        raise ValueError("Frequency must be positive and finite")
    if not all(np.isfinite(v) and v>0 for v in (rs,r,q)):
        raise ValueError("Positive finite parameters required")
    if model=="RQ" and not 0<alpha<=1:
        raise ValueError("Require 0 < alpha <= 1")
    theta=np.log([rs,r,q])
    if model=="RQ":
        theta=np.r_[theta,alpha]
    return _model(model,freq,theta)[0]

@dataclass(frozen=True)
class FitResult:
    model: str
    parameters: dict
    standard_errors: dict | None
    weighted_rss: float
    aicc: float
    condition_number: float
    rank: int
    at_bound: bool
    converged: bool
    predicted: np.ndarray
    standardised_residuals: np.ndarray

def fit(spectrum, model="RQ", starts=12, seed=42):
    """Bounded multistart complex least squares with local identifiability diagnostics.

    Bounds are deliberately broad and are not material-specific priors.
    AICc uses known independent Gaussian channel variances, identical data
    and weights across compared models. Local errors are omitted at a bound
    or for a rank-deficient/poorly conditioned Jacobian.
    """
    if model not in ("RC","RQ") or not isinstance(starts,int) or not 1<=starts<=100:
        raise ValueError("Choose RC/RQ and 1–100 starting points")
    f,z,s=spectrum.frequency_hz,spectrum.impedance_ohm,spectrum.sigma_ohm
    lo=np.log([1e-8,1e-8,1e-12])
    hi=np.log([1e5,1e7,1e3])
    names=["Rs_ohm","R_ohm","C_F" if model=="RC" else "Q_S_s_alpha"]
    if model=="RQ":
        lo=np.r_[lo,.2];hi=np.r_[hi,1.0];names.append("alpha")
    def residual(t):
        d=(_model(model,f,t)[0]-z)/s
        return np.r_[d.real,d.imag]
    def jac(t):
        j=_model(model,f,t)[1]/s[:,None]
        return np.vstack([j.real,j.imag])
    rs=max(float(np.min(z.real)),1e-6)
    r=max(float(np.ptp(z.real)),1e-5)
    fpeak=f[np.argmax(-z.imag)]
    alpha0=.85 if model=="RQ" else 1.
    q=1/(r*(2*np.pi*fpeak)**alpha0)
    t0=np.log([rs,r,q])
    if model=="RQ":
        t0=np.r_[t0,alpha0]
    t0=np.clip(t0,lo+1e-6,hi-1e-6)
    rng=np.random.default_rng(seed)
    candidates=[t0]
    for _ in range(starts-1):
        trial=t0+rng.normal(0,1.8,len(t0))
        if model=="RQ":
            trial[3]=rng.uniform(.35,.99)
        candidates.append(np.clip(trial,lo+1e-6,hi-1e-6))
    results=[least_squares(residual,t,jac=jac,bounds=(lo,hi),max_nfev=1500,
                           x_scale="jac",ftol=1e-10,xtol=1e-10,gtol=1e-10)
             for t in candidates]
    successful=[v for v in results if v.success and np.isfinite(v.cost)]
    if not successful:
        raise RuntimeError("No converged finite fit")
    best=min(successful,key=lambda v:v.cost)
    n=len(best.fun);k=len(best.x);rss=float(best.fun@best.fun)
    _,singular,vh=np.linalg.svd(best.jac,full_matrices=False)
    threshold=np.finfo(float).eps*max(best.jac.shape)*singular[0]
    rank=int(np.sum(singular>threshold))
    condition=float(singular[0]/singular[-1]) if singular[-1]>0 else float("inf")
    at_bound=bool(np.any(best.active_mask!=0) or np.any(np.minimum(best.x-lo,hi-best.x)<1e-5))
    physical=np.r_[np.exp(best.x[:3]),best.x[3:]]
    errors=None
    if rank==k and condition<1e8 and not at_bound:
        # Known channel sigma: no residual variance rescaling.
        cov=(vh.T/singular**2)@vh
        transform=np.r_[physical[:3],np.ones(k-3)]
        errors=dict(zip(names,(np.sqrt(np.maximum(np.diag(cov),0))*transform).tolist()))
    # Additive Gaussian normalisation is common to both models and omitted.
    aicc=rss+2*k+2*k*(k+1)/(n-k-1)
    return FitResult(model,dict(zip(names,physical.tolist())),errors,rss,float(aicc),
                     condition,rank,at_bound,True,_model(model,f,best.x)[0],best.fun)
