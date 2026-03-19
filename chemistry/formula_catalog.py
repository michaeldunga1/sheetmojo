from math import exp, log10


N_A = 6.02214076e23
R_GAS = 0.082057
PLANCK_H = 6.62607015e-34
LIGHT_C = 2.99792458e8


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


def _moles_from_mass(d):
    _positive(d["M"], "Molar mass M")
    return d["m"] / d["M"]


def _molar_mass(d):
    _nonzero(d["n"], "Moles n")
    return d["m"] / d["n"]


def _molarity(d):
    _nonzero(d["V"], "Volume V")
    return d["n"] / d["V"]


def _dilution_v2(d):
    _nonzero(d["M2"], "Target molarity M2")
    return d["M1"] * d["V1"] / d["M2"]


def _dilution_m2(d):
    _nonzero(d["V2"], "Final volume V2")
    return d["M1"] * d["V1"] / d["V2"]


def _ph(d):
    _positive(d["H"], "[H+]")
    return -log10(d["H"])


def _poh(d):
    _positive(d["OH"], "[OH-]")
    return -log10(d["OH"])


def _h_from_ph(d):
    return 10 ** (-d["pH"])


def _oh_from_poh(d):
    return 10 ** (-d["pOH"])


def _percent_yield(d):
    _nonzero(d["theoretical"], "Theoretical yield")
    return (d["actual"] / d["theoretical"]) * 100


def _ideal_pressure(d):
    _nonzero(d["V"], "Volume V")
    return d["n"] * R_GAS * d["T"] / d["V"]


def _ideal_volume(d):
    _nonzero(d["P"], "Pressure P")
    return d["n"] * R_GAS * d["T"] / d["P"]


def _ideal_temperature(d):
    _nonzero(d["n"], "Moles n")
    return d["P"] * d["V"] / (d["n"] * R_GAS)


def _ideal_moles(d):
    _nonzero(d["T"], "Temperature T")
    return d["P"] * d["V"] / (R_GAS * d["T"])


def _combined_gas_p2(d):
    _nonzero(d["V2"], "V2")
    _nonzero(d["T1"], "T1")
    return d["P1"] * d["V1"] * d["T2"] / (d["T1"] * d["V2"])


def _combined_gas_v2(d):
    _nonzero(d["P2"], "P2")
    _nonzero(d["T1"], "T1")
    return d["P1"] * d["V1"] * d["T2"] / (d["T1"] * d["P2"])


def _half_life(d):
    _positive(d["k"], "Rate constant k")
    return 0.693 / d["k"]


def _first_order_concentration(d):
    _positive(d["A0"], "Initial concentration [A]0")
    _positive(d["k"], "Rate constant k")
    return d["A0"] * exp(-d["k"] * d["t"])


def _arrhenius_k2(d):
    _nonzero(d["T1"], "T1")
    _nonzero(d["T2"], "T2")
    return d["k1"] * exp((-d["Ea"] / 8.314462618) * ((1 / d["T2"]) - (1 / d["T1"])))


def _equilibrium_kc(d):
    _positive(d["A"], "[A]")
    _positive(d["B"], "[B]")
    _positive(d["C"], "[C]")
    _positive(d["D"], "[D]")
    return (d["C"] ** d["c"] * d["D"] ** d["d"]) / (d["A"] ** d["a"] * d["B"] ** d["b"])


def _gibbs(d):
    return d["dH"] - d["T"] * d["dS"]


def _photon_energy(d):
    _positive(d["f"], "Frequency f")
    return PLANCK_H * d["f"]


def _wavelength_from_frequency(d):
    _positive(d["f"], "Frequency f")
    return LIGHT_C / d["f"]


def _frequency_from_wavelength(d):
    _positive(d["lam"], "Wavelength lambda")
    return LIGHT_C / d["lam"]


def _de_broglie(d):
    _nonzero(d["m"], "Mass m")
    _nonzero(d["v"], "Velocity v")
    return PLANCK_H / (d["m"] * d["v"])


def _boiling_point_elevation(d):
    return d["i"] * d["Kb"] * d["m"]


def _freezing_point_depression(d):
    return d["i"] * d["Kf"] * d["m"]


CHEMISTRY_FORMULAS = {
    "moles-from-mass": {
        "title": "Moles from Mass",
        "latex": r"n = \frac{m}{M}",
        "fields": [{"name": "m", "label": "Mass m (g)"}, {"name": "M", "label": "Molar mass M (g/mol)"}],
        "compute": _moles_from_mass,
        "substitute": lambda d: f"n = ({_fmt(d['m'])}) / ({_fmt(d['M'])})",
        "answer_label": "n",
        "format_answer": _fmt,
    },
    "mass-from-moles": {
        "title": "Mass from Moles",
        "latex": r"m = nM",
        "fields": [{"name": "n", "label": "Moles n"}, {"name": "M", "label": "Molar mass M"}],
        "compute": lambda d: d["n"] * d["M"],
        "substitute": lambda d: f"m = ({_fmt(d['n'])}) * ({_fmt(d['M'])})",
        "answer_label": "m",
        "format_answer": _fmt,
    },
    "molar-mass": {
        "title": "Molar Mass",
        "latex": r"M = \frac{m}{n}",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "n", "label": "Moles n"}],
        "compute": _molar_mass,
        "substitute": lambda d: f"M = ({_fmt(d['m'])}) / ({_fmt(d['n'])})",
        "answer_label": "M",
        "format_answer": _fmt,
    },
    "particles-from-moles": {
        "title": "Particles from Moles",
        "latex": r"N = nN_A",
        "fields": [{"name": "n", "label": "Moles n"}],
        "compute": lambda d: d["n"] * N_A,
        "substitute": lambda d: f"N = ({_fmt(d['n'])}) * N_A",
        "answer_label": "N",
        "format_answer": _fmt,
    },
    "moles-from-particles": {
        "title": "Moles from Particles",
        "latex": r"n = \frac{N}{N_A}",
        "fields": [{"name": "N", "label": "Particles N"}],
        "compute": lambda d: d["N"] / N_A,
        "substitute": lambda d: "n = N / N_A",
        "answer_label": "n",
        "format_answer": _fmt,
    },
    "molarity": {
        "title": "Molarity",
        "latex": r"M = \frac{n}{V}",
        "fields": [{"name": "n", "label": "Moles n"}, {"name": "V", "label": "Volume V (L)"}],
        "compute": _molarity,
        "substitute": lambda d: f"M = ({_fmt(d['n'])}) / ({_fmt(d['V'])})",
        "answer_label": "M",
        "format_answer": _fmt,
    },
    "moles-from-molarity": {
        "title": "Moles from Molarity",
        "latex": r"n = MV",
        "fields": [{"name": "M", "label": "Molarity M"}, {"name": "V", "label": "Volume V"}],
        "compute": lambda d: d["M"] * d["V"],
        "substitute": lambda d: f"n = ({_fmt(d['M'])}) * ({_fmt(d['V'])})",
        "answer_label": "n",
        "format_answer": _fmt,
    },
    "dilution-final-volume": {
        "title": "Dilution (Find Final Volume)",
        "latex": r"M_1V_1 = M_2V_2",
        "fields": [{"name": "M1", "label": "M1"}, {"name": "V1", "label": "V1"}, {"name": "M2", "label": "M2"}],
        "compute": _dilution_v2,
        "substitute": lambda d: "V2 = (M1*V1)/M2",
        "answer_label": "V2",
        "format_answer": _fmt,
    },
    "dilution-final-molarity": {
        "title": "Dilution (Find Final Molarity)",
        "latex": r"M_1V_1 = M_2V_2",
        "fields": [{"name": "M1", "label": "M1"}, {"name": "V1", "label": "V1"}, {"name": "V2", "label": "V2"}],
        "compute": _dilution_m2,
        "substitute": lambda d: "M2 = (M1*V1)/V2",
        "answer_label": "M2",
        "format_answer": _fmt,
    },
    "ph-from-hplus": {
        "title": "pH from [H+]",
        "latex": r"\mathrm{pH} = -\log_{10}[H^+]",
        "fields": [{"name": "H", "label": "[H+]"}],
        "compute": _ph,
        "substitute": lambda d: "pH = -log10([H+])",
        "answer_label": "pH",
        "format_answer": _fmt,
    },
    "poh-from-ohminus": {
        "title": "pOH from [OH-]",
        "latex": r"\mathrm{pOH} = -\log_{10}[OH^-]",
        "fields": [{"name": "OH", "label": "[OH-]"}],
        "compute": _poh,
        "substitute": lambda d: "pOH = -log10([OH-])",
        "answer_label": "pOH",
        "format_answer": _fmt,
    },
    "hplus-from-ph": {
        "title": "[H+] from pH",
        "latex": r"[H^+] = 10^{-\mathrm{pH}}",
        "fields": [{"name": "pH", "label": "pH"}],
        "compute": _h_from_ph,
        "substitute": lambda d: "[H+] = 10^(-pH)",
        "answer_label": "[H+]",
        "format_answer": _fmt,
    },
    "ohminus-from-poh": {
        "title": "[OH-] from pOH",
        "latex": r"[OH^-] = 10^{-\mathrm{pOH}}",
        "fields": [{"name": "pOH", "label": "pOH"}],
        "compute": _oh_from_poh,
        "substitute": lambda d: "[OH-] = 10^(-pOH)",
        "answer_label": "[OH-]",
        "format_answer": _fmt,
    },
    "percent-yield": {
        "title": "Percent Yield",
        "latex": r"\%\text{yield} = \frac{\text{actual}}{\text{theoretical}}\times100",
        "fields": [{"name": "actual", "label": "Actual yield"}, {"name": "theoretical", "label": "Theoretical yield"}],
        "compute": _percent_yield,
        "substitute": lambda d: "%yield = (actual/theoretical)*100",
        "answer_label": "% yield",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "ideal-gas-pressure": {
        "title": "Ideal Gas Law (Find Pressure)",
        "latex": r"P = \frac{nRT}{V}",
        "fields": [{"name": "n", "label": "n (mol)"}, {"name": "T", "label": "T (K)"}, {"name": "V", "label": "V (L)"}],
        "compute": _ideal_pressure,
        "substitute": lambda d: f"P = (nRT)/V with R={_fmt(R_GAS)}",
        "answer_label": "P",
        "format_answer": _fmt,
    },
    "ideal-gas-volume": {
        "title": "Ideal Gas Law (Find Volume)",
        "latex": r"V = \frac{nRT}{P}",
        "fields": [{"name": "n", "label": "n (mol)"}, {"name": "T", "label": "T (K)"}, {"name": "P", "label": "P (atm)"}],
        "compute": _ideal_volume,
        "substitute": lambda d: f"V = (nRT)/P with R={_fmt(R_GAS)}",
        "answer_label": "V",
        "format_answer": _fmt,
    },
    "ideal-gas-temperature": {
        "title": "Ideal Gas Law (Find Temperature)",
        "latex": r"T = \frac{PV}{nR}",
        "fields": [{"name": "P", "label": "P (atm)"}, {"name": "V", "label": "V (L)"}, {"name": "n", "label": "n (mol)"}],
        "compute": _ideal_temperature,
        "substitute": lambda d: f"T = PV/(nR), R={_fmt(R_GAS)}",
        "answer_label": "T",
        "format_answer": _fmt,
    },
    "ideal-gas-moles": {
        "title": "Ideal Gas Law (Find Moles)",
        "latex": r"n = \frac{PV}{RT}",
        "fields": [{"name": "P", "label": "P (atm)"}, {"name": "V", "label": "V (L)"}, {"name": "T", "label": "T (K)"}],
        "compute": _ideal_moles,
        "substitute": lambda d: f"n = PV/(RT), R={_fmt(R_GAS)}",
        "answer_label": "n",
        "format_answer": _fmt,
    },
    "combined-gas-p2": {
        "title": "Combined Gas Law (Find P2)",
        "latex": r"\frac{P_1V_1}{T_1}=\frac{P_2V_2}{T_2}",
        "fields": [{"name": "P1", "label": "P1"}, {"name": "V1", "label": "V1"}, {"name": "T1", "label": "T1"}, {"name": "V2", "label": "V2"}, {"name": "T2", "label": "T2"}],
        "compute": _combined_gas_p2,
        "substitute": lambda d: "P2 = P1*V1*T2/(T1*V2)",
        "answer_label": "P2",
        "format_answer": _fmt,
    },
    "combined-gas-v2": {
        "title": "Combined Gas Law (Find V2)",
        "latex": r"\frac{P_1V_1}{T_1}=\frac{P_2V_2}{T_2}",
        "fields": [{"name": "P1", "label": "P1"}, {"name": "V1", "label": "V1"}, {"name": "T1", "label": "T1"}, {"name": "P2", "label": "P2"}, {"name": "T2", "label": "T2"}],
        "compute": _combined_gas_v2,
        "substitute": lambda d: "V2 = P1*V1*T2/(T1*P2)",
        "answer_label": "V2",
        "format_answer": _fmt,
    },
    "heat-energy": {
        "title": "Heat Energy",
        "latex": r"q = mc\Delta T",
        "fields": [{"name": "m", "label": "Mass m"}, {"name": "c", "label": "Specific heat c"}, {"name": "dT", "label": "Delta T"}],
        "compute": lambda d: d["m"] * d["c"] * d["dT"],
        "substitute": lambda d: "q = m*c*DeltaT",
        "answer_label": "q",
        "format_answer": _fmt,
    },
    "calorimetry-reaction-heat": {
        "title": "Calorimetry (Reaction Heat)",
        "latex": r"q_{\text{rxn}} = -q_{\text{solution}}",
        "fields": [{"name": "qsol", "label": "q_solution"}],
        "compute": lambda d: -d["qsol"],
        "substitute": lambda d: "q_rxn = -q_solution",
        "answer_label": "q_rxn",
        "format_answer": _fmt,
    },
    "first-order-half-life": {
        "title": "First-Order Half-Life",
        "latex": r"t_{1/2}=\frac{0.693}{k}",
        "fields": [{"name": "k", "label": "Rate constant k"}],
        "compute": _half_life,
        "substitute": lambda d: "t1/2 = 0.693 / k",
        "answer_label": "t1/2",
        "format_answer": _fmt,
    },
    "first-order-concentration": {
        "title": "First-Order Concentration vs Time",
        "latex": r"[A]_t=[A]_0e^{-kt}",
        "fields": [{"name": "A0", "label": "[A]0"}, {"name": "k", "label": "k"}, {"name": "t", "label": "t"}],
        "compute": _first_order_concentration,
        "substitute": lambda d: "[A]t = [A]0*e^(-kt)",
        "answer_label": "[A]t",
        "format_answer": _fmt,
    },
    "arrhenius-k2": {
        "title": "Arrhenius Equation (Find k2)",
        "latex": r"\ln\left(\frac{k_2}{k_1}\right)=-\frac{E_a}{R}\left(\frac{1}{T_2}-\frac{1}{T_1}\right)",
        "fields": [{"name": "k1", "label": "k1"}, {"name": "Ea", "label": "Ea (J/mol)"}, {"name": "T1", "label": "T1 (K)"}, {"name": "T2", "label": "T2 (K)"}],
        "compute": _arrhenius_k2,
        "substitute": lambda d: "k2 = k1*exp((-Ea/R)*(1/T2 - 1/T1))",
        "answer_label": "k2",
        "format_answer": _fmt,
    },
    "equilibrium-kc": {
        "title": "Equilibrium Constant Kc",
        "latex": r"K_c=\frac{[C]^c[D]^d}{[A]^a[B]^b}",
        "fields": [
            {"name": "A", "label": "[A]"},
            {"name": "B", "label": "[B]"},
            {"name": "C", "label": "[C]"},
            {"name": "D", "label": "[D]"},
            {"name": "a", "label": "a", "type": "integer", "min": 1},
            {"name": "b", "label": "b", "type": "integer", "min": 1},
            {"name": "c", "label": "c", "type": "integer", "min": 1},
            {"name": "d", "label": "d", "type": "integer", "min": 1},
        ],
        "compute": _equilibrium_kc,
        "substitute": lambda d: "Kc = ([C]^c[D]^d)/([A]^a[B]^b)",
        "answer_label": "Kc",
        "format_answer": _fmt,
    },
    "gibbs-free-energy": {
        "title": "Gibbs Free Energy",
        "latex": r"\Delta G=\Delta H-T\Delta S",
        "fields": [{"name": "dH", "label": "Delta H"}, {"name": "T", "label": "T (K)"}, {"name": "dS", "label": "Delta S"}],
        "compute": _gibbs,
        "substitute": lambda d: "Delta G = Delta H - T*Delta S",
        "answer_label": "Delta G",
        "format_answer": _fmt,
    },
    "photon-energy": {
        "title": "Photon Energy from Frequency",
        "latex": r"E=hf",
        "fields": [{"name": "f", "label": "Frequency f (Hz)"}],
        "compute": _photon_energy,
        "substitute": lambda d: "E = h*f",
        "answer_label": "E",
        "format_answer": _fmt,
    },
    "wavelength-from-frequency": {
        "title": "Wavelength from Frequency",
        "latex": r"\lambda=\frac{c}{f}",
        "fields": [{"name": "f", "label": "Frequency f (Hz)"}],
        "compute": _wavelength_from_frequency,
        "substitute": lambda d: "lambda = c/f",
        "answer_label": "lambda",
        "format_answer": _fmt,
    },
    "frequency-from-wavelength": {
        "title": "Frequency from Wavelength",
        "latex": r"f=\frac{c}{\lambda}",
        "fields": [{"name": "lam", "label": "Wavelength lambda (m)"}],
        "compute": _frequency_from_wavelength,
        "substitute": lambda d: "f = c/lambda",
        "answer_label": "f",
        "format_answer": _fmt,
    },
    "de-broglie-wavelength": {
        "title": "de Broglie Wavelength",
        "latex": r"\lambda=\frac{h}{mv}",
        "fields": [{"name": "m", "label": "Particle mass m"}, {"name": "v", "label": "Particle speed v"}],
        "compute": _de_broglie,
        "substitute": lambda d: "lambda = h/(m*v)",
        "answer_label": "lambda",
        "format_answer": _fmt,
    },
    "boiling-point-elevation": {
        "title": "Boiling Point Elevation",
        "latex": r"\Delta T_b = iK_bm",
        "fields": [{"name": "i", "label": "van't Hoff factor i"}, {"name": "Kb", "label": "Kb"}, {"name": "m", "label": "Molality m"}],
        "compute": _boiling_point_elevation,
        "substitute": lambda d: "Delta Tb = i*Kb*m",
        "answer_label": "Delta Tb",
        "format_answer": _fmt,
    },
    "freezing-point-depression": {
        "title": "Freezing Point Depression",
        "latex": r"\Delta T_f = iK_fm",
        "fields": [{"name": "i", "label": "van't Hoff factor i"}, {"name": "Kf", "label": "Kf"}, {"name": "m", "label": "Molality m"}],
        "compute": _freezing_point_depression,
        "substitute": lambda d: "Delta Tf = i*Kf*m",
        "answer_label": "Delta Tf",
        "format_answer": _fmt,
    },
}


CHEMISTRY_FORMULA_GROUPS = [
    {
        "title": "Stoichiometry & Mole Concepts",
        "slugs": [
            "moles-from-mass",
            "mass-from-moles",
            "molar-mass",
            "particles-from-moles",
            "moles-from-particles",
            "percent-yield",
        ],
    },
    {
        "title": "Solutions & Acid-Base",
        "slugs": [
            "molarity",
            "moles-from-molarity",
            "dilution-final-volume",
            "dilution-final-molarity",
            "ph-from-hplus",
            "poh-from-ohminus",
            "hplus-from-ph",
            "ohminus-from-poh",
        ],
    },
    {
        "title": "Gases",
        "slugs": [
            "ideal-gas-pressure",
            "ideal-gas-volume",
            "ideal-gas-temperature",
            "ideal-gas-moles",
            "combined-gas-p2",
            "combined-gas-v2",
        ],
    },
    {
        "title": "Thermochemistry & Kinetics",
        "slugs": [
            "heat-energy",
            "calorimetry-reaction-heat",
            "first-order-half-life",
            "first-order-concentration",
            "arrhenius-k2",
        ],
    },
    {
        "title": "Equilibrium & Thermodynamics",
        "slugs": ["equilibrium-kc", "gibbs-free-energy"],
    },
    {
        "title": "Atomic & Colligative Properties",
        "slugs": [
            "photon-energy",
            "wavelength-from-frequency",
            "frequency-from-wavelength",
            "de-broglie-wavelength",
            "boiling-point-elevation",
            "freezing-point-depression",
        ],
    },
]


CHEMISTRY_FORMULA_DESCRIPTIONS = {
    "moles-from-mass": "Convert sample mass into moles using molar mass.",
    "mass-from-moles": "Recover sample mass from moles and molar mass.",
    "molar-mass": "Find molar mass from mass and amount of substance.",
    "particles-from-moles": "Convert moles into particles using Avogadro's constant.",
    "moles-from-particles": "Convert particle count into moles.",
    "molarity": "Compute solution concentration in moles per liter.",
    "moles-from-molarity": "Find dissolved moles from molarity and volume.",
    "dilution-final-volume": "Solve dilution problems for the new solution volume.",
    "dilution-final-molarity": "Solve dilution problems for the new concentration.",
    "ph-from-hplus": "Compute pH from hydrogen ion concentration.",
    "poh-from-ohminus": "Compute pOH from hydroxide ion concentration.",
    "hplus-from-ph": "Recover hydrogen ion concentration from pH.",
    "ohminus-from-poh": "Recover hydroxide ion concentration from pOH.",
    "percent-yield": "Compare actual product to theoretical yield.",
    "ideal-gas-pressure": "Find pressure from the ideal gas law.",
    "ideal-gas-volume": "Find gas volume from the ideal gas law.",
    "ideal-gas-temperature": "Find gas temperature from the ideal gas law.",
    "ideal-gas-moles": "Find amount of gas from pressure, volume, and temperature.",
    "combined-gas-p2": "Compute the final pressure in a changing gas system.",
    "combined-gas-v2": "Compute the final volume in a changing gas system.",
    "heat-energy": "Compute heat transferred from mass, heat capacity, and temperature change.",
    "calorimetry-reaction-heat": "Estimate reaction heat from calorimetry measurements.",
    "first-order-half-life": "Compute half-life for a first-order reaction.",
    "first-order-concentration": "Predict concentration over time for first-order kinetics.",
    "arrhenius-k2": "Relate reaction rate constants at two temperatures.",
    "equilibrium-kc": "Compute the concentration equilibrium constant.",
    "gibbs-free-energy": "Determine spontaneity from enthalpy, entropy, and temperature.",
    "photon-energy": "Compute photon energy from frequency.",
    "wavelength-from-frequency": "Convert frequency into wavelength.",
    "frequency-from-wavelength": "Convert wavelength into frequency.",
    "de-broglie-wavelength": "Compute matter wavelength from momentum.",
    "boiling-point-elevation": "Estimate boiling point increase from a dissolved solute.",
    "freezing-point-depression": "Estimate freezing point decrease from a dissolved solute.",
}
