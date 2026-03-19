import math


G = 9.81
GRAVITATIONAL_CONSTANT = 6.67430e-11


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _positive(value, label):
    if value <= 0:
        raise ValueError(f"{label} must be greater than 0.")


def _velocity_final(d):
    return d["u"] + d["a"] * d["t"]


def _displacement_uniform_acc(d):
    return d["u"] * d["t"] + 0.5 * d["a"] * d["t"] ** 2


def _velocity_squared(d):
    value = d["u"] ** 2 + 2 * d["a"] * d["s"]
    if value < 0:
        raise ValueError("u^2 + 2as is negative, so real velocity does not exist.")
    return math.sqrt(value)


def _average_velocity(d):
    _positive(d["t"], "Time")
    return d["s"] / d["t"]


def _projectile_range(d):
    _positive(d["v0"], "Initial speed")
    angle = math.radians(d["theta_deg"])
    return d["v0"] ** 2 * math.sin(2 * angle) / G


def _projectile_max_height(d):
    _positive(d["v0"], "Initial speed")
    angle = math.radians(d["theta_deg"])
    return d["v0"] ** 2 * (math.sin(angle) ** 2) / (2 * G)


def _projectile_time_of_flight(d):
    _positive(d["v0"], "Initial speed")
    angle = math.radians(d["theta_deg"])
    return 2 * d["v0"] * math.sin(angle) / G


def _circular_speed(d):
    _positive(d["period"], "Period")
    return 2 * math.pi * d["radius"] / d["period"]


def _centripetal_acceleration(d):
    _positive(d["radius"], "Radius")
    return d["v"] ** 2 / d["radius"]


def _newton_force(d):
    return d["m"] * d["a"]


def _weight(d):
    return d["m"] * G


def _friction_force(d):
    return d["mu"] * d["normal"]


def _pressure(d):
    _positive(d["area"], "Area")
    return d["force"] / d["area"]


def _momentum(d):
    return d["m"] * d["v"]


def _impulse(d):
    return d["force"] * d["dt"]


def _universal_gravitation(d):
    _positive(d["r"], "Distance r")
    return GRAVITATIONAL_CONSTANT * d["m1"] * d["m2"] / (d["r"] ** 2)


def _torque(d):
    angle = math.radians(d["theta_deg"])
    return d["force"] * d["lever_arm"] * math.sin(angle)


def _work(d):
    angle = math.radians(d["theta_deg"])
    return d["force"] * d["displacement"] * math.cos(angle)


def _kinetic_energy(d):
    return 0.5 * d["m"] * d["v"] ** 2


def _gravitational_potential_energy(d):
    return d["m"] * G * d["h"]


def _power(d):
    _positive(d["time"], "Time")
    return d["work"] / d["time"]


def _spring_potential_energy(d):
    return 0.5 * d["k"] * d["x"] ** 2


def _hooke_force_magnitude(d):
    return d["k"] * abs(d["x"])


def _efficiency(d):
    _positive(d["input_power"], "Input power")
    return (d["output_power"] / d["input_power"]) * 100


def _frequency(d):
    _positive(d["period"], "Period")
    return 1 / d["period"]


def _period(d):
    _positive(d["frequency"], "Frequency")
    return 1 / d["frequency"]


def _wave_speed(d):
    return d["frequency"] * d["wavelength"]


def _spring_period(d):
    _positive(d["k"], "Spring constant k")
    _positive(d["m"], "Mass")
    return 2 * math.pi * math.sqrt(d["m"] / d["k"])


def _pendulum_period(d):
    _positive(d["length"], "Length")
    return 2 * math.pi * math.sqrt(d["length"] / G)


def _angular_speed(d):
    _positive(d["period"], "Period")
    return 2 * math.pi / d["period"]


def _density(d):
    _positive(d["volume"], "Volume")
    return d["mass"] / d["volume"]


def _heat_energy(d):
    return d["mass"] * d["specific_heat"] * d["delta_t"]


def _linear_expansion(d):
    return d["alpha"] * d["length0"] * d["delta_t"]


def _buoyant_force(d):
    return d["rho"] * G * d["displaced_volume"]


def _continuity_v2(d):
    _positive(d["area2"], "Area A2")
    return d["area1"] * d["velocity1"] / d["area2"]


MECHANICS_FORMULAS = {
    "final-velocity": {
        "title": "Final Velocity (v = u + at)",
        "latex": r"v = u + at",
        "fields": [
            {"name": "u", "label": "Initial velocity u (m/s)"},
            {"name": "a", "label": "Acceleration a (m/s^2)"},
            {"name": "t", "label": "Time t (s)", "min": 0},
        ],
        "compute": _velocity_final,
        "substitute": lambda d: f"v = {_fmt(d['u'])} + {_fmt(d['a'])} x {_fmt(d['t'])}",
        "answer_label": "Final Velocity v (m/s)",
        "format_answer": _fmt,
    },
    "displacement-uniform-acc": {
        "title": "Displacement (s = ut + 1/2at^2)",
        "latex": r"s = ut + \tfrac{1}{2}at^2",
        "fields": [
            {"name": "u", "label": "Initial velocity u (m/s)"},
            {"name": "a", "label": "Acceleration a (m/s^2)"},
            {"name": "t", "label": "Time t (s)", "min": 0},
        ],
        "compute": _displacement_uniform_acc,
        "substitute": lambda d: f"s = {_fmt(d['u'])}x{_fmt(d['t'])} + 0.5x{_fmt(d['a'])}x{_fmt(d['t'])}^2",
        "answer_label": "Displacement s (m)",
        "format_answer": _fmt,
    },
    "third-kinematic": {
        "title": "Third Kinematic Equation",
        "latex": r"v^2 = u^2 + 2as",
        "fields": [
            {"name": "u", "label": "Initial velocity u (m/s)"},
            {"name": "a", "label": "Acceleration a (m/s^2)"},
            {"name": "s", "label": "Displacement s (m)"},
        ],
        "compute": _velocity_squared,
        "substitute": lambda d: f"v = sqrt({_fmt(d['u'])}^2 + 2x{_fmt(d['a'])}x{_fmt(d['s'])})",
        "answer_label": "Final Speed v (m/s)",
        "format_answer": _fmt,
    },
    "average-velocity": {
        "title": "Average Velocity",
        "latex": r"\bar{v} = \frac{s}{t}",
        "fields": [
            {"name": "s", "label": "Displacement s (m)"},
            {"name": "t", "label": "Time t (s)", "min": 0},
        ],
        "compute": _average_velocity,
        "substitute": lambda d: f"v_avg = {_fmt(d['s'])} / {_fmt(d['t'])}",
        "answer_label": "Average Velocity (m/s)",
        "format_answer": _fmt,
    },
    "projectile-range": {
        "title": "Projectile Range",
        "latex": r"R = \frac{v_0^2\sin(2\theta)}{g}",
        "fields": [
            {"name": "v0", "label": "Initial speed v0 (m/s)", "min": 0},
            {"name": "theta_deg", "label": "Launch angle theta (deg)", "min": 0, "max": 90},
        ],
        "compute": _projectile_range,
        "substitute": lambda d: f"R = {_fmt(d['v0'])}^2 sin(2x{_fmt(d['theta_deg'])}) / 9.81",
        "answer_label": "Range R (m)",
        "format_answer": _fmt,
    },
    "projectile-max-height": {
        "title": "Projectile Maximum Height",
        "latex": r"H = \frac{v_0^2\sin^2\theta}{2g}",
        "fields": [
            {"name": "v0", "label": "Initial speed v0 (m/s)", "min": 0},
            {"name": "theta_deg", "label": "Launch angle theta (deg)", "min": 0, "max": 90},
        ],
        "compute": _projectile_max_height,
        "substitute": lambda d: f"H = {_fmt(d['v0'])}^2 sin^2({_fmt(d['theta_deg'])}) / (2x9.81)",
        "answer_label": "Max Height H (m)",
        "format_answer": _fmt,
    },
    "projectile-time": {
        "title": "Projectile Time of Flight",
        "latex": r"T = \frac{2v_0\sin\theta}{g}",
        "fields": [
            {"name": "v0", "label": "Initial speed v0 (m/s)", "min": 0},
            {"name": "theta_deg", "label": "Launch angle theta (deg)", "min": 0, "max": 90},
        ],
        "compute": _projectile_time_of_flight,
        "substitute": lambda d: f"T = 2x{_fmt(d['v0'])}xsin({_fmt(d['theta_deg'])}) / 9.81",
        "answer_label": "Time of Flight T (s)",
        "format_answer": _fmt,
    },
    "circular-speed": {
        "title": "Circular Motion Speed",
        "latex": r"v = \frac{2\pi r}{T}",
        "fields": [
            {"name": "radius", "label": "Radius r (m)", "min": 0},
            {"name": "period", "label": "Period T (s)", "min": 0},
        ],
        "compute": _circular_speed,
        "substitute": lambda d: f"v = 2pi x {_fmt(d['radius'])} / {_fmt(d['period'])}",
        "answer_label": "Speed v (m/s)",
        "format_answer": _fmt,
    },
    "centripetal-acceleration": {
        "title": "Centripetal Acceleration",
        "latex": r"a_c = \frac{v^2}{r}",
        "fields": [
            {"name": "v", "label": "Speed v (m/s)"},
            {"name": "radius", "label": "Radius r (m)", "min": 0},
        ],
        "compute": _centripetal_acceleration,
        "substitute": lambda d: f"a_c = {_fmt(d['v'])}^2 / {_fmt(d['radius'])}",
        "answer_label": "Centripetal Acceleration (m/s^2)",
        "format_answer": _fmt,
    },
    "newton-force": {
        "title": "Newton's Second Law",
        "latex": r"F = ma",
        "fields": [
            {"name": "m", "label": "Mass m (kg)", "min": 0},
            {"name": "a", "label": "Acceleration a (m/s^2)"},
        ],
        "compute": _newton_force,
        "substitute": lambda d: f"F = {_fmt(d['m'])} x {_fmt(d['a'])}",
        "answer_label": "Force F (N)",
        "format_answer": _fmt,
    },
    "weight": {
        "title": "Weight",
        "latex": r"W = mg",
        "fields": [{"name": "m", "label": "Mass m (kg)", "min": 0}],
        "compute": _weight,
        "substitute": lambda d: f"W = {_fmt(d['m'])} x 9.81",
        "answer_label": "Weight W (N)",
        "format_answer": _fmt,
    },
    "friction-force": {
        "title": "Friction Force",
        "latex": r"F_f = \mu N",
        "fields": [
            {"name": "mu", "label": "Coefficient of friction mu", "min": 0},
            {"name": "normal", "label": "Normal force N (N)", "min": 0},
        ],
        "compute": _friction_force,
        "substitute": lambda d: f"F_f = {_fmt(d['mu'])} x {_fmt(d['normal'])}",
        "answer_label": "Friction Force F_f (N)",
        "format_answer": _fmt,
    },
    "pressure": {
        "title": "Pressure",
        "latex": r"P = \frac{F}{A}",
        "fields": [
            {"name": "force", "label": "Force F (N)"},
            {"name": "area", "label": "Area A (m^2)", "min": 0},
        ],
        "compute": _pressure,
        "substitute": lambda d: f"P = {_fmt(d['force'])} / {_fmt(d['area'])}",
        "answer_label": "Pressure P (Pa)",
        "format_answer": _fmt,
    },
    "momentum": {
        "title": "Linear Momentum",
        "latex": r"p = mv",
        "fields": [
            {"name": "m", "label": "Mass m (kg)", "min": 0},
            {"name": "v", "label": "Velocity v (m/s)"},
        ],
        "compute": _momentum,
        "substitute": lambda d: f"p = {_fmt(d['m'])} x {_fmt(d['v'])}",
        "answer_label": "Momentum p (kg m/s)",
        "format_answer": _fmt,
    },
    "impulse": {
        "title": "Impulse",
        "latex": r"J = F\Delta t",
        "fields": [
            {"name": "force", "label": "Force F (N)"},
            {"name": "dt", "label": "Time interval dt (s)", "min": 0},
        ],
        "compute": _impulse,
        "substitute": lambda d: f"J = {_fmt(d['force'])} x {_fmt(d['dt'])}",
        "answer_label": "Impulse J (N s)",
        "format_answer": _fmt,
    },
    "universal-gravitation": {
        "title": "Universal Gravitation",
        "latex": r"F = G\frac{m_1m_2}{r^2}",
        "fields": [
            {"name": "m1", "label": "Mass m1 (kg)", "min": 0},
            {"name": "m2", "label": "Mass m2 (kg)", "min": 0},
            {"name": "r", "label": "Distance r (m)", "min": 0},
        ],
        "compute": _universal_gravitation,
        "substitute": lambda d: f"F = 6.67430e-11 x {_fmt(d['m1'])} x {_fmt(d['m2'])} / {_fmt(d['r'])}^2",
        "answer_label": "Gravitational Force F (N)",
        "format_answer": _fmt,
    },
    "torque": {
        "title": "Torque",
        "latex": r"\tau = rF\sin\theta",
        "fields": [
            {"name": "force", "label": "Force F (N)"},
            {"name": "lever_arm", "label": "Lever arm r (m)", "min": 0},
            {"name": "theta_deg", "label": "Angle theta (deg)", "min": 0, "max": 180},
        ],
        "compute": _torque,
        "substitute": lambda d: f"tau = {_fmt(d['lever_arm'])} x {_fmt(d['force'])} x sin({_fmt(d['theta_deg'])})",
        "answer_label": "Torque tau (N m)",
        "format_answer": _fmt,
    },
    "work": {
        "title": "Work Done",
        "latex": r"W = Fd\cos\theta",
        "fields": [
            {"name": "force", "label": "Force F (N)"},
            {"name": "displacement", "label": "Displacement d (m)"},
            {"name": "theta_deg", "label": "Angle theta (deg)", "min": 0, "max": 180},
        ],
        "compute": _work,
        "substitute": lambda d: f"W = {_fmt(d['force'])} x {_fmt(d['displacement'])} x cos({_fmt(d['theta_deg'])})",
        "answer_label": "Work W (J)",
        "format_answer": _fmt,
    },
    "kinetic-energy": {
        "title": "Kinetic Energy",
        "latex": r"KE = \tfrac{1}{2}mv^2",
        "fields": [
            {"name": "m", "label": "Mass m (kg)", "min": 0},
            {"name": "v", "label": "Speed v (m/s)"},
        ],
        "compute": _kinetic_energy,
        "substitute": lambda d: f"KE = 0.5 x {_fmt(d['m'])} x {_fmt(d['v'])}^2",
        "answer_label": "Kinetic Energy KE (J)",
        "format_answer": _fmt,
    },
    "gravitational-potential-energy": {
        "title": "Gravitational Potential Energy",
        "latex": r"PE = mgh",
        "fields": [
            {"name": "m", "label": "Mass m (kg)", "min": 0},
            {"name": "h", "label": "Height h (m)"},
        ],
        "compute": _gravitational_potential_energy,
        "substitute": lambda d: f"PE = {_fmt(d['m'])} x 9.81 x {_fmt(d['h'])}",
        "answer_label": "Potential Energy PE (J)",
        "format_answer": _fmt,
    },
    "power": {
        "title": "Power",
        "latex": r"P = \frac{W}{t}",
        "fields": [
            {"name": "work", "label": "Work W (J)"},
            {"name": "time", "label": "Time t (s)", "min": 0},
        ],
        "compute": _power,
        "substitute": lambda d: f"P = {_fmt(d['work'])} / {_fmt(d['time'])}",
        "answer_label": "Power P (W)",
        "format_answer": _fmt,
    },
    "spring-potential-energy": {
        "title": "Spring Potential Energy",
        "latex": r"U = \tfrac{1}{2}kx^2",
        "fields": [
            {"name": "k", "label": "Spring constant k (N/m)", "min": 0},
            {"name": "x", "label": "Extension x (m)"},
        ],
        "compute": _spring_potential_energy,
        "substitute": lambda d: f"U = 0.5 x {_fmt(d['k'])} x {_fmt(d['x'])}^2",
        "answer_label": "Spring Energy U (J)",
        "format_answer": _fmt,
    },
    "hooke-force": {
        "title": "Hooke's Law Force Magnitude",
        "latex": r"|F| = k|x|",
        "fields": [
            {"name": "k", "label": "Spring constant k (N/m)", "min": 0},
            {"name": "x", "label": "Extension/compression x (m)"},
        ],
        "compute": _hooke_force_magnitude,
        "substitute": lambda d: f"|F| = {_fmt(d['k'])} x |{_fmt(d['x'])}|",
        "answer_label": "Spring Force |F| (N)",
        "format_answer": _fmt,
    },
    "efficiency": {
        "title": "Efficiency",
        "latex": r"\eta = \frac{P_{out}}{P_{in}}\times 100\%",
        "fields": [
            {"name": "output_power", "label": "Output power P_out (W)", "min": 0},
            {"name": "input_power", "label": "Input power P_in (W)", "min": 0},
        ],
        "compute": _efficiency,
        "substitute": lambda d: f"eta = ({_fmt(d['output_power'])} / {_fmt(d['input_power'])}) x 100",
        "answer_label": "Efficiency eta (%)",
        "format_answer": _fmt,
    },
    "frequency": {
        "title": "Frequency from Period",
        "latex": r"f = \frac{1}{T}",
        "fields": [{"name": "period", "label": "Period T (s)", "min": 0}],
        "compute": _frequency,
        "substitute": lambda d: f"f = 1 / {_fmt(d['period'])}",
        "answer_label": "Frequency f (Hz)",
        "format_answer": _fmt,
    },
    "period": {
        "title": "Period from Frequency",
        "latex": r"T = \frac{1}{f}",
        "fields": [{"name": "frequency", "label": "Frequency f (Hz)", "min": 0}],
        "compute": _period,
        "substitute": lambda d: f"T = 1 / {_fmt(d['frequency'])}",
        "answer_label": "Period T (s)",
        "format_answer": _fmt,
    },
    "wave-speed": {
        "title": "Wave Speed",
        "latex": r"v = f\lambda",
        "fields": [
            {"name": "frequency", "label": "Frequency f (Hz)", "min": 0},
            {"name": "wavelength", "label": "Wavelength lambda (m)", "min": 0},
        ],
        "compute": _wave_speed,
        "substitute": lambda d: f"v = {_fmt(d['frequency'])} x {_fmt(d['wavelength'])}",
        "answer_label": "Wave Speed v (m/s)",
        "format_answer": _fmt,
    },
    "spring-period": {
        "title": "Mass-Spring Period",
        "latex": r"T = 2\pi\sqrt{\frac{m}{k}}",
        "fields": [
            {"name": "m", "label": "Mass m (kg)", "min": 0},
            {"name": "k", "label": "Spring constant k (N/m)", "min": 0},
        ],
        "compute": _spring_period,
        "substitute": lambda d: f"T = 2pi x sqrt({_fmt(d['m'])}/{_fmt(d['k'])})",
        "answer_label": "Period T (s)",
        "format_answer": _fmt,
    },
    "pendulum-period": {
        "title": "Simple Pendulum Period",
        "latex": r"T = 2\pi\sqrt{\frac{L}{g}}",
        "fields": [{"name": "length", "label": "Length L (m)", "min": 0}],
        "compute": _pendulum_period,
        "substitute": lambda d: f"T = 2pi x sqrt({_fmt(d['length'])}/9.81)",
        "answer_label": "Period T (s)",
        "format_answer": _fmt,
    },
    "angular-speed": {
        "title": "Angular Speed",
        "latex": r"\omega = \frac{2\pi}{T}",
        "fields": [{"name": "period", "label": "Period T (s)", "min": 0}],
        "compute": _angular_speed,
        "substitute": lambda d: f"omega = 2pi / {_fmt(d['period'])}",
        "answer_label": "Angular Speed omega (rad/s)",
        "format_answer": _fmt,
    },
    "density": {
        "title": "Density",
        "latex": r"\rho = \frac{m}{V}",
        "fields": [
            {"name": "mass", "label": "Mass m (kg)", "min": 0},
            {"name": "volume", "label": "Volume V (m^3)", "min": 0},
        ],
        "compute": _density,
        "substitute": lambda d: f"rho = {_fmt(d['mass'])} / {_fmt(d['volume'])}",
        "answer_label": "Density rho (kg/m^3)",
        "format_answer": _fmt,
    },
    "heat-energy": {
        "title": "Heat Energy",
        "latex": r"Q = mc\Delta T",
        "fields": [
            {"name": "mass", "label": "Mass m (kg)", "min": 0},
            {"name": "specific_heat", "label": "Specific heat c (J/kg K)", "min": 0},
            {"name": "delta_t", "label": "Temperature change delta T (K)"},
        ],
        "compute": _heat_energy,
        "substitute": lambda d: f"Q = {_fmt(d['mass'])} x {_fmt(d['specific_heat'])} x {_fmt(d['delta_t'])}",
        "answer_label": "Heat Q (J)",
        "format_answer": _fmt,
    },
    "linear-expansion": {
        "title": "Linear Thermal Expansion",
        "latex": r"\Delta L = \alpha L_0 \Delta T",
        "fields": [
            {"name": "alpha", "label": "Expansion coefficient alpha (1/K)", "min": 0},
            {"name": "length0", "label": "Original length L0 (m)", "min": 0},
            {"name": "delta_t", "label": "Temperature change delta T (K)"},
        ],
        "compute": _linear_expansion,
        "substitute": lambda d: f"delta L = {_fmt(d['alpha'])} x {_fmt(d['length0'])} x {_fmt(d['delta_t'])}",
        "answer_label": "Length Change delta L (m)",
        "format_answer": _fmt,
    },
    "buoyant-force": {
        "title": "Buoyant Force",
        "latex": r"F_b = \rho g V",
        "fields": [
            {"name": "rho", "label": "Fluid density rho (kg/m^3)", "min": 0},
            {"name": "displaced_volume", "label": "Displaced volume V (m^3)", "min": 0},
        ],
        "compute": _buoyant_force,
        "substitute": lambda d: f"F_b = {_fmt(d['rho'])} x 9.81 x {_fmt(d['displaced_volume'])}",
        "answer_label": "Buoyant Force F_b (N)",
        "format_answer": _fmt,
    },
    "continuity-v2": {
        "title": "Continuity Equation (Solve v2)",
        "latex": r"A_1 v_1 = A_2 v_2",
        "fields": [
            {"name": "area1", "label": "Area A1 (m^2)", "min": 0},
            {"name": "velocity1", "label": "Velocity v1 (m/s)"},
            {"name": "area2", "label": "Area A2 (m^2)", "min": 0},
        ],
        "compute": _continuity_v2,
        "substitute": lambda d: f"v2 = {_fmt(d['area1'])} x {_fmt(d['velocity1'])} / {_fmt(d['area2'])}",
        "answer_label": "Velocity v2 (m/s)",
        "format_answer": _fmt,
    },
}

MECHANICS_FORMULA_GROUPS = [
    {
        "title": "Kinematics",
        "slugs": [
            "final-velocity",
            "displacement-uniform-acc",
            "third-kinematic",
            "average-velocity",
            "projectile-range",
            "projectile-max-height",
            "projectile-time",
            "circular-speed",
            "centripetal-acceleration",
        ],
    },
    {
        "title": "Dynamics",
        "slugs": [
            "newton-force",
            "weight",
            "friction-force",
            "pressure",
            "momentum",
            "impulse",
            "universal-gravitation",
            "torque",
        ],
    },
    {
        "title": "Work, Energy, and Power",
        "slugs": [
            "work",
            "kinetic-energy",
            "gravitational-potential-energy",
            "power",
            "spring-potential-energy",
            "hooke-force",
            "efficiency",
        ],
    },
    {
        "title": "Oscillations and Waves",
        "slugs": [
            "frequency",
            "period",
            "wave-speed",
            "spring-period",
            "pendulum-period",
            "angular-speed",
        ],
    },
    {
        "title": "Fluids and Thermal Physics",
        "slugs": [
            "density",
            "heat-energy",
            "linear-expansion",
            "buoyant-force",
            "continuity-v2",
        ],
    },
]

MECHANICS_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in MECHANICS_FORMULAS.items()
}
