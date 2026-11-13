"""Command-line entry points for independent engineering calculations."""
import argparse
import json
from .stack import calculate
from .pipeline import publish
from .battery import throughput
from .impedance import impedance, bode

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command",required=True)
    s = subs.add_parser("stack")
    for name in ("area","density","voltage"):
        s.add_argument("--"+name,type=float,required=True)
    s.add_argument("--cells",type=int,required=True)
    s.add_argument("--efficiency",type=float,default=1)
    p = subs.add_parser("report")
    p.add_argument("source");p.add_argument("destination")
    e = subs.add_parser("impedance")
    for name in ("frequency","rs","rct","capacitance"):
        e.add_argument("--"+name,type=float,required=True)
    b = subs.add_parser("battery")
    b.add_argument("--time",type=float,nargs="+",required=True)
    b.add_argument("--current",type=float,nargs="+",required=True)
    a = parser.parse_args()
    try:
        if a.command=="stack":
            out=calculate(a.cells,a.area,a.density,a.voltage,a.efficiency)
        elif a.command=="report":
            out=publish(a.source,a.destination)
        elif a.command=="battery":
            out=throughput(a.time,a.current)
        else:
            z=impedance(a.frequency,a.rs,a.rct,a.capacitance)
            magnitude,phase=bode([a.frequency],a.rs,a.rct,a.capacitance)[0]
            out={"real_ohm":z.real,"imag_ohm":z.imag,"magnitude_ohm":magnitude,"phase_deg":phase}
        print(json.dumps(out,indent=2,allow_nan=False))
    except (ValueError,OSError) as exc:
        parser.error(str(exc))

if __name__=="__main__":
    main()
