from math import acos, asin, pi, radians, sin, sqrt


G = 6.67430e-11
K_E = 8.9875517923e9
R_GAS = 8.314462618


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    return f"{value:.10g}"


def _positive(value, name):
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0.")


def _nonzero(value, name):
    if abs(value) < 1e-12:
        raise ValueError(f"{name} must not be zero.")


def _projectile_range(d):
    _positive(d["v0"], "Initial speed")
    _positive(d["g"], "g")
    return d["v0"] ** 2 * sin(radians(2 * d["theta"])) / d["g"]


def _projectile_max_height(d):
    _positive(d["v0"], "Initial speed")
    _positive(d["g"], "g")
    return (d["v0"] ** 2 * (sin(radians(d["theta"])) ** 2)) / (2 * d["g"])


def _snells_theta2(d):
    _positive(d["n1"], "n1")
    _positive(d["n2"], "n2")
    value = d["n1"] * sin(radians(d["theta1"])) / d["n2"]
    if value < -1 or value > 1:
        raise ValueError("No real refraction angle; check inputs for total internal reflection.")
    return asin(value) * 180 / pi


def _mirror_focal_length(d):
    _nonzero(d["u"], "u")
    _nonzero(d["v"], "v")
    return 1 / ((1 / d["u"]) + (1 / d["v"]))


def _law_of_cosines_angle(d):
    _positive(d["a"], "a")
    _positive(d["b"], "b")
    _positive(d["c"], "c")
    if d["a"] + d["b"] <= d["c"] or d["a"] + d["c"] <= d["b"] or d["b"] + d["c"] <= d["a"]:
        raise ValueError("Sides do not form a valid triangle.")
    value = (d["a"] ** 2 + d["b"] ** 2 - d["c"] ** 2) / (2 * d["a"] * d["b"])
    return acos(value) * 180 / pi


PHYSICS_FORMULAS = {
    "speed": {
        "title": "Speed",
        "latex": r"v = \frac{d}{t}",
        "fields": [{"name": "d", "label": "Distance d"}, {"name": "t", "label": "Time t"}],
        "compute": lambda d: d["d"] / d["t"] if abs(d["t"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Time t must not be zero.")),
        "substitute": lambda d: f"v = ({_fmt(d['d'])}) / ({_fmt(d['t'])})",
        "answer_label": "v",
        "format_answer": _fmt,
    },
    "distance": {
        "title": "Distance",
        "latex": r"d = vt",
        "fields": [{"name": "v", "label": "Speed v"}, {"name": "t", "label": "Time t"}],
        "compute": lambda d: d["v"] * d["t"],
        "substitute": lambda d: f"d = ({_fmt(d['v'])}) * ({_fmt(d['t'])})",
        "answer_label": "d",
        "format_answer": _fmt,
    },
    "acceleration": {
        "title": "Acceleration",
        "latex": r"a = \frac{\Delta v}{\Delta t}",
        "fields": [{"name": "dv", "label": "Delta v"}, {"name": "dt", "label": "Delta t"}],
        "compute": lambda d: d["dv"] / d["dt"] if abs(d["dt"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Delta t must not be zero.")),
        "substitute": lambda d: f"a = ({_fmt(d['dv'])}) / ({_fmt(d['dt'])})",
        "answer_label": "a",
        "format_answer": _fmt,
    },
    "newtons-second-law": {
        "title": "Newton's Second Law",
        "latex": r"F = ma",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "a", "label": "Acceleration a"}],
        "compute": lambda d: d["m"] * d["a"],
        "substitute": lambda d: f"F = ({_fmt(d['m'])}) * ({_fmt(d['a'])})",
        "answer_label": "F",
        "format_answer": _fmt,
    },
    "weight": {
        "title": "Weight",
        "latex": r"W = mg",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "g", "label": "g"}],
        "compute": lambda d: d["m"] * d["g"],
        "substitute": lambda d: f"W = ({_fmt(d['m'])}) * ({_fmt(d['g'])})",
        "answer_label": "W",
        "format_answer": _fmt,
    },
    "momentum": {
        "title": "Momentum",
        "latex": r"p = mv",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "v", "label": "Velocity v"}],
        "compute": lambda d: d["m"] * d["v"],
        "substitute": lambda d: f"p = ({_fmt(d['m'])}) * ({_fmt(d['v'])})",
        "answer_label": "p",
        "format_answer": _fmt,
    },
    "impulse": {
        "title": "Impulse",
        "latex": r"J = F\Delta t",
        "fields": [{"name": "F", "label": "Force F"}, {"name": "dt", "label": "Delta t"}],
        "compute": lambda d: d["F"] * d["dt"],
        "substitute": lambda d: f"J = ({_fmt(d['F'])}) * ({_fmt(d['dt'])})",
        "answer_label": "J",
        "format_answer": _fmt,
    },
    "kinetic-energy": {
        "title": "Kinetic Energy",
        "latex": r"KE = \frac{1}{2}mv^2",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "v", "label": "Speed v"}],
        "compute": lambda d: 0.5 * d["m"] * d["v"] ** 2,
        "substitute": lambda d: f"KE = 0.5 * ({_fmt(d['m'])}) * ({_fmt(d['v'])})^2",
        "answer_label": "KE",
        "format_answer": _fmt,
    },
    "potential-energy": {
        "title": "Potential Energy",
        "latex": r"PE = mgh",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "g", "label": "g"}, {"name": "h", "label": "Height h"}],
        "compute": lambda d: d["m"] * d["g"] * d["h"],
        "substitute": lambda d: f"PE = ({_fmt(d['m'])}) * ({_fmt(d['g'])}) * ({_fmt(d['h'])})",
        "answer_label": "PE",
        "format_answer": _fmt,
    },
    "work": {
        "title": "Work",
        "latex": r"W = Fd",
        "fields": [{"name": "F", "label": "Force F"}, {"name": "d", "label": "Displacement d"}],
        "compute": lambda d: d["F"] * d["d"],
        "substitute": lambda d: f"W = ({_fmt(d['F'])}) * ({_fmt(d['d'])})",
        "answer_label": "W",
        "format_answer": _fmt,
    },
    "power": {
        "title": "Power",
        "latex": r"P = \frac{W}{t}",
        "fields": [{"name": "W", "label": "Work W"}, {"name": "t", "label": "Time t"}],
        "compute": lambda d: d["W"] / d["t"] if abs(d["t"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Time t must not be zero.")),
        "substitute": lambda d: f"P = ({_fmt(d['W'])}) / ({_fmt(d['t'])})",
        "answer_label": "P",
        "format_answer": _fmt,
    },
    "pressure": {
        "title": "Pressure",
        "latex": r"p = \frac{F}{A}",
        "fields": [{"name": "F", "label": "Force F"}, {"name": "A", "label": "Area A"}],
        "compute": lambda d: d["F"] / d["A"] if abs(d["A"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Area A must not be zero.")),
        "substitute": lambda d: f"p = ({_fmt(d['F'])}) / ({_fmt(d['A'])})",
        "answer_label": "p",
        "format_answer": _fmt,
    },
    "density": {
        "title": "Density",
        "latex": r"\rho = \frac{m}{V}",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "V", "label": "Volume V"}],
        "compute": lambda d: d["m"] / d["V"] if abs(d["V"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Volume V must not be zero.")),
        "substitute": lambda d: f"rho = ({_fmt(d['m'])}) / ({_fmt(d['V'])})",
        "answer_label": "rho",
        "format_answer": _fmt,
    },
    "buoyant-force": {
        "title": "Buoyant Force",
        "latex": r"F_b = \rho gV",
        "fields": [{"name": "rho", "label": "Fluid density rho"}, {"name": "g", "label": "g"}, {"name": "V", "label": "Displaced volume V"}],
        "compute": lambda d: d["rho"] * d["g"] * d["V"],
        "substitute": lambda d: f"Fb = ({_fmt(d['rho'])}) * ({_fmt(d['g'])}) * ({_fmt(d['V'])})",
        "answer_label": "Fb",
        "format_answer": _fmt,
    },
    "ohms-law-voltage": {
        "title": "Ohm's Law (Voltage)",
        "latex": r"V = IR",
        "fields": [{"name": "I", "label": "Current I"}, {"name": "R", "label": "Resistance R"}],
        "compute": lambda d: d["I"] * d["R"],
        "substitute": lambda d: f"V = ({_fmt(d['I'])}) * ({_fmt(d['R'])})",
        "answer_label": "V",
        "format_answer": _fmt,
    },
    "ohms-law-current": {
        "title": "Ohm's Law (Current)",
        "latex": r"I = \frac{V}{R}",
        "fields": [{"name": "V", "label": "Voltage V"}, {"name": "R", "label": "Resistance R"}],
        "compute": lambda d: d["V"] / d["R"] if abs(d["R"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Resistance R must not be zero.")),
        "substitute": lambda d: f"I = ({_fmt(d['V'])}) / ({_fmt(d['R'])})",
        "answer_label": "I",
        "format_answer": _fmt,
    },
    "ohms-law-resistance": {
        "title": "Ohm's Law (Resistance)",
        "latex": r"R = \frac{V}{I}",
        "fields": [{"name": "V", "label": "Voltage V"}, {"name": "I", "label": "Current I"}],
        "compute": lambda d: d["V"] / d["I"] if abs(d["I"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Current I must not be zero.")),
        "substitute": lambda d: f"R = ({_fmt(d['V'])}) / ({_fmt(d['I'])})",
        "answer_label": "R",
        "format_answer": _fmt,
    },
    "electric-power": {
        "title": "Electric Power",
        "latex": r"P = VI",
        "fields": [{"name": "V", "label": "Voltage V"}, {"name": "I", "label": "Current I"}],
        "compute": lambda d: d["V"] * d["I"],
        "substitute": lambda d: f"P = ({_fmt(d['V'])}) * ({_fmt(d['I'])})",
        "answer_label": "P",
        "format_answer": _fmt,
    },
    "electric-energy": {
        "title": "Electric Energy",
        "latex": r"E = Pt",
        "fields": [{"name": "P", "label": "Power P"}, {"name": "t", "label": "Time t"}],
        "compute": lambda d: d["P"] * d["t"],
        "substitute": lambda d: f"E = ({_fmt(d['P'])}) * ({_fmt(d['t'])})",
        "answer_label": "E",
        "format_answer": _fmt,
    },
    "coulombs-law": {
        "title": "Coulomb's Law",
        "latex": r"F = k\frac{|q_1 q_2|}{r^2}",
        "fields": [{"name": "q1", "label": "Charge q1"}, {"name": "q2", "label": "Charge q2"}, {"name": "r", "label": "Distance r"}],
        "compute": lambda d: K_E * abs(d["q1"] * d["q2"]) / (d["r"] ** 2) if d["r"] > 0 else (_ for _ in ()).throw(ValueError("Distance r must be greater than 0.")),
        "substitute": lambda d: f"F = k * |{_fmt(d['q1'])} * {_fmt(d['q2'])}| / ({_fmt(d['r'])})^2",
        "answer_label": "F",
        "format_answer": _fmt,
    },
    "newtons-law-of-gravitation": {
        "title": "Newton's Law of Gravitation",
        "latex": r"F = G\frac{m_1 m_2}{r^2}",
        "fields": [{"name": "m1", "label": "Mass m1"}, {"name": "m2", "label": "Mass m2"}, {"name": "r", "label": "Distance r"}],
        "compute": lambda d: G * d["m1"] * d["m2"] / (d["r"] ** 2) if d["r"] > 0 else (_ for _ in ()).throw(ValueError("Distance r must be greater than 0.")),
        "substitute": lambda d: f"F = G * ({_fmt(d['m1'])} * {_fmt(d['m2'])}) / ({_fmt(d['r'])})^2",
        "answer_label": "F",
        "format_answer": _fmt,
    },
    "wave-speed": {
        "title": "Wave Speed",
        "latex": r"v = f\lambda",
        "fields": [{"name": "f", "label": "Frequency f"}, {"name": "lam", "label": "Wavelength lambda"}],
        "compute": lambda d: d["f"] * d["lam"],
        "substitute": lambda d: f"v = ({_fmt(d['f'])}) * ({_fmt(d['lam'])})",
        "answer_label": "v",
        "format_answer": _fmt,
    },
    "frequency-from-period": {
        "title": "Frequency from Period",
        "latex": r"f = \frac{1}{T}",
        "fields": [{"name": "T", "label": "Period T"}],
        "compute": lambda d: 1 / d["T"] if abs(d["T"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Period T must not be zero.")),
        "substitute": lambda d: f"f = 1 / ({_fmt(d['T'])})",
        "answer_label": "f",
        "format_answer": _fmt,
    },
    "period-from-frequency": {
        "title": "Period from Frequency",
        "latex": r"T = \frac{1}{f}",
        "fields": [{"name": "f", "label": "Frequency f"}],
        "compute": lambda d: 1 / d["f"] if abs(d["f"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Frequency f must not be zero.")),
        "substitute": lambda d: f"T = 1 / ({_fmt(d['f'])})",
        "answer_label": "T",
        "format_answer": _fmt,
    },
    "snells-law-theta2": {
        "title": "Snell's Law (Find theta2)",
        "latex": r"n_1\sin\theta_1 = n_2\sin\theta_2",
        "fields": [{"name": "n1", "label": "Refractive index n1"}, {"name": "theta1", "label": "theta1 (deg)"}, {"name": "n2", "label": "Refractive index n2"}],
        "compute": _snells_theta2,
        "substitute": lambda d: f"theta2 = asin((n1*sin(theta1))/n2)",
        "answer_label": "theta2",
        "format_answer": lambda v: f"{_fmt(v)} deg",
    },
    "mirror-focal-length": {
        "title": "Mirror Formula (Focal Length)",
        "latex": r"\frac{1}{f} = \frac{1}{u} + \frac{1}{v}",
        "fields": [{"name": "u", "label": "Object distance u"}, {"name": "v", "label": "Image distance v"}],
        "compute": _mirror_focal_length,
        "substitute": lambda d: "f = 1 / (1/u + 1/v)",
        "answer_label": "f",
        "format_answer": _fmt,
    },
    "heat-energy": {
        "title": "Heat Energy",
        "latex": r"Q = mc\Delta T",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "c", "label": "Specific heat c"}, {"name": "dT", "label": "Delta T"}],
        "compute": lambda d: d["m"] * d["c"] * d["dT"],
        "substitute": lambda d: f"Q = ({_fmt(d['m'])}) * ({_fmt(d['c'])}) * ({_fmt(d['dT'])})",
        "answer_label": "Q",
        "format_answer": _fmt,
    },
    "ideal-gas-pressure": {
        "title": "Ideal Gas Law (Pressure)",
        "latex": r"P = \frac{nRT}{V}",
        "fields": [{"name": "n", "label": "Moles n"}, {"name": "T", "label": "Temperature T"}, {"name": "V", "label": "Volume V"}],
        "compute": lambda d: d["n"] * R_GAS * d["T"] / d["V"] if abs(d["V"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Volume V must not be zero.")),
        "substitute": lambda d: f"P = (n*R*T)/V with R={_fmt(R_GAS)}",
        "answer_label": "P",
        "format_answer": _fmt,
    },
    "thermal-expansion": {
        "title": "Linear Thermal Expansion",
        "latex": r"\Delta L = \alpha L_0 \Delta T",
        "fields": [{"name": "alpha", "label": "Coefficient alpha"}, {"name": "L0", "label": "Initial length L0"}, {"name": "dT", "label": "Delta T"}],
        "compute": lambda d: d["alpha"] * d["L0"] * d["dT"],
        "substitute": lambda d: f"Delta L = ({_fmt(d['alpha'])})*({_fmt(d['L0'])})*({_fmt(d['dT'])})",
        "answer_label": "Delta L",
        "format_answer": _fmt,
    },
    "centripetal-acceleration": {
        "title": "Centripetal Acceleration",
        "latex": r"a_c = \frac{v^2}{r}",
        "fields": [{"name": "v", "label": "Speed v"}, {"name": "r", "label": "Radius r"}],
        "compute": lambda d: d["v"] ** 2 / d["r"] if d["r"] > 0 else (_ for _ in ()).throw(ValueError("Radius r must be greater than 0.")),
        "substitute": lambda d: f"ac = ({_fmt(d['v'])})^2 / ({_fmt(d['r'])})",
        "answer_label": "ac",
        "format_answer": _fmt,
    },
    "centripetal-force": {
        "title": "Centripetal Force",
        "latex": r"F_c = \frac{mv^2}{r}",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "v", "label": "Speed v"}, {"name": "r", "label": "Radius r"}],
        "compute": lambda d: d["m"] * d["v"] ** 2 / d["r"] if d["r"] > 0 else (_ for _ in ()).throw(ValueError("Radius r must be greater than 0.")),
        "substitute": lambda d: f"Fc = ({_fmt(d['m'])})*({_fmt(d['v'])})^2/({_fmt(d['r'])})",
        "answer_label": "Fc",
        "format_answer": _fmt,
    },
    "angular-velocity": {
        "title": "Angular Velocity",
        "latex": r"\omega = \frac{2\pi}{T}",
        "fields": [{"name": "T", "label": "Period T"}],
        "compute": lambda d: 2 * pi / d["T"] if abs(d["T"]) >= 1e-12 else (_ for _ in ()).throw(ValueError("Period T must not be zero.")),
        "substitute": lambda d: f"omega = 2*pi/({_fmt(d['T'])})",
        "answer_label": "omega",
        "format_answer": _fmt,
    },
    "projectile-range": {
        "title": "Projectile Range",
        "latex": r"R = \frac{v_0^2\sin(2\theta)}{g}",
        "fields": [{"name": "v0", "label": "Initial speed v0"}, {"name": "theta", "label": "Launch angle theta (deg)"}, {"name": "g", "label": "g"}],
        "compute": _projectile_range,
        "substitute": lambda d: "R = v0^2 * sin(2*theta) / g",
        "answer_label": "R",
        "format_answer": _fmt,
    },
    "projectile-max-height": {
        "title": "Projectile Maximum Height",
        "latex": r"H = \frac{v_0^2\sin^2\theta}{2g}",
        "fields": [{"name": "v0", "label": "Initial speed v0"}, {"name": "theta", "label": "Launch angle theta (deg)"}, {"name": "g", "label": "g"}],
        "compute": _projectile_max_height,
        "substitute": lambda d: "H = v0^2 * sin^2(theta) / (2*g)",
        "answer_label": "H",
        "format_answer": _fmt,
    },
    "triangle-angle-from-sides": {
        "title": "Triangle Angle from 3 Sides",
        "latex": r"C = \cos^{-1}\left(\frac{a^2+b^2-c^2}{2ab}\right)",
        "fields": [{"name": "a", "label": "Side a"}, {"name": "b", "label": "Side b"}, {"name": "c", "label": "Side c"}],
        "compute": _law_of_cosines_angle,
        "substitute": lambda d: "C = arccos((a^2+b^2-c^2)/(2ab))",
        "answer_label": "C",
        "format_answer": lambda v: f"{_fmt(v)} deg",
    },
}


PHYSICS_FORMULA_GROUPS = [
    {
        "title": "Mechanics & Motion",
        "slugs": [
            "speed",
            "distance",
            "acceleration",
            "newtons-second-law",
            "weight",
            "momentum",
            "impulse",
            "kinetic-energy",
            "potential-energy",
            "work",
            "power",
        ],
    },
    {
        "title": "Fluids & Matter",
        "slugs": ["pressure", "density", "buoyant-force"],
    },
    {
        "title": "Electricity & Gravitation",
        "slugs": [
            "ohms-law-voltage",
            "ohms-law-current",
            "ohms-law-resistance",
            "electric-power",
            "electric-energy",
            "coulombs-law",
            "newtons-law-of-gravitation",
        ],
    },
    {
        "title": "Waves & Optics",
        "slugs": [
            "wave-speed",
            "frequency-from-period",
            "period-from-frequency",
            "snells-law-theta2",
            "mirror-focal-length",
            "triangle-angle-from-sides",
        ],
    },
    {
        "title": "Thermal Physics",
        "slugs": ["heat-energy", "ideal-gas-pressure", "thermal-expansion"],
    },
    {
        "title": "Circular & Projectile Motion",
        "slugs": [
            "centripetal-acceleration",
            "centripetal-force",
            "angular-velocity",
            "projectile-range",
            "projectile-max-height",
        ],
    },
]


PHYSICS_FORMULA_DESCRIPTIONS = {
    "speed": "Compute velocity from distance traveled over time.",
    "distance": "Find total distance from speed and elapsed time.",
    "acceleration": "Measure change in velocity per unit time.",
    "newtons-second-law": "Relate force to mass and acceleration.",
    "weight": "Compute gravitational force on a mass.",
    "momentum": "Find linear momentum from mass and velocity.",
    "impulse": "Compute force applied over a time interval.",
    "kinetic-energy": "Find motion energy from mass and speed.",
    "potential-energy": "Find gravitational potential energy from height.",
    "work": "Compute energy transferred by a force through distance.",
    "power": "Measure work done or energy transferred per second.",
    "pressure": "Find force intensity over an area.",
    "density": "Compute mass per unit volume.",
    "buoyant-force": "Estimate upward fluid force on a displaced volume.",
    "ohms-law-voltage": "Find voltage from current and resistance.",
    "ohms-law-current": "Find current from voltage and resistance.",
    "ohms-law-resistance": "Find resistance from voltage and current.",
    "electric-power": "Compute electrical power in a circuit.",
    "electric-energy": "Compute electrical energy from power and time.",
    "coulombs-law": "Compute electrostatic force between charges.",
    "newtons-law-of-gravitation": "Compute gravitational attraction between masses.",
    "wave-speed": "Relate wave speed to frequency and wavelength.",
    "frequency-from-period": "Convert a time period into frequency.",
    "period-from-frequency": "Convert frequency into oscillation period.",
    "snells-law-theta2": "Find the refraction angle across two media.",
    "mirror-focal-length": "Compute focal length from object and image distances.",
    "heat-energy": "Compute heat gained or lost from mass, heat capacity, and temperature change.",
    "ideal-gas-pressure": "Find gas pressure from moles, temperature, and volume.",
    "thermal-expansion": "Estimate length change due to heating.",
    "centripetal-acceleration": "Find inward acceleration in circular motion.",
    "centripetal-force": "Find inward force required for circular motion.",
    "angular-velocity": "Relate angular position change to time.",
    "projectile-range": "Find horizontal range for projectile launch conditions.",
    "projectile-max-height": "Find maximum vertical height in projectile motion.",
    "triangle-angle-from-sides": "Compute an angle from three side lengths using the cosine rule.",
}
