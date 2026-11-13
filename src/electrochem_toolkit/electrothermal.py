"""Lumped electrothermal model of an ideal series electrolyser stack.

All electrochemical parameters are illustrative, not fitted to industrial data.
One temperature, uniform current, pure gases, liquid water activity = 1,
100% Faradaic efficiency, constant reaction enthalpy and entropy.
"""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp

F=96485.33212
R=8.314462618
H2_MASS=0.00201588
# Standard reaction H2O(l) -> H2(g) + 0.5 O2(g), near 298.15 K.
DH=285830.0
DS=163.34
TREF=298.15

@dataclass(frozen=True)
class Stack:
    cells: int=20
    area_cm2: float=100.0
    j0_ref_A_cm2: float=0.003
    activation_Ea_J_mol: float=22000.0
    asr_ref_ohm_cm2: float=0.30
    ohmic_Ea_J_mol: float=12000.0
    heat_capacity_J_K: float=18000.0
    UA_W_K: float=18.0
    ambient_K: float=298.15
    hydrogen_bar: float=1.0
    oxygen_bar: float=1.0

    def __post_init__(self):
        if not isinstance(self.cells,int) or isinstance(self.cells,bool) or self.cells<1:
            raise ValueError("cells must be a positive integer")
        values=[self.area_cm2,self.j0_ref_A_cm2,self.asr_ref_ohm_cm2,
                self.heat_capacity_J_K,self.hydrogen_bar,self.oxygen_bar]
        if not all(np.isfinite(v) and v>0 for v in values):
            raise ValueError("Positive finite area, kinetic/ohmic parameters, capacity and pressure required")
        if not all(np.isfinite(v) and v>=0 for v in
                   [self.activation_Ea_J_mol,self.ohmic_Ea_J_mol,self.UA_W_K]):
            raise ValueError("Activation energies and UA must be finite and nonnegative")
        if not 273.15<=self.ambient_K<=373.15:
            raise ValueError("Ambient outside model range")

def operating_point(stack,j,T):
    if not np.isfinite(j) or j<0 or not np.isfinite(T) or not 273.15<=T<=373.15:
        raise ValueError("Require nonnegative finite current density and 273.15–373.15 K")
    s=stack
    # Standard-state pressure is 1 bar; pressures in bar are numerical activities.
    erev=(DH-T*DS)/(2*F)+R*T/(2*F)*(np.log(s.hydrogen_bar)+.5*np.log(s.oxygen_bar))
    etn=DH/(2*F)
    j0=s.j0_ref_A_cm2*np.exp(-s.activation_Ea_J_mol/R*(1/T-1/TREF))
    asr=s.asr_ref_ohm_cm2*np.exp(s.ohmic_Ea_J_mol/R*(1/T-1/TREF))
    # Effective symmetric Butler–Volmer loss; one lumped apparent kinetic term.
    eta=2*R*T/F*np.arcsinh(j/(2*j0))
    ohmic=j*asr
    v=erev+eta+ohmic
    I=s.area_cm2*j
    power=s.cells*I*v
    mol_s=s.cells*I/(2*F)
    chemical=mol_s*DH
    return {"E_rev_V":float(erev),"E_tn_V":float(etn),"eta_activation_V":float(eta),
            "eta_ohmic_V":float(ohmic),"cell_voltage_V":float(v),"current_A":float(I),
            "dc_power_W":float(power),"hydrogen_mol_s":float(mol_s),
            "hydrogen_kg_h":float(mol_s*H2_MASS*3600),
            "chemical_enthalpy_W":float(chemical),"net_reaction_heat_W":float(power-chemical)}

def simulate(stack, segments, initial_K=298.15, sample_s=5.0):
    """Integrate piecewise constant (duration_s, j_A_cm2, heater_W) segments.

    Integrates electrical, chemical, heater and rejected-heat energies as
    states, not by post-hoc interpolation. Rejects out-of-domain trajectories.
    """
    if not np.isfinite(sample_s) or sample_s<=0 or not 273.15<initial_K<373.15:
        raise ValueError("Positive sample interval and interior initial temperature required")
    segments=list(segments)
    if not segments:
        raise ValueError("At least one segment required")
    state=np.array([initial_K,0.,0.,0.,0.]);offset=0.;rows=[]
    for duration,j,heater in segments:
        if not all(np.isfinite(x) and x>=0 for x in (duration,j,heater)) or duration<=0:
            raise ValueError("Positive duration, nonnegative finite current density and heater required")
        def rhs(t,y):
            # Numerical stages can slightly overstep event boundaries.
            T=float(np.clip(y[0],273.15,373.15))
            op=operating_point(stack,j,T)
            loss=stack.UA_W_K*(T-stack.ambient_K)
            return [(op["net_reaction_heat_W"]+heater-loss)/stack.heat_capacity_J_K,
                    op["dc_power_W"],op["chemical_enthalpy_W"],heater,loss]
        def upper(t,y): return 373.15-y[0]
        def lower(t,y): return y[0]-273.15
        upper.terminal=lower.terminal=True
        upper.direction=lower.direction=-1
        times=np.linspace(0,duration,max(2,int(np.ceil(duration/sample_s))+1))
        sol=solve_ivp(rhs,(0,duration),state,t_eval=times,rtol=1e-8,atol=1e-8,
                      events=(upper,lower),max_step=min(30.,duration))
        if not sol.success or sol.status==1 or sol.t[-1]<duration:
            raise ValueError("Integration failed or temperature left the model domain")
        # At a current step the new operating point is right-continuous.
        if rows: rows.pop()
        for t,y in zip(sol.t,sol.y.T):
            op=operating_point(stack,j,y[0])
            rows.append({"time_s":float(offset+t),"temperature_K":float(y[0]),
                         "current_density_A_cm2":float(j),**op,
                         "dc_energy_J":float(y[1]),"chemical_energy_J":float(y[2]),
                         "heater_energy_J":float(y[3]),"heat_loss_J":float(y[4]),
                         "thermal_storage_J":float(stack.heat_capacity_J_K*(y[0]-initial_K)),
                         "balance_residual_J":float(y[1]-y[2]+y[3]-y[4]-
                                                  stack.heat_capacity_J_K*(y[0]-initial_K))})
        state=sol.y[:,-1];offset+=duration
    return rows
