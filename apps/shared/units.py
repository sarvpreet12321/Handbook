import re

def c_to_f(c): return c * 9/5 + 32
def f_to_c(f): return (f - 32) * 5/9

def linear_convert(val, to_base, u_from, u_to):
    v_base = val * to_base[u_from]
    return v_base / to_base[u_to]

velocity_to_base = {   # base: m/s
    "m/s": 1.0, "ft/s": 0.3048, "ft/min": 0.3048/60, "km/hr": 1000/3600, "mile/hr": 1609.344/3600,
}
flow_to_base = {       # base: L/s
    "L/s": 1.0, "CFM": 0.47194745,
}
pressure_to_base = {   # base: Pa
    "Pa": 1.0, "kPa": 1_000.0, "psi": 6_894.757293, "in H₂O": 249.08891,
    "mm H₂O": 9.80665, "in Hg": 3_386.389, "mm Hg (Torr)": 133.322368, "bar": 100_000.0, "Std. Atmos.": 101_325.0,
}
power_to_base = {      # base: W
    "W": 1.0, "kW": 1_000.0, "HP": 745.699872, "Btu/hr": 0.29307107,
    "ton refriger.": 3_516.852842, "MJ/hr": 1_000_000/3600,
}

gauge_to_mm = {
    "26 #": 0.5, "24 #": 0.6, "22 #": 0.8, "20 #": 1.0, "18 #": 1.2,
    "16 #": 1.6, "14 #": 2.0, "12 #": 2.5, "10 #": 3.0,
}

def parse_fraction(txt: str) -> float:
    if txt is None:
        raise ValueError("empty")
    s = str(txt).strip().replace("−", "-")
    s = re.sub(r"\s+", " ", s)

    m = re.fullmatch(r"(?i)\s*(?P<w>-?\d+)\s*[- ]\s*(?P<n>\d+)\s*/\s*(?P<d>\d+)\s*", s)
    if m:
        w = float(m.group("w")); n = float(m.group("n")); d = float(m.group("d"))
        return w + (n/d if w >= 0 else -n/d)

    m = re.fullmatch(r"\s*(?P<n>-?\d+)\s*/\s*(?P<d>\d+)\s*", s)
    if m:
        n = float(m.group("n")); d = float(m.group("d"))
        return n/d

    return float(s)
