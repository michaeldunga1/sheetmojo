from math import pow


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


def _profit(d):
    return d["revenue"] - d["cost"]


def _revenue(d):
    return d["price"] * d["quantity"]


def _cost(d):
    return d["fixed_cost"] + d["variable_cost_per_unit"] * d["quantity"]


def _break_even_units(d):
    contribution = d["selling_price"] - d["variable_cost_per_unit"]
    _nonzero(contribution, "Unit contribution margin")
    return d["fixed_cost"] / contribution


def _break_even_sales(d):
    _nonzero(d["cm_ratio"], "Contribution margin ratio")
    return d["fixed_cost"] / d["cm_ratio"]


def _contribution_margin_per_unit(d):
    return d["selling_price"] - d["variable_cost_per_unit"]


def _contribution_margin_ratio(d):
    _nonzero(d["sales"], "Sales")
    return (d["sales"] - d["variable_cost"]) / d["sales"]


def _gross_profit_margin(d):
    _nonzero(d["revenue"], "Revenue")
    return (d["revenue"] - d["cogs"]) / d["revenue"] * 100


def _operating_margin(d):
    _nonzero(d["revenue"], "Revenue")
    return d["operating_income"] / d["revenue"] * 100


def _net_profit_margin(d):
    _nonzero(d["revenue"], "Revenue")
    return d["net_income"] / d["revenue"] * 100


def _markup(d):
    _nonzero(d["cost"], "Cost")
    return (d["price"] - d["cost"]) / d["cost"] * 100


def _margin(d):
    _nonzero(d["price"], "Price")
    return (d["price"] - d["cost"]) / d["price"] * 100


def _roi(d):
    _nonzero(d["investment_cost"], "Investment cost")
    return (d["gain"] - d["investment_cost"]) / d["investment_cost"] * 100


def _roe(d):
    _nonzero(d["shareholder_equity"], "Shareholder equity")
    return d["net_income"] / d["shareholder_equity"] * 100


def _roa(d):
    _nonzero(d["total_assets"], "Total assets")
    return d["net_income"] / d["total_assets"] * 100


def _asset_turnover(d):
    _nonzero(d["average_assets"], "Average assets")
    return d["net_sales"] / d["average_assets"]


def _current_ratio(d):
    _nonzero(d["current_liabilities"], "Current liabilities")
    return d["current_assets"] / d["current_liabilities"]


def _quick_ratio(d):
    _nonzero(d["current_liabilities"], "Current liabilities")
    return (d["current_assets"] - d["inventory"]) / d["current_liabilities"]


def _debt_to_equity(d):
    _nonzero(d["equity"], "Equity")
    return d["debt"] / d["equity"]


def _inventory_turnover(d):
    _nonzero(d["average_inventory"], "Average inventory")
    return d["cogs"] / d["average_inventory"]


def _days_sales_outstanding(d):
    _nonzero(d["credit_sales"], "Credit sales")
    return d["accounts_receivable"] / d["credit_sales"] * d["days"]


def _days_inventory_outstanding(d):
    _nonzero(d["cogs"], "COGS")
    return d["average_inventory"] / d["cogs"] * d["days"]


def _cash_conversion_cycle(d):
    return d["dso"] + d["dio"] - d["dpo"]


def _simple_interest(d):
    return d["P"] * d["r"] * d["t"]


def _compound_amount(d):
    _positive(d["n"], "Compounds per year n")
    return d["P"] * pow(1 + d["r"] / d["n"], d["n"] * d["t"])


def _future_value_lump_sum(d):
    return d["PV"] * pow(1 + d["r"], d["n"])


def _present_value_lump_sum(d):
    return d["FV"] / pow(1 + d["r"], d["n"])


def _future_value_annuity(d):
    _nonzero(d["r"], "Rate r")
    return d["PMT"] * (pow(1 + d["r"], d["n"]) - 1) / d["r"]


def _present_value_annuity(d):
    _nonzero(d["r"], "Rate r")
    return d["PMT"] * (1 - pow(1 + d["r"], -d["n"])) / d["r"]


def _loan_payment(d):
    _nonzero(d["r"], "Periodic rate r")
    num = d["PV"] * d["r"] * pow(1 + d["r"], d["n"])
    den = pow(1 + d["r"], d["n"]) - 1
    _nonzero(den, "Denominator")
    return num / den


def _cagr(d):
    _positive(d["begin_value"], "Begin value")
    _positive(d["n"], "Number of periods n")
    return (pow(d["end_value"] / d["begin_value"], 1 / d["n"]) - 1) * 100


def _straight_line_depreciation(d):
    _nonzero(d["useful_life"], "Useful life")
    return (d["cost"] - d["salvage_value"]) / d["useful_life"]


def _payback_period(d):
    _nonzero(d["annual_cash_inflow"], "Annual cash inflow")
    return d["initial_investment"] / d["annual_cash_inflow"]


def _npv(d):
    return d["cf0"] + d["cf1"] / (1 + d["r"]) + d["cf2"] / pow(1 + d["r"], 2) + d["cf3"] / pow(1 + d["r"], 3)


BUSINESS_FORMULAS = {
    "profit": {
        "title": "Profit",
        "latex": r"\text{Profit}=\text{Revenue}-\text{Cost}",
        "fields": [{"name": "revenue", "label": "Revenue"}, {"name": "cost", "label": "Cost"}],
        "compute": _profit,
        "substitute": lambda d: "Profit = Revenue - Cost",
        "answer_label": "Profit",
        "format_answer": _fmt,
    },
    "revenue": {
        "title": "Revenue",
        "latex": r"R=P\times Q",
        "fields": [{"name": "price", "label": "Price P"}, {"name": "quantity", "label": "Quantity Q"}],
        "compute": _revenue,
        "substitute": lambda d: "Revenue = Price * Quantity",
        "answer_label": "Revenue",
        "format_answer": _fmt,
    },
    "total-cost": {
        "title": "Total Cost",
        "latex": r"TC=FC+VC_u\times Q",
        "fields": [{"name": "fixed_cost", "label": "Fixed cost FC"}, {"name": "variable_cost_per_unit", "label": "Variable cost per unit VCu"}, {"name": "quantity", "label": "Quantity Q"}],
        "compute": _cost,
        "substitute": lambda d: "TC = FC + VCu*Q",
        "answer_label": "TC",
        "format_answer": _fmt,
    },
    "break-even-units": {
        "title": "Break-even Point (Units)",
        "latex": r"Q_{BE}=\frac{FC}{SP-VC_u}",
        "fields": [{"name": "fixed_cost", "label": "Fixed cost FC"}, {"name": "selling_price", "label": "Selling price SP"}, {"name": "variable_cost_per_unit", "label": "Variable cost per unit VCu"}],
        "compute": _break_even_units,
        "substitute": lambda d: "Qbe = FC/(SP-VCu)",
        "answer_label": "Break-even units",
        "format_answer": _fmt,
    },
    "break-even-sales": {
        "title": "Break-even Sales",
        "latex": r"S_{BE}=\frac{FC}{CMR}",
        "fields": [{"name": "fixed_cost", "label": "Fixed cost FC"}, {"name": "cm_ratio", "label": "Contribution margin ratio CMR"}],
        "compute": _break_even_sales,
        "substitute": lambda d: "Sbe = FC/CMR",
        "answer_label": "Break-even sales",
        "format_answer": _fmt,
    },
    "contribution-margin-per-unit": {
        "title": "Contribution Margin per Unit",
        "latex": r"CM_u=SP-VC_u",
        "fields": [{"name": "selling_price", "label": "Selling price SP"}, {"name": "variable_cost_per_unit", "label": "Variable cost per unit VCu"}],
        "compute": _contribution_margin_per_unit,
        "substitute": lambda d: "CMu = SP-VCu",
        "answer_label": "CMu",
        "format_answer": _fmt,
    },
    "contribution-margin-ratio": {
        "title": "Contribution Margin Ratio",
        "latex": r"CMR=\frac{S-VC}{S}",
        "fields": [{"name": "sales", "label": "Sales S"}, {"name": "variable_cost", "label": "Variable cost VC"}],
        "compute": _contribution_margin_ratio,
        "substitute": lambda d: "CMR = (S-VC)/S",
        "answer_label": "CMR",
        "format_answer": _fmt,
    },
    "gross-profit-margin": {
        "title": "Gross Profit Margin",
        "latex": r"GPM=\frac{Revenue-COGS}{Revenue}\times100",
        "fields": [{"name": "revenue", "label": "Revenue"}, {"name": "cogs", "label": "COGS"}],
        "compute": _gross_profit_margin,
        "substitute": lambda d: "GPM = (Revenue-COGS)/Revenue*100",
        "answer_label": "GPM",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "operating-margin": {
        "title": "Operating Margin",
        "latex": r"OM=\frac{Operating\ Income}{Revenue}\times100",
        "fields": [{"name": "operating_income", "label": "Operating income"}, {"name": "revenue", "label": "Revenue"}],
        "compute": _operating_margin,
        "substitute": lambda d: "OM = operating_income/revenue*100",
        "answer_label": "OM",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "net-profit-margin": {
        "title": "Net Profit Margin",
        "latex": r"NPM=\frac{Net\ Income}{Revenue}\times100",
        "fields": [{"name": "net_income", "label": "Net income"}, {"name": "revenue", "label": "Revenue"}],
        "compute": _net_profit_margin,
        "substitute": lambda d: "NPM = net_income/revenue*100",
        "answer_label": "NPM",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "markup": {
        "title": "Markup (%)",
        "latex": r"Markup=\frac{Price-Cost}{Cost}\times100",
        "fields": [{"name": "price", "label": "Price"}, {"name": "cost", "label": "Cost"}],
        "compute": _markup,
        "substitute": lambda d: "Markup = (Price-Cost)/Cost*100",
        "answer_label": "Markup",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "margin": {
        "title": "Margin (%)",
        "latex": r"Margin=\frac{Price-Cost}{Price}\times100",
        "fields": [{"name": "price", "label": "Price"}, {"name": "cost", "label": "Cost"}],
        "compute": _margin,
        "substitute": lambda d: "Margin = (Price-Cost)/Price*100",
        "answer_label": "Margin",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "roi": {
        "title": "Return on Investment (ROI)",
        "latex": r"ROI=\frac{Gain-Cost}{Cost}\times100",
        "fields": [{"name": "gain", "label": "Gain"}, {"name": "investment_cost", "label": "Investment cost"}],
        "compute": _roi,
        "substitute": lambda d: "ROI = (Gain-Cost)/Cost*100",
        "answer_label": "ROI",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "roe": {
        "title": "Return on Equity (ROE)",
        "latex": r"ROE=\frac{Net\ Income}{Equity}\times100",
        "fields": [{"name": "net_income", "label": "Net income"}, {"name": "shareholder_equity", "label": "Shareholder equity"}],
        "compute": _roe,
        "substitute": lambda d: "ROE = net_income/equity*100",
        "answer_label": "ROE",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "roa": {
        "title": "Return on Assets (ROA)",
        "latex": r"ROA=\frac{Net\ Income}{Total\ Assets}\times100",
        "fields": [{"name": "net_income", "label": "Net income"}, {"name": "total_assets", "label": "Total assets"}],
        "compute": _roa,
        "substitute": lambda d: "ROA = net_income/total_assets*100",
        "answer_label": "ROA",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "asset-turnover": {
        "title": "Asset Turnover Ratio",
        "latex": r"ATR=\frac{Net\ Sales}{Average\ Assets}",
        "fields": [{"name": "net_sales", "label": "Net sales"}, {"name": "average_assets", "label": "Average assets"}],
        "compute": _asset_turnover,
        "substitute": lambda d: "ATR = net_sales/average_assets",
        "answer_label": "ATR",
        "format_answer": _fmt,
    },
    "current-ratio": {
        "title": "Current Ratio",
        "latex": r"CR=\frac{Current\ Assets}{Current\ Liabilities}",
        "fields": [{"name": "current_assets", "label": "Current assets"}, {"name": "current_liabilities", "label": "Current liabilities"}],
        "compute": _current_ratio,
        "substitute": lambda d: "CR = current_assets/current_liabilities",
        "answer_label": "CR",
        "format_answer": _fmt,
    },
    "quick-ratio": {
        "title": "Quick Ratio",
        "latex": r"QR=\frac{Current\ Assets-Inventory}{Current\ Liabilities}",
        "fields": [{"name": "current_assets", "label": "Current assets"}, {"name": "inventory", "label": "Inventory"}, {"name": "current_liabilities", "label": "Current liabilities"}],
        "compute": _quick_ratio,
        "substitute": lambda d: "QR = (current_assets-inventory)/current_liabilities",
        "answer_label": "QR",
        "format_answer": _fmt,
    },
    "debt-to-equity": {
        "title": "Debt to Equity Ratio",
        "latex": r"D/E=\frac{Debt}{Equity}",
        "fields": [{"name": "debt", "label": "Debt"}, {"name": "equity", "label": "Equity"}],
        "compute": _debt_to_equity,
        "substitute": lambda d: "D/E = debt/equity",
        "answer_label": "D/E",
        "format_answer": _fmt,
    },
    "inventory-turnover": {
        "title": "Inventory Turnover",
        "latex": r"IT=\frac{COGS}{Average\ Inventory}",
        "fields": [{"name": "cogs", "label": "COGS"}, {"name": "average_inventory", "label": "Average inventory"}],
        "compute": _inventory_turnover,
        "substitute": lambda d: "IT = COGS/average_inventory",
        "answer_label": "IT",
        "format_answer": _fmt,
    },
    "days-sales-outstanding": {
        "title": "Days Sales Outstanding (DSO)",
        "latex": r"DSO=\frac{AR}{Credit\ Sales}\times Days",
        "fields": [{"name": "accounts_receivable", "label": "Accounts receivable AR"}, {"name": "credit_sales", "label": "Credit sales"}, {"name": "days", "label": "Days"}],
        "compute": _days_sales_outstanding,
        "substitute": lambda d: "DSO = AR/credit_sales*days",
        "answer_label": "DSO",
        "format_answer": _fmt,
    },
    "days-inventory-outstanding": {
        "title": "Days Inventory Outstanding (DIO)",
        "latex": r"DIO=\frac{Average\ Inventory}{COGS}\times Days",
        "fields": [{"name": "average_inventory", "label": "Average inventory"}, {"name": "cogs", "label": "COGS"}, {"name": "days", "label": "Days"}],
        "compute": _days_inventory_outstanding,
        "substitute": lambda d: "DIO = average_inventory/COGS*days",
        "answer_label": "DIO",
        "format_answer": _fmt,
    },
    "cash-conversion-cycle": {
        "title": "Cash Conversion Cycle",
        "latex": r"CCC=DSO+DIO-DPO",
        "fields": [{"name": "dso", "label": "DSO"}, {"name": "dio", "label": "DIO"}, {"name": "dpo", "label": "DPO"}],
        "compute": _cash_conversion_cycle,
        "substitute": lambda d: "CCC = DSO + DIO - DPO",
        "answer_label": "CCC",
        "format_answer": _fmt,
    },
    "simple-interest": {
        "title": "Simple Interest",
        "latex": r"I=Prt",
        "fields": [{"name": "P", "label": "Principal P"}, {"name": "r", "label": "Rate r (decimal)"}, {"name": "t", "label": "Time t"}],
        "compute": _simple_interest,
        "substitute": lambda d: "I = P*r*t",
        "answer_label": "I",
        "format_answer": _fmt,
    },
    "compound-amount": {
        "title": "Compound Amount",
        "latex": r"A=P\left(1+\frac{r}{n}\right)^{nt}",
        "fields": [{"name": "P", "label": "Principal P"}, {"name": "r", "label": "Annual rate r (decimal)"}, {"name": "n", "label": "Compounds/year n"}, {"name": "t", "label": "Years t"}],
        "compute": _compound_amount,
        "substitute": lambda d: "A = P*(1+r/n)^(n*t)",
        "answer_label": "A",
        "format_answer": _fmt,
    },
    "future-value-lump-sum": {
        "title": "Future Value (Lump Sum)",
        "latex": r"FV=PV(1+r)^n",
        "fields": [{"name": "PV", "label": "Present value PV"}, {"name": "r", "label": "Rate r"}, {"name": "n", "label": "Periods n"}],
        "compute": _future_value_lump_sum,
        "substitute": lambda d: "FV = PV*(1+r)^n",
        "answer_label": "FV",
        "format_answer": _fmt,
    },
    "present-value-lump-sum": {
        "title": "Present Value (Lump Sum)",
        "latex": r"PV=\frac{FV}{(1+r)^n}",
        "fields": [{"name": "FV", "label": "Future value FV"}, {"name": "r", "label": "Rate r"}, {"name": "n", "label": "Periods n"}],
        "compute": _present_value_lump_sum,
        "substitute": lambda d: "PV = FV/(1+r)^n",
        "answer_label": "PV",
        "format_answer": _fmt,
    },
    "future-value-annuity": {
        "title": "Future Value of Annuity",
        "latex": r"FV=PMT\frac{(1+r)^n-1}{r}",
        "fields": [{"name": "PMT", "label": "Payment PMT"}, {"name": "r", "label": "Rate r"}, {"name": "n", "label": "Periods n"}],
        "compute": _future_value_annuity,
        "substitute": lambda d: "FV = PMT*((1+r)^n-1)/r",
        "answer_label": "FV",
        "format_answer": _fmt,
    },
    "present-value-annuity": {
        "title": "Present Value of Annuity",
        "latex": r"PV=PMT\frac{1-(1+r)^{-n}}{r}",
        "fields": [{"name": "PMT", "label": "Payment PMT"}, {"name": "r", "label": "Rate r"}, {"name": "n", "label": "Periods n"}],
        "compute": _present_value_annuity,
        "substitute": lambda d: "PV = PMT*(1-(1+r)^(-n))/r",
        "answer_label": "PV",
        "format_answer": _fmt,
    },
    "loan-payment": {
        "title": "Loan Payment (PMT)",
        "latex": r"PMT=PV\frac{r(1+r)^n}{(1+r)^n-1}",
        "fields": [{"name": "PV", "label": "Loan principal PV"}, {"name": "r", "label": "Periodic rate r"}, {"name": "n", "label": "Number of payments n"}],
        "compute": _loan_payment,
        "substitute": lambda d: "PMT = PV*r*(1+r)^n/((1+r)^n-1)",
        "answer_label": "PMT",
        "format_answer": _fmt,
    },
    "cagr": {
        "title": "Compound Annual Growth Rate (CAGR)",
        "latex": r"CAGR=\left(\frac{EV}{BV}\right)^{1/n}-1",
        "fields": [{"name": "begin_value", "label": "Beginning value BV"}, {"name": "end_value", "label": "Ending value EV"}, {"name": "n", "label": "Periods n"}],
        "compute": _cagr,
        "substitute": lambda d: "CAGR = (EV/BV)^(1/n)-1",
        "answer_label": "CAGR",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "straight-line-depreciation": {
        "title": "Straight-Line Depreciation",
        "latex": r"Dep=\frac{Cost-Salvage}{Life}",
        "fields": [{"name": "cost", "label": "Asset cost"}, {"name": "salvage_value", "label": "Salvage value"}, {"name": "useful_life", "label": "Useful life"}],
        "compute": _straight_line_depreciation,
        "substitute": lambda d: "Dep = (cost-salvage)/life",
        "answer_label": "Annual depreciation",
        "format_answer": _fmt,
    },
    "payback-period": {
        "title": "Payback Period",
        "latex": r"PP=\frac{Initial\ Investment}{Annual\ Cash\ Inflow}",
        "fields": [{"name": "initial_investment", "label": "Initial investment"}, {"name": "annual_cash_inflow", "label": "Annual cash inflow"}],
        "compute": _payback_period,
        "substitute": lambda d: "PP = initial_investment/annual_cash_inflow",
        "answer_label": "Payback period",
        "format_answer": _fmt,
    },
    "npv-3-period": {
        "title": "Net Present Value (3 Period)",
        "latex": r"NPV=CF_0+\frac{CF_1}{(1+r)}+\frac{CF_2}{(1+r)^2}+\frac{CF_3}{(1+r)^3}",
        "fields": [{"name": "cf0", "label": "Cash flow CF0"}, {"name": "cf1", "label": "Cash flow CF1"}, {"name": "cf2", "label": "Cash flow CF2"}, {"name": "cf3", "label": "Cash flow CF3"}, {"name": "r", "label": "Discount rate r"}],
        "compute": _npv,
        "substitute": lambda d: "NPV = CF0 + CF1/(1+r) + CF2/(1+r)^2 + CF3/(1+r)^3",
        "answer_label": "NPV",
        "format_answer": _fmt,
    },
}


BUSINESS_FORMULA_GROUPS = [
    {
        "title": "Profitability & Pricing",
        "slugs": [
            "profit",
            "revenue",
            "total-cost",
            "break-even-units",
            "break-even-sales",
            "contribution-margin-per-unit",
            "contribution-margin-ratio",
            "gross-profit-margin",
            "operating-margin",
            "net-profit-margin",
            "markup",
            "margin",
        ],
    },
    {
        "title": "Returns & Efficiency",
        "slugs": [
            "roi",
            "roe",
            "roa",
            "asset-turnover",
        ],
    },
    {
        "title": "Liquidity & Working Capital",
        "slugs": [
            "current-ratio",
            "quick-ratio",
            "debt-to-equity",
            "inventory-turnover",
            "days-sales-outstanding",
            "days-inventory-outstanding",
            "cash-conversion-cycle",
        ],
    },
    {
        "title": "Finance & Investment",
        "slugs": [
            "simple-interest",
            "compound-amount",
            "future-value-lump-sum",
            "present-value-lump-sum",
            "future-value-annuity",
            "present-value-annuity",
            "loan-payment",
            "cagr",
            "straight-line-depreciation",
            "payback-period",
            "npv-3-period",
        ],
    },
]


BUSINESS_FORMULA_DESCRIPTIONS = {
    "profit": "Compute profit from revenue minus cost.",
    "revenue": "Find sales revenue from price and quantity.",
    "total-cost": "Compute total cost from fixed and variable components.",
    "break-even-units": "Find unit sales needed to cover all costs.",
    "break-even-sales": "Find break-even revenue directly.",
    "contribution-margin-per-unit": "Find contribution left after variable unit cost.",
    "contribution-margin-ratio": "Measure contribution margin as a share of sales.",
    "gross-profit-margin": "Compute gross margin percentage from revenue and COGS.",
    "operating-margin": "Compute operating income as a percentage of sales.",
    "net-profit-margin": "Compute final net income margin on sales.",
    "markup": "Convert cost and selling price into markup percentage.",
    "margin": "Convert selling price and cost into margin percentage.",
    "roi": "Measure return relative to invested capital.",
    "roe": "Measure return generated on shareholder equity.",
    "roa": "Measure return generated from total assets.",
    "asset-turnover": "Measure revenue generated per unit of assets.",
    "current-ratio": "Assess short-term liquidity from current assets and liabilities.",
    "quick-ratio": "Assess near-cash liquidity excluding inventory.",
    "debt-to-equity": "Measure leverage from debt relative to equity.",
    "inventory-turnover": "Measure how often inventory cycles through sales.",
    "days-sales-outstanding": "Estimate average collection days for receivables.",
    "days-inventory-outstanding": "Estimate how long inventory sits before sale.",
    "cash-conversion-cycle": "Estimate working-capital cash cycle duration.",
    "simple-interest": "Compute interest without compounding.",
    "compound-amount": "Compute total amount after compound growth.",
    "future-value-lump-sum": "Project a present amount into future value.",
    "present-value-lump-sum": "Discount a future amount back to present value.",
    "future-value-annuity": "Project repeated equal payments into future value.",
    "present-value-annuity": "Find present worth of repeated equal payments.",
    "loan-payment": "Compute installment payment for an amortized loan.",
    "cagr": "Compute smoothed annual growth over multiple periods.",
    "straight-line-depreciation": "Allocate asset cost evenly across useful life.",
    "payback-period": "Estimate years required to recover an investment.",
    "npv-3-period": "Compute discounted net value across three future periods.",
}
