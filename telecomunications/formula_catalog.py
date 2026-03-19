import math


LIGHT_SPEED = 299_792_458.0
BOLTZMANN = 1.380649e-23


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _positive(value, label):
    if value <= 0:
        raise ValueError(f"{label} must be greater than 0.")


def _power_to_dbm(d):
    _positive(d["power_w"], "Power")
    return 10 * math.log10(d["power_w"] * 1000)


def _dbm_to_power_w(d):
    return 10 ** ((d["power_dbm"] - 30) / 10)


def _db_ratio_from_power(d):
    _positive(d["p2"], "P2")
    _positive(d["p1"], "P1")
    return 10 * math.log10(d["p2"] / d["p1"])


def _db_ratio_from_voltage(d):
    _positive(d["v2"], "V2")
    _positive(d["v1"], "V1")
    return 20 * math.log10(d["v2"] / d["v1"])


def _linear_from_db(d):
    return 10 ** (d["db"] / 10)


def _wavelength(d):
    _positive(d["frequency_hz"], "Frequency")
    return LIGHT_SPEED / d["frequency_hz"]


def _frequency_from_wavelength(d):
    _positive(d["wavelength_m"], "Wavelength")
    return LIGHT_SPEED / d["wavelength_m"]


def _free_space_path_loss_db(d):
    _positive(d["distance_km"], "Distance")
    _positive(d["frequency_mhz"], "Frequency")
    return 32.44 + 20 * math.log10(d["distance_km"]) + 20 * math.log10(d["frequency_mhz"])


def _received_power_link_budget(d):
    return d["tx_power_dbm"] + d["tx_gain_dbi"] + d["rx_gain_dbi"] - d["path_loss_db"] - d["other_losses_db"]


def _friis_received_power_w(d):
    _positive(d["distance_m"], "Distance")
    _positive(d["frequency_hz"], "Frequency")
    wavelength = LIGHT_SPEED / d["frequency_hz"]
    factor = wavelength / (4 * math.pi * d["distance_m"])
    return d["tx_power_w"] * d["tx_gain_linear"] * d["rx_gain_linear"] * factor ** 2


def _propagation_delay(d):
    _positive(d["velocity_m_s"], "Velocity")
    return d["distance_m"] / d["velocity_m_s"]


def _round_trip_time(d):
    _positive(d["velocity_m_s"], "Velocity")
    return 2 * d["distance_m"] / d["velocity_m_s"]


def _thermal_noise_power_w(d):
    _positive(d["temperature_k"], "Temperature")
    _positive(d["bandwidth_hz"], "Bandwidth")
    return BOLTZMANN * d["temperature_k"] * d["bandwidth_hz"]


def _thermal_noise_floor_dbm(d):
    _positive(d["bandwidth_hz"], "Bandwidth")
    return -174 + 10 * math.log10(d["bandwidth_hz"])


def _snr_db(d):
    _positive(d["signal_w"], "Signal power")
    _positive(d["noise_w"], "Noise power")
    return 10 * math.log10(d["signal_w"] / d["noise_w"])


def _snr_linear(d):
    return 10 ** (d["snr_db"] / 10)


def _shannon_capacity(d):
    _positive(d["bandwidth_hz"], "Bandwidth")
    if d["snr_linear"] <= 0:
        raise ValueError("SNR must be greater than 0.")
    return d["bandwidth_hz"] * math.log2(1 + d["snr_linear"])


def _nyquist_bitrate(d):
    _positive(d["bandwidth_hz"], "Bandwidth")
    if d["levels"] < 2:
        raise ValueError("Signal levels must be at least 2.")
    return 2 * d["bandwidth_hz"] * math.log2(d["levels"])


def _symbol_rate(d):
    _positive(d["bits_per_second"], "Bit rate")
    _positive(d["bits_per_symbol"], "Bits per symbol")
    return d["bits_per_second"] / d["bits_per_symbol"]


def _qam_bits_per_symbol(d):
    if d["mod_order"] < 2:
        raise ValueError("M must be at least 2.")
    return math.log2(d["mod_order"])


def _ebn0_from_snr(d):
    _positive(d["bitrate_bps"], "Bitrate")
    _positive(d["bandwidth_hz"], "Bandwidth")
    return d["snr_db"] + 10 * math.log10(d["bandwidth_hz"] / d["bitrate_bps"])


def _snr_from_ebn0(d):
    _positive(d["bitrate_bps"], "Bitrate")
    _positive(d["bandwidth_hz"], "Bandwidth")
    return d["ebn0_db"] + 10 * math.log10(d["bitrate_bps"] / d["bandwidth_hz"])


def _ber_bpsk_awgn(d):
    linear = 10 ** (d["ebn0_db"] / 10)
    return 0.5 * math.erfc(math.sqrt(linear))


def _vswr_from_gamma(d):
    gamma = d["gamma"]
    if gamma < 0 or gamma >= 1:
        raise ValueError("Reflection coefficient magnitude must satisfy 0 <= |Gamma| < 1.")
    return (1 + gamma) / (1 - gamma)


def _return_loss_from_gamma(d):
    gamma = d["gamma"]
    if gamma <= 0 or gamma >= 1:
        raise ValueError("Reflection coefficient magnitude must satisfy 0 < |Gamma| < 1.")
    return -20 * math.log10(gamma)


def _gamma_from_vswr(d):
    _positive(d["vswr"], "VSWR")
    if d["vswr"] < 1:
        raise ValueError("VSWR must be at least 1.")
    return (d["vswr"] - 1) / (d["vswr"] + 1)


def _bandwidth_from_risetime(d):
    _positive(d["rise_time_s"], "Rise time")
    return 0.35 / d["rise_time_s"]


def _channel_utilization(d):
    _positive(d["capacity_bps"], "Capacity")
    return (d["throughput_bps"] / d["capacity_bps"]) * 100


TELECOMUNICATIONS_FORMULAS = {
    "power-to-dbm": {
        "title": "Power to dBm",
        "latex": r"P_{dBm} = 10\log_{10}(P_W\cdot1000)",
        "fields": [{"name": "power_w", "label": "Power (W)", "min": 0}],
        "compute": _power_to_dbm,
        "substitute": lambda d: f"P_dBm = 10log10({_fmt(d['power_w'])}x1000)",
        "answer_label": "Power (dBm)",
        "format_answer": _fmt,
    },
    "dbm-to-power": {
        "title": "dBm to Power",
        "latex": r"P_W = 10^{(P_{dBm}-30)/10}",
        "fields": [{"name": "power_dbm", "label": "Power (dBm)"}],
        "compute": _dbm_to_power_w,
        "substitute": lambda d: f"P_W = 10^(({_fmt(d['power_dbm'])}-30)/10)",
        "answer_label": "Power (W)",
        "format_answer": _fmt,
    },
    "db-power-ratio": {
        "title": "dB from Power Ratio",
        "latex": r"G_{dB}=10\log_{10}(P_2/P_1)",
        "fields": [
            {"name": "p2", "label": "Output power P2", "min": 0},
            {"name": "p1", "label": "Input power P1", "min": 0},
        ],
        "compute": _db_ratio_from_power,
        "substitute": lambda d: f"G_dB = 10log10({_fmt(d['p2'])}/{_fmt(d['p1'])})",
        "answer_label": "Gain/Loss (dB)",
        "format_answer": _fmt,
    },
    "db-voltage-ratio": {
        "title": "dB from Voltage Ratio",
        "latex": r"G_{dB}=20\log_{10}(V_2/V_1)",
        "fields": [
            {"name": "v2", "label": "Output voltage V2", "min": 0},
            {"name": "v1", "label": "Input voltage V1", "min": 0},
        ],
        "compute": _db_ratio_from_voltage,
        "substitute": lambda d: f"G_dB = 20log10({_fmt(d['v2'])}/{_fmt(d['v1'])})",
        "answer_label": "Gain/Loss (dB)",
        "format_answer": _fmt,
    },
    "linear-from-db": {
        "title": "Linear Ratio from dB",
        "latex": r"R=10^{dB/10}",
        "fields": [{"name": "db", "label": "Value in dB"}],
        "compute": _linear_from_db,
        "substitute": lambda d: f"R = 10^({_fmt(d['db'])}/10)",
        "answer_label": "Linear Ratio",
        "format_answer": _fmt,
    },
    "wavelength": {
        "title": "Wavelength",
        "latex": r"\lambda = c/f",
        "fields": [{"name": "frequency_hz", "label": "Frequency f (Hz)", "min": 0}],
        "compute": _wavelength,
        "substitute": lambda d: f"lambda = c/{_fmt(d['frequency_hz'])}",
        "answer_label": "Wavelength (m)",
        "format_answer": _fmt,
    },
    "frequency-from-wavelength": {
        "title": "Frequency from Wavelength",
        "latex": r"f = c/\lambda",
        "fields": [{"name": "wavelength_m", "label": "Wavelength lambda (m)", "min": 0}],
        "compute": _frequency_from_wavelength,
        "substitute": lambda d: f"f = c/{_fmt(d['wavelength_m'])}",
        "answer_label": "Frequency (Hz)",
        "format_answer": _fmt,
    },
    "fspl-db": {
        "title": "Free-Space Path Loss",
        "latex": r"FSPL_{dB}=32.44+20\log_{10}(d_{km})+20\log_{10}(f_{MHz})",
        "fields": [
            {"name": "distance_km", "label": "Distance d (km)", "min": 0},
            {"name": "frequency_mhz", "label": "Frequency f (MHz)", "min": 0},
        ],
        "compute": _free_space_path_loss_db,
        "substitute": lambda d: f"FSPL = 32.44 + 20log10({_fmt(d['distance_km'])}) + 20log10({_fmt(d['frequency_mhz'])})",
        "answer_label": "FSPL (dB)",
        "format_answer": _fmt,
    },
    "link-budget-rx-power": {
        "title": "Received Power (Link Budget)",
        "latex": r"P_r=P_t+G_t+G_r-L_p-L_o",
        "fields": [
            {"name": "tx_power_dbm", "label": "Tx power Pt (dBm)"},
            {"name": "tx_gain_dbi", "label": "Tx antenna gain Gt (dBi)"},
            {"name": "rx_gain_dbi", "label": "Rx antenna gain Gr (dBi)"},
            {"name": "path_loss_db", "label": "Path loss Lp (dB)"},
            {"name": "other_losses_db", "label": "Other losses Lo (dB)", "min": 0},
        ],
        "compute": _received_power_link_budget,
        "substitute": lambda d: f"Pr = {_fmt(d['tx_power_dbm'])}+{_fmt(d['tx_gain_dbi'])}+{_fmt(d['rx_gain_dbi'])}-{_fmt(d['path_loss_db'])}-{_fmt(d['other_losses_db'])}",
        "answer_label": "Received Power Pr (dBm)",
        "format_answer": _fmt,
    },
    "friis-received-power": {
        "title": "Friis Received Power (Linear)",
        "latex": r"P_r=P_tG_tG_r\left(\frac{\lambda}{4\pi d}\right)^2",
        "fields": [
            {"name": "tx_power_w", "label": "Transmit power Pt (W)", "min": 0},
            {"name": "tx_gain_linear", "label": "Tx gain Gt (linear)", "min": 0},
            {"name": "rx_gain_linear", "label": "Rx gain Gr (linear)", "min": 0},
            {"name": "frequency_hz", "label": "Frequency f (Hz)", "min": 0},
            {"name": "distance_m", "label": "Distance d (m)", "min": 0},
        ],
        "compute": _friis_received_power_w,
        "substitute": lambda d: f"Pr from Pt={_fmt(d['tx_power_w'])}, Gt={_fmt(d['tx_gain_linear'])}, Gr={_fmt(d['rx_gain_linear'])}",
        "answer_label": "Received Power Pr (W)",
        "format_answer": _fmt,
    },
    "propagation-delay": {
        "title": "Propagation Delay",
        "latex": r"t_p=d/v",
        "fields": [
            {"name": "distance_m", "label": "Distance d (m)", "min": 0},
            {"name": "velocity_m_s", "label": "Propagation velocity v (m/s)", "min": 0},
        ],
        "compute": _propagation_delay,
        "substitute": lambda d: f"tp = {_fmt(d['distance_m'])}/{_fmt(d['velocity_m_s'])}",
        "answer_label": "Delay tp (s)",
        "format_answer": _fmt,
    },
    "round-trip-time": {
        "title": "Round Trip Time (RTT)",
        "latex": r"RTT=2d/v",
        "fields": [
            {"name": "distance_m", "label": "One-way distance d (m)", "min": 0},
            {"name": "velocity_m_s", "label": "Propagation velocity v (m/s)", "min": 0},
        ],
        "compute": _round_trip_time,
        "substitute": lambda d: f"RTT = 2x{_fmt(d['distance_m'])}/{_fmt(d['velocity_m_s'])}",
        "answer_label": "RTT (s)",
        "format_answer": _fmt,
    },
    "thermal-noise-power": {
        "title": "Thermal Noise Power",
        "latex": r"N=kTB",
        "fields": [
            {"name": "temperature_k", "label": "Temperature T (K)", "min": 0},
            {"name": "bandwidth_hz", "label": "Bandwidth B (Hz)", "min": 0},
        ],
        "compute": _thermal_noise_power_w,
        "substitute": lambda d: f"N = kx{_fmt(d['temperature_k'])}x{_fmt(d['bandwidth_hz'])}",
        "answer_label": "Noise Power N (W)",
        "format_answer": _fmt,
    },
    "thermal-noise-floor": {
        "title": "Thermal Noise Floor",
        "latex": r"N_{dBm}=-174+10\log_{10}(B_{Hz})",
        "fields": [{"name": "bandwidth_hz", "label": "Bandwidth B (Hz)", "min": 0}],
        "compute": _thermal_noise_floor_dbm,
        "substitute": lambda d: f"N_dBm = -174 + 10log10({_fmt(d['bandwidth_hz'])})",
        "answer_label": "Noise Floor (dBm)",
        "format_answer": _fmt,
    },
    "snr-db": {
        "title": "SNR in dB",
        "latex": r"SNR_{dB}=10\log_{10}(S/N)",
        "fields": [
            {"name": "signal_w", "label": "Signal power S (W)", "min": 0},
            {"name": "noise_w", "label": "Noise power N (W)", "min": 0},
        ],
        "compute": _snr_db,
        "substitute": lambda d: f"SNR_dB = 10log10({_fmt(d['signal_w'])}/{_fmt(d['noise_w'])})",
        "answer_label": "SNR (dB)",
        "format_answer": _fmt,
    },
    "snr-linear": {
        "title": "SNR Linear from dB",
        "latex": r"SNR=10^{SNR_{dB}/10}",
        "fields": [{"name": "snr_db", "label": "SNR (dB)"}],
        "compute": _snr_linear,
        "substitute": lambda d: f"SNR = 10^({_fmt(d['snr_db'])}/10)",
        "answer_label": "SNR (linear)",
        "format_answer": _fmt,
    },
    "shannon-capacity": {
        "title": "Shannon Capacity",
        "latex": r"C=B\log_2(1+SNR)",
        "fields": [
            {"name": "bandwidth_hz", "label": "Bandwidth B (Hz)", "min": 0},
            {"name": "snr_linear", "label": "SNR (linear)", "min": 0},
        ],
        "compute": _shannon_capacity,
        "substitute": lambda d: f"C = {_fmt(d['bandwidth_hz'])}log2(1+{_fmt(d['snr_linear'])})",
        "answer_label": "Capacity C (bps)",
        "format_answer": _fmt,
    },
    "nyquist-bitrate": {
        "title": "Nyquist Bit Rate",
        "latex": r"R_b=2B\log_2(M)",
        "fields": [
            {"name": "bandwidth_hz", "label": "Bandwidth B (Hz)", "min": 0},
            {"name": "levels", "label": "Signal levels M", "type": "integer", "min": 2},
        ],
        "compute": _nyquist_bitrate,
        "substitute": lambda d: f"Rb = 2x{_fmt(d['bandwidth_hz'])}xlog2({_fmt(d['levels'])})",
        "answer_label": "Bit Rate Rb (bps)",
        "format_answer": _fmt,
    },
    "symbol-rate": {
        "title": "Symbol Rate",
        "latex": r"R_s = R_b / k",
        "fields": [
            {"name": "bits_per_second", "label": "Bit rate Rb (bps)", "min": 0},
            {"name": "bits_per_symbol", "label": "Bits per symbol k", "min": 1},
        ],
        "compute": _symbol_rate,
        "substitute": lambda d: f"Rs = {_fmt(d['bits_per_second'])}/{_fmt(d['bits_per_symbol'])}",
        "answer_label": "Symbol Rate Rs (baud)",
        "format_answer": _fmt,
    },
    "qam-bits-per-symbol": {
        "title": "QAM Bits per Symbol",
        "latex": r"k=\log_2(M)",
        "fields": [{"name": "mod_order", "label": "QAM order M", "type": "integer", "min": 2}],
        "compute": _qam_bits_per_symbol,
        "substitute": lambda d: f"k = log2({_fmt(d['mod_order'])})",
        "answer_label": "Bits per Symbol k",
        "format_answer": _fmt,
    },
    "ebn0-from-snr": {
        "title": "Eb/N0 from SNR",
        "latex": r"\frac{E_b}{N_0}_{dB}=SNR_{dB}+10\log_{10}(B/R_b)",
        "fields": [
            {"name": "snr_db", "label": "SNR (dB)"},
            {"name": "bandwidth_hz", "label": "Bandwidth B (Hz)", "min": 0},
            {"name": "bitrate_bps", "label": "Bitrate Rb (bps)", "min": 0},
        ],
        "compute": _ebn0_from_snr,
        "substitute": lambda d: f"Eb/N0 = {_fmt(d['snr_db'])} + 10log10({_fmt(d['bandwidth_hz'])}/{_fmt(d['bitrate_bps'])})",
        "answer_label": "Eb/N0 (dB)",
        "format_answer": _fmt,
    },
    "snr-from-ebn0": {
        "title": "SNR from Eb/N0",
        "latex": r"SNR_{dB}=\frac{E_b}{N_0}_{dB}+10\log_{10}(R_b/B)",
        "fields": [
            {"name": "ebn0_db", "label": "Eb/N0 (dB)"},
            {"name": "bitrate_bps", "label": "Bitrate Rb (bps)", "min": 0},
            {"name": "bandwidth_hz", "label": "Bandwidth B (Hz)", "min": 0},
        ],
        "compute": _snr_from_ebn0,
        "substitute": lambda d: f"SNR = {_fmt(d['ebn0_db'])} + 10log10({_fmt(d['bitrate_bps'])}/{_fmt(d['bandwidth_hz'])})",
        "answer_label": "SNR (dB)",
        "format_answer": _fmt,
    },
    "ber-bpsk-awgn": {
        "title": "BER for BPSK in AWGN",
        "latex": r"BER=\frac{1}{2}\operatorname{erfc}(\sqrt{E_b/N_0})",
        "fields": [{"name": "ebn0_db", "label": "Eb/N0 (dB)"}],
        "compute": _ber_bpsk_awgn,
        "substitute": lambda d: f"BER from Eb/N0={_fmt(d['ebn0_db'])} dB",
        "answer_label": "Bit Error Rate",
        "format_answer": _fmt,
    },
    "vswr-from-gamma": {
        "title": "VSWR from Reflection Coefficient",
        "latex": r"VSWR=\frac{1+|\Gamma|}{1-|\Gamma|}",
        "fields": [{"name": "gamma", "label": "|Gamma|"}],
        "compute": _vswr_from_gamma,
        "substitute": lambda d: f"VSWR=(1+{_fmt(d['gamma'])})/(1-{_fmt(d['gamma'])})",
        "answer_label": "VSWR",
        "format_answer": _fmt,
    },
    "return-loss": {
        "title": "Return Loss",
        "latex": r"RL=-20\log_{10}|\Gamma|",
        "fields": [{"name": "gamma", "label": "|Gamma|"}],
        "compute": _return_loss_from_gamma,
        "substitute": lambda d: f"RL=-20log10({_fmt(d['gamma'])})",
        "answer_label": "Return Loss (dB)",
        "format_answer": _fmt,
    },
    "gamma-from-vswr": {
        "title": "Reflection Coefficient from VSWR",
        "latex": r"|\Gamma|=\frac{VSWR-1}{VSWR+1}",
        "fields": [{"name": "vswr", "label": "VSWR", "min": 1}],
        "compute": _gamma_from_vswr,
        "substitute": lambda d: f"|Gamma|=({_fmt(d['vswr'])}-1)/({_fmt(d['vswr'])}+1)",
        "answer_label": "|Gamma|",
        "format_answer": _fmt,
    },
    "bandwidth-from-rise-time": {
        "title": "Bandwidth from Rise Time",
        "latex": r"BW\approx0.35/t_r",
        "fields": [{"name": "rise_time_s", "label": "Rise time tr (s)", "min": 0}],
        "compute": _bandwidth_from_risetime,
        "substitute": lambda d: f"BW=0.35/{_fmt(d['rise_time_s'])}",
        "answer_label": "Bandwidth (Hz)",
        "format_answer": _fmt,
    },
    "channel-utilization": {
        "title": "Channel Utilization",
        "latex": r"U=(T/C)\times100\%",
        "fields": [
            {"name": "throughput_bps", "label": "Throughput T (bps)", "min": 0},
            {"name": "capacity_bps", "label": "Capacity C (bps)", "min": 0},
        ],
        "compute": _channel_utilization,
        "substitute": lambda d: f"U=({_fmt(d['throughput_bps'])}/{_fmt(d['capacity_bps'])})x100",
        "answer_label": "Utilization (%)",
        "format_answer": _fmt,
    },
}

TELECOMUNICATIONS_FORMULA_GROUPS = [
    {
        "title": "Signal Levels and RF Basics",
        "slugs": [
            "power-to-dbm",
            "dbm-to-power",
            "db-power-ratio",
            "db-voltage-ratio",
            "linear-from-db",
            "wavelength",
            "frequency-from-wavelength",
            "fspl-db",
            "link-budget-rx-power",
            "friis-received-power",
            "propagation-delay",
            "round-trip-time",
        ],
    },
    {
        "title": "Noise, Capacity, and Digital Links",
        "slugs": [
            "thermal-noise-power",
            "thermal-noise-floor",
            "snr-db",
            "snr-linear",
            "shannon-capacity",
            "nyquist-bitrate",
            "symbol-rate",
            "qam-bits-per-symbol",
            "ebn0-from-snr",
            "snr-from-ebn0",
            "ber-bpsk-awgn",
            "channel-utilization",
        ],
    },
    {
        "title": "Transmission Lines and Timing",
        "slugs": [
            "vswr-from-gamma",
            "return-loss",
            "gamma-from-vswr",
            "bandwidth-from-rise-time",
        ],
    },
]

TELECOMUNICATIONS_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in TELECOMUNICATIONS_FORMULAS.items()
}
