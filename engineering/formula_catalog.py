from math import pi


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    return f"{value:.10g}"


def _nonzero(value, label):
    if abs(value) < 1e-12:
        raise ValueError(f"{label} must not be zero.")


def _positive(value, label):
    if value <= 0:
        raise ValueError(f"{label} must be greater than 0.")


def _stress(d):
    _nonzero(d["area"], "Area")
    return d["force"] / d["area"]


def _strain(d):
    _nonzero(d["original_length"], "Original length")
    return d["delta_length"] / d["original_length"]


def _youngs_modulus(d):
    _nonzero(d["strain"], "Strain")
    return d["stress"] / d["strain"]


def _bending_stress(d):
    _nonzero(d["I"], "Second moment of area I")
    return d["M"] * d["c"] / d["I"]


def _torsional_shear(d):
    _nonzero(d["J"], "Polar moment of inertia J")
    return d["T"] * d["r"] / d["J"]


def _pressure(d):
    _nonzero(d["area"], "Area")
    return d["force"] / d["area"]


def _hydraulic_power(d):
    return d["rho"] * d["g"] * d["Q"] * d["H"]


def _efficiency(d):
    _nonzero(d["input"], "Input power/value")
    return d["output"] / d["input"] * 100


def _ohms_v(d):
    return d["I"] * d["R"]


def _ohms_i(d):
    _nonzero(d["R"], "Resistance")
    return d["V"] / d["R"]


def _ohms_r(d):
    _nonzero(d["I"], "Current")
    return d["V"] / d["I"]


def _power_dc(d):
    return d["V"] * d["I"]


def _energy_kwh(d):
    return d["P_kw"] * d["t_h"]


def _voltage_divider(d):
    _nonzero(d["R1"] + d["R2"], "R1+R2")
    return d["Vin"] * d["R2"] / (d["R1"] + d["R2"])


def _capacitor_energy(d):
    return 0.5 * d["C"] * d["V"] ** 2


def _inductor_energy(d):
    return 0.5 * d["L"] * d["I"] ** 2


def _thermal_conduction(d):
    _nonzero(d["L"], "Thickness L")
    return d["k"] * d["A"] * d["dT"] / d["L"]


def _convection(d):
    return d["h"] * d["A"] * d["dT"]


def _reynolds(d):
    _nonzero(d["mu"], "Dynamic viscosity mu")
    return d["rho"] * d["v"] * d["D"] / d["mu"]


def _mach(d):
    _nonzero(d["a"], "Speed of sound a")
    return d["v"] / d["a"]


def _flow_rate(d):
    return d["A"] * d["v"]


def _dynamic_pressure(d):
    return 0.5 * d["rho"] * d["v"] ** 2


def _beam_deflection_cantilever(d):
    _nonzero(d["E"], "Elastic modulus E")
    _nonzero(d["I"], "Second moment I")
    return d["P"] * d["L"] ** 3 / (3 * d["E"] * d["I"])


def _beam_deflection_simply(d):
    _nonzero(d["E"], "Elastic modulus E")
    _nonzero(d["I"], "Second moment I")
    return d["P"] * d["L"] ** 3 / (48 * d["E"] * d["I"])


def _slope_percent(d):
    _nonzero(d["run"], "Run")
    return d["rise"] / d["run"] * 100


def _concrete_volume(d):
    return d["L"] * d["W"] * d["H"]


def _unit_weight(d):
    _nonzero(d["V"], "Volume")
    return d["W"] / d["V"]


def _safety_factor(d):
    _nonzero(d["working_stress"], "Working stress")
    return d["ultimate_strength"] / d["working_stress"]


def _gear_ratio(d):
    _nonzero(d["driving_teeth"], "Driving teeth")
    return d["driven_teeth"] / d["driving_teeth"]


def _mechanical_advantage(d):
    _nonzero(d["input_force"], "Input force")
    return d["output_force"] / d["input_force"]


def _rpm_from_cutting_speed(d):
    _nonzero(d["diameter_mm"], "Diameter")
    return (1000 * d["cutting_speed_m_min"]) / (pi * d["diameter_mm"])


def _mrr(d):
    return d["width_mm"] * d["depth_mm"] * d["feed_mm_min"]


def _specific_energy(d):
    _nonzero(d["mrr_mm3_min"], "Material removal rate")
    return d["power_w"] / d["mrr_mm3_min"]


def _battery_life(d):
    _nonzero(d["load_current_a"], "Load current")
    return d["capacity_ah"] / d["load_current_a"]


ENGINEERING_FORMULAS = {
    "stress": {"title": "Stress", "latex": r"sigma = F/A", "fields": [{"name": "force", "label": "Force F"}, {"name": "area", "label": "Area A"}], "compute": _stress, "substitute": lambda d: "sigma = F/A", "answer_label": "sigma", "format_answer": _fmt},
    "strain": {"title": "Strain", "latex": r"epsilon = Delta L/L0", "fields": [{"name": "delta_length", "label": "Delta L"}, {"name": "original_length", "label": "Original length L0"}], "compute": _strain, "substitute": lambda d: "epsilon = DeltaL/L0", "answer_label": "epsilon", "format_answer": _fmt},
    "youngs-modulus": {"title": "Young's Modulus", "latex": r"E = sigma/epsilon", "fields": [{"name": "stress", "label": "Stress sigma"}, {"name": "strain", "label": "Strain epsilon"}], "compute": _youngs_modulus, "substitute": lambda d: "E = stress/strain", "answer_label": "E", "format_answer": _fmt},
    "bending-stress": {"title": "Bending Stress", "latex": r"sigma = Mc/I", "fields": [{"name": "M", "label": "Moment M"}, {"name": "c", "label": "Distance c"}, {"name": "I", "label": "Second moment I"}], "compute": _bending_stress, "substitute": lambda d: "sigma = M*c/I", "answer_label": "sigma", "format_answer": _fmt},
    "torsional-shear-stress": {"title": "Torsional Shear Stress", "latex": r"tau = Tr/J", "fields": [{"name": "T", "label": "Torque T"}, {"name": "r", "label": "Radius r"}, {"name": "J", "label": "Polar moment J"}], "compute": _torsional_shear, "substitute": lambda d: "tau = T*r/J", "answer_label": "tau", "format_answer": _fmt},
    "pressure": {"title": "Pressure", "latex": r"p = F/A", "fields": [{"name": "force", "label": "Force F"}, {"name": "area", "label": "Area A"}], "compute": _pressure, "substitute": lambda d: "p = F/A", "answer_label": "p", "format_answer": _fmt},
    "hydraulic-power": {"title": "Hydraulic Power", "latex": r"P = rho g Q H", "fields": [{"name": "rho", "label": "Density rho"}, {"name": "g", "label": "g"}, {"name": "Q", "label": "Flow rate Q"}, {"name": "H", "label": "Head H"}], "compute": _hydraulic_power, "substitute": lambda d: "P = rho*g*Q*H", "answer_label": "P", "format_answer": _fmt},
    "efficiency": {"title": "Efficiency", "latex": r"eta = Output/Input", "fields": [{"name": "output", "label": "Output"}, {"name": "input", "label": "Input"}], "compute": _efficiency, "substitute": lambda d: "eta = output/input", "answer_label": "eta", "format_answer": lambda v: f"{_fmt(v)} %"},
    "ohms-law-voltage": {"title": "Ohm's Law (Voltage)", "latex": r"V = IR", "fields": [{"name": "I", "label": "Current I"}, {"name": "R", "label": "Resistance R"}], "compute": _ohms_v, "substitute": lambda d: "V = I*R", "answer_label": "V", "format_answer": _fmt},
    "ohms-law-current": {"title": "Ohm's Law (Current)", "latex": r"I = V/R", "fields": [{"name": "V", "label": "Voltage V"}, {"name": "R", "label": "Resistance R"}], "compute": _ohms_i, "substitute": lambda d: "I = V/R", "answer_label": "I", "format_answer": _fmt},
    "ohms-law-resistance": {"title": "Ohm's Law (Resistance)", "latex": r"R = V/I", "fields": [{"name": "V", "label": "Voltage V"}, {"name": "I", "label": "Current I"}], "compute": _ohms_r, "substitute": lambda d: "R = V/I", "answer_label": "R", "format_answer": _fmt},
    "power-dc": {"title": "Electrical Power (DC)", "latex": r"P = VI", "fields": [{"name": "V", "label": "Voltage V"}, {"name": "I", "label": "Current I"}], "compute": _power_dc, "substitute": lambda d: "P = V*I", "answer_label": "P", "format_answer": _fmt},
    "energy-kwh": {"title": "Energy (kWh)", "latex": r"E = P t", "fields": [{"name": "P_kw", "label": "Power P (kW)"}, {"name": "t_h", "label": "Time t (h)"}], "compute": _energy_kwh, "substitute": lambda d: "E = P*t", "answer_label": "E", "format_answer": _fmt},
    "voltage-divider": {"title": "Voltage Divider", "latex": r"Vout = Vin * R2/(R1+R2)", "fields": [{"name": "Vin", "label": "Input voltage Vin"}, {"name": "R1", "label": "R1"}, {"name": "R2", "label": "R2"}], "compute": _voltage_divider, "substitute": lambda d: "Vout = Vin*R2/(R1+R2)", "answer_label": "Vout", "format_answer": _fmt},
    "capacitor-energy": {"title": "Energy Stored in Capacitor", "latex": r"E = 1/2 C V^2", "fields": [{"name": "C", "label": "Capacitance C"}, {"name": "V", "label": "Voltage V"}], "compute": _capacitor_energy, "substitute": lambda d: "E = 0.5*C*V^2", "answer_label": "E", "format_answer": _fmt},
    "inductor-energy": {"title": "Energy Stored in Inductor", "latex": r"E = 1/2 L I^2", "fields": [{"name": "L", "label": "Inductance L"}, {"name": "I", "label": "Current I"}], "compute": _inductor_energy, "substitute": lambda d: "E = 0.5*L*I^2", "answer_label": "E", "format_answer": _fmt},
    "thermal-conduction-rate": {"title": "Thermal Conduction Rate", "latex": r"Qdot = k A DeltaT / L", "fields": [{"name": "k", "label": "Thermal conductivity k"}, {"name": "A", "label": "Area A"}, {"name": "dT", "label": "Temperature difference DeltaT"}, {"name": "L", "label": "Thickness L"}], "compute": _thermal_conduction, "substitute": lambda d: "Qdot = k*A*dT/L", "answer_label": "Qdot", "format_answer": _fmt},
    "convection-heat-rate": {"title": "Convection Heat Rate", "latex": r"Qdot = h A DeltaT", "fields": [{"name": "h", "label": "Convection coefficient h"}, {"name": "A", "label": "Area A"}, {"name": "dT", "label": "Temperature difference DeltaT"}], "compute": _convection, "substitute": lambda d: "Qdot = h*A*dT", "answer_label": "Qdot", "format_answer": _fmt},
    "reynolds-number": {"title": "Reynolds Number", "latex": r"Re = rho v D / mu", "fields": [{"name": "rho", "label": "Density rho"}, {"name": "v", "label": "Velocity v"}, {"name": "D", "label": "Characteristic length D"}, {"name": "mu", "label": "Dynamic viscosity mu"}], "compute": _reynolds, "substitute": lambda d: "Re = rho*v*D/mu", "answer_label": "Re", "format_answer": _fmt},
    "mach-number": {"title": "Mach Number", "latex": r"M = v/a", "fields": [{"name": "v", "label": "Object speed v"}, {"name": "a", "label": "Speed of sound a"}], "compute": _mach, "substitute": lambda d: "M = v/a", "answer_label": "Mach", "format_answer": _fmt},
    "flow-rate": {"title": "Volumetric Flow Rate", "latex": r"Q = A v", "fields": [{"name": "A", "label": "Area A"}, {"name": "v", "label": "Velocity v"}], "compute": _flow_rate, "substitute": lambda d: "Q = A*v", "answer_label": "Q", "format_answer": _fmt},
    "dynamic-pressure": {"title": "Dynamic Pressure", "latex": r"q = 1/2 rho v^2", "fields": [{"name": "rho", "label": "Density rho"}, {"name": "v", "label": "Velocity v"}], "compute": _dynamic_pressure, "substitute": lambda d: "q = 0.5*rho*v^2", "answer_label": "q", "format_answer": _fmt},
    "cantilever-deflection-end-load": {"title": "Cantilever Deflection (End Load)", "latex": r"delta = P L^3 / (3 E I)", "fields": [{"name": "P", "label": "Load P"}, {"name": "L", "label": "Length L"}, {"name": "E", "label": "Elastic modulus E"}, {"name": "I", "label": "Second moment I"}], "compute": _beam_deflection_cantilever, "substitute": lambda d: "delta = P*L^3/(3*E*I)", "answer_label": "delta", "format_answer": _fmt},
    "simply-supported-deflection-center-load": {"title": "Simply Supported Deflection (Center Load)", "latex": r"delta = P L^3 / (48 E I)", "fields": [{"name": "P", "label": "Load P"}, {"name": "L", "label": "Length L"}, {"name": "E", "label": "Elastic modulus E"}, {"name": "I", "label": "Second moment I"}], "compute": _beam_deflection_simply, "substitute": lambda d: "delta = P*L^3/(48*E*I)", "answer_label": "delta", "format_answer": _fmt},
    "slope-percent": {"title": "Slope Percent", "latex": r"Slope(%) = rise/run * 100", "fields": [{"name": "rise", "label": "Rise"}, {"name": "run", "label": "Run"}], "compute": _slope_percent, "substitute": lambda d: "Slope = rise/run*100", "answer_label": "Slope", "format_answer": lambda v: f"{_fmt(v)} %"},
    "concrete-volume": {"title": "Concrete Volume", "latex": r"V = L W H", "fields": [{"name": "L", "label": "Length L"}, {"name": "W", "label": "Width W"}, {"name": "H", "label": "Height H"}], "compute": _concrete_volume, "substitute": lambda d: "V = L*W*H", "answer_label": "V", "format_answer": _fmt},
    "unit-weight": {"title": "Unit Weight", "latex": r"gamma = W/V", "fields": [{"name": "W", "label": "Weight W"}, {"name": "V", "label": "Volume V"}], "compute": _unit_weight, "substitute": lambda d: "gamma = W/V", "answer_label": "gamma", "format_answer": _fmt},
    "factor-of-safety": {"title": "Factor of Safety", "latex": r"FOS = strength/working", "fields": [{"name": "ultimate_strength", "label": "Ultimate strength"}, {"name": "working_stress", "label": "Working stress"}], "compute": _safety_factor, "substitute": lambda d: "FOS = ultimate/working", "answer_label": "FOS", "format_answer": _fmt},
    "gear-ratio": {"title": "Gear Ratio", "latex": r"GR = driven/driving", "fields": [{"name": "driven_teeth", "label": "Driven gear teeth"}, {"name": "driving_teeth", "label": "Driving gear teeth"}], "compute": _gear_ratio, "substitute": lambda d: "GR = driven/driving", "answer_label": "GR", "format_answer": _fmt},
    "mechanical-advantage": {"title": "Mechanical Advantage", "latex": r"MA = Fout/Fin", "fields": [{"name": "output_force", "label": "Output force"}, {"name": "input_force", "label": "Input force"}], "compute": _mechanical_advantage, "substitute": lambda d: "MA = output/input", "answer_label": "MA", "format_answer": _fmt},
    "spindle-rpm-from-cutting-speed": {"title": "Spindle RPM from Cutting Speed", "latex": r"N = 1000V/(pi D)", "fields": [{"name": "cutting_speed_m_min", "label": "Cutting speed V (m/min)"}, {"name": "diameter_mm", "label": "Tool diameter D (mm)"}], "compute": _rpm_from_cutting_speed, "substitute": lambda d: "N = 1000*V/(pi*D)", "answer_label": "RPM", "format_answer": _fmt},
    "material-removal-rate": {"title": "Material Removal Rate", "latex": r"MRR = width * depth * feed", "fields": [{"name": "width_mm", "label": "Width (mm)"}, {"name": "depth_mm", "label": "Depth (mm)"}, {"name": "feed_mm_min", "label": "Feed (mm/min)"}], "compute": _mrr, "substitute": lambda d: "MRR = width*depth*feed", "answer_label": "MRR (mm^3/min)", "format_answer": _fmt},
    "specific-energy-machining": {"title": "Specific Energy in Machining", "latex": r"u = P/MRR", "fields": [{"name": "power_w", "label": "Power P (W)"}, {"name": "mrr_mm3_min", "label": "MRR (mm^3/min)"}], "compute": _specific_energy, "substitute": lambda d: "u = power/MRR", "answer_label": "u", "format_answer": _fmt},
    "battery-life-hours": {"title": "Battery Life (Hours)", "latex": r"t = Capacity/Load", "fields": [{"name": "capacity_ah", "label": "Battery capacity (Ah)"}, {"name": "load_current_a", "label": "Load current (A)"}], "compute": _battery_life, "substitute": lambda d: "t = capacity/load", "answer_label": "Battery life (h)", "format_answer": _fmt},
}


ENGINEERING_FORMULA_GROUPS = [
    {
        "title": "Mechanics & Strength",
        "slugs": [
            "stress",
            "strain",
            "youngs-modulus",
            "bending-stress",
            "torsional-shear-stress",
            "pressure",
            "factor-of-safety",
            "gear-ratio",
            "mechanical-advantage",
        ],
    },
    {
        "title": "Electrical & Electronics",
        "slugs": [
            "efficiency",
            "ohms-law-voltage",
            "ohms-law-current",
            "ohms-law-resistance",
            "power-dc",
            "energy-kwh",
            "voltage-divider",
            "capacitor-energy",
            "inductor-energy",
            "battery-life-hours",
        ],
    },
    {
        "title": "Fluids & Thermal",
        "slugs": [
            "hydraulic-power",
            "thermal-conduction-rate",
            "convection-heat-rate",
            "reynolds-number",
            "mach-number",
            "flow-rate",
            "dynamic-pressure",
        ],
    },
    {
        "title": "Structures & Civil",
        "slugs": [
            "cantilever-deflection-end-load",
            "simply-supported-deflection-center-load",
            "slope-percent",
            "concrete-volume",
            "unit-weight",
        ],
    },
    {
        "title": "Manufacturing",
        "slugs": [
            "spindle-rpm-from-cutting-speed",
            "material-removal-rate",
            "specific-energy-machining",
        ],
    },
]


ENGINEERING_FORMULA_DESCRIPTIONS = {
    "stress": "Compute force intensity over a loaded area.",
    "strain": "Measure deformation relative to original length.",
    "youngs-modulus": "Relate stress to strain in elastic materials.",
    "bending-stress": "Find bending stress from moment and section geometry.",
    "torsional-shear-stress": "Find shaft shear stress caused by torque.",
    "pressure": "Compute applied force per unit area.",
    "hydraulic-power": "Estimate power in a fluid system from head and flow.",
    "efficiency": "Measure output as a percentage of input.",
    "ohms-law-voltage": "Find voltage from current and resistance.",
    "ohms-law-current": "Find current from voltage and resistance.",
    "ohms-law-resistance": "Find resistance from voltage and current.",
    "power-dc": "Compute electrical power in a DC circuit.",
    "energy-kwh": "Estimate energy usage from power and operating time.",
    "voltage-divider": "Find the output voltage across a resistor divider.",
    "capacitor-energy": "Compute stored energy in a charged capacitor.",
    "inductor-energy": "Compute stored energy in a current-carrying inductor.",
    "thermal-conduction-rate": "Estimate heat transfer through a solid layer.",
    "convection-heat-rate": "Estimate heat transfer by convection.",
    "reynolds-number": "Classify flow regime from inertia and viscosity.",
    "mach-number": "Compare object speed to local speed of sound.",
    "flow-rate": "Compute volumetric flow from area and velocity.",
    "dynamic-pressure": "Find kinetic pressure from fluid density and speed.",
    "cantilever-deflection-end-load": "Estimate end deflection of a cantilever beam.",
    "simply-supported-deflection-center-load": "Estimate center deflection of a simply supported beam.",
    "slope-percent": "Convert rise and run into percent grade.",
    "concrete-volume": "Compute concrete volume from length, width, and height.",
    "unit-weight": "Find weight per unit volume of a material.",
    "factor-of-safety": "Compare ultimate strength to working stress.",
    "gear-ratio": "Relate driven and driving gear tooth counts.",
    "mechanical-advantage": "Compare output force to input force.",
    "spindle-rpm-from-cutting-speed": "Convert cutting speed and tool size into spindle RPM.",
    "material-removal-rate": "Estimate how quickly material is removed in machining.",
    "specific-energy-machining": "Measure power required per unit removal rate.",
    "battery-life-hours": "Estimate battery runtime from capacity and load current.",
}
