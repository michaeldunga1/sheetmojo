from math import exp, log, log10


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


def _population_density(d):
    _nonzero(d["area"], "Area")
    return d["population"] / d["area"]


def _population_growth_exponential(d):
    return d["N0"] * exp(d["r"] * d["t"])


def _doubling_time(d):
    _positive(d["r"], "Growth rate r")
    return 0.693 / d["r"]


def _relative_growth_rate(d):
    _positive(d["W1"], "Initial biomass W1")
    _positive(d["W2"], "Final biomass W2")
    _nonzero(d["t2"] - d["t1"], "Time interval")
    return (log(d["W2"]) - log(d["W1"])) / (d["t2"] - d["t1"])


def _percent_growth_rate(d):
    _nonzero(d["initial"], "Initial value")
    return (d["final"] - d["initial"]) / d["initial"] * 100


def _logistic_population(d):
    _positive(d["N0"], "Initial population N0")
    _positive(d["K"], "Carrying capacity K")
    return d["K"] / (1 + ((d["K"] - d["N0"]) / d["N0"]) * exp(-d["r"] * d["t"]))


def _survivorship(d):
    _nonzero(d["initial_population"], "Initial population")
    return d["survivors"] / d["initial_population"] * 100


def _mortality_rate(d):
    _nonzero(d["initial_population"], "Initial population")
    return d["deaths"] / d["initial_population"] * 100


def _birth_rate(d):
    _nonzero(d["population"], "Population")
    return d["births"] / d["population"] * 1000


def _death_rate(d):
    _nonzero(d["population"], "Population")
    return d["deaths"] / d["population"] * 1000


def _net_reproductive_rate(d):
    _nonzero(d["parents"] , "Parents")
    return d["offspring_surviving"] / d["parents"]


def _hardy_q(d):
    return 1 - d["p"]


def _hardy_p2(d):
    return d["p"] ** 2


def _hardy_2pq(d):
    return 2 * d["p"] * d["q"]


def _hardy_q2(d):
    return d["q"] ** 2


def _allele_frequency_p(d):
    _nonzero(d["N"], "Population size N")
    return (2 * d["AA"] + d["Aa"]) / (2 * d["N"])


def _allele_frequency_q(d):
    _nonzero(d["N"], "Population size N")
    return (2 * d["aa"] + d["Aa"]) / (2 * d["N"])


def _heterozygosity(d):
    return 2 * d["p"] * d["q"]


def _dominant_phenotype_frequency(d):
    return d["p"] ** 2 + 2 * d["p"] * d["q"]


def _mitotic_index(d):
    _nonzero(d["total_cells"], "Total cells")
    return d["dividing_cells"] / d["total_cells"] * 100


def _magnification(d):
    _nonzero(d["actual_size"], "Actual size")
    return d["image_size"] / d["actual_size"]


def _water_potential(d):
    return d["solute_potential"] + d["pressure_potential"]


def _osmotic_potential(d):
    return -d["i"] * d["C"] * d["R"] * d["T"]


def _surface_area_to_volume_sphere(d):
    _positive(d["r"], "Radius r")
    return (4 * 3.141592653589793 * d["r"] ** 2) / ((4 / 3) * 3.141592653589793 * d["r"] ** 3)


def _bacterial_population(d):
    return d["N0"] * (2 ** d["n"])


def _number_of_generations(d):
    _positive(d["Nt"], "Final population Nt")
    _positive(d["N0"], "Initial population N0")
    return log(d["Nt"] / d["N0"], 2)


def _generation_time(d):
    _nonzero(d["n"], "Number of generations n")
    return d["t"] / d["n"]


def _specific_growth_rate(d):
    _positive(d["N0"], "Initial population N0")
    _positive(d["Nt"], "Final population Nt")
    _nonzero(d["t"], "Time t")
    return (log(d["Nt"]) - log(d["N0"])) / d["t"]


def _enzyme_q10(d):
    _nonzero(d["T2"] - d["T1"], "Temperature interval")
    _positive(d["R1"], "Rate R1")
    _positive(d["R2"], "Rate R2")
    return (d["R2"] / d["R1"]) ** (10 / (d["T2"] - d["T1"]))


def _photosynthetic_efficiency(d):
    _nonzero(d["solar_energy_input"], "Solar energy input")
    return d["biomass_energy_output"] / d["solar_energy_input"] * 100


def _npp(d):
    return d["gpp"] - d["respiration"]


def _assimilation_efficiency(d):
    _nonzero(d["ingested_energy"], "Ingested energy")
    return d["assimilated_energy"] / d["ingested_energy"] * 100


def _production_efficiency(d):
    _nonzero(d["assimilated_energy"], "Assimilated energy")
    return d["production_energy"] / d["assimilated_energy"] * 100


def _ecological_efficiency(d):
    _nonzero(d["energy_prev_trophic"], "Energy in previous trophic level")
    return d["energy_next_trophic"] / d["energy_prev_trophic"] * 100


def _leaf_area_index(d):
    _nonzero(d["ground_area"], "Ground area")
    return d["leaf_area"] / d["ground_area"]


def _bmi(d):
    _positive(d["height_m"], "Height")
    return d["mass_kg"] / (d["height_m"] ** 2)


def _bmr_simple(d):
    return 24 * d["mass_kg"]


def _shannon_diversity_3(d):
    total = d["n1"] + d["n2"] + d["n3"]
    _positive(total, "Total individuals")
    result = 0
    for value in (d["n1"], d["n2"], d["n3"]):
        if value > 0:
            p = value / total
            result -= p * log(p)
    return result


def _species_evenness_3(d):
    total = d["n1"] + d["n2"] + d["n3"]
    _positive(total, "Total individuals")
    h = _shannon_diversity_3(d)
    return h / log(3)


def _percent_composition(d):
    _nonzero(d["total"], "Total")
    return d["part"] / d["total"] * 100


def _dilution_factor(d):
    _nonzero(d["sample_volume"], "Sample volume")
    return d["total_volume"] / d["sample_volume"]


def _cell_viability(d):
    _nonzero(d["live_cells"] + d["dead_cells"], "Total cells")
    return d["live_cells"] / (d["live_cells"] + d["dead_cells"]) * 100


def _doublings_from_cf(d):
    _positive(d["initial_count"], "Initial count")
    _positive(d["final_count"], "Final count")
    return log10(d["final_count"] / d["initial_count"]) / log10(2)


BIOLOGY_FORMULAS = {
    "population-density": {
        "title": "Population Density",
        "latex": r"D=\frac{N}{A}",
        "fields": [{"name": "population", "label": "Population N"}, {"name": "area", "label": "Area A"}],
        "compute": _population_density,
        "substitute": lambda d: "D = population/area",
        "answer_label": "D",
        "format_answer": _fmt,
    },
    "population-growth-exponential": {
        "title": "Exponential Population Growth",
        "latex": r"N_t=N_0e^{rt}",
        "fields": [{"name": "N0", "label": "Initial population N0"}, {"name": "r", "label": "Growth rate r"}, {"name": "t", "label": "Time t"}],
        "compute": _population_growth_exponential,
        "substitute": lambda d: "Nt = N0*e^(r*t)",
        "answer_label": "Nt",
        "format_answer": _fmt,
    },
    "doubling-time": {
        "title": "Doubling Time",
        "latex": r"t_d=\frac{0.693}{r}",
        "fields": [{"name": "r", "label": "Growth rate r"}],
        "compute": _doubling_time,
        "substitute": lambda d: "td = 0.693/r",
        "answer_label": "td",
        "format_answer": _fmt,
    },
    "relative-growth-rate": {
        "title": "Relative Growth Rate",
        "latex": r"RGR=\frac{\ln W_2-\ln W_1}{t_2-t_1}",
        "fields": [{"name": "W1", "label": "Initial biomass W1"}, {"name": "W2", "label": "Final biomass W2"}, {"name": "t1", "label": "Initial time t1"}, {"name": "t2", "label": "Final time t2"}],
        "compute": _relative_growth_rate,
        "substitute": lambda d: "RGR = (lnW2-lnW1)/(t2-t1)",
        "answer_label": "RGR",
        "format_answer": _fmt,
    },
    "percent-growth-rate": {
        "title": "Percent Growth Rate",
        "latex": r"\%G=\frac{Final-Initial}{Initial}\times100",
        "fields": [{"name": "initial", "label": "Initial"}, {"name": "final", "label": "Final"}],
        "compute": _percent_growth_rate,
        "substitute": lambda d: "%G = (final-initial)/initial*100",
        "answer_label": "Growth rate",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "logistic-population": {
        "title": "Logistic Population Growth",
        "latex": r"N_t=\frac{K}{1+\left(\frac{K-N_0}{N_0}\right)e^{-rt}}",
        "fields": [{"name": "N0", "label": "Initial population N0"}, {"name": "K", "label": "Carrying capacity K"}, {"name": "r", "label": "Growth rate r"}, {"name": "t", "label": "Time t"}],
        "compute": _logistic_population,
        "substitute": lambda d: "Logistic growth formula",
        "answer_label": "Nt",
        "format_answer": _fmt,
    },
    "survivorship": {
        "title": "Survivorship (%)",
        "latex": r"S=\frac{Survivors}{Initial}\times100",
        "fields": [{"name": "survivors", "label": "Survivors"}, {"name": "initial_population", "label": "Initial population"}],
        "compute": _survivorship,
        "substitute": lambda d: "S = survivors/initial*100",
        "answer_label": "Survivorship",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "mortality-rate": {
        "title": "Mortality Rate (%)",
        "latex": r"M=\frac{Deaths}{Initial}\times100",
        "fields": [{"name": "deaths", "label": "Deaths"}, {"name": "initial_population", "label": "Initial population"}],
        "compute": _mortality_rate,
        "substitute": lambda d: "M = deaths/initial*100",
        "answer_label": "Mortality rate",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "birth-rate": {
        "title": "Birth Rate",
        "latex": r"B=\frac{Births}{Population}\times1000",
        "fields": [{"name": "births", "label": "Births"}, {"name": "population", "label": "Population"}],
        "compute": _birth_rate,
        "substitute": lambda d: "B = births/population*1000",
        "answer_label": "Birth rate",
        "format_answer": _fmt,
    },
    "death-rate": {
        "title": "Death Rate",
        "latex": r"D=\frac{Deaths}{Population}\times1000",
        "fields": [{"name": "deaths", "label": "Deaths"}, {"name": "population", "label": "Population"}],
        "compute": _death_rate,
        "substitute": lambda d: "D = deaths/population*1000",
        "answer_label": "Death rate",
        "format_answer": _fmt,
    },
    "net-reproductive-rate": {
        "title": "Net Reproductive Rate",
        "latex": r"R_0=\frac{Offspring\ Surviving}{Parents}",
        "fields": [{"name": "offspring_surviving", "label": "Offspring surviving"}, {"name": "parents", "label": "Parents"}],
        "compute": _net_reproductive_rate,
        "substitute": lambda d: "R0 = offspring_surviving/parents",
        "answer_label": "R0",
        "format_answer": _fmt,
    },
    "hardy-weinberg-q": {
        "title": "Hardy-Weinberg q from p",
        "latex": r"q=1-p",
        "fields": [{"name": "p", "label": "Allele frequency p"}],
        "compute": _hardy_q,
        "substitute": lambda d: "q = 1-p",
        "answer_label": "q",
        "format_answer": _fmt,
    },
    "hardy-weinberg-p2": {
        "title": "Hardy-Weinberg Homozygous Dominant",
        "latex": r"p^2",
        "fields": [{"name": "p", "label": "Allele frequency p"}],
        "compute": _hardy_p2,
        "substitute": lambda d: "p^2",
        "answer_label": "p^2",
        "format_answer": _fmt,
    },
    "hardy-weinberg-2pq": {
        "title": "Hardy-Weinberg Heterozygous",
        "latex": r"2pq",
        "fields": [{"name": "p", "label": "Allele frequency p"}, {"name": "q", "label": "Allele frequency q"}],
        "compute": _hardy_2pq,
        "substitute": lambda d: "2pq",
        "answer_label": "2pq",
        "format_answer": _fmt,
    },
    "hardy-weinberg-q2": {
        "title": "Hardy-Weinberg Homozygous Recessive",
        "latex": r"q^2",
        "fields": [{"name": "q", "label": "Allele frequency q"}],
        "compute": _hardy_q2,
        "substitute": lambda d: "q^2",
        "answer_label": "q^2",
        "format_answer": _fmt,
    },
    "allele-frequency-p": {
        "title": "Allele Frequency p",
        "latex": r"p=\frac{2AA+Aa}{2N}",
        "fields": [{"name": "AA", "label": "AA count"}, {"name": "Aa", "label": "Aa count"}, {"name": "N", "label": "Population size N"}],
        "compute": _allele_frequency_p,
        "substitute": lambda d: "p=(2AA+Aa)/(2N)",
        "answer_label": "p",
        "format_answer": _fmt,
    },
    "allele-frequency-q": {
        "title": "Allele Frequency q",
        "latex": r"q=\frac{2aa+Aa}{2N}",
        "fields": [{"name": "aa", "label": "aa count"}, {"name": "Aa", "label": "Aa count"}, {"name": "N", "label": "Population size N"}],
        "compute": _allele_frequency_q,
        "substitute": lambda d: "q=(2aa+Aa)/(2N)",
        "answer_label": "q",
        "format_answer": _fmt,
    },
    "heterozygosity": {
        "title": "Expected Heterozygosity",
        "latex": r"H=2pq",
        "fields": [{"name": "p", "label": "p"}, {"name": "q", "label": "q"}],
        "compute": _heterozygosity,
        "substitute": lambda d: "H=2pq",
        "answer_label": "H",
        "format_answer": _fmt,
    },
    "dominant-phenotype-frequency": {
        "title": "Dominant Phenotype Frequency",
        "latex": r"p^2+2pq",
        "fields": [{"name": "p", "label": "p"}, {"name": "q", "label": "q"}],
        "compute": _dominant_phenotype_frequency,
        "substitute": lambda d: "p^2+2pq",
        "answer_label": "Dominant phenotype",
        "format_answer": _fmt,
    },
    "mitotic-index": {
        "title": "Mitotic Index",
        "latex": r"MI=\frac{Dividing\ Cells}{Total\ Cells}\times100",
        "fields": [{"name": "dividing_cells", "label": "Dividing cells"}, {"name": "total_cells", "label": "Total cells"}],
        "compute": _mitotic_index,
        "substitute": lambda d: "MI = dividing/total*100",
        "answer_label": "Mitotic index",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "magnification": {
        "title": "Magnification",
        "latex": r"M=\frac{Image\ Size}{Actual\ Size}",
        "fields": [{"name": "image_size", "label": "Image size"}, {"name": "actual_size", "label": "Actual size"}],
        "compute": _magnification,
        "substitute": lambda d: "M = image_size/actual_size",
        "answer_label": "M",
        "format_answer": _fmt,
    },
    "water-potential": {
        "title": "Water Potential",
        "latex": r"\Psi=\Psi_s+\Psi_p",
        "fields": [{"name": "solute_potential", "label": "Solute potential"}, {"name": "pressure_potential", "label": "Pressure potential"}],
        "compute": _water_potential,
        "substitute": lambda d: "Psi = Psi_s + Psi_p",
        "answer_label": "Psi",
        "format_answer": _fmt,
    },
    "osmotic-potential": {
        "title": "Osmotic Potential",
        "latex": r"\Psi_s=-iCRT",
        "fields": [{"name": "i", "label": "Ionization factor i"}, {"name": "C", "label": "Molar concentration C"}, {"name": "R", "label": "Gas constant R"}, {"name": "T", "label": "Temperature T"}],
        "compute": _osmotic_potential,
        "substitute": lambda d: "Psi_s = -iCRT",
        "answer_label": "Psi_s",
        "format_answer": _fmt,
    },
    "surface-area-to-volume-sphere": {
        "title": "Surface Area to Volume Ratio (Sphere)",
        "latex": r"\frac{SA}{V}=\frac{4\pi r^2}{\frac{4}{3}\pi r^3}",
        "fields": [{"name": "r", "label": "Radius r"}],
        "compute": _surface_area_to_volume_sphere,
        "substitute": lambda d: "SA/V for sphere",
        "answer_label": "SA:V",
        "format_answer": _fmt,
    },
    "bacterial-population": {
        "title": "Bacterial Population After n Generations",
        "latex": r"N_t=N_0\cdot2^n",
        "fields": [{"name": "N0", "label": "Initial population N0"}, {"name": "n", "label": "Number of generations n"}],
        "compute": _bacterial_population,
        "substitute": lambda d: "Nt = N0*2^n",
        "answer_label": "Nt",
        "format_answer": _fmt,
    },
    "number-of-generations": {
        "title": "Number of Generations",
        "latex": r"n=\log_2\left(\frac{N_t}{N_0}\right)",
        "fields": [{"name": "N0", "label": "Initial population N0"}, {"name": "Nt", "label": "Final population Nt"}],
        "compute": _number_of_generations,
        "substitute": lambda d: "n = log2(Nt/N0)",
        "answer_label": "n",
        "format_answer": _fmt,
    },
    "generation-time": {
        "title": "Generation Time",
        "latex": r"g=\frac{t}{n}",
        "fields": [{"name": "t", "label": "Total time t"}, {"name": "n", "label": "Number of generations n"}],
        "compute": _generation_time,
        "substitute": lambda d: "g = t/n",
        "answer_label": "g",
        "format_answer": _fmt,
    },
    "specific-growth-rate": {
        "title": "Specific Growth Rate",
        "latex": r"\mu=\frac{\ln N_t-\ln N_0}{t}",
        "fields": [{"name": "N0", "label": "Initial population N0"}, {"name": "Nt", "label": "Final population Nt"}, {"name": "t", "label": "Time t"}],
        "compute": _specific_growth_rate,
        "substitute": lambda d: "mu = (lnNt-lnN0)/t",
        "answer_label": "mu",
        "format_answer": _fmt,
    },
    "enzyme-q10": {
        "title": "Enzyme Temperature Coefficient (Q10)",
        "latex": r"Q_{10}=\left(\frac{R_2}{R_1}\right)^{10/(T_2-T_1)}",
        "fields": [{"name": "R1", "label": "Rate R1"}, {"name": "R2", "label": "Rate R2"}, {"name": "T1", "label": "Temperature T1"}, {"name": "T2", "label": "Temperature T2"}],
        "compute": _enzyme_q10,
        "substitute": lambda d: "Q10 = (R2/R1)^(10/(T2-T1))",
        "answer_label": "Q10",
        "format_answer": _fmt,
    },
    "photosynthetic-efficiency": {
        "title": "Photosynthetic Efficiency",
        "latex": r"PE=\frac{Biomass\ Energy}{Solar\ Energy}\times100",
        "fields": [{"name": "biomass_energy_output", "label": "Biomass energy output"}, {"name": "solar_energy_input", "label": "Solar energy input"}],
        "compute": _photosynthetic_efficiency,
        "substitute": lambda d: "PE = biomass/solar*100",
        "answer_label": "PE",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "net-primary-productivity": {
        "title": "Net Primary Productivity",
        "latex": r"NPP=GPP-R",
        "fields": [{"name": "gpp", "label": "Gross primary productivity GPP"}, {"name": "respiration", "label": "Respiration R"}],
        "compute": _npp,
        "substitute": lambda d: "NPP = GPP-R",
        "answer_label": "NPP",
        "format_answer": _fmt,
    },
    "assimilation-efficiency": {
        "title": "Assimilation Efficiency",
        "latex": r"AE=\frac{Assimilated}{Ingested}\times100",
        "fields": [{"name": "assimilated_energy", "label": "Assimilated energy"}, {"name": "ingested_energy", "label": "Ingested energy"}],
        "compute": _assimilation_efficiency,
        "substitute": lambda d: "AE = assimilated/ingested*100",
        "answer_label": "AE",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "production-efficiency": {
        "title": "Production Efficiency",
        "latex": r"PE=\frac{Production}{Assimilated}\times100",
        "fields": [{"name": "production_energy", "label": "Production energy"}, {"name": "assimilated_energy", "label": "Assimilated energy"}],
        "compute": _production_efficiency,
        "substitute": lambda d: "PE = production/assimilated*100",
        "answer_label": "PE",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "ecological-efficiency": {
        "title": "Ecological Efficiency",
        "latex": r"EE=\frac{E_{next}}{E_{prev}}\times100",
        "fields": [{"name": "energy_next_trophic", "label": "Energy next trophic level"}, {"name": "energy_prev_trophic", "label": "Energy previous trophic level"}],
        "compute": _ecological_efficiency,
        "substitute": lambda d: "EE = next/prev*100",
        "answer_label": "EE",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "leaf-area-index": {
        "title": "Leaf Area Index",
        "latex": r"LAI=\frac{Leaf\ Area}{Ground\ Area}",
        "fields": [{"name": "leaf_area", "label": "Leaf area"}, {"name": "ground_area", "label": "Ground area"}],
        "compute": _leaf_area_index,
        "substitute": lambda d: "LAI = leaf_area/ground_area",
        "answer_label": "LAI",
        "format_answer": _fmt,
    },
    "body-mass-index": {
        "title": "Body Mass Index",
        "latex": r"BMI=\frac{m}{h^2}",
        "fields": [{"name": "mass_kg", "label": "Mass (kg)"}, {"name": "height_m", "label": "Height (m)"}],
        "compute": _bmi,
        "substitute": lambda d: "BMI = mass/height^2",
        "answer_label": "BMI",
        "format_answer": _fmt,
    },
    "basal-metabolic-rate-simple": {
        "title": "Basal Metabolic Rate (Simple)",
        "latex": r"BMR\approx24\times mass_{kg}",
        "fields": [{"name": "mass_kg", "label": "Mass (kg)"}],
        "compute": _bmr_simple,
        "substitute": lambda d: "BMR approx 24*mass",
        "answer_label": "BMR (kcal/day)",
        "format_answer": _fmt,
    },
    "shannon-diversity-index-3": {
        "title": "Shannon Diversity Index (3 Species)",
        "latex": r"H'=-\sum p_i\ln p_i",
        "fields": [{"name": "n1", "label": "Species 1 count"}, {"name": "n2", "label": "Species 2 count"}, {"name": "n3", "label": "Species 3 count"}],
        "compute": _shannon_diversity_3,
        "substitute": lambda d: "H' = -sum(pi ln pi)",
        "answer_label": "H'",
        "format_answer": _fmt,
    },
    "species-evenness-3": {
        "title": "Species Evenness (3 Species)",
        "latex": r"E=\frac{H'}{\ln S}",
        "fields": [{"name": "n1", "label": "Species 1 count"}, {"name": "n2", "label": "Species 2 count"}, {"name": "n3", "label": "Species 3 count"}],
        "compute": _species_evenness_3,
        "substitute": lambda d: "E = H'/ln(3)",
        "answer_label": "E",
        "format_answer": _fmt,
    },
    "percent-composition": {
        "title": "Percent Composition",
        "latex": r"\%=\frac{Part}{Total}\times100",
        "fields": [{"name": "part", "label": "Part"}, {"name": "total", "label": "Total"}],
        "compute": _percent_composition,
        "substitute": lambda d: "% = part/total*100",
        "answer_label": "Percent composition",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "dilution-factor": {
        "title": "Dilution Factor",
        "latex": r"DF=\frac{Total\ Volume}{Sample\ Volume}",
        "fields": [{"name": "total_volume", "label": "Total volume"}, {"name": "sample_volume", "label": "Sample volume"}],
        "compute": _dilution_factor,
        "substitute": lambda d: "DF = total_volume/sample_volume",
        "answer_label": "DF",
        "format_answer": _fmt,
    },
    "cell-viability": {
        "title": "Cell Viability",
        "latex": r"Viability=\frac{Live}{Live+Dead}\times100",
        "fields": [{"name": "live_cells", "label": "Live cells"}, {"name": "dead_cells", "label": "Dead cells"}],
        "compute": _cell_viability,
        "substitute": lambda d: "Viability = live/(live+dead)*100",
        "answer_label": "Viability",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "population-doublings": {
        "title": "Population Doublings",
        "latex": r"PD=\log_2\left(\frac{N_f}{N_i}\right)",
        "fields": [{"name": "initial_count", "label": "Initial count"}, {"name": "final_count", "label": "Final count"}],
        "compute": _doublings_from_cf,
        "substitute": lambda d: "PD = log2(final/initial)",
        "answer_label": "PD",
        "format_answer": _fmt,
    },
}


BIOLOGY_FORMULA_GROUPS = [
    {
        "title": "Population Ecology",
        "slugs": [
            "population-density",
            "population-growth-exponential",
            "doubling-time",
            "relative-growth-rate",
            "percent-growth-rate",
            "logistic-population",
            "survivorship",
            "mortality-rate",
            "birth-rate",
            "death-rate",
            "net-reproductive-rate",
        ],
    },
    {
        "title": "Genetics & Evolution",
        "slugs": [
            "hardy-weinberg-q",
            "hardy-weinberg-p2",
            "hardy-weinberg-2pq",
            "hardy-weinberg-q2",
            "allele-frequency-p",
            "allele-frequency-q",
            "heterozygosity",
            "dominant-phenotype-frequency",
        ],
    },
    {
        "title": "Cells & Osmosis",
        "slugs": [
            "mitotic-index",
            "magnification",
            "water-potential",
            "osmotic-potential",
            "surface-area-to-volume-sphere",
        ],
    },
    {
        "title": "Microbiology & Growth",
        "slugs": [
            "bacterial-population",
            "number-of-generations",
            "generation-time",
            "specific-growth-rate",
            "enzyme-q10",
            "dilution-factor",
            "cell-viability",
            "population-doublings",
        ],
    },
    {
        "title": "Ecosystems & Productivity",
        "slugs": [
            "photosynthetic-efficiency",
            "net-primary-productivity",
            "assimilation-efficiency",
            "production-efficiency",
            "ecological-efficiency",
            "leaf-area-index",
            "shannon-diversity-index-3",
            "species-evenness-3",
        ],
    },
    {
        "title": "Human Biology & Composition",
        "slugs": [
            "body-mass-index",
            "basal-metabolic-rate-simple",
            "percent-composition",
        ],
    },
]


BIOLOGY_FORMULA_DESCRIPTIONS = {
    "population-density": "Compute individuals per unit area.",
    "population-growth-exponential": "Project growth under exponential assumptions.",
    "doubling-time": "Estimate population doubling time from growth rate.",
    "relative-growth-rate": "Measure growth relative to initial population.",
    "percent-growth-rate": "Express growth as a percentage.",
    "logistic-population": "Model growth with carrying-capacity limits.",
    "survivorship": "Compute survival percentage from cohorts.",
    "mortality-rate": "Compute death proportion in a population.",
    "birth-rate": "Compute birth proportion in a population.",
    "death-rate": "Compute death proportion in a population.",
    "net-reproductive-rate": "Measure generational replacement potential.",
    "hardy-weinberg-q": "Find recessive allele frequency from dominant frequency.",
    "hardy-weinberg-p2": "Compute homozygous dominant genotype frequency.",
    "hardy-weinberg-2pq": "Compute heterozygous genotype frequency.",
    "hardy-weinberg-q2": "Compute homozygous recessive genotype frequency.",
    "allele-frequency-p": "Compute p allele frequency from genotype counts.",
    "allele-frequency-q": "Compute q allele frequency from genotype counts.",
    "heterozygosity": "Measure expected heterozygous proportion.",
    "dominant-phenotype-frequency": "Compute dominant phenotype frequency.",
    "mitotic-index": "Measure dividing cells as a percentage.",
    "magnification": "Relate image size to actual specimen size.",
    "water-potential": "Compute total water potential in a cell system.",
    "osmotic-potential": "Estimate osmotic component of water potential.",
    "surface-area-to-volume-sphere": "Compute SA:V ratio for a spherical cell.",
    "bacterial-population": "Estimate population after binary fission cycles.",
    "number-of-generations": "Compute generation count from initial and final cells.",
    "generation-time": "Estimate time per generation.",
    "specific-growth-rate": "Compute microbial specific growth rate.",
    "enzyme-q10": "Estimate rate change per 10 C temperature shift.",
    "photosynthetic-efficiency": "Compute photosynthetic conversion efficiency.",
    "net-primary-productivity": "Compute biomass gain after respiration losses.",
    "assimilation-efficiency": "Compute assimilated fraction of ingested energy.",
    "production-efficiency": "Compute production fraction of assimilated energy.",
    "ecological-efficiency": "Compute trophic transfer efficiency.",
    "leaf-area-index": "Estimate canopy density from leaf and ground area.",
    "body-mass-index": "Compute BMI from mass and height.",
    "basal-metabolic-rate-simple": "Estimate baseline metabolic energy expenditure.",
    "shannon-diversity-index-3": "Compute species diversity index for three groups.",
    "species-evenness-3": "Compute diversity evenness for three groups.",
    "percent-composition": "Compute percent share of a component.",
    "dilution-factor": "Compute sample dilution factor.",
    "cell-viability": "Compute percentage of live cells.",
    "population-doublings": "Compute total doublings across a culture period.",
}
