"""Helpers."""

from sys import stderr
from typing import Any

# Pretty print a dicts with the following keys
# ['serial', 'protocol', 'timestamp', 'pconsume', 'pconsumeunit', 'pconsumecounter', 'pconsumecounterunit', 'psupply', 'psupplyunit', 'psupplycounter', 'psupplycounterunit', 'qconsume', 'qconsumeunit', 'qconsumecounter', 'qconsumecounterunit', 'qsupply', 'qsupplyunit', 'qsupplycounter', 'qsupplycounterunit', 'sconsume', 'sconsumeunit', 'sconsumecounter', 'sconsumecounterunit', 'ssupply', 'ssupplyunit', 'ssupplycounter', 'ssupplycounterunit', 'cosphi', 'cosphiunit', 'p1consume', 'p1consumeunit', 'p1consumecounter', 'p1consumecounterunit', 'p1supply', 'p1supplyunit', 'p1supplycounter', 'p1supplycounterunit', 'q1consume', 'q1consumeunit', 'q1consumecounter', 'q1consumecounterunit', 'q1supply', 'q1supplyunit', 'q1supplycounter', 'q1supplycounterunit', 's1consume', 's1consumeunit', 's1consumecounter', 's1consumecounterunit', 's1supply', 's1supplyunit', 's1supplycounter', 's1supplycounterunit', 'i1', 'i1unit', 'u1', 'u1unit', 'cosphi1', 'cosphi1unit', 'p2consume', 'p2consumeunit', 'p2consumecounter', 'p2consumecounterunit', 'p2supply', 'p2supplyunit', 'p2supplycounter', 'p2supplycounterunit', 'q2consume', 'q2consumeunit', 'q2consumecounter', 'q2consumecounterunit', 'q2supply', 'q2supplyunit', 'q2supplycounter', 'q2supplycounterunit', 's2consume', 's2consumeunit', 's2consumecounter', 's2consumecounterunit', 's2supply', 's2supplyunit', 's2supplycounter', 's2supplycounterunit', 'i2', 'i2unit', 'u2', 'u2unit', 'cosphi2', 'cosphi2unit', 'p3consume', 'p3consumeunit', 'p3consumecounter', 'p3consumecounterunit', 'p3supply', 'p3supplyunit', 'p3supplycounter', 'p3supplycounterunit', 'q3consume', 'q3consumeunit', 'q3consumecounter', 'q3consumecounterunit', 'q3supply', 'q3supplyunit', 'q3supplycounter', 'q3supplycounterunit', 's3consume', 's3consumeunit', 's3consumecounter', 's3consumecounterunit', 's3supply', 's3supplyunit', 's3supplycounter', 's3supplycounterunit', 'i3', 'i3unit', 'u3', 'u3unit', 'cosphi3', 'cosphi3unit', 'speedwire-version']
# the dict contains pair of x and xunit, where x is the sensor name and xunit is the unit of the sensor.


def pretty_print_dict(data: dict[str, Any], indent: int = 0) -> dict[str, str]:
    """Pretty print a dict. Indent>0 will print the dict with indentation."""
    res = {}
    for key, val in data.items():
        if key.endswith("unit"):
            continue
        unit = data.get(f"{key}unit", "")
        res[key] = f"{val} {unit}".strip()
    if indent:
        ind = "\n" + (" " * indent)
        result = ind.join(f"{k}: {res[k]}" for k in sorted(res))
        print(f"\n{ind}{result}", file=stderr, flush=True)
    return res
