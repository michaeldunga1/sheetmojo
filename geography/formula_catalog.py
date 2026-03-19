from math import asin, cos, radians, sin, sqrt, pi


EARTH_RADIUS_KM = 6371.0


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


def _haversine(d):
    lat1 = radians(d["lat1"])
    lon1 = radians(d["lon1"])
    lat2 = radians(d["lat2"])
    lon2 = radians(d["lon2"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return EARTH_RADIUS_KM * c


def _distance_from_scale(d):
    _positive(d["scale_denominator"], "Scale denominator")
    return d["map_distance_cm"] * d["scale_denominator"] / 100000


def _map_distance_from_scale(d):
    _positive(d["scale_denominator"], "Scale denominator")
    return d["ground_distance_km"] * 100000 / d["scale_denominator"]


def _scale_denominator(d):
    _positive(d["map_distance_cm"], "Map distance")
    return d["ground_distance_km"] * 100000 / d["map_distance_cm"]


def _population_density(d):
    _nonzero(d["area"], "Area")
    return d["population"] / d["area"]


def _population_growth(d):
    return d["P0"] * ((1 + d["r"]) ** d["t"])


def _growth_rate_percent(d):
    _nonzero(d["P0"], "Initial population")
    return ((d["P1"] - d["P0"]) / d["P0"]) * 100


def _doubling_time_rule70(d):
    _nonzero(d["rate_percent"], "Growth rate (%)")
    return 70 / d["rate_percent"]


def _cbr(d):
    _nonzero(d["population"], "Population")
    return d["births"] / d["population"] * 1000


def _cdr(d):
    _nonzero(d["population"], "Population")
    return d["deaths"] / d["population"] * 1000


def _migration_rate(d):
    _nonzero(d["population"], "Population")
    return d["net_migration"] / d["population"] * 1000


def _sex_ratio(d):
    _nonzero(d["females"], "Females")
    return d["males"] / d["females"] * 100


def _dependency_ratio(d):
    _nonzero(d["working_age"], "Working age population")
    return (d["young"] + d["old"]) / d["working_age"] * 100


def _arithmetic_density(d):
    return _population_density(d)


def _physiological_density(d):
    _nonzero(d["arable_land"], "Arable land")
    return d["population"] / d["arable_land"]


def _agricultural_density(d):
    _nonzero(d["arable_land"], "Arable land")
    return d["farmers"] / d["arable_land"]


def _natural_increase_per_thousand(d):
    return d["cbr"] - d["cdr"]


def _gradient(d):
    _nonzero(d["horizontal_distance"], "Horizontal distance")
    return d["vertical_change"] / d["horizontal_distance"]


def _slope_percent(d):
    return _gradient(d) * 100


def _relief_ratio(d):
    _nonzero(d["basin_length"], "Basin length")
    return d["relief"] / d["basin_length"]


def _drainage_density(d):
    _nonzero(d["basin_area"], "Basin area")
    return d["channel_length"] / d["basin_area"]


def _stream_discharge(d):
    return d["area"] * d["velocity"]


def _runoff_coefficient(d):
    _nonzero(d["precipitation"], "Precipitation")
    return d["runoff"] / d["precipitation"]


def _infiltration_rate(d):
    _nonzero(d["time"], "Time")
    return d["infiltrated_water"] / d["time"]


def _lapse_rate(d):
    _nonzero(d["height_diff_m"], "Height difference")
    return (d["temp_lower"] - d["temp_upper"]) / d["height_diff_m"] * 1000


def _relative_humidity(d):
    _nonzero(d["saturation_vapor_pressure"], "Saturation vapor pressure")
    return d["actual_vapor_pressure"] / d["saturation_vapor_pressure"] * 100


def _dew_point_approx(d):
    return d["temperature_c"] - ((100 - d["relative_humidity"]) / 5)


def _c_to_f(d):
    return d["c"] * 9 / 5 + 32


def _f_to_c(d):
    return (d["f"] - 32) * 5 / 9


def _kelvin_to_celsius(d):
    return d["k"] - 273.15


def _celsius_to_kelvin(d):
    return d["c"] + 273.15


def _earth_circumference_lat(d):
    return 2 * pi * EARTH_RADIUS_KM * cos(radians(d["latitude"]))


def _length_of_degree_longitude(d):
    return 111.32 * cos(radians(d["latitude"]))


def _length_of_degree_latitude(_d):
    return 111.32


def _time_zone_offset(d):
    return d["longitude"] / 15


def _local_time_from_gmt(d):
    return d["gmt_hour"] + _time_zone_offset({"longitude": d["longitude"]})


def _solar_noon_difference_minutes(d):
    return d["longitude_diff"] * 4


GEOGRAPHY_FORMULAS = {
    "great-circle-distance": {
        "title": "Great-Circle Distance (Haversine)",
        "latex": r"d=2R\arcsin\left(\sqrt{\sin^2\frac{\Delta\phi}{2}+\cos\phi_1\cos\phi_2\sin^2\frac{\Delta\lambda}{2}}\right)",
        "fields": [
            {"name": "lat1", "label": "Latitude 1 (deg)"},
            {"name": "lon1", "label": "Longitude 1 (deg)"},
            {"name": "lat2", "label": "Latitude 2 (deg)"},
            {"name": "lon2", "label": "Longitude 2 (deg)"},
        ],
        "compute": _haversine,
        "substitute": lambda d: "Haversine formula using Earth radius 6371 km",
        "answer_label": "Distance (km)",
        "format_answer": _fmt,
    },
    "ground-distance-from-scale": {
        "title": "Ground Distance from Map Scale",
        "latex": r"D_g=\frac{D_m \times \text{RF}}{100000}",
        "fields": [
            {"name": "map_distance_cm", "label": "Map distance (cm)", "min": 0},
            {"name": "scale_denominator", "label": "Scale denominator (1:n)", "min": 1},
        ],
        "compute": _distance_from_scale,
        "substitute": lambda d: "Ground km = map_cm * n / 100000",
        "answer_label": "Ground distance (km)",
        "format_answer": _fmt,
    },
    "map-distance-from-scale": {
        "title": "Map Distance from Scale",
        "latex": r"D_m=\frac{D_g\times100000}{\text{RF}}",
        "fields": [
            {"name": "ground_distance_km", "label": "Ground distance (km)", "min": 0},
            {"name": "scale_denominator", "label": "Scale denominator (1:n)", "min": 1},
        ],
        "compute": _map_distance_from_scale,
        "substitute": lambda d: "Map cm = ground_km * 100000 / n",
        "answer_label": "Map distance (cm)",
        "format_answer": _fmt,
    },
    "scale-denominator": {
        "title": "Scale Denominator (1:n)",
        "latex": r"n=\frac{D_g\times100000}{D_m}",
        "fields": [
            {"name": "ground_distance_km", "label": "Ground distance (km)", "min": 0},
            {"name": "map_distance_cm", "label": "Map distance (cm)", "min": 0},
        ],
        "compute": _scale_denominator,
        "substitute": lambda d: "n = ground_km * 100000 / map_cm",
        "answer_label": "n",
        "format_answer": _fmt,
    },
    "population-density": {
        "title": "Population Density",
        "latex": r"D_p=\frac{P}{A}",
        "fields": [{"name": "population", "label": "Population"}, {"name": "area", "label": "Area"}],
        "compute": _population_density,
        "substitute": lambda d: "Density = population / area",
        "answer_label": "People per unit area",
        "format_answer": _fmt,
    },
    "population-growth-future": {
        "title": "Population Growth (Exponential)",
        "latex": r"P_t=P_0(1+r)^t",
        "fields": [{"name": "P0", "label": "Initial population P0"}, {"name": "r", "label": "Growth rate r (decimal)"}, {"name": "t", "label": "Time t"}],
        "compute": _population_growth,
        "substitute": lambda d: "Pt = P0*(1+r)^t",
        "answer_label": "Pt",
        "format_answer": _fmt,
    },
    "population-growth-rate-percent": {
        "title": "Population Growth Rate (%)",
        "latex": r"r=\frac{P_1-P_0}{P_0}\times100",
        "fields": [{"name": "P0", "label": "Initial population P0"}, {"name": "P1", "label": "Final population P1"}],
        "compute": _growth_rate_percent,
        "substitute": lambda d: "r% = (P1-P0)/P0*100",
        "answer_label": "Growth rate",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "doubling-time-rule-70": {
        "title": "Doubling Time (Rule of 70)",
        "latex": r"T_d=\frac{70}{r\%}",
        "fields": [{"name": "rate_percent", "label": "Growth rate (%)"}],
        "compute": _doubling_time_rule70,
        "substitute": lambda d: "Td = 70 / r%",
        "answer_label": "Doubling time",
        "format_answer": _fmt,
    },
    "crude-birth-rate": {
        "title": "Crude Birth Rate",
        "latex": r"\mathrm{CBR}=\frac{B}{P}\times1000",
        "fields": [{"name": "births", "label": "Births B"}, {"name": "population", "label": "Population P"}],
        "compute": _cbr,
        "substitute": lambda d: "CBR = births/population*1000",
        "answer_label": "CBR (per 1000)",
        "format_answer": _fmt,
    },
    "crude-death-rate": {
        "title": "Crude Death Rate",
        "latex": r"\mathrm{CDR}=\frac{D}{P}\times1000",
        "fields": [{"name": "deaths", "label": "Deaths D"}, {"name": "population", "label": "Population P"}],
        "compute": _cdr,
        "substitute": lambda d: "CDR = deaths/population*1000",
        "answer_label": "CDR (per 1000)",
        "format_answer": _fmt,
    },
    "net-migration-rate": {
        "title": "Net Migration Rate",
        "latex": r"\mathrm{NMR}=\frac{M_{net}}{P}\times1000",
        "fields": [{"name": "net_migration", "label": "Net migration"}, {"name": "population", "label": "Population"}],
        "compute": _migration_rate,
        "substitute": lambda d: "NMR = net_migration/population*1000",
        "answer_label": "NMR (per 1000)",
        "format_answer": _fmt,
    },
    "sex-ratio": {
        "title": "Sex Ratio",
        "latex": r"\mathrm{SR}=\frac{M}{F}\times100",
        "fields": [{"name": "males", "label": "Males M"}, {"name": "females", "label": "Females F"}],
        "compute": _sex_ratio,
        "substitute": lambda d: "SR = males/females*100",
        "answer_label": "Sex ratio",
        "format_answer": _fmt,
    },
    "dependency-ratio": {
        "title": "Dependency Ratio",
        "latex": r"\mathrm{DR}=\frac{Y+O}{W}\times100",
        "fields": [{"name": "young", "label": "Young population Y"}, {"name": "old", "label": "Old population O"}, {"name": "working_age", "label": "Working age W"}],
        "compute": _dependency_ratio,
        "substitute": lambda d: "DR = (young+old)/working*100",
        "answer_label": "Dependency ratio",
        "format_answer": _fmt,
    },
    "arithmetic-density": {
        "title": "Arithmetic Density",
        "latex": r"D_a=\frac{P}{A}",
        "fields": [{"name": "population", "label": "Population"}, {"name": "area", "label": "Total land area"}],
        "compute": _arithmetic_density,
        "substitute": lambda d: "Da = population/total_land",
        "answer_label": "Da",
        "format_answer": _fmt,
    },
    "physiological-density": {
        "title": "Physiological Density",
        "latex": r"D_{phys}=\frac{P}{A_{arable}}",
        "fields": [{"name": "population", "label": "Population"}, {"name": "arable_land", "label": "Arable land area"}],
        "compute": _physiological_density,
        "substitute": lambda d: "Dphys = population/arable_land",
        "answer_label": "Dphys",
        "format_answer": _fmt,
    },
    "agricultural-density": {
        "title": "Agricultural Density",
        "latex": r"D_{agri}=\frac{F}{A_{arable}}",
        "fields": [{"name": "farmers", "label": "Number of farmers"}, {"name": "arable_land", "label": "Arable land area"}],
        "compute": _agricultural_density,
        "substitute": lambda d: "Dagri = farmers/arable_land",
        "answer_label": "Dagri",
        "format_answer": _fmt,
    },
    "natural-increase-rate-per-thousand": {
        "title": "Natural Increase (per 1000)",
        "latex": r"\mathrm{NIR}_{1000}=\mathrm{CBR}-\mathrm{CDR}",
        "fields": [{"name": "cbr", "label": "CBR"}, {"name": "cdr", "label": "CDR"}],
        "compute": _natural_increase_per_thousand,
        "substitute": lambda d: "NIR(per1000)=CBR-CDR",
        "answer_label": "NIR (per 1000)",
        "format_answer": _fmt,
    },
    "gradient": {
        "title": "Gradient",
        "latex": r"G=\frac{\Delta h}{d}",
        "fields": [{"name": "vertical_change", "label": "Vertical change"}, {"name": "horizontal_distance", "label": "Horizontal distance"}],
        "compute": _gradient,
        "substitute": lambda d: "Gradient = vertical/horizontal",
        "answer_label": "Gradient",
        "format_answer": _fmt,
    },
    "slope-percent": {
        "title": "Slope (%)",
        "latex": r"\mathrm{Slope\%}=\frac{\Delta h}{d}\times100",
        "fields": [{"name": "vertical_change", "label": "Vertical change"}, {"name": "horizontal_distance", "label": "Horizontal distance"}],
        "compute": _slope_percent,
        "substitute": lambda d: "Slope%=vertical/horizontal*100",
        "answer_label": "Slope",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "relief-ratio": {
        "title": "Relief Ratio",
        "latex": r"R_r=\frac{\text{Relief}}{\text{Basin Length}}",
        "fields": [{"name": "relief", "label": "Relief"}, {"name": "basin_length", "label": "Basin length"}],
        "compute": _relief_ratio,
        "substitute": lambda d: "Rr = relief/basin_length",
        "answer_label": "Rr",
        "format_answer": _fmt,
    },
    "drainage-density": {
        "title": "Drainage Density",
        "latex": r"D_d=\frac{L_{channels}}{A_{basin}}",
        "fields": [{"name": "channel_length", "label": "Total channel length"}, {"name": "basin_area", "label": "Basin area"}],
        "compute": _drainage_density,
        "substitute": lambda d: "Dd = channel_length/basin_area",
        "answer_label": "Dd",
        "format_answer": _fmt,
    },
    "stream-discharge": {
        "title": "Stream Discharge",
        "latex": r"Q=Av",
        "fields": [{"name": "area", "label": "Cross-sectional area A"}, {"name": "velocity", "label": "Flow velocity v"}],
        "compute": _stream_discharge,
        "substitute": lambda d: "Q = A*v",
        "answer_label": "Q",
        "format_answer": _fmt,
    },
    "runoff-coefficient": {
        "title": "Runoff Coefficient",
        "latex": r"C=\frac{R}{P}",
        "fields": [{"name": "runoff", "label": "Runoff R"}, {"name": "precipitation", "label": "Precipitation P"}],
        "compute": _runoff_coefficient,
        "substitute": lambda d: "C = runoff/precipitation",
        "answer_label": "C",
        "format_answer": _fmt,
    },
    "infiltration-rate": {
        "title": "Infiltration Rate",
        "latex": r"I=\frac{W}{t}",
        "fields": [{"name": "infiltrated_water", "label": "Infiltrated water W"}, {"name": "time", "label": "Time t"}],
        "compute": _infiltration_rate,
        "substitute": lambda d: "I = infiltrated_water/time",
        "answer_label": "I",
        "format_answer": _fmt,
    },
    "environmental-lapse-rate": {
        "title": "Environmental Lapse Rate",
        "latex": r"\Gamma=\frac{T_{lower}-T_{upper}}{\Delta z}\times1000",
        "fields": [{"name": "temp_lower", "label": "Lower temp (C)"}, {"name": "temp_upper", "label": "Upper temp (C)"}, {"name": "height_diff_m", "label": "Height difference (m)"}],
        "compute": _lapse_rate,
        "substitute": lambda d: "Gamma = (Tlower-Tupper)/height_diff*1000",
        "answer_label": "Lapse rate (C/km)",
        "format_answer": _fmt,
    },
    "relative-humidity": {
        "title": "Relative Humidity",
        "latex": r"\mathrm{RH}=\frac{e}{e_s}\times100",
        "fields": [{"name": "actual_vapor_pressure", "label": "Actual vapor pressure e"}, {"name": "saturation_vapor_pressure", "label": "Saturation vapor pressure es"}],
        "compute": _relative_humidity,
        "substitute": lambda d: "RH = e/es*100",
        "answer_label": "RH",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "dew-point-approximation": {
        "title": "Dew Point Approximation",
        "latex": r"T_d\approx T-\frac{100-\mathrm{RH}}{5}",
        "fields": [{"name": "temperature_c", "label": "Air temperature T (C)"}, {"name": "relative_humidity", "label": "RH (%)"}],
        "compute": _dew_point_approx,
        "substitute": lambda d: "Td approx T - (100-RH)/5",
        "answer_label": "Dew point (C)",
        "format_answer": _fmt,
    },
    "celsius-to-fahrenheit": {
        "title": "Celsius to Fahrenheit",
        "latex": r"F=\frac{9}{5}C+32",
        "fields": [{"name": "c", "label": "Temperature C"}],
        "compute": _c_to_f,
        "substitute": lambda d: "F = 9/5*C + 32",
        "answer_label": "F",
        "format_answer": _fmt,
    },
    "fahrenheit-to-celsius": {
        "title": "Fahrenheit to Celsius",
        "latex": r"C=\frac{5}{9}(F-32)",
        "fields": [{"name": "f", "label": "Temperature F"}],
        "compute": _f_to_c,
        "substitute": lambda d: "C = 5/9*(F-32)",
        "answer_label": "C",
        "format_answer": _fmt,
    },
    "kelvin-to-celsius": {
        "title": "Kelvin to Celsius",
        "latex": r"C=K-273.15",
        "fields": [{"name": "k", "label": "Temperature K"}],
        "compute": _kelvin_to_celsius,
        "substitute": lambda d: "C = K-273.15",
        "answer_label": "C",
        "format_answer": _fmt,
    },
    "celsius-to-kelvin": {
        "title": "Celsius to Kelvin",
        "latex": r"K=C+273.15",
        "fields": [{"name": "c", "label": "Temperature C"}],
        "compute": _celsius_to_kelvin,
        "substitute": lambda d: "K = C+273.15",
        "answer_label": "K",
        "format_answer": _fmt,
    },
    "earth-circumference-at-latitude": {
        "title": "Earth Circumference at Latitude",
        "latex": r"C_{lat}=2\pi R\cos\phi",
        "fields": [{"name": "latitude", "label": "Latitude phi (deg)"}],
        "compute": _earth_circumference_lat,
        "substitute": lambda d: "Clat = 2*pi*R*cos(latitude)",
        "answer_label": "Circumference (km)",
        "format_answer": _fmt,
    },
    "length-of-degree-longitude": {
        "title": "Length of 1 Degree Longitude",
        "latex": r"L_{lon}=111.32\cos\phi",
        "fields": [{"name": "latitude", "label": "Latitude phi (deg)"}],
        "compute": _length_of_degree_longitude,
        "substitute": lambda d: "Llon = 111.32*cos(latitude)",
        "answer_label": "Length (km)",
        "format_answer": _fmt,
    },
    "length-of-degree-latitude": {
        "title": "Length of 1 Degree Latitude",
        "latex": r"L_{lat}\approx111.32\,\text{km}",
        "fields": [{"name": "dummy", "label": "Any value (ignored)", "min": 0}],
        "compute": _length_of_degree_latitude,
        "substitute": lambda d: "Llat approx 111.32 km",
        "answer_label": "Length (km)",
        "format_answer": _fmt,
    },
    "time-zone-offset-from-longitude": {
        "title": "Time Zone Offset from Longitude",
        "latex": r"\Delta t=\frac{\lambda}{15}",
        "fields": [{"name": "longitude", "label": "Longitude lambda (deg)"}],
        "compute": _time_zone_offset,
        "substitute": lambda d: "offset_hours = longitude/15",
        "answer_label": "Offset (hours)",
        "format_answer": _fmt,
    },
    "local-time-from-gmt": {
        "title": "Local Time from GMT",
        "latex": r"\text{Local}=\text{GMT}+\frac{\lambda}{15}",
        "fields": [{"name": "gmt_hour", "label": "GMT hour (0-24)"}, {"name": "longitude", "label": "Longitude lambda (deg)"}],
        "compute": _local_time_from_gmt,
        "substitute": lambda d: "Local hour = GMT + longitude/15",
        "answer_label": "Local hour",
        "format_answer": _fmt,
    },
    "solar-time-difference-minutes": {
        "title": "Solar Time Difference",
        "latex": r"\Delta t_{min}=4\times\Delta\lambda",
        "fields": [{"name": "longitude_diff", "label": "Longitude difference (deg)"}],
        "compute": _solar_noon_difference_minutes,
        "substitute": lambda d: "Delta t (min)=4*longitude_diff",
        "answer_label": "Time difference (min)",
        "format_answer": _fmt,
    },
}


GEOGRAPHY_FORMULA_GROUPS = [
    {
        "title": "Cartography & Spatial Measurement",
        "slugs": [
            "great-circle-distance",
            "ground-distance-from-scale",
            "map-distance-from-scale",
            "scale-denominator",
        ],
    },
    {
        "title": "Population Geography",
        "slugs": [
            "population-density",
            "population-growth-future",
            "population-growth-rate-percent",
            "doubling-time-rule-70",
            "crude-birth-rate",
            "crude-death-rate",
            "net-migration-rate",
            "sex-ratio",
            "dependency-ratio",
            "arithmetic-density",
            "physiological-density",
            "agricultural-density",
            "natural-increase-rate-per-thousand",
        ],
    },
    {
        "title": "Geomorphology & Hydrology",
        "slugs": [
            "gradient",
            "slope-percent",
            "relief-ratio",
            "drainage-density",
            "stream-discharge",
            "runoff-coefficient",
            "infiltration-rate",
        ],
    },
    {
        "title": "Climatology & Weather",
        "slugs": [
            "environmental-lapse-rate",
            "relative-humidity",
            "dew-point-approximation",
            "celsius-to-fahrenheit",
            "fahrenheit-to-celsius",
            "kelvin-to-celsius",
            "celsius-to-kelvin",
        ],
    },
    {
        "title": "Earth Geometry & Time",
        "slugs": [
            "earth-circumference-at-latitude",
            "length-of-degree-longitude",
            "length-of-degree-latitude",
            "time-zone-offset-from-longitude",
            "local-time-from-gmt",
            "solar-time-difference-minutes",
        ],
    },
]


GEOGRAPHY_FORMULA_DESCRIPTIONS = {
    "great-circle-distance": "Estimate shortest path distance between two coordinates on Earth.",
    "ground-distance-from-scale": "Convert map distance into real-world distance.",
    "map-distance-from-scale": "Convert real-world distance into map distance.",
    "scale-denominator": "Find map scale denominator from map and ground distances.",
    "population-density": "Compute people per unit area.",
    "population-growth-future": "Project future population from growth rate and time.",
    "population-growth-rate-percent": "Compute percent growth between two population values.",
    "doubling-time-rule-70": "Estimate doubling time from annual growth rate.",
    "crude-birth-rate": "Compute births per thousand people.",
    "crude-death-rate": "Compute deaths per thousand people.",
    "net-migration-rate": "Measure migration balance per thousand people.",
    "sex-ratio": "Compute males per 100 females.",
    "dependency-ratio": "Measure dependent population relative to working-age group.",
    "arithmetic-density": "Compute basic population density measure.",
    "physiological-density": "Compute pressure on arable land from population.",
    "agricultural-density": "Compute farmers per unit arable land.",
    "natural-increase-rate-per-thousand": "Compute natural increase from birth and death rates.",
    "gradient": "Compute vertical change over horizontal distance.",
    "slope-percent": "Express slope as a percentage.",
    "relief-ratio": "Compare basin relief to basin length.",
    "drainage-density": "Measure stream network density in a basin.",
    "stream-discharge": "Compute river discharge from area and velocity.",
    "runoff-coefficient": "Estimate runoff share of precipitation.",
    "infiltration-rate": "Estimate water infiltration into soil over time.",
    "environmental-lapse-rate": "Estimate temperature change with elevation.",
    "relative-humidity": "Compute moisture level relative to saturation.",
    "dew-point-approximation": "Estimate dew point from temperature and relative humidity.",
    "celsius-to-fahrenheit": "Convert temperature from Celsius to Fahrenheit.",
    "fahrenheit-to-celsius": "Convert temperature from Fahrenheit to Celsius.",
    "kelvin-to-celsius": "Convert temperature from Kelvin to Celsius.",
    "celsius-to-kelvin": "Convert temperature from Celsius to Kelvin.",
    "earth-circumference-at-latitude": "Estimate east-west circumference at a latitude.",
    "length-of-degree-longitude": "Find longitude degree length by latitude.",
    "length-of-degree-latitude": "Find approximate latitude degree length.",
    "time-zone-offset-from-longitude": "Convert longitude into UTC offset.",
    "local-time-from-gmt": "Compute local solar time from GMT and longitude.",
    "solar-time-difference-minutes": "Compute solar time difference from longitude difference.",
}
