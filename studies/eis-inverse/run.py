"""Reproduce noisy RC/RQ model discrimination and save diagnostic outputs."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from electrochem_toolkit.inverse import Spectrum,response,fit

def main():
    out=Path("study-output/eis");out.mkdir(parents=True,exist_ok=True)
    f=np.logspace(-2,4,60);rng=np.random.default_rng(7)
    truth=response("RQ",f,.12,.8,.025,.82)
    sigma=np.full(len(f),.002)
    z=truth+sigma*(rng.normal(size=len(f))+1j*rng.normal(size=len(f)))
    data=Spectrum(f,z,sigma)
    fits=[fit(data,m) for m in ("RC","RQ")]
    summary={x.model:{"parameters":x.parameters,"standard_errors":x.standard_errors,
                       "weighted_rss":x.weighted_rss,"aicc":x.aicc,
                       "condition_number":x.condition_number,"rank":x.rank,
                       "at_bound":x.at_bound} for x in fits}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
    print(json.dumps(summary,indent=2,allow_nan=False))
    fig,axes=plt.subplots(2,2,figsize=(10,7),layout="constrained")
    ax=axes[0,0];ax.scatter(z.real,-z.imag,s=12,label="Synthetic observations")
    for x in fits: ax.plot(x.predicted.real,-x.predicted.imag,label=x.model)
    ax.set(xlabel="Re(Z) / Ω",ylabel="−Im(Z) / Ω",title="Nyquist response");ax.set_aspect("equal");ax.legend()
    for x in fits:
        axes[0,1].loglog(f,abs(x.predicted),label=x.model)
        axes[1,0].semilogx(f,np.angle(x.predicted,deg=True),label=x.model)
    axes[0,1].scatter(f,abs(z),s=9);axes[0,1].set(xlabel="f / Hz",ylabel="|Z| / Ω",title="Bode magnitude");axes[0,1].legend()
    axes[1,0].scatter(f,np.angle(z,deg=True),s=9);axes[1,0].set(xlabel="f / Hz",ylabel="Phase / °",title="Bode phase")
    ax=axes[1,1]
    for x in fits:
        ax.semilogx(f,x.standardised_residuals[:len(f)],label=x.model+" real")
        ax.semilogx(f,x.standardised_residuals[len(f):],ls="--",label=x.model+" imag")
    ax.axhline(0,color="black",lw=.7);ax.set(xlabel="f / Hz",ylabel="Residual / σ",title="Standardised residuals");ax.legend(fontsize=8)
    for ax in axes.flat: ax.grid(alpha=.2)
    fig.suptitle("Synthetic impedance inverse problem | RC versus RQ")
    fig.savefig(out/"results.svg")
    return summary

if __name__=="__main__":main()
