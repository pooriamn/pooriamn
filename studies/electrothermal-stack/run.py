"""Reproduce a dynamic stack calculation and export energy-balance diagnostics."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"]="electrochem-toolkit-study"
matplotlib.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,"axes.titleweight":"semibold","axes.prop_cycle":matplotlib.cycler(color=["#156b79","#b96138","#395575","#7f8d96"])})
import matplotlib.pyplot as plt
from electrochem_toolkit.electrothermal import Stack,simulate

def main():
    out=Path("study-output/electrothermal");out.mkdir(parents=True,exist_ok=True)
    rows=simulate(Stack(),[(300,.1,0),(900,.6,0),(900,1.0,0),(600,.2,0),(600,0,0)],sample_s=10)
    with (out/"timeseries.csv").open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    summary={"peak_temperature_K":max(r["temperature_K"] for r in rows),
             "final_temperature_K":rows[-1]["temperature_K"],
             "max_abs_balance_residual_J":max(abs(r["balance_residual_J"]) for r in rows),
             "final_dc_energy_J":rows[-1]["dc_energy_J"],
             "final_chemical_energy_J":rows[-1]["chemical_energy_J"],
             "final_heat_loss_J":rows[-1]["heat_loss_J"],
             "final_thermal_storage_J":rows[-1]["thermal_storage_J"]}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
    print(json.dumps(summary,indent=2,allow_nan=False))
    t=[r["time_s"]/60 for r in rows]
    fig,axes=plt.subplots(2,2,figsize=(10,7),layout="constrained")
    ax=axes[0,0];ax.step(t,[r["current_density_A_cm2"] for r in rows],where="post")
    ax.set(xlabel="Time / min",ylabel="j / A cm⁻²",title="Current programme")
    ax=axes[0,1];ax.plot(t,[r["temperature_K"]-273.15 for r in rows])
    ax.set(xlabel="Time / min",ylabel="Temperature / °C",title="Thermal response")
    ax=axes[1,0]
    for field,label in [("E_rev_V","Reversible"),("E_tn_V","Thermoneutral"),("cell_voltage_V","Cell")]:
        ax.plot(t,[r[field] for r in rows],label=label)
    ax.set(xlabel="Time / min",ylabel="Voltage / V",title="Cell voltage");ax.legend()
    ax=axes[1,1]
    for field,label in [("dc_energy_J","DC input"),("chemical_energy_J","Reaction enthalpy"),
                        ("heat_loss_J","Heat rejected"),("thermal_storage_J","Thermal storage")]:
        ax.plot(t,[r[field]/1e6 for r in rows],label=label)
    ax.set(xlabel="Time / min",ylabel="Energy / MJ",title="Integrated energy balance");ax.legend(fontsize=8)
    for ax in axes.flat:ax.grid(alpha=.2)
    fig.suptitle("Illustrative dynamic electrolyser stack | lumped electrothermal model")
    fig.savefig(out/"results.svg",metadata={"Date":None})
    return summary

if __name__=="__main__":main()
