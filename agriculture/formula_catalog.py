from math import exp


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


def _yield_per_hectare(d):
    _nonzero(d["area_ha"], "Area")
    return d["total_yield_ton"] / d["area_ha"]


def _total_yield(d):
    return d["yield_per_ha"] * d["area_ha"]


def _seed_rate_per_ha(d):
    _nonzero(d["area_ha"], "Area")
    return d["seed_total_kg"] / d["area_ha"]


def _seed_requirement_total(d):
    return d["seed_rate_kg_ha"] * d["area_ha"]


def _plant_population(d):
    _positive(d["row_spacing_m"], "Row spacing")
    _positive(d["plant_spacing_m"], "Plant spacing")
    return d["area_m2"] / (d["row_spacing_m"] * d["plant_spacing_m"])


def _fertilizer_required(d):
    _positive(d["fertilizer_n_percent"], "Fertilizer N percent")
    return d["n_required_kg_ha"] / (d["fertilizer_n_percent"] / 100)


def _nutrient_applied(d):
    return d["fertilizer_rate_kg_ha"] * (d["nutrient_percent"] / 100)


def _water_use_efficiency(d):
    _nonzero(d["water_used_mm"], "Water used")
    return d["yield_kg_ha"] / d["water_used_mm"]


def _irrigation_volume(d):
    # 1 mm over 1 ha = 10 m3
    return d["depth_mm"] * d["area_ha"] * 10


def _irrigation_time(d):
    _nonzero(d["discharge_m3_h"], "Discharge")
    return d["volume_m3"] / d["discharge_m3_h"]


def _field_efficiency(d):
    _nonzero(d["theoretical_field_capacity"], "Theoretical field capacity")
    return d["effective_field_capacity"] / d["theoretical_field_capacity"] * 100


def _theoretical_field_capacity(d):
    # ha/h = speed(km/h) * width(m) / 10
    return d["speed_km_h"] * d["implement_width_m"] / 10


def _effective_field_capacity(d):
    return d["theoretical_field_capacity"] * (d["field_efficiency_percent"] / 100)


def _feed_conversion_ratio(d):
    _nonzero(d["weight_gain_kg"], "Weight gain")
    return d["feed_intake_kg"] / d["weight_gain_kg"]


def _average_daily_gain(d):
    _nonzero(d["days"], "Days")
    return d["weight_gain_kg"] / d["days"]


def _stocking_rate(d):
    _nonzero(d["land_area_ha"], "Land area")
    return d["animals"] / d["land_area_ha"]


def _milk_yield_per_cow(d):
    _nonzero(d["number_of_cows"], "Number of cows")
    return d["total_milk_l_day"] / d["number_of_cows"]


def _mortality_rate(d):
    _nonzero(d["initial_animals"], "Initial animals")
    return d["deaths"] / d["initial_animals"] * 100


def _hatchability(d):
    _nonzero(d["fertile_eggs"], "Fertile eggs")
    return d["chicks_hatched"] / d["fertile_eggs"] * 100


def _harvest_index(d):
    _nonzero(d["biological_yield"], "Biological yield")
    return d["economic_yield"] / d["biological_yield"] * 100


def _cropping_intensity(d):
    _nonzero(d["net_sown_area"], "Net sown area")
    return d["gross_cropped_area"] / d["net_sown_area"] * 100


def _land_equivalent_ratio(d):
    return d["yield_intercrop_a"] / d["yield_sole_a"] + d["yield_intercrop_b"] / d["yield_sole_b"]


def _benefit_cost_ratio(d):
    _nonzero(d["total_cost"], "Total cost")
    return d["gross_return"] / d["total_cost"]


def _net_return(d):
    return d["gross_return"] - d["total_cost"]


def _gross_margin(d):
    return d["gross_return"] - d["variable_cost"]


def _return_on_investment(d):
    _nonzero(d["cost"], "Cost")
    return (d["profit"] / d["cost"]) * 100


def _soil_bulk_density(d):
    _nonzero(d["core_volume_cm3"], "Core volume")
    return d["oven_dry_mass_g"] / d["core_volume_cm3"]


def _soil_porosity(d):
    _nonzero(d["particle_density"], "Particle density")
    return (1 - d["bulk_density"] / d["particle_density"]) * 100


def _soil_moisture_gravimetric(d):
    _nonzero(d["dry_weight"], "Dry weight")
    return (d["wet_weight"] - d["dry_weight"]) / d["dry_weight"] * 100


def _compost_ratio(d):
    _nonzero(d["nitrogen"], "Nitrogen")
    return d["carbon"] / d["nitrogen"]


def _pesticide_solution_amount(d):
    return d["spray_volume_l"] * (d["concentration_percent"] / 100)


def _sprayer_application_rate(d):
    _nonzero(d["speed_km_h"], "Speed")
    _nonzero(d["swath_width_m"], "Swath width")
    return 600 * d["nozzle_flow_l_min"] / (d["speed_km_h"] * d["swath_width_m"])


def _emission_intensity(d):
    _nonzero(d["production_ton"], "Production")
    return d["emissions_kg_co2e"] / d["production_ton"]


def _compound_growth(d):
    _positive(d["years"], "Years")
    return d["initial_value"] * exp(d["annual_rate"] * d["years"])


AGRICULTURE_FORMULAS = {
    "yield-per-hectare": {
        "title": "Yield per Hectare",
        "latex": r"Y_{ha}=\frac{Y_{total}}{A}",
        "fields": [{"name": "total_yield_ton", "label": "Total yield (ton)"}, {"name": "area_ha", "label": "Area (ha)"}],
        "compute": _yield_per_hectare,
        "substitute": lambda d: "Yield per ha = total_yield / area",
        "answer_label": "Yield (ton/ha)",
        "format_answer": _fmt,
    },
    "total-yield": {
        "title": "Total Yield",
        "latex": r"Y_{total}=Y_{ha}\times A",
        "fields": [{"name": "yield_per_ha", "label": "Yield per ha (ton/ha)"}, {"name": "area_ha", "label": "Area (ha)"}],
        "compute": _total_yield,
        "substitute": lambda d: "Total yield = yield_per_ha * area",
        "answer_label": "Total yield (ton)",
        "format_answer": _fmt,
    },
    "seed-rate-per-hectare": {
        "title": "Seed Rate per Hectare",
        "latex": r"SR=\frac{Seed_{total}}{Area}",
        "fields": [{"name": "seed_total_kg", "label": "Total seed (kg)"}, {"name": "area_ha", "label": "Area (ha)"}],
        "compute": _seed_rate_per_ha,
        "substitute": lambda d: "Seed rate = total_seed / area",
        "answer_label": "Seed rate (kg/ha)",
        "format_answer": _fmt,
    },
    "seed-requirement-total": {
        "title": "Total Seed Requirement",
        "latex": r"Seed_{total}=SR\times Area",
        "fields": [{"name": "seed_rate_kg_ha", "label": "Seed rate (kg/ha)"}, {"name": "area_ha", "label": "Area (ha)"}],
        "compute": _seed_requirement_total,
        "substitute": lambda d: "Total seed = seed_rate * area",
        "answer_label": "Total seed (kg)",
        "format_answer": _fmt,
    },
    "plant-population": {
        "title": "Plant Population",
        "latex": r"N=\frac{Area}{Row\ Spacing\times Plant\ Spacing}",
        "fields": [{"name": "area_m2", "label": "Area (m2)"}, {"name": "row_spacing_m", "label": "Row spacing (m)"}, {"name": "plant_spacing_m", "label": "Plant spacing (m)"}],
        "compute": _plant_population,
        "substitute": lambda d: "Plants = area/(row_spacing*plant_spacing)",
        "answer_label": "Plant count",
        "format_answer": _fmt,
    },
    "fertilizer-required": {
        "title": "Fertilizer Required for N Target",
        "latex": r"F=\frac{N_{req}}{N\%/100}",
        "fields": [{"name": "n_required_kg_ha", "label": "Required N (kg/ha)"}, {"name": "fertilizer_n_percent", "label": "Fertilizer N (%)"}],
        "compute": _fertilizer_required,
        "substitute": lambda d: "Fertilizer required = N_required/(N_percent/100)",
        "answer_label": "Fertilizer (kg/ha)",
        "format_answer": _fmt,
    },
    "nutrient-applied": {
        "title": "Nutrient Applied",
        "latex": r"N_{applied}=F\times N\%",
        "fields": [{"name": "fertilizer_rate_kg_ha", "label": "Fertilizer rate (kg/ha)"}, {"name": "nutrient_percent", "label": "Nutrient (%)"}],
        "compute": _nutrient_applied,
        "substitute": lambda d: "Nutrient applied = fertilizer_rate*(nutrient_percent/100)",
        "answer_label": "Nutrient (kg/ha)",
        "format_answer": _fmt,
    },
    "water-use-efficiency": {
        "title": "Water Use Efficiency",
        "latex": r"WUE=\frac{Yield}{Water\ Used}",
        "fields": [{"name": "yield_kg_ha", "label": "Yield (kg/ha)"}, {"name": "water_used_mm", "label": "Water used (mm)"}],
        "compute": _water_use_efficiency,
        "substitute": lambda d: "WUE = yield/water_used",
        "answer_label": "WUE (kg/ha/mm)",
        "format_answer": _fmt,
    },
    "irrigation-volume": {
        "title": "Irrigation Volume",
        "latex": r"V=Depth(mm)\times Area(ha)\times10",
        "fields": [{"name": "depth_mm", "label": "Depth (mm)"}, {"name": "area_ha", "label": "Area (ha)"}],
        "compute": _irrigation_volume,
        "substitute": lambda d: "Volume = depth_mm*area_ha*10",
        "answer_label": "Volume (m3)",
        "format_answer": _fmt,
    },
    "irrigation-time": {
        "title": "Irrigation Time",
        "latex": r"t=\frac{V}{Q}",
        "fields": [{"name": "volume_m3", "label": "Volume (m3)"}, {"name": "discharge_m3_h", "label": "Discharge (m3/h)"}],
        "compute": _irrigation_time,
        "substitute": lambda d: "Time = volume/discharge",
        "answer_label": "Time (h)",
        "format_answer": _fmt,
    },
    "theoretical-field-capacity": {
        "title": "Theoretical Field Capacity",
        "latex": r"TFC=\frac{Speed\times Width}{10}",
        "fields": [{"name": "speed_km_h", "label": "Speed (km/h)"}, {"name": "implement_width_m", "label": "Implement width (m)"}],
        "compute": _theoretical_field_capacity,
        "substitute": lambda d: "TFC = speed*width/10",
        "answer_label": "TFC (ha/h)",
        "format_answer": _fmt,
    },
    "effective-field-capacity": {
        "title": "Effective Field Capacity",
        "latex": r"EFC=TFC\times FE\%",
        "fields": [{"name": "theoretical_field_capacity", "label": "TFC (ha/h)"}, {"name": "field_efficiency_percent", "label": "Field efficiency (%)"}],
        "compute": _effective_field_capacity,
        "substitute": lambda d: "EFC = TFC*(efficiency/100)",
        "answer_label": "EFC (ha/h)",
        "format_answer": _fmt,
    },
    "field-efficiency": {
        "title": "Field Efficiency",
        "latex": r"FE=\frac{EFC}{TFC}\times100",
        "fields": [{"name": "effective_field_capacity", "label": "EFC (ha/h)"}, {"name": "theoretical_field_capacity", "label": "TFC (ha/h)"}],
        "compute": _field_efficiency,
        "substitute": lambda d: "FE = EFC/TFC*100",
        "answer_label": "Field efficiency",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "feed-conversion-ratio": {
        "title": "Feed Conversion Ratio",
        "latex": r"FCR=\frac{Feed\ Intake}{Weight\ Gain}",
        "fields": [{"name": "feed_intake_kg", "label": "Feed intake (kg)"}, {"name": "weight_gain_kg", "label": "Weight gain (kg)"}],
        "compute": _feed_conversion_ratio,
        "substitute": lambda d: "FCR = feed_intake/weight_gain",
        "answer_label": "FCR",
        "format_answer": _fmt,
    },
    "average-daily-gain": {
        "title": "Average Daily Gain",
        "latex": r"ADG=\frac{Weight\ Gain}{Days}",
        "fields": [{"name": "weight_gain_kg", "label": "Weight gain (kg)"}, {"name": "days", "label": "Days"}],
        "compute": _average_daily_gain,
        "substitute": lambda d: "ADG = weight_gain/days",
        "answer_label": "ADG (kg/day)",
        "format_answer": _fmt,
    },
    "stocking-rate": {
        "title": "Stocking Rate",
        "latex": r"SR=\frac{Animals}{Land\ Area}",
        "fields": [{"name": "animals", "label": "Animals"}, {"name": "land_area_ha", "label": "Land area (ha)"}],
        "compute": _stocking_rate,
        "substitute": lambda d: "Stocking rate = animals/land_area",
        "answer_label": "Animals per ha",
        "format_answer": _fmt,
    },
    "milk-yield-per-cow": {
        "title": "Milk Yield per Cow",
        "latex": r"MY=\frac{Total\ Milk}{Number\ of\ Cows}",
        "fields": [{"name": "total_milk_l_day", "label": "Total milk (L/day)"}, {"name": "number_of_cows", "label": "Number of cows"}],
        "compute": _milk_yield_per_cow,
        "substitute": lambda d: "Milk per cow = total_milk/cows",
        "answer_label": "Milk per cow (L/day)",
        "format_answer": _fmt,
    },
    "mortality-rate": {
        "title": "Mortality Rate",
        "latex": r"MR=\frac{Deaths}{Initial\ Animals}\times100",
        "fields": [{"name": "deaths", "label": "Deaths"}, {"name": "initial_animals", "label": "Initial animals"}],
        "compute": _mortality_rate,
        "substitute": lambda d: "MR = deaths/initial_animals*100",
        "answer_label": "Mortality rate",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "hatchability": {
        "title": "Hatchability",
        "latex": r"H=\frac{Chicks\ Hatched}{Fertile\ Eggs}\times100",
        "fields": [{"name": "chicks_hatched", "label": "Chicks hatched"}, {"name": "fertile_eggs", "label": "Fertile eggs"}],
        "compute": _hatchability,
        "substitute": lambda d: "Hatchability = chicks_hatched/fertile_eggs*100",
        "answer_label": "Hatchability",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "harvest-index": {
        "title": "Harvest Index",
        "latex": r"HI=\frac{Economic\ Yield}{Biological\ Yield}\times100",
        "fields": [{"name": "economic_yield", "label": "Economic yield"}, {"name": "biological_yield", "label": "Biological yield"}],
        "compute": _harvest_index,
        "substitute": lambda d: "HI = economic_yield/biological_yield*100",
        "answer_label": "Harvest index",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "cropping-intensity": {
        "title": "Cropping Intensity",
        "latex": r"CI=\frac{Gross\ Cropped\ Area}{Net\ Sown\ Area}\times100",
        "fields": [{"name": "gross_cropped_area", "label": "Gross cropped area"}, {"name": "net_sown_area", "label": "Net sown area"}],
        "compute": _cropping_intensity,
        "substitute": lambda d: "CI = gross_cropped/net_sown*100",
        "answer_label": "Cropping intensity",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "land-equivalent-ratio": {
        "title": "Land Equivalent Ratio",
        "latex": r"LER=\frac{Y_{ia}}{Y_{sa}}+\frac{Y_{ib}}{Y_{sb}}",
        "fields": [{"name": "yield_intercrop_a", "label": "Intercrop yield A"}, {"name": "yield_sole_a", "label": "Sole crop yield A"}, {"name": "yield_intercrop_b", "label": "Intercrop yield B"}, {"name": "yield_sole_b", "label": "Sole crop yield B"}],
        "compute": _land_equivalent_ratio,
        "substitute": lambda d: "LER = (Yia/Ysa)+(Yib/Ysb)",
        "answer_label": "LER",
        "format_answer": _fmt,
    },
    "benefit-cost-ratio": {
        "title": "Benefit-Cost Ratio",
        "latex": r"BCR=\frac{Gross\ Return}{Total\ Cost}",
        "fields": [{"name": "gross_return", "label": "Gross return"}, {"name": "total_cost", "label": "Total cost"}],
        "compute": _benefit_cost_ratio,
        "substitute": lambda d: "BCR = gross_return/total_cost",
        "answer_label": "BCR",
        "format_answer": _fmt,
    },
    "net-return": {
        "title": "Net Return",
        "latex": r"NR=Gross\ Return-Total\ Cost",
        "fields": [{"name": "gross_return", "label": "Gross return"}, {"name": "total_cost", "label": "Total cost"}],
        "compute": _net_return,
        "substitute": lambda d: "Net return = gross_return-total_cost",
        "answer_label": "Net return",
        "format_answer": _fmt,
    },
    "gross-margin": {
        "title": "Gross Margin",
        "latex": r"GM=Gross\ Return-Variable\ Cost",
        "fields": [{"name": "gross_return", "label": "Gross return"}, {"name": "variable_cost", "label": "Variable cost"}],
        "compute": _gross_margin,
        "substitute": lambda d: "Gross margin = gross_return-variable_cost",
        "answer_label": "Gross margin",
        "format_answer": _fmt,
    },
    "return-on-investment": {
        "title": "Return on Investment",
        "latex": r"ROI=\frac{Profit}{Cost}\times100",
        "fields": [{"name": "profit", "label": "Profit"}, {"name": "cost", "label": "Cost"}],
        "compute": _return_on_investment,
        "substitute": lambda d: "ROI = profit/cost*100",
        "answer_label": "ROI",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "soil-bulk-density": {
        "title": "Soil Bulk Density",
        "latex": r"BD=\frac{Dry\ Mass}{Core\ Volume}",
        "fields": [{"name": "oven_dry_mass_g", "label": "Oven dry mass (g)"}, {"name": "core_volume_cm3", "label": "Core volume (cm3)"}],
        "compute": _soil_bulk_density,
        "substitute": lambda d: "BD = dry_mass/core_volume",
        "answer_label": "Bulk density (g/cm3)",
        "format_answer": _fmt,
    },
    "soil-porosity": {
        "title": "Soil Porosity",
        "latex": r"Porosity=(1-\frac{BD}{PD})\times100",
        "fields": [{"name": "bulk_density", "label": "Bulk density BD"}, {"name": "particle_density", "label": "Particle density PD"}],
        "compute": _soil_porosity,
        "substitute": lambda d: "Porosity=(1-BD/PD)*100",
        "answer_label": "Porosity",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "soil-moisture-gravimetric": {
        "title": "Gravimetric Soil Moisture",
        "latex": r"SM=\frac{Wet-Dry}{Dry}\times100",
        "fields": [{"name": "wet_weight", "label": "Wet weight"}, {"name": "dry_weight", "label": "Dry weight"}],
        "compute": _soil_moisture_gravimetric,
        "substitute": lambda d: "SM = (wet-dry)/dry*100",
        "answer_label": "Soil moisture",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "compost-c-n-ratio": {
        "title": "Compost C:N Ratio",
        "latex": r"C:N=\frac{C}{N}",
        "fields": [{"name": "carbon", "label": "Carbon"}, {"name": "nitrogen", "label": "Nitrogen"}],
        "compute": _compost_ratio,
        "substitute": lambda d: "C:N = carbon/nitrogen",
        "answer_label": "C:N ratio",
        "format_answer": _fmt,
    },
    "pesticide-solution-amount": {
        "title": "Pesticide Active Ingredient Amount",
        "latex": r"AI=Volume\times\frac{Conc\%}{100}",
        "fields": [{"name": "spray_volume_l", "label": "Spray volume (L)"}, {"name": "concentration_percent", "label": "Concentration (%)"}],
        "compute": _pesticide_solution_amount,
        "substitute": lambda d: "AI = spray_volume*(conc/100)",
        "answer_label": "Active ingredient (L eq.)",
        "format_answer": _fmt,
    },
    "sprayer-application-rate": {
        "title": "Sprayer Application Rate",
        "latex": r"Rate=\frac{600\times Nozzle\ Flow}{Speed\times Width}",
        "fields": [{"name": "nozzle_flow_l_min", "label": "Nozzle flow (L/min)"}, {"name": "speed_km_h", "label": "Speed (km/h)"}, {"name": "swath_width_m", "label": "Swath width (m)"}],
        "compute": _sprayer_application_rate,
        "substitute": lambda d: "Rate = 600*nozzle_flow/(speed*width)",
        "answer_label": "Application rate (L/ha)",
        "format_answer": _fmt,
    },
    "emission-intensity": {
        "title": "Emission Intensity",
        "latex": r"EI=\frac{Emissions}{Production}",
        "fields": [{"name": "emissions_kg_co2e", "label": "Emissions (kg CO2e)"}, {"name": "production_ton", "label": "Production (ton)"}],
        "compute": _emission_intensity,
        "substitute": lambda d: "EI = emissions/production",
        "answer_label": "Emission intensity (kg CO2e/ton)",
        "format_answer": _fmt,
    },
    "compound-growth": {
        "title": "Compound Growth (Continuous)",
        "latex": r"V_t=V_0e^{rt}",
        "fields": [{"name": "initial_value", "label": "Initial value V0"}, {"name": "annual_rate", "label": "Annual rate r"}, {"name": "years", "label": "Years t"}],
        "compute": _compound_growth,
        "substitute": lambda d: "Vt = V0*exp(r*t)",
        "answer_label": "Vt",
        "format_answer": _fmt,
    },
}


AGRICULTURE_FORMULA_GROUPS = [
    {
        "title": "Crop Production",
        "slugs": [
            "yield-per-hectare",
            "total-yield",
            "seed-rate-per-hectare",
            "seed-requirement-total",
            "plant-population",
            "harvest-index",
            "cropping-intensity",
            "land-equivalent-ratio",
            "compound-growth",
        ],
    },
    {
        "title": "Nutrients & Inputs",
        "slugs": [
            "fertilizer-required",
            "nutrient-applied",
            "pesticide-solution-amount",
            "sprayer-application-rate",
            "water-use-efficiency",
            "irrigation-volume",
            "irrigation-time",
        ],
    },
    {
        "title": "Farm Mechanization",
        "slugs": [
            "theoretical-field-capacity",
            "effective-field-capacity",
            "field-efficiency",
        ],
    },
    {
        "title": "Livestock & Poultry",
        "slugs": [
            "feed-conversion-ratio",
            "average-daily-gain",
            "stocking-rate",
            "milk-yield-per-cow",
            "mortality-rate",
            "hatchability",
        ],
    },
    {
        "title": "Farm Economics",
        "slugs": [
            "benefit-cost-ratio",
            "net-return",
            "gross-margin",
            "return-on-investment",
            "emission-intensity",
        ],
    },
    {
        "title": "Soil & Compost",
        "slugs": [
            "soil-bulk-density",
            "soil-porosity",
            "soil-moisture-gravimetric",
            "compost-c-n-ratio",
        ],
    },
]


AGRICULTURE_FORMULA_DESCRIPTIONS = {
    "yield-per-hectare": "Compute production yield per hectare of land.",
    "total-yield": "Compute total output from area and per-hectare yield.",
    "seed-rate-per-hectare": "Find seeding rate for a field area.",
    "seed-requirement-total": "Estimate total seed needed for planting.",
    "plant-population": "Estimate plant count from spacing and field area.",
    "fertilizer-required": "Estimate fertilizer amount needed for target nutrients.",
    "nutrient-applied": "Compute actual nutrient delivered from fertilizer.",
    "water-use-efficiency": "Measure crop output per unit of water used.",
    "irrigation-volume": "Compute total irrigation water volume required.",
    "irrigation-time": "Estimate irrigation duration from flow rate.",
    "theoretical-field-capacity": "Estimate ideal field coverage rate.",
    "effective-field-capacity": "Estimate real field coverage including losses.",
    "field-efficiency": "Compare effective to theoretical field capacity.",
    "feed-conversion-ratio": "Measure feed required per unit of weight gain.",
    "average-daily-gain": "Compute daily animal growth rate.",
    "stocking-rate": "Estimate livestock density per grazing area.",
    "milk-yield-per-cow": "Compute average milk output per cow.",
    "mortality-rate": "Compute percent mortality in a herd or flock.",
    "hatchability": "Measure successful hatch percentage.",
    "harvest-index": "Measure economic yield as share of total biomass.",
    "cropping-intensity": "Measure annual crop area use relative to net sown area.",
    "land-equivalent-ratio": "Compare intercropping land advantage over monoculture.",
    "benefit-cost-ratio": "Compare gross return to production cost.",
    "net-return": "Compute return after subtracting costs.",
    "gross-margin": "Compute gross income minus variable costs.",
    "return-on-investment": "Measure profit as a percent of cost.",
    "soil-bulk-density": "Compute dry soil mass per unit core volume.",
    "soil-porosity": "Estimate soil pore-space percentage from densities.",
    "soil-moisture-gravimetric": "Compute moisture content from wet and dry mass.",
    "compost-c-n-ratio": "Compute compost carbon-to-nitrogen ratio.",
    "pesticide-solution-amount": "Estimate spray solution needed for target concentration.",
    "sprayer-application-rate": "Compute application volume per hectare.",
    "emission-intensity": "Measure emissions per unit of agricultural output.",
    "compound-growth": "Project continuous growth over time.",
}
