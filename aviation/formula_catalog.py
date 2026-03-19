import math


G = 9.81
R_AIR = 287.05
GAMMA_AIR = 1.4


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _positive(value, label):
    if value <= 0:
        raise ValueError(f"{label} must be greater than 0.")


def _density(d):
    _positive(d["temperature_k"], "Temperature")
    return d["pressure_pa"] / (R_AIR * d["temperature_k"])


def _dynamic_pressure(d):
    return 0.5 * d["rho"] * d["v"] ** 2


def _lift_force(d):
    return 0.5 * d["rho"] * d["v"] ** 2 * d["wing_area"] * d["cl"]


def _drag_force(d):
    return 0.5 * d["rho"] * d["v"] ** 2 * d["wing_area"] * d["cd"]


def _stall_speed(d):
    _positive(d["rho"], "Air density")
    _positive(d["wing_area"], "Wing area")
    _positive(d["cl_max"], "CLmax")
    return math.sqrt((2 * d["weight_n"]) / (d["rho"] * d["wing_area"] * d["cl_max"]))


def _lift_coefficient(d):
    _positive(d["rho"], "Air density")
    _positive(d["v"], "Airspeed")
    _positive(d["wing_area"], "Wing area")
    return (2 * d["lift_n"]) / (d["rho"] * d["v"] ** 2 * d["wing_area"])


def _drag_coefficient(d):
    _positive(d["rho"], "Air density")
    _positive(d["v"], "Airspeed")
    _positive(d["wing_area"], "Wing area")
    return (2 * d["drag_n"]) / (d["rho"] * d["v"] ** 2 * d["wing_area"])


def _best_glide_ratio(d):
    _positive(d["cd"], "Drag coefficient")
    return d["cl"] / d["cd"]


def _rate_of_climb(d):
    _positive(d["weight_n"], "Weight")
    return (d["power_available_w"] - d["power_required_w"]) / d["weight_n"]


def _turn_radius(d):
    _positive(d["bank_deg"], "Bank angle")
    bank_rad = math.radians(d["bank_deg"])
    tan_bank = math.tan(bank_rad)
    _positive(tan_bank, "tan(bank angle)")
    return d["v"] ** 2 / (G * tan_bank)


def _turn_rate_deg_s(d):
    _positive(d["v"], "Airspeed")
    bank_rad = math.radians(d["bank_deg"])
    return math.degrees(G * math.tan(bank_rad) / d["v"])


def _load_factor(d):
    bank_rad = math.radians(d["bank_deg"])
    cos_bank = math.cos(bank_rad)
    _positive(cos_bank, "cos(bank angle)")
    return 1 / cos_bank


def _thrust_to_weight(d):
    _positive(d["weight_n"], "Weight")
    return d["thrust_n"] / d["weight_n"]


def _wing_loading(d):
    _positive(d["wing_area"] , "Wing area")
    return d["weight_n"] / d["wing_area"]


def _power_required(d):
    return d["drag_n"] * d["v"]


def _propulsive_efficiency(d):
    _positive(d["shaft_power_w"], "Shaft power")
    return (d["thrust_n"] * d["v"] / d["shaft_power_w"]) * 100


def _specific_fuel_consumption(d):
    _positive(d["thrust_n"], "Thrust")
    return d["fuel_flow_kg_s"] / d["thrust_n"]


def _breguet_range_jet(d):
    _positive(d["sfc_1_s"], "SFC")
    _positive(d["ld"], "L/D")
    _positive(d["wi"], "Initial weight")
    _positive(d["wf"], "Final weight")
    if d["wi"] <= d["wf"]:
        raise ValueError("Initial weight must be greater than final weight.")
    return (d["v"] / d["sfc_1_s"]) * d["ld"] * math.log(d["wi"] / d["wf"])


def _breguet_endurance_prop(d):
    _positive(d["cp_1_s"], "Power-specific fuel consumption")
    _positive(d["ld"], "L/D")
    _positive(d["eta_p"], "Propulsive efficiency")
    _positive(d["wi"], "Initial weight")
    _positive(d["wf"], "Final weight")
    if d["wi"] <= d["wf"]:
        raise ValueError("Initial weight must be greater than final weight.")
    return (d["eta_p"] / d["cp_1_s"]) * d["ld"] * math.log(d["wi"] / d["wf"])


def _ground_speed(d):
    return d["true_airspeed"] + d["tailwind"]


def _mach_number(d):
    _positive(d["temperature_k"], "Temperature")
    a = math.sqrt(GAMMA_AIR * R_AIR * d["temperature_k"])
    _positive(a, "Speed of sound")
    return d["v"] / a


def _speed_of_sound(d):
    _positive(d["temperature_k"], "Temperature")
    return math.sqrt(GAMMA_AIR * R_AIR * d["temperature_k"])


def _isa_temperature(d):
    return 288.15 - 0.0065 * d["altitude_m"]


def _isa_pressure(d):
    temp = 288.15 - 0.0065 * d["altitude_m"]
    _positive(temp, "ISA layer temperature")
    return 101325 * (temp / 288.15) ** 5.25588


def _crosswind_component(d):
    return d["wind_speed"] * math.sin(math.radians(d["runway_angle_diff_deg"]))


def _headwind_component(d):
    return d["wind_speed"] * math.cos(math.radians(d["runway_angle_diff_deg"]))


def _takeoff_distance_simple(d):
    _positive(d["acceleration"], "Acceleration")
    return d["liftoff_speed"] ** 2 / (2 * d["acceleration"])


AVIATION_FORMULAS = {
    "air-density": {
        "title": "Air Density (Ideal Gas)",
        "latex": r"\rho = \frac{p}{RT}",
        "fields": [
            {"name": "pressure_pa", "label": "Pressure p (Pa)", "min": 0},
            {"name": "temperature_k", "label": "Temperature T (K)", "min": 0},
        ],
        "compute": _density,
        "substitute": lambda d: f"rho = {_fmt(d['pressure_pa'])}/(287.05x{_fmt(d['temperature_k'])})",
        "answer_label": "Air Density rho (kg/m^3)",
        "format_answer": _fmt,
    },
    "dynamic-pressure": {
        "title": "Dynamic Pressure",
        "latex": r"q = \frac{1}{2}\rho V^2",
        "fields": [
            {"name": "rho", "label": "Air density rho (kg/m^3)", "min": 0},
            {"name": "v", "label": "Airspeed V (m/s)", "min": 0},
        ],
        "compute": _dynamic_pressure,
        "substitute": lambda d: f"q = 0.5x{_fmt(d['rho'])}x{_fmt(d['v'])}^2",
        "answer_label": "Dynamic Pressure q (Pa)",
        "format_answer": _fmt,
    },
    "lift-force": {
        "title": "Lift Force",
        "latex": r"L = \frac{1}{2}\rho V^2 S C_L",
        "fields": [
            {"name": "rho", "label": "Air density rho (kg/m^3)", "min": 0},
            {"name": "v", "label": "Airspeed V (m/s)", "min": 0},
            {"name": "wing_area", "label": "Wing area S (m^2)", "min": 0},
            {"name": "cl", "label": "Lift coefficient CL", "min": 0},
        ],
        "compute": _lift_force,
        "substitute": lambda d: f"L = 0.5x{_fmt(d['rho'])}x{_fmt(d['v'])}^2x{_fmt(d['wing_area'])}x{_fmt(d['cl'])}",
        "answer_label": "Lift L (N)",
        "format_answer": _fmt,
    },
    "drag-force": {
        "title": "Drag Force",
        "latex": r"D = \frac{1}{2}\rho V^2 S C_D",
        "fields": [
            {"name": "rho", "label": "Air density rho (kg/m^3)", "min": 0},
            {"name": "v", "label": "Airspeed V (m/s)", "min": 0},
            {"name": "wing_area", "label": "Wing area S (m^2)", "min": 0},
            {"name": "cd", "label": "Drag coefficient CD", "min": 0},
        ],
        "compute": _drag_force,
        "substitute": lambda d: f"D = 0.5x{_fmt(d['rho'])}x{_fmt(d['v'])}^2x{_fmt(d['wing_area'])}x{_fmt(d['cd'])}",
        "answer_label": "Drag D (N)",
        "format_answer": _fmt,
    },
    "stall-speed": {
        "title": "Stall Speed",
        "latex": r"V_s = \sqrt{\frac{2W}{\rho S C_{Lmax}}}",
        "fields": [
            {"name": "weight_n", "label": "Weight W (N)", "min": 0},
            {"name": "rho", "label": "Air density rho (kg/m^3)", "min": 0},
            {"name": "wing_area", "label": "Wing area S (m^2)", "min": 0},
            {"name": "cl_max", "label": "CLmax", "min": 0},
        ],
        "compute": _stall_speed,
        "substitute": lambda d: f"Vs = sqrt((2x{_fmt(d['weight_n'])})/({_fmt(d['rho'])}x{_fmt(d['wing_area'])}x{_fmt(d['cl_max'])}))",
        "answer_label": "Stall Speed Vs (m/s)",
        "format_answer": _fmt,
    },
    "lift-coefficient": {
        "title": "Lift Coefficient from Flight Data",
        "latex": r"C_L = \frac{2L}{\rho V^2 S}",
        "fields": [
            {"name": "lift_n", "label": "Lift L (N)"},
            {"name": "rho", "label": "Air density rho (kg/m^3)", "min": 0},
            {"name": "v", "label": "Airspeed V (m/s)", "min": 0},
            {"name": "wing_area", "label": "Wing area S (m^2)", "min": 0},
        ],
        "compute": _lift_coefficient,
        "substitute": lambda d: f"CL = (2x{_fmt(d['lift_n'])})/({_fmt(d['rho'])}x{_fmt(d['v'])}^2x{_fmt(d['wing_area'])})",
        "answer_label": "Lift Coefficient CL",
        "format_answer": _fmt,
    },
    "drag-coefficient": {
        "title": "Drag Coefficient from Flight Data",
        "latex": r"C_D = \frac{2D}{\rho V^2 S}",
        "fields": [
            {"name": "drag_n", "label": "Drag D (N)"},
            {"name": "rho", "label": "Air density rho (kg/m^3)", "min": 0},
            {"name": "v", "label": "Airspeed V (m/s)", "min": 0},
            {"name": "wing_area", "label": "Wing area S (m^2)", "min": 0},
        ],
        "compute": _drag_coefficient,
        "substitute": lambda d: f"CD = (2x{_fmt(d['drag_n'])})/({_fmt(d['rho'])}x{_fmt(d['v'])}^2x{_fmt(d['wing_area'])})",
        "answer_label": "Drag Coefficient CD",
        "format_answer": _fmt,
    },
    "best-glide-ratio": {
        "title": "Best Glide Ratio",
        "latex": r"\frac{L}{D} = \frac{C_L}{C_D}",
        "fields": [
            {"name": "cl", "label": "Lift coefficient CL", "min": 0},
            {"name": "cd", "label": "Drag coefficient CD", "min": 0},
        ],
        "compute": _best_glide_ratio,
        "substitute": lambda d: f"L/D = {_fmt(d['cl'])}/{_fmt(d['cd'])}",
        "answer_label": "Glide Ratio L/D",
        "format_answer": _fmt,
    },
    "rate-of-climb": {
        "title": "Rate of Climb",
        "latex": r"ROC = \frac{P_{avail} - P_{req}}{W}",
        "fields": [
            {"name": "power_available_w", "label": "Power available (W)"},
            {"name": "power_required_w", "label": "Power required (W)"},
            {"name": "weight_n", "label": "Weight W (N)", "min": 0},
        ],
        "compute": _rate_of_climb,
        "substitute": lambda d: f"ROC = ({_fmt(d['power_available_w'])}-{_fmt(d['power_required_w'])})/{_fmt(d['weight_n'])}",
        "answer_label": "Rate of Climb (m/s)",
        "format_answer": _fmt,
    },
    "turn-radius": {
        "title": "Coordinated Turn Radius",
        "latex": r"R = \frac{V^2}{g\tan\phi}",
        "fields": [
            {"name": "v", "label": "True airspeed V (m/s)", "min": 0},
            {"name": "bank_deg", "label": "Bank angle phi (deg)", "min": 1, "max": 89},
        ],
        "compute": _turn_radius,
        "substitute": lambda d: f"R = {_fmt(d['v'])}^2/(9.81xtan({_fmt(d['bank_deg'])}))",
        "answer_label": "Turn Radius R (m)",
        "format_answer": _fmt,
    },
    "turn-rate": {
        "title": "Turn Rate",
        "latex": r"\dot{\psi} = \frac{g\tan\phi}{V}",
        "fields": [
            {"name": "v", "label": "True airspeed V (m/s)", "min": 0},
            {"name": "bank_deg", "label": "Bank angle phi (deg)", "min": 0, "max": 89},
        ],
        "compute": _turn_rate_deg_s,
        "substitute": lambda d: f"turn rate = 9.81xtan({_fmt(d['bank_deg'])})/{_fmt(d['v'])}",
        "answer_label": "Turn Rate (deg/s)",
        "format_answer": _fmt,
    },
    "load-factor-bank": {
        "title": "Load Factor from Bank Angle",
        "latex": r"n = \frac{1}{\cos\phi}",
        "fields": [{"name": "bank_deg", "label": "Bank angle phi (deg)", "min": 0, "max": 89}],
        "compute": _load_factor,
        "substitute": lambda d: f"n = 1/cos({_fmt(d['bank_deg'])})",
        "answer_label": "Load Factor n (g)",
        "format_answer": _fmt,
    },
    "thrust-to-weight": {
        "title": "Thrust-to-Weight Ratio",
        "latex": r"\frac{T}{W}",
        "fields": [
            {"name": "thrust_n", "label": "Thrust T (N)", "min": 0},
            {"name": "weight_n", "label": "Weight W (N)", "min": 0},
        ],
        "compute": _thrust_to_weight,
        "substitute": lambda d: f"T/W = {_fmt(d['thrust_n'])}/{_fmt(d['weight_n'])}",
        "answer_label": "Thrust-to-Weight T/W",
        "format_answer": _fmt,
    },
    "wing-loading": {
        "title": "Wing Loading",
        "latex": r"\frac{W}{S}",
        "fields": [
            {"name": "weight_n", "label": "Weight W (N)", "min": 0},
            {"name": "wing_area", "label": "Wing area S (m^2)", "min": 0},
        ],
        "compute": _wing_loading,
        "substitute": lambda d: f"W/S = {_fmt(d['weight_n'])}/{_fmt(d['wing_area'])}",
        "answer_label": "Wing Loading (N/m^2)",
        "format_answer": _fmt,
    },
    "power-required": {
        "title": "Power Required",
        "latex": r"P = DV",
        "fields": [
            {"name": "drag_n", "label": "Drag D (N)"},
            {"name": "v", "label": "Airspeed V (m/s)", "min": 0},
        ],
        "compute": _power_required,
        "substitute": lambda d: f"P = {_fmt(d['drag_n'])}x{_fmt(d['v'])}",
        "answer_label": "Power Required (W)",
        "format_answer": _fmt,
    },
    "propulsive-efficiency": {
        "title": "Propulsive Efficiency",
        "latex": r"\eta_p = \frac{TV}{P_{shaft}}",
        "fields": [
            {"name": "thrust_n", "label": "Thrust T (N)", "min": 0},
            {"name": "v", "label": "Airspeed V (m/s)", "min": 0},
            {"name": "shaft_power_w", "label": "Shaft power (W)", "min": 0},
        ],
        "compute": _propulsive_efficiency,
        "substitute": lambda d: f"eta_p = ({_fmt(d['thrust_n'])}x{_fmt(d['v'])})/{_fmt(d['shaft_power_w'])}",
        "answer_label": "Propulsive Efficiency (%)",
        "format_answer": _fmt,
    },
    "specific-fuel-consumption": {
        "title": "Specific Fuel Consumption",
        "latex": r"SFC = \frac{\dot{m}_f}{T}",
        "fields": [
            {"name": "fuel_flow_kg_s", "label": "Fuel flow mdot_f (kg/s)", "min": 0},
            {"name": "thrust_n", "label": "Thrust T (N)", "min": 0},
        ],
        "compute": _specific_fuel_consumption,
        "substitute": lambda d: f"SFC = {_fmt(d['fuel_flow_kg_s'])}/{_fmt(d['thrust_n'])}",
        "answer_label": "SFC (kg/(N s))",
        "format_answer": _fmt,
    },
    "breguet-range-jet": {
        "title": "Breguet Range (Jet)",
        "latex": r"R = \frac{V}{c_t}\frac{L}{D}\ln\left(\frac{W_i}{W_f}\right)",
        "fields": [
            {"name": "v", "label": "Cruise speed V (m/s)", "min": 0},
            {"name": "sfc_1_s", "label": "Thrust SFC c_t (1/s)", "min": 0},
            {"name": "ld", "label": "Lift-to-drag L/D", "min": 0},
            {"name": "wi", "label": "Initial weight Wi (N)", "min": 0},
            {"name": "wf", "label": "Final weight Wf (N)", "min": 0},
        ],
        "compute": _breguet_range_jet,
        "substitute": lambda d: f"R = ({_fmt(d['v'])}/{_fmt(d['sfc_1_s'])})x{_fmt(d['ld'])}xln({_fmt(d['wi'])}/{_fmt(d['wf'])})",
        "answer_label": "Range R (m)",
        "format_answer": _fmt,
    },
    "breguet-endurance-prop": {
        "title": "Breguet Endurance (Prop)",
        "latex": r"E = \frac{\eta_p}{c_p}\frac{L}{D}\ln\left(\frac{W_i}{W_f}\right)",
        "fields": [
            {"name": "eta_p", "label": "Propulsive efficiency eta_p", "min": 0},
            {"name": "cp_1_s", "label": "Power SFC c_p (1/s)", "min": 0},
            {"name": "ld", "label": "Lift-to-drag L/D", "min": 0},
            {"name": "wi", "label": "Initial weight Wi (N)", "min": 0},
            {"name": "wf", "label": "Final weight Wf (N)", "min": 0},
        ],
        "compute": _breguet_endurance_prop,
        "substitute": lambda d: f"E = ({_fmt(d['eta_p'])}/{_fmt(d['cp_1_s'])})x{_fmt(d['ld'])}xln({_fmt(d['wi'])}/{_fmt(d['wf'])})",
        "answer_label": "Endurance E (s)",
        "format_answer": _fmt,
    },
    "ground-speed": {
        "title": "Ground Speed with Wind",
        "latex": r"V_g = V_{TAS} + V_{wind}",
        "fields": [
            {"name": "true_airspeed", "label": "True airspeed TAS (m/s)"},
            {"name": "tailwind", "label": "Tailwind (+) / Headwind (-) (m/s)"},
        ],
        "compute": _ground_speed,
        "substitute": lambda d: f"Vg = {_fmt(d['true_airspeed'])}+{_fmt(d['tailwind'])}",
        "answer_label": "Ground Speed Vg (m/s)",
        "format_answer": _fmt,
    },
    "mach-number": {
        "title": "Mach Number",
        "latex": r"M = \frac{V}{a},\quad a=\sqrt{\gamma RT}",
        "fields": [
            {"name": "v", "label": "True airspeed V (m/s)", "min": 0},
            {"name": "temperature_k", "label": "Static temperature T (K)", "min": 0},
        ],
        "compute": _mach_number,
        "substitute": lambda d: f"M = {_fmt(d['v'])}/sqrt(1.4x287.05x{_fmt(d['temperature_k'])})",
        "answer_label": "Mach Number M",
        "format_answer": _fmt,
    },
    "speed-of-sound": {
        "title": "Speed of Sound",
        "latex": r"a=\sqrt{\gamma RT}",
        "fields": [{"name": "temperature_k", "label": "Static temperature T (K)", "min": 0}],
        "compute": _speed_of_sound,
        "substitute": lambda d: f"a = sqrt(1.4x287.05x{_fmt(d['temperature_k'])})",
        "answer_label": "Speed of Sound a (m/s)",
        "format_answer": _fmt,
    },
    "isa-temperature": {
        "title": "ISA Temperature (Troposphere)",
        "latex": r"T = 288.15 - 0.0065h",
        "fields": [{"name": "altitude_m", "label": "Altitude h (m)", "min": 0}],
        "compute": _isa_temperature,
        "substitute": lambda d: f"T = 288.15 - 0.0065x{_fmt(d['altitude_m'])}",
        "answer_label": "ISA Temperature T (K)",
        "format_answer": _fmt,
    },
    "isa-pressure": {
        "title": "ISA Pressure (Troposphere)",
        "latex": r"p = p_0\left(\frac{T}{T_0}\right)^{5.25588}",
        "fields": [{"name": "altitude_m", "label": "Altitude h (m)", "min": 0}],
        "compute": _isa_pressure,
        "substitute": lambda d: f"p = 101325x((288.15-0.0065x{_fmt(d['altitude_m'])})/288.15)^5.25588",
        "answer_label": "ISA Pressure p (Pa)",
        "format_answer": _fmt,
    },
    "crosswind-component": {
        "title": "Crosswind Component",
        "latex": r"V_x = V_w\sin\Delta\theta",
        "fields": [
            {"name": "wind_speed", "label": "Wind speed Vw (m/s)", "min": 0},
            {"name": "runway_angle_diff_deg", "label": "Wind/runway angle diff (deg)", "min": 0, "max": 180},
        ],
        "compute": _crosswind_component,
        "substitute": lambda d: f"Vx = {_fmt(d['wind_speed'])}xsin({_fmt(d['runway_angle_diff_deg'])})",
        "answer_label": "Crosswind Component (m/s)",
        "format_answer": _fmt,
    },
    "headwind-component": {
        "title": "Headwind Component",
        "latex": r"V_h = V_w\cos\Delta\theta",
        "fields": [
            {"name": "wind_speed", "label": "Wind speed Vw (m/s)", "min": 0},
            {"name": "runway_angle_diff_deg", "label": "Wind/runway angle diff (deg)", "min": 0, "max": 180},
        ],
        "compute": _headwind_component,
        "substitute": lambda d: f"Vh = {_fmt(d['wind_speed'])}xcos({_fmt(d['runway_angle_diff_deg'])})",
        "answer_label": "Headwind Component (m/s)",
        "format_answer": _fmt,
    },
    "takeoff-distance-simple": {
        "title": "Takeoff Ground Roll (Simple)",
        "latex": r"s = \frac{V_{LOF}^2}{2a}",
        "fields": [
            {"name": "liftoff_speed", "label": "Liftoff speed V_LOF (m/s)", "min": 0},
            {"name": "acceleration", "label": "Average acceleration a (m/s^2)", "min": 0},
        ],
        "compute": _takeoff_distance_simple,
        "substitute": lambda d: f"s = {_fmt(d['liftoff_speed'])}^2/(2x{_fmt(d['acceleration'])})",
        "answer_label": "Ground Roll s (m)",
        "format_answer": _fmt,
    },
}

AVIATION_FORMULA_GROUPS = [
    {
        "title": "Aerodynamics",
        "slugs": [
            "air-density",
            "dynamic-pressure",
            "lift-force",
            "drag-force",
            "stall-speed",
            "lift-coefficient",
            "drag-coefficient",
            "best-glide-ratio",
        ],
    },
    {
        "title": "Performance",
        "slugs": [
            "rate-of-climb",
            "turn-radius",
            "turn-rate",
            "load-factor-bank",
            "thrust-to-weight",
            "wing-loading",
            "power-required",
            "propulsive-efficiency",
            "specific-fuel-consumption",
            "breguet-range-jet",
            "breguet-endurance-prop",
        ],
    },
    {
        "title": "Atmosphere and Navigation",
        "slugs": [
            "ground-speed",
            "mach-number",
            "speed-of-sound",
            "isa-temperature",
            "isa-pressure",
            "crosswind-component",
            "headwind-component",
            "takeoff-distance-simple",
        ],
    },
]

AVIATION_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in AVIATION_FORMULAS.items()
}
