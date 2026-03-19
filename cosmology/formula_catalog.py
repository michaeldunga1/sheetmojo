import math


C_LIGHT_M_S = 299_792_458.0
C_LIGHT_KM_S = 299_792.458
G_GRAVITY = 6.67430e-11
MPC_IN_METERS = 3.085677581491367e22
SOLAR_MASS_KG = 1.98847e30
SECONDS_PER_GYR = 365.25 * 24 * 3600 * 1_000_000_000
WIEN_B = 2.897771955e-3


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _positive(value, label):
    if value <= 0:
        raise ValueError(f"{label} must be greater than 0.")


def _nonnegative(value, label):
    if value < 0:
        raise ValueError(f"{label} must be at least 0.")


def _fraction_0_1(value, label):
    if value < 0 or value > 1:
        raise ValueError(f"{label} must be between 0 and 1.")


def _hubble_to_si(h0_km_s_mpc):
    return h0_km_s_mpc * 1000 / MPC_IN_METERS


def _hubble_law_velocity(d):
    return d["h0_km_s_mpc"] * d["distance_mpc"]


def _distance_from_redshift(d):
    return C_LIGHT_KM_S * d["redshift"] / d["h0_km_s_mpc"]


def _lookback_time_small_z(d):
    h_si = _hubble_to_si(d["h0_km_s_mpc"])
    return d["redshift"] / h_si / SECONDS_PER_GYR


def _age_from_hubble(d):
    h = d["h0_km_s_mpc"] / 100
    _positive(h, "Reduced Hubble parameter h")
    return 9.78 / h


def _scale_factor_to_redshift(d):
    a = d["scale_factor"]
    if a <= 0 or a > 1:
        raise ValueError("Scale factor must be greater than 0 and at most 1.")
    return 1 / a - 1


def _redshift_to_scale_factor(d):
    z = d["redshift"]
    if z <= -1:
        raise ValueError("Redshift must be greater than -1.")
    return 1 / (1 + z)


def _luminosity_distance(d):
    return d["comoving_distance_mpc"] * (1 + d["redshift"])


def _angular_diameter_distance(d):
    if d["redshift"] <= -1:
        raise ValueError("Redshift must be greater than -1.")
    return d["comoving_distance_mpc"] / (1 + d["redshift"])


def _distance_modulus(d):
    d_pc = d["distance_mpc"] * 1_000_000
    _positive(d_pc, "Distance")
    return 5 * math.log10(d_pc) - 5


def _flux_from_luminosity(d):
    distance_m = d["distance_mpc"] * MPC_IN_METERS
    _positive(distance_m, "Distance")
    return d["luminosity_w"] / (4 * math.pi * distance_m**2)


def _luminosity_from_flux(d):
    distance_m = d["distance_mpc"] * MPC_IN_METERS
    _positive(distance_m, "Distance")
    return 4 * math.pi * distance_m**2 * d["flux_w_m2"]


def _critical_density(d):
    h_si = _hubble_to_si(d["h0_km_s_mpc"])
    return (3 * h_si**2) / (8 * math.pi * G_GRAVITY)


def _deceleration_parameter(d):
    return 0.5 * d["omega_m"] - d["omega_lambda"]


def _matter_radiation_equality_redshift(d):
    _positive(d["omega_r"], "Omega radiation")
    return d["omega_m"] / d["omega_r"] - 1


def _schwarzschild_radius_km(d):
    mass_kg = d["mass_solar"] * SOLAR_MASS_KG
    return (2 * G_GRAVITY * mass_kg / (C_LIGHT_M_S**2)) / 1000


def _escape_velocity_km_s(d):
    mass_kg = d["mass_solar"] * SOLAR_MASS_KG
    radius_m = d["radius_km"] * 1000
    _positive(radius_m, "Radius")
    return math.sqrt((2 * G_GRAVITY * mass_kg) / radius_m) / 1000


def _orbital_period_years(d):
    _positive(d["central_mass_solar"], "Central mass")
    return math.sqrt((d["semi_major_axis_au"] ** 3) / d["central_mass_solar"])


def _central_mass_from_kepler(d):
    _positive(d["orbital_period_years"], "Orbital period")
    return (d["semi_major_axis_au"] ** 3) / (d["orbital_period_years"] ** 2)


def _wien_peak_nm(d):
    return (WIEN_B / d["temperature_k"]) * 1_000_000_000


def _cmb_photon_density(d):
    return 20.29 * (d["temperature_k"] ** 3)


COSMOLOGY_FORMULAS = {
    "hubble-law": {
        "title": "Hubble Law Velocity",
        "latex": r"v = H_0 d",
        "fields": [
            {"name": "h0_km_s_mpc", "label": "Hubble constant H0 (km/s/Mpc)", "min": 0},
            {"name": "distance_mpc", "label": "Distance d (Mpc)", "min": 0},
        ],
        "compute": _hubble_law_velocity,
        "substitute": lambda d: f"v = {_fmt(d['h0_km_s_mpc'])} x {_fmt(d['distance_mpc'])}",
        "answer_label": "Recession Velocity (km/s)",
        "format_answer": _fmt,
    },
    "distance-redshift": {
        "title": "Distance from Redshift (Low z)",
        "latex": r"d \approx \dfrac{cz}{H_0}",
        "fields": [
            {"name": "redshift", "label": "Redshift z", "min": 0},
            {"name": "h0_km_s_mpc", "label": "Hubble constant H0 (km/s/Mpc)", "min": 0},
        ],
        "compute": _distance_from_redshift,
        "substitute": lambda d: f"d = (299792.458 x {_fmt(d['redshift'])}) / {_fmt(d['h0_km_s_mpc'])}",
        "answer_label": "Distance (Mpc)",
        "format_answer": _fmt,
    },
    "lookback-time-small-z": {
        "title": "Lookback Time (Small z Approx)",
        "latex": r"t_L \approx \dfrac{z}{H_0}",
        "fields": [
            {"name": "redshift", "label": "Redshift z", "min": 0},
            {"name": "h0_km_s_mpc", "label": "Hubble constant H0 (km/s/Mpc)", "min": 0},
        ],
        "compute": _lookback_time_small_z,
        "substitute": lambda d: f"t_L = {_fmt(d['redshift'])} / H0",
        "answer_label": "Lookback Time (Gyr)",
        "format_answer": _fmt,
    },
    "age-from-hubble": {
        "title": "Age from Hubble Constant",
        "latex": r"t_0 \approx \dfrac{9.78}{h}\ \text{Gyr},\ h=H_0/100",
        "fields": [
            {"name": "h0_km_s_mpc", "label": "Hubble constant H0 (km/s/Mpc)", "min": 0},
        ],
        "compute": _age_from_hubble,
        "substitute": lambda d: f"h = {_fmt(d['h0_km_s_mpc'])}/100, t_0 = 9.78/h",
        "answer_label": "Age (Gyr)",
        "format_answer": _fmt,
    },
    "scale-factor-to-redshift": {
        "title": "Redshift from Scale Factor",
        "latex": r"z = \dfrac{1}{a} - 1",
        "fields": [
            {"name": "scale_factor", "label": "Scale factor a", "min": 0, "max": 1},
        ],
        "compute": _scale_factor_to_redshift,
        "substitute": lambda d: f"z = 1/{_fmt(d['scale_factor'])} - 1",
        "answer_label": "Redshift z",
        "format_answer": _fmt,
    },
    "redshift-to-scale-factor": {
        "title": "Scale Factor from Redshift",
        "latex": r"a = \dfrac{1}{1+z}",
        "fields": [
            {"name": "redshift", "label": "Redshift z"},
        ],
        "compute": _redshift_to_scale_factor,
        "substitute": lambda d: f"a = 1/(1 + {_fmt(d['redshift'])})",
        "answer_label": "Scale Factor a",
        "format_answer": _fmt,
    },
    "luminosity-distance": {
        "title": "Luminosity Distance",
        "latex": r"d_L = (1+z)d_C",
        "fields": [
            {"name": "redshift", "label": "Redshift z"},
            {"name": "comoving_distance_mpc", "label": "Comoving distance dC (Mpc)", "min": 0},
        ],
        "compute": _luminosity_distance,
        "substitute": lambda d: f"d_L = (1 + {_fmt(d['redshift'])}) x {_fmt(d['comoving_distance_mpc'])}",
        "answer_label": "Luminosity Distance (Mpc)",
        "format_answer": _fmt,
    },
    "angular-diameter-distance": {
        "title": "Angular Diameter Distance",
        "latex": r"d_A = \dfrac{d_C}{1+z}",
        "fields": [
            {"name": "redshift", "label": "Redshift z"},
            {"name": "comoving_distance_mpc", "label": "Comoving distance dC (Mpc)", "min": 0},
        ],
        "compute": _angular_diameter_distance,
        "substitute": lambda d: f"d_A = {_fmt(d['comoving_distance_mpc'])}/(1 + {_fmt(d['redshift'])})",
        "answer_label": "Angular Diameter Distance (Mpc)",
        "format_answer": _fmt,
    },
    "distance-modulus": {
        "title": "Distance Modulus",
        "latex": r"\mu = 5\log_{10}(d_{pc}) - 5",
        "fields": [
            {"name": "distance_mpc", "label": "Distance (Mpc)", "min": 0},
        ],
        "compute": _distance_modulus,
        "substitute": lambda d: f"mu = 5log10({_fmt(d['distance_mpc'])} x 10^6) - 5",
        "answer_label": "Distance Modulus",
        "format_answer": _fmt,
    },
    "flux-from-luminosity": {
        "title": "Flux from Luminosity",
        "latex": r"F = \dfrac{L}{4\pi d^2}",
        "fields": [
            {"name": "luminosity_w", "label": "Luminosity L (W)", "min": 0},
            {"name": "distance_mpc", "label": "Distance (Mpc)", "min": 0},
        ],
        "compute": _flux_from_luminosity,
        "substitute": lambda d: f"F = {_fmt(d['luminosity_w'])}/(4pi d^2)",
        "answer_label": "Flux (W/m^2)",
        "format_answer": _fmt,
    },
    "luminosity-from-flux": {
        "title": "Luminosity from Flux",
        "latex": r"L = 4\pi d^2F",
        "fields": [
            {"name": "flux_w_m2", "label": "Flux F (W/m^2)", "min": 0},
            {"name": "distance_mpc", "label": "Distance (Mpc)", "min": 0},
        ],
        "compute": _luminosity_from_flux,
        "substitute": lambda d: f"L = 4pi d^2 x {_fmt(d['flux_w_m2'])}",
        "answer_label": "Luminosity (W)",
        "format_answer": _fmt,
    },
    "critical-density": {
        "title": "Critical Density",
        "latex": r"\rho_c = \dfrac{3H_0^2}{8\pi G}",
        "fields": [
            {"name": "h0_km_s_mpc", "label": "Hubble constant H0 (km/s/Mpc)", "min": 0},
        ],
        "compute": _critical_density,
        "substitute": lambda d: f"rho_c = 3H0^2/(8piG), H0={_fmt(d['h0_km_s_mpc'])}",
        "answer_label": "Critical Density (kg/m^3)",
        "format_answer": _fmt,
    },
    "deceleration-parameter": {
        "title": "Deceleration Parameter",
        "latex": r"q_0 = \dfrac{\Omega_m}{2} - \Omega_\Lambda",
        "fields": [
            {"name": "omega_m", "label": "Omega matter (Omega_m)", "min": 0},
            {"name": "omega_lambda", "label": "Omega dark energy (Omega_lambda)", "min": 0},
        ],
        "compute": _deceleration_parameter,
        "substitute": lambda d: f"q0 = 0.5 x {_fmt(d['omega_m'])} - {_fmt(d['omega_lambda'])}",
        "answer_label": "q0",
        "format_answer": _fmt,
    },
    "matter-radiation-equality": {
        "title": "Matter-Radiation Equality Redshift",
        "latex": r"z_{eq} = \dfrac{\Omega_m}{\Omega_r} - 1",
        "fields": [
            {"name": "omega_m", "label": "Omega matter (Omega_m)", "min": 0},
            {"name": "omega_r", "label": "Omega radiation (Omega_r)", "min": 0},
        ],
        "compute": _matter_radiation_equality_redshift,
        "substitute": lambda d: f"z_eq = {_fmt(d['omega_m'])}/{_fmt(d['omega_r'])} - 1",
        "answer_label": "z_eq",
        "format_answer": _fmt,
    },
    "schwarzschild-radius": {
        "title": "Schwarzschild Radius",
        "latex": r"r_s = \dfrac{2GM}{c^2}",
        "fields": [
            {"name": "mass_solar", "label": "Mass (solar masses)", "min": 0},
        ],
        "compute": _schwarzschild_radius_km,
        "substitute": lambda d: f"r_s = 2GM/c^2 for M={_fmt(d['mass_solar'])} Msun",
        "answer_label": "Schwarzschild Radius (km)",
        "format_answer": _fmt,
    },
    "escape-velocity": {
        "title": "Escape Velocity",
        "latex": r"v_e = \sqrt{\dfrac{2GM}{r}}",
        "fields": [
            {"name": "mass_solar", "label": "Mass (solar masses)", "min": 0},
            {"name": "radius_km", "label": "Radius (km)", "min": 0},
        ],
        "compute": _escape_velocity_km_s,
        "substitute": lambda d: f"v_e = sqrt(2GM/r) with M={_fmt(d['mass_solar'])}, r={_fmt(d['radius_km'])}",
        "answer_label": "Escape Velocity (km/s)",
        "format_answer": _fmt,
    },
    "orbital-period-kepler": {
        "title": "Orbital Period (Kepler)",
        "latex": r"T^2 = \dfrac{a^3}{M}",
        "fields": [
            {"name": "semi_major_axis_au", "label": "Semi-major axis a (AU)", "min": 0},
            {"name": "central_mass_solar", "label": "Central mass (solar masses)", "min": 0},
        ],
        "compute": _orbital_period_years,
        "substitute": lambda d: f"T = sqrt({_fmt(d['semi_major_axis_au'])}^3 / {_fmt(d['central_mass_solar'])})",
        "answer_label": "Orbital Period (years)",
        "format_answer": _fmt,
    },
    "central-mass-kepler": {
        "title": "Central Mass from Orbit",
        "latex": r"M = \dfrac{a^3}{T^2}",
        "fields": [
            {"name": "semi_major_axis_au", "label": "Semi-major axis a (AU)", "min": 0},
            {"name": "orbital_period_years", "label": "Orbital period T (years)", "min": 0},
        ],
        "compute": _central_mass_from_kepler,
        "substitute": lambda d: f"M = {_fmt(d['semi_major_axis_au'])}^3 / {_fmt(d['orbital_period_years'])}^2",
        "answer_label": "Central Mass (solar masses)",
        "format_answer": _fmt,
    },
    "wien-peak": {
        "title": "Wien Peak Wavelength",
        "latex": r"\lambda_{max} = \dfrac{b}{T}",
        "fields": [
            {"name": "temperature_k", "label": "Temperature T (K)", "min": 0},
        ],
        "compute": _wien_peak_nm,
        "substitute": lambda d: f"lambda_max = b/{_fmt(d['temperature_k'])}",
        "answer_label": "Peak Wavelength (nm)",
        "format_answer": _fmt,
    },
    "cmb-photon-density": {
        "title": "CMB Photon Number Density",
        "latex": r"n_\gamma \approx 20.29 T^3\ \text{cm}^{-3}",
        "fields": [
            {"name": "temperature_k", "label": "Temperature T (K)", "min": 0},
        ],
        "compute": _cmb_photon_density,
        "substitute": lambda d: f"n_gamma = 20.29 x {_fmt(d['temperature_k'])}^3",
        "answer_label": "Photon Density (cm^-3)",
        "format_answer": _fmt,
    },
}


COSMOLOGY_FORMULA_GROUPS = [
    {
        "title": "Expansion & Redshift",
        "slugs": [
            "hubble-law",
            "distance-redshift",
            "lookback-time-small-z",
            "age-from-hubble",
            "scale-factor-to-redshift",
            "redshift-to-scale-factor",
        ],
    },
    {
        "title": "Distances & Observables",
        "slugs": [
            "luminosity-distance",
            "angular-diameter-distance",
            "distance-modulus",
            "flux-from-luminosity",
            "luminosity-from-flux",
        ],
    },
    {
        "title": "Cosmic Parameters",
        "slugs": [
            "critical-density",
            "deceleration-parameter",
            "matter-radiation-equality",
        ],
    },
    {
        "title": "Gravity & Orbits",
        "slugs": [
            "schwarzschild-radius",
            "escape-velocity",
            "orbital-period-kepler",
            "central-mass-kepler",
        ],
    },
    {
        "title": "Radiation & Thermal Physics",
        "slugs": [
            "wien-peak",
            "cmb-photon-density",
        ],
    },
]


COSMOLOGY_FORMULA_DESCRIPTIONS = {
    "hubble-law": "Estimate recession velocity from distance and the Hubble constant.",
    "distance-redshift": "Approximate cosmological distance from redshift at low z.",
    "lookback-time-small-z": "Estimate how far back in time light was emitted for small redshift.",
    "age-from-hubble": "Get a quick universe age estimate from H0.",
    "scale-factor-to-redshift": "Convert cosmic scale factor to redshift.",
    "redshift-to-scale-factor": "Convert observed redshift into cosmic scale factor.",
    "luminosity-distance": "Compute luminosity distance from comoving distance and redshift.",
    "angular-diameter-distance": "Compute angular diameter distance from comoving distance.",
    "distance-modulus": "Translate distance in Mpc into astronomical distance modulus.",
    "flux-from-luminosity": "Infer observed flux from source luminosity and distance.",
    "luminosity-from-flux": "Recover intrinsic luminosity from observed flux and distance.",
    "critical-density": "Compute critical density for a flat-universe threshold.",
    "deceleration-parameter": "Estimate present-day deceleration parameter from density fractions.",
    "matter-radiation-equality": "Estimate redshift where matter and radiation densities match.",
    "schwarzschild-radius": "Find event-horizon radius for a non-rotating compact object.",
    "escape-velocity": "Compute escape speed from mass and radius.",
    "orbital-period-kepler": "Compute orbital period from semi-major axis and central mass.",
    "central-mass-kepler": "Infer central mass from orbital size and period.",
    "wien-peak": "Find blackbody peak wavelength from temperature.",
    "cmb-photon-density": "Estimate CMB photon number density from temperature.",
}
