import math


EPSILON_0 = 8.8541878128e-12
MU_0 = 4 * math.pi * 1e-7


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _positive(value, label):
    if value <= 0:
        raise ValueError(f"{label} must be greater than 0.")


def _ohms_law_voltage(d):
    return d["current_a"] * d["resistance_ohm"]


def _ohms_law_current(d):
    _positive(d["resistance_ohm"], "Resistance")
    return d["voltage_v"] / d["resistance_ohm"]


def _ohms_law_resistance(d):
    _positive(d["current_a"], "Current")
    return d["voltage_v"] / d["current_a"]


def _power_vi(d):
    return d["voltage_v"] * d["current_a"]


def _power_i2r(d):
    return d["current_a"] ** 2 * d["resistance_ohm"]


def _power_v2r(d):
    _positive(d["resistance_ohm"], "Resistance")
    return d["voltage_v"] ** 2 / d["resistance_ohm"]


def _resistors_series(d):
    return d["r1"] + d["r2"] + d["r3"]


def _resistors_parallel_two(d):
    _positive(d["r1"], "R1")
    _positive(d["r2"], "R2")
    return (d["r1"] * d["r2"]) / (d["r1"] + d["r2"])


def _voltage_divider(d):
    _positive(d["r1"], "R1")
    _positive(d["r2"], "R2")
    return d["vin"] * d["r2"] / (d["r1"] + d["r2"])


def _current_divider(d):
    _positive(d["r1"], "R1")
    _positive(d["r2"], "R2")
    return d["itotal"] * d["r2"] / (d["r1"] + d["r2"])


def _charge(d):
    return d["current_a"] * d["time_s"]


def _energy_power_time(d):
    return d["power_w"] * d["time_s"]


def _capacitor_energy(d):
    return 0.5 * d["cap_f"] * d["voltage_v"] ** 2


def _capacitive_reactance(d):
    _positive(d["frequency_hz"], "Frequency")
    _positive(d["cap_f"], "Capacitance")
    return 1 / (2 * math.pi * d["frequency_hz"] * d["cap_f"])


def _inductive_reactance(d):
    return 2 * math.pi * d["frequency_hz"] * d["ind_h"]


def _impedance_rlc(d):
    xl = 2 * math.pi * d["frequency_hz"] * d["ind_h"]
    xc = 1 / (2 * math.pi * d["frequency_hz"] * d["cap_f"])
    return math.sqrt(d["resistance_ohm"] ** 2 + (xl - xc) ** 2)


def _resonant_frequency(d):
    _positive(d["ind_h"], "Inductance")
    _positive(d["cap_f"], "Capacitance")
    return 1 / (2 * math.pi * math.sqrt(d["ind_h"] * d["cap_f"]))


def _rc_time_constant(d):
    return d["resistance_ohm"] * d["cap_f"]


def _rl_time_constant(d):
    _positive(d["resistance_ohm"], "Resistance")
    return d["ind_h"] / d["resistance_ohm"]


def _phase_angle_rl(d):
    _positive(d["resistance_ohm"], "Resistance")
    xl = 2 * math.pi * d["frequency_hz"] * d["ind_h"]
    return math.degrees(math.atan(xl / d["resistance_ohm"]))


def _phase_angle_rc(d):
    _positive(d["resistance_ohm"], "Resistance")
    xc = 1 / (2 * math.pi * d["frequency_hz"] * d["cap_f"])
    return -math.degrees(math.atan(xc / d["resistance_ohm"]))


def _real_power(d):
    return d["vrms"] * d["irms"] * d["pf"]


def _apparent_power(d):
    return d["vrms"] * d["irms"]


def _power_factor(d):
    _positive(d["apparent_va"], "Apparent power")
    return d["real_w"] / d["apparent_va"]


def _transformer_ratio_vout(d):
    _positive(d["n_primary"], "Primary turns")
    return d["v_primary"] * d["n_secondary"] / d["n_primary"]


def _transformer_ratio_iout(d):
    _positive(d["n_secondary"], "Secondary turns")
    return d["i_primary"] * d["n_primary"] / d["n_secondary"]


def _diode_current_shockley(d):
    exponent = d["voltage_v"] / (d["n"] * d["vt"])
    if exponent > 100:
        raise ValueError("Exponent too large; reduce voltage or adjust n and Vt.")
    return d["is_a"] * (math.exp(exponent) - 1)


def _led_resistor(d):
    _positive(d["led_current_a"], "LED current")
    return (d["supply_v"] - d["led_vf"]) / d["led_current_a"]


def _cutoff_frequency_rc(d):
    _positive(d["resistance_ohm"], "Resistance")
    _positive(d["cap_f"], "Capacitance")
    return 1 / (2 * math.pi * d["resistance_ohm"] * d["cap_f"])


def _cutoff_frequency_rl(d):
    _positive(d["ind_h"], "Inductance")
    return d["resistance_ohm"] / (2 * math.pi * d["ind_h"])


def _electric_field(d):
    _positive(d["distance_m"], "Distance")
    return d["voltage_v"] / d["distance_m"]


def _capacitance_parallel_plate(d):
    _positive(d["distance_m"], "Plate spacing")
    return d["epsilon_r"] * EPSILON_0 * d["area_m2"] / d["distance_m"]


def _inductor_energy(d):
    return 0.5 * d["ind_h"] * d["current_a"] ** 2


ELECTRONICS_FORMULAS = {
    "ohms-voltage": {
        "title": "Ohm's Law (Solve V)",
        "latex": r"V = IR",
        "fields": [
            {"name": "current_a", "label": "Current I (A)"},
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
        ],
        "compute": _ohms_law_voltage,
        "substitute": lambda d: f"V = {_fmt(d['current_a'])}x{_fmt(d['resistance_ohm'])}",
        "answer_label": "Voltage V (V)",
        "format_answer": _fmt,
    },
    "ohms-current": {
        "title": "Ohm's Law (Solve I)",
        "latex": r"I = \frac{V}{R}",
        "fields": [
            {"name": "voltage_v", "label": "Voltage V (V)"},
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
        ],
        "compute": _ohms_law_current,
        "substitute": lambda d: f"I = {_fmt(d['voltage_v'])}/{_fmt(d['resistance_ohm'])}",
        "answer_label": "Current I (A)",
        "format_answer": _fmt,
    },
    "ohms-resistance": {
        "title": "Ohm's Law (Solve R)",
        "latex": r"R = \frac{V}{I}",
        "fields": [
            {"name": "voltage_v", "label": "Voltage V (V)"},
            {"name": "current_a", "label": "Current I (A)"},
        ],
        "compute": _ohms_law_resistance,
        "substitute": lambda d: f"R = {_fmt(d['voltage_v'])}/{_fmt(d['current_a'])}",
        "answer_label": "Resistance R (ohm)",
        "format_answer": _fmt,
    },
    "power-vi": {
        "title": "Electrical Power (P=VI)",
        "latex": r"P = VI",
        "fields": [
            {"name": "voltage_v", "label": "Voltage V (V)"},
            {"name": "current_a", "label": "Current I (A)"},
        ],
        "compute": _power_vi,
        "substitute": lambda d: f"P = {_fmt(d['voltage_v'])}x{_fmt(d['current_a'])}",
        "answer_label": "Power P (W)",
        "format_answer": _fmt,
    },
    "power-i2r": {
        "title": "Power (P=I^2R)",
        "latex": r"P = I^2R",
        "fields": [
            {"name": "current_a", "label": "Current I (A)"},
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
        ],
        "compute": _power_i2r,
        "substitute": lambda d: f"P = {_fmt(d['current_a'])}^2x{_fmt(d['resistance_ohm'])}",
        "answer_label": "Power P (W)",
        "format_answer": _fmt,
    },
    "power-v2r": {
        "title": "Power (P=V^2/R)",
        "latex": r"P = \frac{V^2}{R}",
        "fields": [
            {"name": "voltage_v", "label": "Voltage V (V)"},
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
        ],
        "compute": _power_v2r,
        "substitute": lambda d: f"P = {_fmt(d['voltage_v'])}^2/{_fmt(d['resistance_ohm'])}",
        "answer_label": "Power P (W)",
        "format_answer": _fmt,
    },
    "resistors-series": {
        "title": "Resistors in Series",
        "latex": r"R_{eq} = R_1+R_2+R_3",
        "fields": [
            {"name": "r1", "label": "R1 (ohm)", "min": 0},
            {"name": "r2", "label": "R2 (ohm)", "min": 0},
            {"name": "r3", "label": "R3 (ohm)", "min": 0},
        ],
        "compute": _resistors_series,
        "substitute": lambda d: f"Req = {_fmt(d['r1'])}+{_fmt(d['r2'])}+{_fmt(d['r3'])}",
        "answer_label": "Equivalent Resistance (ohm)",
        "format_answer": _fmt,
    },
    "resistors-parallel-two": {
        "title": "Two Resistors in Parallel",
        "latex": r"R_{eq} = \frac{R_1R_2}{R_1+R_2}",
        "fields": [
            {"name": "r1", "label": "R1 (ohm)", "min": 0},
            {"name": "r2", "label": "R2 (ohm)", "min": 0},
        ],
        "compute": _resistors_parallel_two,
        "substitute": lambda d: f"Req = ({_fmt(d['r1'])}x{_fmt(d['r2'])})/({_fmt(d['r1'])}+{_fmt(d['r2'])})",
        "answer_label": "Equivalent Resistance (ohm)",
        "format_answer": _fmt,
    },
    "voltage-divider": {
        "title": "Voltage Divider",
        "latex": r"V_{out}=V_{in}\frac{R_2}{R_1+R_2}",
        "fields": [
            {"name": "vin", "label": "Input voltage Vin (V)"},
            {"name": "r1", "label": "R1 (ohm)", "min": 0},
            {"name": "r2", "label": "R2 (ohm)", "min": 0},
        ],
        "compute": _voltage_divider,
        "substitute": lambda d: f"Vout = {_fmt(d['vin'])}x{_fmt(d['r2'])}/({_fmt(d['r1'])}+{_fmt(d['r2'])})",
        "answer_label": "Output Voltage Vout (V)",
        "format_answer": _fmt,
    },
    "current-divider": {
        "title": "Current Divider (Current in R1)",
        "latex": r"I_1=I_t\frac{R_2}{R_1+R_2}",
        "fields": [
            {"name": "itotal", "label": "Total current It (A)"},
            {"name": "r1", "label": "R1 (ohm)", "min": 0},
            {"name": "r2", "label": "R2 (ohm)", "min": 0},
        ],
        "compute": _current_divider,
        "substitute": lambda d: f"I1 = {_fmt(d['itotal'])}x{_fmt(d['r2'])}/({_fmt(d['r1'])}+{_fmt(d['r2'])})",
        "answer_label": "Branch Current I1 (A)",
        "format_answer": _fmt,
    },
    "charge": {
        "title": "Electric Charge",
        "latex": r"Q = It",
        "fields": [
            {"name": "current_a", "label": "Current I (A)"},
            {"name": "time_s", "label": "Time t (s)", "min": 0},
        ],
        "compute": _charge,
        "substitute": lambda d: f"Q = {_fmt(d['current_a'])}x{_fmt(d['time_s'])}",
        "answer_label": "Charge Q (C)",
        "format_answer": _fmt,
    },
    "energy-power-time": {
        "title": "Electrical Energy",
        "latex": r"E = Pt",
        "fields": [
            {"name": "power_w", "label": "Power P (W)"},
            {"name": "time_s", "label": "Time t (s)", "min": 0},
        ],
        "compute": _energy_power_time,
        "substitute": lambda d: f"E = {_fmt(d['power_w'])}x{_fmt(d['time_s'])}",
        "answer_label": "Energy E (J)",
        "format_answer": _fmt,
    },
    "capacitor-energy": {
        "title": "Capacitor Stored Energy",
        "latex": r"E=\frac{1}{2}CV^2",
        "fields": [
            {"name": "cap_f", "label": "Capacitance C (F)", "min": 0},
            {"name": "voltage_v", "label": "Voltage V (V)"},
        ],
        "compute": _capacitor_energy,
        "substitute": lambda d: f"E=0.5x{_fmt(d['cap_f'])}x{_fmt(d['voltage_v'])}^2",
        "answer_label": "Energy E (J)",
        "format_answer": _fmt,
    },
    "capacitive-reactance": {
        "title": "Capacitive Reactance",
        "latex": r"X_C=\frac{1}{2\pi fC}",
        "fields": [
            {"name": "frequency_hz", "label": "Frequency f (Hz)", "min": 0},
            {"name": "cap_f", "label": "Capacitance C (F)", "min": 0},
        ],
        "compute": _capacitive_reactance,
        "substitute": lambda d: f"Xc=1/(2pix{_fmt(d['frequency_hz'])}x{_fmt(d['cap_f'])})",
        "answer_label": "Reactance Xc (ohm)",
        "format_answer": _fmt,
    },
    "inductive-reactance": {
        "title": "Inductive Reactance",
        "latex": r"X_L=2\pi fL",
        "fields": [
            {"name": "frequency_hz", "label": "Frequency f (Hz)", "min": 0},
            {"name": "ind_h", "label": "Inductance L (H)", "min": 0},
        ],
        "compute": _inductive_reactance,
        "substitute": lambda d: f"Xl=2pix{_fmt(d['frequency_hz'])}x{_fmt(d['ind_h'])}",
        "answer_label": "Reactance Xl (ohm)",
        "format_answer": _fmt,
    },
    "impedance-rlc": {
        "title": "Series RLC Impedance",
        "latex": r"|Z|=\sqrt{R^2+(X_L-X_C)^2}",
        "fields": [
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
            {"name": "frequency_hz", "label": "Frequency f (Hz)", "min": 0},
            {"name": "ind_h", "label": "Inductance L (H)", "min": 0},
            {"name": "cap_f", "label": "Capacitance C (F)", "min": 0},
        ],
        "compute": _impedance_rlc,
        "substitute": lambda d: f"|Z| from R={_fmt(d['resistance_ohm'])}, f={_fmt(d['frequency_hz'])}, L={_fmt(d['ind_h'])}, C={_fmt(d['cap_f'])}",
        "answer_label": "Impedance |Z| (ohm)",
        "format_answer": _fmt,
    },
    "resonant-frequency": {
        "title": "RLC Resonant Frequency",
        "latex": r"f_0=\frac{1}{2\pi\sqrt{LC}}",
        "fields": [
            {"name": "ind_h", "label": "Inductance L (H)", "min": 0},
            {"name": "cap_f", "label": "Capacitance C (F)", "min": 0},
        ],
        "compute": _resonant_frequency,
        "substitute": lambda d: f"f0=1/(2pisqrt({_fmt(d['ind_h'])}x{_fmt(d['cap_f'])}))",
        "answer_label": "Resonant Frequency f0 (Hz)",
        "format_answer": _fmt,
    },
    "rc-time-constant": {
        "title": "RC Time Constant",
        "latex": r"\tau = RC",
        "fields": [
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
            {"name": "cap_f", "label": "Capacitance C (F)", "min": 0},
        ],
        "compute": _rc_time_constant,
        "substitute": lambda d: f"tau={_fmt(d['resistance_ohm'])}x{_fmt(d['cap_f'])}",
        "answer_label": "Time Constant tau (s)",
        "format_answer": _fmt,
    },
    "rl-time-constant": {
        "title": "RL Time Constant",
        "latex": r"\tau = \frac{L}{R}",
        "fields": [
            {"name": "ind_h", "label": "Inductance L (H)", "min": 0},
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
        ],
        "compute": _rl_time_constant,
        "substitute": lambda d: f"tau={_fmt(d['ind_h'])}/{_fmt(d['resistance_ohm'])}",
        "answer_label": "Time Constant tau (s)",
        "format_answer": _fmt,
    },
    "phase-angle-rl": {
        "title": "RL Phase Angle",
        "latex": r"\phi=\tan^{-1}(X_L/R)",
        "fields": [
            {"name": "frequency_hz", "label": "Frequency f (Hz)", "min": 0},
            {"name": "ind_h", "label": "Inductance L (H)", "min": 0},
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
        ],
        "compute": _phase_angle_rl,
        "substitute": lambda d: f"phi=atan(Xl/R) with f={_fmt(d['frequency_hz'])}",
        "answer_label": "Phase Angle phi (deg)",
        "format_answer": _fmt,
    },
    "phase-angle-rc": {
        "title": "RC Phase Angle",
        "latex": r"\phi=-\tan^{-1}(X_C/R)",
        "fields": [
            {"name": "frequency_hz", "label": "Frequency f (Hz)", "min": 0},
            {"name": "cap_f", "label": "Capacitance C (F)", "min": 0},
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
        ],
        "compute": _phase_angle_rc,
        "substitute": lambda d: f"phi=-atan(Xc/R) with f={_fmt(d['frequency_hz'])}",
        "answer_label": "Phase Angle phi (deg)",
        "format_answer": _fmt,
    },
    "real-power": {
        "title": "Real AC Power",
        "latex": r"P=V_{rms}I_{rms}\cos\phi",
        "fields": [
            {"name": "vrms", "label": "Vrms (V)"},
            {"name": "irms", "label": "Irms (A)"},
            {"name": "pf", "label": "Power factor cos(phi)", "min": 0, "max": 1},
        ],
        "compute": _real_power,
        "substitute": lambda d: f"P={_fmt(d['vrms'])}x{_fmt(d['irms'])}x{_fmt(d['pf'])}",
        "answer_label": "Real Power P (W)",
        "format_answer": _fmt,
    },
    "apparent-power": {
        "title": "Apparent AC Power",
        "latex": r"S=V_{rms}I_{rms}",
        "fields": [
            {"name": "vrms", "label": "Vrms (V)"},
            {"name": "irms", "label": "Irms (A)"},
        ],
        "compute": _apparent_power,
        "substitute": lambda d: f"S={_fmt(d['vrms'])}x{_fmt(d['irms'])}",
        "answer_label": "Apparent Power S (VA)",
        "format_answer": _fmt,
    },
    "power-factor": {
        "title": "Power Factor from P and S",
        "latex": r"PF = \frac{P}{S}",
        "fields": [
            {"name": "real_w", "label": "Real power P (W)"},
            {"name": "apparent_va", "label": "Apparent power S (VA)", "min": 0},
        ],
        "compute": _power_factor,
        "substitute": lambda d: f"PF={_fmt(d['real_w'])}/{_fmt(d['apparent_va'])}",
        "answer_label": "Power Factor",
        "format_answer": _fmt,
    },
    "transformer-vout": {
        "title": "Transformer Voltage Ratio",
        "latex": r"\frac{V_s}{V_p}=\frac{N_s}{N_p}",
        "fields": [
            {"name": "v_primary", "label": "Primary voltage Vp (V)"},
            {"name": "n_primary", "label": "Primary turns Np", "min": 1},
            {"name": "n_secondary", "label": "Secondary turns Ns", "min": 1},
        ],
        "compute": _transformer_ratio_vout,
        "substitute": lambda d: f"Vs={_fmt(d['v_primary'])}x{_fmt(d['n_secondary'])}/{_fmt(d['n_primary'])}",
        "answer_label": "Secondary Voltage Vs (V)",
        "format_answer": _fmt,
    },
    "transformer-iout": {
        "title": "Transformer Current Ratio",
        "latex": r"\frac{I_s}{I_p}=\frac{N_p}{N_s}",
        "fields": [
            {"name": "i_primary", "label": "Primary current Ip (A)"},
            {"name": "n_primary", "label": "Primary turns Np", "min": 1},
            {"name": "n_secondary", "label": "Secondary turns Ns", "min": 1},
        ],
        "compute": _transformer_ratio_iout,
        "substitute": lambda d: f"Is={_fmt(d['i_primary'])}x{_fmt(d['n_primary'])}/{_fmt(d['n_secondary'])}",
        "answer_label": "Secondary Current Is (A)",
        "format_answer": _fmt,
    },
    "diode-shockley": {
        "title": "Diode Shockley Current",
        "latex": r"I=I_s\left(e^{V/(nV_T)}-1\right)",
        "fields": [
            {"name": "is_a", "label": "Saturation current Is (A)", "min": 0},
            {"name": "voltage_v", "label": "Diode voltage Vd (V)"},
            {"name": "n", "label": "Ideality factor n", "min": 0},
            {"name": "vt", "label": "Thermal voltage Vt (V)", "min": 0},
        ],
        "compute": _diode_current_shockley,
        "substitute": lambda d: f"I=Is(exp(V/(nVt))-1) with Is={_fmt(d['is_a'])}",
        "answer_label": "Diode Current I (A)",
        "format_answer": _fmt,
    },
    "led-resistor": {
        "title": "LED Series Resistor",
        "latex": r"R=\frac{V_s-V_f}{I_{LED}}",
        "fields": [
            {"name": "supply_v", "label": "Supply voltage Vs (V)"},
            {"name": "led_vf", "label": "LED forward voltage Vf (V)"},
            {"name": "led_current_a", "label": "LED current I (A)", "min": 0},
        ],
        "compute": _led_resistor,
        "substitute": lambda d: f"R=({_fmt(d['supply_v'])}-{_fmt(d['led_vf'])})/{_fmt(d['led_current_a'])}",
        "answer_label": "Series Resistor R (ohm)",
        "format_answer": _fmt,
    },
    "cutoff-rc": {
        "title": "RC Cutoff Frequency",
        "latex": r"f_c=\frac{1}{2\pi RC}",
        "fields": [
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
            {"name": "cap_f", "label": "Capacitance C (F)", "min": 0},
        ],
        "compute": _cutoff_frequency_rc,
        "substitute": lambda d: f"fc=1/(2pix{_fmt(d['resistance_ohm'])}x{_fmt(d['cap_f'])})",
        "answer_label": "Cutoff Frequency fc (Hz)",
        "format_answer": _fmt,
    },
    "cutoff-rl": {
        "title": "RL Cutoff Frequency",
        "latex": r"f_c=\frac{R}{2\pi L}",
        "fields": [
            {"name": "resistance_ohm", "label": "Resistance R (ohm)", "min": 0},
            {"name": "ind_h", "label": "Inductance L (H)", "min": 0},
        ],
        "compute": _cutoff_frequency_rl,
        "substitute": lambda d: f"fc={_fmt(d['resistance_ohm'])}/(2pix{_fmt(d['ind_h'])})",
        "answer_label": "Cutoff Frequency fc (Hz)",
        "format_answer": _fmt,
    },
    "electric-field": {
        "title": "Electric Field Strength",
        "latex": r"E=\frac{V}{d}",
        "fields": [
            {"name": "voltage_v", "label": "Voltage V (V)"},
            {"name": "distance_m", "label": "Distance d (m)", "min": 0},
        ],
        "compute": _electric_field,
        "substitute": lambda d: f"E={_fmt(d['voltage_v'])}/{_fmt(d['distance_m'])}",
        "answer_label": "Electric Field E (V/m)",
        "format_answer": _fmt,
    },
    "parallel-plate-capacitance": {
        "title": "Parallel Plate Capacitance",
        "latex": r"C=\epsilon_r\epsilon_0\frac{A}{d}",
        "fields": [
            {"name": "epsilon_r", "label": "Relative permittivity eps_r", "min": 1},
            {"name": "area_m2", "label": "Plate area A (m^2)", "min": 0},
            {"name": "distance_m", "label": "Plate distance d (m)", "min": 0},
        ],
        "compute": _capacitance_parallel_plate,
        "substitute": lambda d: f"C={_fmt(d['epsilon_r'])}xeps0x{_fmt(d['area_m2'])}/{_fmt(d['distance_m'])}",
        "answer_label": "Capacitance C (F)",
        "format_answer": _fmt,
    },
    "inductor-energy": {
        "title": "Inductor Stored Energy",
        "latex": r"E=\frac{1}{2}LI^2",
        "fields": [
            {"name": "ind_h", "label": "Inductance L (H)", "min": 0},
            {"name": "current_a", "label": "Current I (A)"},
        ],
        "compute": _inductor_energy,
        "substitute": lambda d: f"E=0.5x{_fmt(d['ind_h'])}x{_fmt(d['current_a'])}^2",
        "answer_label": "Energy E (J)",
        "format_answer": _fmt,
    },
}

ELECTRONICS_FORMULA_GROUPS = [
    {
        "title": "DC Circuits",
        "slugs": [
            "ohms-voltage",
            "ohms-current",
            "ohms-resistance",
            "power-vi",
            "power-i2r",
            "power-v2r",
            "resistors-series",
            "resistors-parallel-two",
            "voltage-divider",
            "current-divider",
            "charge",
            "energy-power-time",
        ],
    },
    {
        "title": "AC and Reactive Circuits",
        "slugs": [
            "capacitor-energy",
            "capacitive-reactance",
            "inductive-reactance",
            "impedance-rlc",
            "resonant-frequency",
            "rc-time-constant",
            "rl-time-constant",
            "phase-angle-rl",
            "phase-angle-rc",
            "real-power",
            "apparent-power",
            "power-factor",
            "cutoff-rc",
            "cutoff-rl",
        ],
    },
    {
        "title": "Components and Fields",
        "slugs": [
            "transformer-vout",
            "transformer-iout",
            "diode-shockley",
            "led-resistor",
            "electric-field",
            "parallel-plate-capacitance",
            "inductor-energy",
        ],
    },
]

ELECTRONICS_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in ELECTRONICS_FORMULAS.items()
}
