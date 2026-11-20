"""Validate experimental CSV and write a deterministic JSON report."""
import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import tempfile

FIELDS = ("time_s", "voltage_V", "current_A")

def summarise(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    if reader.fieldnames != list(FIELDS):
        raise ValueError("Expected exact columns: " + ", ".join(FIELDS))
    points = []
    for row in reader:
        if None in row:
            raise ValueError("Unexpected extra CSV fields")
        try:
            t, v, i = (float(row[k]) for k in FIELDS)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid numeric row") from exc
        if not all(math.isfinite(x) and x >= 0 for x in (t, v, i)):
            raise ValueError("Values must be finite and non-negative")
        if points and t <= points[-1][0]:
            raise ValueError("Timestamps must strictly increase")
        points.append((t, v*i, i))
    if len(points) < 2:
        raise ValueError("At least two measurements required")
    energy_j = sum((b[0]-a[0])*(a[1]+b[1])/2 for a,b in zip(points, points[1:]))
    charge_c = sum((b[0]-a[0])*(a[2]+b[2])/2 for a,b in zip(points, points[1:]))
    if not all(math.isfinite(x) for x in (energy_j, charge_c)):
        raise ValueError("Energy or charge calculation overflow")
    duration = points[-1][0] - points[0][0]
    return {"source_sha256": hashlib.sha256(raw).hexdigest(), "sample_count": len(points),
            "duration_s": duration, "energy_Wh": energy_j / 3600,
            "mean_power_W": energy_j / duration,
            "charge_Ah": charge_c / 3600,
            "mean_current_A": charge_c / duration}

def publish(source, destination):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("Source and report must be different files")
    report = summarise(source.read_bytes())
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                         delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    print(json.dumps(publish(args.source, args.destination), indent=2))
