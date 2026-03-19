def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _nonzero(value, label):
    if abs(value) < 1e-12:
        raise ValueError(f"{label} must not be zero.")


def _positive(value, label):
    if value <= 0:
        raise ValueError(f"{label} must be greater than 0.")


def _fraction(value, label):
    if value < 0 or value > 1:
        raise ValueError(f"{label} must be between 0 and 1.")


def _percentage(value, label):
    if value <= 0 or value > 100:
        raise ValueError(f"{label} must be greater than 0 and at most 100.")


def _clean_text(value):
    return value.strip().replace(" ", "")


def _parse_base_number(value, base, label, allowed_chars):
    text = _clean_text(value)
    if not text:
        raise ValueError(f"{label} is required.")

    if base == 16 and text.lower().startswith("0x"):
        text = text[2:]
    if base == 8 and text.lower().startswith("0o"):
        text = text[2:]
    if base == 2 and text.lower().startswith("0b"):
        text = text[2:]

    if not text or any(ch.lower() not in allowed_chars for ch in text):
        raise ValueError(f"{label} must contain only valid base-{base} digits.")
    return int(text, base)


def _binary_to_decimal(d):
    return _parse_base_number(d["binary"], 2, "Binary number", {"0", "1"})


def _decimal_to_binary(d):
    if d["decimal"] < 0:
        raise ValueError("Decimal number must be non-negative.")
    return format(d["decimal"], "b")


def _hex_to_decimal(d):
    return _parse_base_number(
        d["hex_value"],
        16,
        "Hexadecimal number",
        set("0123456789abcdef"),
    )


def _decimal_to_hex(d):
    if d["decimal"] < 0:
        raise ValueError("Decimal number must be non-negative.")
    return format(d["decimal"], "X")


def _octal_to_decimal(d):
    return _parse_base_number(d["octal"], 8, "Octal number", set("01234567"))


def _decimal_to_octal(d):
    if d["decimal"] < 0:
        raise ValueError("Decimal number must be non-negative.")
    return format(d["decimal"], "o")


def _bytes_to_bits(d):
    return d["bytes"] * 8


def _bits_to_bytes(d):
    return d["bits"] / 8


def _kilobytes_to_megabytes(d):
    return d["kilobytes"] / 1024


def _megabytes_to_gigabytes(d):
    return d["megabytes"] / 1024


def _data_transfer_time(d):
    _positive(d["bandwidth_mbps"], "Bandwidth")
    return d["file_size_mb"] * 8 / d["bandwidth_mbps"]


def _download_time_with_efficiency(d):
    _positive(d["bandwidth_mbps"], "Bandwidth")
    _percentage(d["efficiency_percent"], "Efficiency")
    effective_bandwidth = d["bandwidth_mbps"] * (d["efficiency_percent"] / 100)
    return d["file_size_mb"] * 8 / effective_bandwidth


def _cpu_clock_cycles(d):
    return d["instruction_count"] * d["cpi"]


def _cpu_execution_time(d):
    _positive(d["clock_rate_ghz"], "Clock rate")
    return d["instruction_count"] * d["cpi"] / (d["clock_rate_ghz"] * 1_000_000_000)


def _mips(d):
    _positive(d["execution_time_s"], "Execution time")
    return d["instruction_count"] / (d["execution_time_s"] * 1_000_000)


def _speedup(d):
    _positive(d["new_time_s"], "New execution time")
    return d["old_time_s"] / d["new_time_s"]


def _amdahl_speedup(d):
    _fraction(d["parallel_fraction"], "Parallel fraction")
    _positive(d["parallel_speedup"], "Parallel speedup")
    denominator = (1 - d["parallel_fraction"]) + (
        d["parallel_fraction"] / d["parallel_speedup"]
    )
    _nonzero(denominator, "Amdahl denominator")
    return 1 / denominator


def _cache_hit_rate(d):
    _positive(d["accesses"], "Total accesses")
    if d["hits"] > d["accesses"]:
        raise ValueError("Hits cannot exceed total accesses.")
    return d["hits"] / d["accesses"] * 100


def _cache_miss_rate(d):
    _positive(d["accesses"], "Total accesses")
    if d["misses"] > d["accesses"]:
        raise ValueError("Misses cannot exceed total accesses.")
    return d["misses"] / d["accesses"] * 100


def _effective_access_time(d):
    _fraction(d["miss_rate"], "Miss rate")
    return d["hit_time_ns"] + d["miss_rate"] * d["miss_penalty_ns"]


def _network_throughput(d):
    _positive(d["time_s"], "Time")
    return d["data_mb"] / d["time_s"]


def _propagation_delay(d):
    _positive(d["speed_m_s"], "Propagation speed")
    return d["distance_km"] * 1000 / d["speed_m_s"]


def _bandwidth_delay_product(d):
    return d["bandwidth_mbps"] * 1_000_000 * (d["rtt_ms"] / 1000)


def _subnet_usable_hosts(d):
    prefix = d["prefix_length"]
    if prefix < 0 or prefix > 32:
        raise ValueError("Prefix length must be between 0 and 32.")
    host_bits = 32 - prefix
    if host_bits <= 1:
        return 0
    return (2 ** host_bits) - 2


def _subnets_from_borrowed_bits(d):
    return 2 ** d["borrowed_bits"]


def _hamming_parity_bits(d):
    data_bits = d["data_bits"]
    r = 0
    while 2 ** r < data_bits + r + 1:
        r += 1
    return r


def _audio_file_size_mb(d):
    bits = d["sample_rate_hz"] * d["bit_depth"] * d["channels"] * d["duration_s"]
    return bits / 8 / 1_000_000


def _image_file_size_mb(d):
    bits = d["width_px"] * d["height_px"] * d["color_depth_bits"]
    return bits / 8 / 1_000_000


COMPUTING_FORMULAS = {
    "binary-to-decimal": {
        "title": "Binary to Decimal",
        "latex": r"\text{Decimal} = \sum b_i 2^i",
        "fields": [
            {"name": "binary", "label": "Binary number", "type": "text", "placeholder": "e.g. 101101"},
        ],
        "compute": _binary_to_decimal,
        "substitute": lambda d: f"Convert binary {d['binary']} to base 10",
        "answer_label": "Decimal",
        "format_answer": _fmt,
    },
    "decimal-to-binary": {
        "title": "Decimal to Binary",
        "latex": r"\text{Binary} = \text{base-2 representation of } n",
        "fields": [
            {"name": "decimal", "label": "Decimal number", "type": "integer", "min": 0},
        ],
        "compute": _decimal_to_binary,
        "substitute": lambda d: f"Convert decimal {_fmt(d['decimal'])} to base 2",
        "answer_label": "Binary",
        "format_answer": lambda v: v,
    },
    "hex-to-decimal": {
        "title": "Hexadecimal to Decimal",
        "latex": r"\text{Decimal} = \sum h_i 16^i",
        "fields": [
            {"name": "hex_value", "label": "Hexadecimal number", "type": "text", "placeholder": "e.g. 2F or 0x2F"},
        ],
        "compute": _hex_to_decimal,
        "substitute": lambda d: f"Convert hexadecimal {d['hex_value']} to base 10",
        "answer_label": "Decimal",
        "format_answer": _fmt,
    },
    "decimal-to-hex": {
        "title": "Decimal to Hexadecimal",
        "latex": r"\text{Hex} = \text{base-16 representation of } n",
        "fields": [
            {"name": "decimal", "label": "Decimal number", "type": "integer", "min": 0},
        ],
        "compute": _decimal_to_hex,
        "substitute": lambda d: f"Convert decimal {_fmt(d['decimal'])} to base 16",
        "answer_label": "Hex",
        "format_answer": lambda v: v,
    },
    "octal-to-decimal": {
        "title": "Octal to Decimal",
        "latex": r"\text{Decimal} = \sum o_i 8^i",
        "fields": [
            {"name": "octal", "label": "Octal number", "type": "text", "placeholder": "e.g. 745 or 0o745"},
        ],
        "compute": _octal_to_decimal,
        "substitute": lambda d: f"Convert octal {d['octal']} to base 10",
        "answer_label": "Decimal",
        "format_answer": _fmt,
    },
    "decimal-to-octal": {
        "title": "Decimal to Octal",
        "latex": r"\text{Octal} = \text{base-8 representation of } n",
        "fields": [
            {"name": "decimal", "label": "Decimal number", "type": "integer", "min": 0},
        ],
        "compute": _decimal_to_octal,
        "substitute": lambda d: f"Convert decimal {_fmt(d['decimal'])} to base 8",
        "answer_label": "Octal",
        "format_answer": lambda v: v,
    },
    "bytes-to-bits": {
        "title": "Bytes to Bits",
        "latex": r"\text{bits} = 8 \cdot \text{bytes}",
        "fields": [
            {"name": "bytes", "label": "Bytes", "min": 0},
        ],
        "compute": _bytes_to_bits,
        "substitute": lambda d: f"bits = 8 x {_fmt(d['bytes'])}",
        "answer_label": "Bits",
        "format_answer": _fmt,
    },
    "bits-to-bytes": {
        "title": "Bits to Bytes",
        "latex": r"\text{bytes} = \text{bits} / 8",
        "fields": [
            {"name": "bits", "label": "Bits", "min": 0},
        ],
        "compute": _bits_to_bytes,
        "substitute": lambda d: f"bytes = {_fmt(d['bits'])} / 8",
        "answer_label": "Bytes",
        "format_answer": _fmt,
    },
    "kilobytes-to-megabytes": {
        "title": "Kilobytes to Megabytes",
        "latex": r"\text{MB} = \text{KB} / 1024",
        "fields": [
            {"name": "kilobytes", "label": "Kilobytes", "min": 0},
        ],
        "compute": _kilobytes_to_megabytes,
        "substitute": lambda d: f"MB = {_fmt(d['kilobytes'])} / 1024",
        "answer_label": "MB",
        "format_answer": _fmt,
    },
    "megabytes-to-gigabytes": {
        "title": "Megabytes to Gigabytes",
        "latex": r"\text{GB} = \text{MB} / 1024",
        "fields": [
            {"name": "megabytes", "label": "Megabytes", "min": 0},
        ],
        "compute": _megabytes_to_gigabytes,
        "substitute": lambda d: f"GB = {_fmt(d['megabytes'])} / 1024",
        "answer_label": "GB",
        "format_answer": _fmt,
    },
    "data-transfer-time": {
        "title": "Data Transfer Time",
        "latex": r"t = \dfrac{\text{file size (MB)} \cdot 8}{\text{bandwidth (Mb/s)}}",
        "fields": [
            {"name": "file_size_mb", "label": "File size (MB)", "min": 0},
            {"name": "bandwidth_mbps", "label": "Bandwidth (Mb/s)", "min": 0},
        ],
        "compute": _data_transfer_time,
        "substitute": lambda d: f"t = ({_fmt(d['file_size_mb'])} x 8) / {_fmt(d['bandwidth_mbps'])}",
        "answer_label": "Time (s)",
        "format_answer": _fmt,
    },
    "download-time-with-efficiency": {
        "title": "Download Time with Efficiency",
        "latex": r"t = \dfrac{\text{file size (MB)} \cdot 8}{\text{bandwidth} \cdot \eta}",
        "fields": [
            {"name": "file_size_mb", "label": "File size (MB)", "min": 0},
            {"name": "bandwidth_mbps", "label": "Bandwidth (Mb/s)", "min": 0},
            {"name": "efficiency_percent", "label": "Efficiency (%)", "min": 0, "max": 100},
        ],
        "compute": _download_time_with_efficiency,
        "substitute": lambda d: (
            f"t = ({_fmt(d['file_size_mb'])} x 8) / ({_fmt(d['bandwidth_mbps'])} x {_fmt(d['efficiency_percent'])}/100)"
        ),
        "answer_label": "Time (s)",
        "format_answer": _fmt,
    },
    "cpu-clock-cycles": {
        "title": "CPU Clock Cycles",
        "latex": r"\text{Cycles} = \text{Instruction Count} \cdot \text{CPI}",
        "fields": [
            {"name": "instruction_count", "label": "Instruction count", "min": 0},
            {"name": "cpi", "label": "Cycles per instruction (CPI)", "min": 0},
        ],
        "compute": _cpu_clock_cycles,
        "substitute": lambda d: f"Cycles = {_fmt(d['instruction_count'])} x {_fmt(d['cpi'])}",
        "answer_label": "Cycles",
        "format_answer": _fmt,
    },
    "cpu-execution-time": {
        "title": "CPU Execution Time",
        "latex": r"t = \dfrac{\text{Instruction Count} \cdot \text{CPI}}{\text{Clock Rate}}",
        "fields": [
            {"name": "instruction_count", "label": "Instruction count", "min": 0},
            {"name": "cpi", "label": "Cycles per instruction (CPI)", "min": 0},
            {"name": "clock_rate_ghz", "label": "Clock rate (GHz)", "min": 0},
        ],
        "compute": _cpu_execution_time,
        "substitute": lambda d: (
            f"t = ({_fmt(d['instruction_count'])} x {_fmt(d['cpi'])}) / ({_fmt(d['clock_rate_ghz'])} x 10^9)"
        ),
        "answer_label": "Time (s)",
        "format_answer": _fmt,
    },
    "mips": {
        "title": "MIPS",
        "latex": r"\text{MIPS} = \dfrac{\text{Instruction Count}}{\text{Execution Time} \cdot 10^6}",
        "fields": [
            {"name": "instruction_count", "label": "Instruction count", "min": 0},
            {"name": "execution_time_s", "label": "Execution time (s)", "min": 0},
        ],
        "compute": _mips,
        "substitute": lambda d: f"MIPS = {_fmt(d['instruction_count'])} / ({_fmt(d['execution_time_s'])} x 10^6)",
        "answer_label": "MIPS",
        "format_answer": _fmt,
    },
    "speedup": {
        "title": "Speedup",
        "latex": r"S = \dfrac{T_{old}}{T_{new}}",
        "fields": [
            {"name": "old_time_s", "label": "Old execution time (s)", "min": 0},
            {"name": "new_time_s", "label": "New execution time (s)", "min": 0},
        ],
        "compute": _speedup,
        "substitute": lambda d: f"S = {_fmt(d['old_time_s'])} / {_fmt(d['new_time_s'])}",
        "answer_label": "Speedup",
        "format_answer": _fmt,
    },
    "amdahls-law": {
        "title": "Amdahl's Law",
        "latex": r"S = \dfrac{1}{(1-p) + p/s}",
        "fields": [
            {"name": "parallel_fraction", "label": "Parallel fraction p", "min": 0, "max": 1},
            {"name": "parallel_speedup", "label": "Parallel speedup s", "min": 0},
        ],
        "compute": _amdahl_speedup,
        "substitute": lambda d: (
            f"S = 1 / ((1 - {_fmt(d['parallel_fraction'])}) + {_fmt(d['parallel_fraction'])}/{_fmt(d['parallel_speedup'])})"
        ),
        "answer_label": "Speedup",
        "format_answer": _fmt,
    },
    "cache-hit-rate": {
        "title": "Cache Hit Rate",
        "latex": r"\text{Hit Rate} = \dfrac{\text{Hits}}{\text{Accesses}} \cdot 100\%",
        "fields": [
            {"name": "hits", "label": "Hits", "min": 0},
            {"name": "accesses", "label": "Total accesses", "min": 0},
        ],
        "compute": _cache_hit_rate,
        "substitute": lambda d: f"Hit rate = {_fmt(d['hits'])} / {_fmt(d['accesses'])} x 100",
        "answer_label": "Hit Rate",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "cache-miss-rate": {
        "title": "Cache Miss Rate",
        "latex": r"\text{Miss Rate} = \dfrac{\text{Misses}}{\text{Accesses}} \cdot 100\%",
        "fields": [
            {"name": "misses", "label": "Misses", "min": 0},
            {"name": "accesses", "label": "Total accesses", "min": 0},
        ],
        "compute": _cache_miss_rate,
        "substitute": lambda d: f"Miss rate = {_fmt(d['misses'])} / {_fmt(d['accesses'])} x 100",
        "answer_label": "Miss Rate",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "effective-access-time": {
        "title": "Effective Access Time",
        "latex": r"\text{EAT} = \text{Hit Time} + \text{Miss Rate} \cdot \text{Miss Penalty}",
        "fields": [
            {"name": "hit_time_ns", "label": "Hit time (ns)", "min": 0},
            {"name": "miss_rate", "label": "Miss rate", "min": 0, "max": 1},
            {"name": "miss_penalty_ns", "label": "Miss penalty (ns)", "min": 0},
        ],
        "compute": _effective_access_time,
        "substitute": lambda d: (
            f"EAT = {_fmt(d['hit_time_ns'])} + {_fmt(d['miss_rate'])} x {_fmt(d['miss_penalty_ns'])}"
        ),
        "answer_label": "EAT (ns)",
        "format_answer": _fmt,
    },
    "network-throughput": {
        "title": "Network Throughput",
        "latex": r"\text{Throughput} = \dfrac{\text{Data}}{\text{Time}}",
        "fields": [
            {"name": "data_mb", "label": "Data transferred (MB)", "min": 0},
            {"name": "time_s", "label": "Time (s)", "min": 0},
        ],
        "compute": _network_throughput,
        "substitute": lambda d: f"Throughput = {_fmt(d['data_mb'])} / {_fmt(d['time_s'])}",
        "answer_label": "Throughput (MB/s)",
        "format_answer": _fmt,
    },
    "propagation-delay": {
        "title": "Propagation Delay",
        "latex": r"t = \dfrac{d}{v}",
        "fields": [
            {"name": "distance_km", "label": "Distance (km)", "min": 0},
            {"name": "speed_m_s", "label": "Propagation speed (m/s)", "min": 0},
        ],
        "compute": _propagation_delay,
        "substitute": lambda d: f"t = ({_fmt(d['distance_km'])} x 1000) / {_fmt(d['speed_m_s'])}",
        "answer_label": "Delay (s)",
        "format_answer": _fmt,
    },
    "bandwidth-delay-product": {
        "title": "Bandwidth-Delay Product",
        "latex": r"\text{BDP} = \text{Bandwidth} \cdot \text{RTT}",
        "fields": [
            {"name": "bandwidth_mbps", "label": "Bandwidth (Mb/s)", "min": 0},
            {"name": "rtt_ms", "label": "Round-trip time (ms)", "min": 0},
        ],
        "compute": _bandwidth_delay_product,
        "substitute": lambda d: f"BDP = {_fmt(d['bandwidth_mbps'])} x 10^6 x ({_fmt(d['rtt_ms'])}/1000)",
        "answer_label": "BDP (bits)",
        "format_answer": _fmt,
    },
    "subnet-usable-hosts": {
        "title": "Subnet Usable Hosts",
        "latex": r"\text{Hosts} = 2^{32-p} - 2",
        "fields": [
            {"name": "prefix_length", "label": "Prefix length", "type": "integer", "min": 0, "max": 32},
        ],
        "compute": _subnet_usable_hosts,
        "substitute": lambda d: f"Hosts = 2^(32 - {_fmt(d['prefix_length'])}) - 2",
        "answer_label": "Usable Hosts",
        "format_answer": _fmt,
    },
    "subnets-from-borrowed-bits": {
        "title": "Subnets from Borrowed Bits",
        "latex": r"\text{Subnets} = 2^n",
        "fields": [
            {"name": "borrowed_bits", "label": "Borrowed bits", "type": "integer", "min": 0},
        ],
        "compute": _subnets_from_borrowed_bits,
        "substitute": lambda d: f"Subnets = 2^{_fmt(d['borrowed_bits'])}",
        "answer_label": "Subnets",
        "format_answer": _fmt,
    },
    "hamming-parity-bits": {
        "title": "Hamming Code Parity Bits",
        "latex": r"2^r \ge m + r + 1",
        "fields": [
            {"name": "data_bits", "label": "Data bits m", "type": "integer", "min": 1},
        ],
        "compute": _hamming_parity_bits,
        "substitute": lambda d: f"Find smallest r such that 2^r >= {_fmt(d['data_bits'])} + r + 1",
        "answer_label": "Parity Bits",
        "format_answer": _fmt,
    },
    "audio-file-size": {
        "title": "Uncompressed Audio File Size",
        "latex": r"\text{Size} = \dfrac{f_s \cdot b \cdot c \cdot t}{8}",
        "fields": [
            {"name": "sample_rate_hz", "label": "Sample rate (Hz)", "min": 0},
            {"name": "bit_depth", "label": "Bit depth", "type": "integer", "min": 1},
            {"name": "channels", "label": "Channels", "type": "integer", "min": 1},
            {"name": "duration_s", "label": "Duration (s)", "min": 0},
        ],
        "compute": _audio_file_size_mb,
        "substitute": lambda d: (
            f"Size = ({_fmt(d['sample_rate_hz'])} x {_fmt(d['bit_depth'])} x {_fmt(d['channels'])} x {_fmt(d['duration_s'])}) / 8 / 10^6"
        ),
        "answer_label": "Size (MB)",
        "format_answer": _fmt,
    },
    "image-file-size": {
        "title": "Uncompressed Image File Size",
        "latex": r"\text{Size} = \dfrac{\text{width} \cdot \text{height} \cdot \text{color depth}}{8}",
        "fields": [
            {"name": "width_px", "label": "Width (px)", "type": "integer", "min": 1},
            {"name": "height_px", "label": "Height (px)", "type": "integer", "min": 1},
            {"name": "color_depth_bits", "label": "Color depth (bits)", "type": "integer", "min": 1},
        ],
        "compute": _image_file_size_mb,
        "substitute": lambda d: (
            f"Size = ({_fmt(d['width_px'])} x {_fmt(d['height_px'])} x {_fmt(d['color_depth_bits'])}) / 8 / 10^6"
        ),
        "answer_label": "Size (MB)",
        "format_answer": _fmt,
    },
}


COMPUTING_FORMULA_GROUPS = [
    {
        "title": "Number Systems & Units",
        "slugs": [
            "binary-to-decimal",
            "decimal-to-binary",
            "hex-to-decimal",
            "decimal-to-hex",
            "octal-to-decimal",
            "decimal-to-octal",
            "bytes-to-bits",
            "bits-to-bytes",
            "kilobytes-to-megabytes",
            "megabytes-to-gigabytes",
        ],
    },
    {
        "title": "Storage & Transfer",
        "slugs": [
            "data-transfer-time",
            "download-time-with-efficiency",
            "audio-file-size",
            "image-file-size",
        ],
    },
    {
        "title": "Computer Architecture & Performance",
        "slugs": [
            "cpu-clock-cycles",
            "cpu-execution-time",
            "mips",
            "speedup",
            "amdahls-law",
            "cache-hit-rate",
            "cache-miss-rate",
            "effective-access-time",
        ],
    },
    {
        "title": "Networking & Subnetting",
        "slugs": [
            "network-throughput",
            "propagation-delay",
            "bandwidth-delay-product",
            "subnet-usable-hosts",
            "subnets-from-borrowed-bits",
        ],
    },
    {
        "title": "Digital Communication",
        "slugs": [
            "hamming-parity-bits",
        ],
    },
]


COMPUTING_FORMULA_DESCRIPTIONS = {
    "binary-to-decimal": "Convert binary digits into a base-10 value.",
    "decimal-to-binary": "Express a decimal integer in base 2.",
    "hex-to-decimal": "Decode hexadecimal notation into decimal form.",
    "decimal-to-hex": "Convert a decimal integer into hexadecimal notation.",
    "octal-to-decimal": "Translate octal digits into decimal value.",
    "decimal-to-octal": "Represent a decimal integer in base 8.",
    "bytes-to-bits": "Convert byte counts into bit counts.",
    "bits-to-bytes": "Convert raw bits into bytes.",
    "kilobytes-to-megabytes": "Scale kilobytes into megabytes using 1024 KB per MB.",
    "megabytes-to-gigabytes": "Scale megabytes into gigabytes using 1024 MB per GB.",
    "data-transfer-time": "Estimate transfer time from file size and link bandwidth.",
    "download-time-with-efficiency": "Model download time with real-world link efficiency losses.",
    "cpu-clock-cycles": "Find the total cycles needed from instruction count and CPI.",
    "cpu-execution-time": "Compute processor run time from instructions, CPI, and clock rate.",
    "mips": "Measure throughput in millions of instructions per second.",
    "speedup": "Compare old and new execution times directly.",
    "amdahls-law": "Estimate the upper bound of parallel performance improvement.",
    "cache-hit-rate": "Find the percentage of memory accesses served by cache.",
    "cache-miss-rate": "Find the percentage of accesses that miss the cache.",
    "effective-access-time": "Combine hit time and miss penalty into average access latency.",
    "network-throughput": "Measure delivered data rate over elapsed time.",
    "propagation-delay": "Compute signal travel time over a physical medium.",
    "bandwidth-delay-product": "Estimate in-flight data capacity on a network path.",
    "subnet-usable-hosts": "Calculate assignable host addresses for an IPv4 prefix.",
    "subnets-from-borrowed-bits": "Determine the number of subnets created by borrowing bits.",
    "hamming-parity-bits": "Find the minimum parity bits required for Hamming code.",
    "audio-file-size": "Estimate uncompressed audio size from sample settings and duration.",
    "image-file-size": "Estimate uncompressed image size from resolution and color depth.",
}
