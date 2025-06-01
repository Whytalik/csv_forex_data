# Базовий набір метрик
BASE_METRICS = {
    "Volatility & Range Metrics": [
        "Average Daily Range (pips)",
        "Average Daily Body Size (pips)",
        "Average Weekly Range (pips)",
        "Average Weekly Body Size (pips)",
        "Average Asia Range",
        "Average Frankfurt Range",
        "Average London Range",
        "Average Lunch Range",
        "Average NY Range",
        "Average Monday Range",
        "Average Tuesday Range",
        "Average Wednesday Range",
        "Average Thursday Range",
        "Average Friday Range",
    ],
    "High/Low Timing Distribution (per Session)": [
        "Daily High in Asia %",
        "Daily High in Frankfurt %",
        "Daily High in London %",
        "Daily High in Lunch %",
        "Daily High in NY %",
        "Daily High in Out of Session %",
        "Daily Low in Asia %",
        "Daily Low in Frankfurt %",
        "Daily Low in London %",
        "Daily Low in NY %",
        "Daily Low in Lunch %",
        "Daily Low in Out of Session %",
    ],
    "Intraday Interval High/Low Percentages": [
        "Frankfurt-Asia High %",
        "Frankfurt-Asia Low %",
        "London-Asia High %",
        "London-Asia Low %",
        "London-Frankfurt High %",
        "London-Frankfurt Low %",
        "Lunch-Asia High %",
        "Lunch-Asia Low %",
        "Lunch-London High %",
        "Lunch-London Low %",
        "Lunch-Frankfurt High %",
        "Lunch-Frankfurt Low %",
        "NY-Asia High %",
        "NY-Asia Low %",
        "NY-Frankfurt High %",
        "NY-Frankfurt Low %",
        "NY-London High %",
        "NY-London Low %",
        "NY-Lunch High %",
        "NY-Lunch Low %",
    ],
    "Bullish / Bearish Specific Metrics": [
        "Bullish Frankfurt-Asia Low %",
        "Bullish London-Asia Low %",
        "Bullish London-Frankfurt Low %",
        "Bullish Lunch-Asia Low %",
        "Bullish Lunch-Frankfurt Low %",
        "Bullish Lunch-London Low %",
        "Bullish NY-Asia Low %",
        "Bullish NY-Frankfurt Low %",
        "Bullish NY-London Low %",
        "Bullish NY-Lunch Low %",
        "Bearish Frankfurt-Asia High %",
        "Bearish London-Asia High %",
        "Bearish London-Frankfurt High %",
        "Bearish Lunch-Asia High %",
        "Bearish Lunch-Frankfurt High %",
        "Bearish Lunch-London High %",
        "Bearish NY-Asia High %",
        "Bearish NY-Frankfurt High %",
        "Bearish NY-London High %",
        "Bearish NY-Lunch High %",
    ],
    "Daily/Weekly Occurrence Statistics": [
        "High in Monday",
        "High in Tuesday",
        "High in Wednesday",
        "High in Thursday",
        "High in Friday",
        "Low in Monday",
        "Low in Tuesday",
        "Low in Wednesday",
        "Low in Thursday",
        "Low in Friday",
        "PDH Probability",
        "PDL Probability",
        "PD Levels Probability",
    ],
    "Aggregated / Thematic Metrics": [
        "Date Range",
    ],
}

WHYTALIK_EXTRA_METRICS = {
    "Volatility & Range Metrics": [],
    "Custom Metrics": [],
}

MORDAN_EXTRA_METRICS = {
    "Volatility & Range Metrics": [],
    "Custom Metrics": [],
}

PROFILE_METRICS = {
    "Whytalik": {
        "Volatility & Range Metrics": BASE_METRICS["Volatility & Range Metrics"],
        "High/Low Timing Distribution (per Session)": BASE_METRICS[
            "High/Low Timing Distribution (per Session)"
        ],
        "Intraday Interval High/Low Percentages": BASE_METRICS[
            "Intraday Interval High/Low Percentages"
        ],
        "Bullish / Bearish Specific Metrics": BASE_METRICS[
            "Bullish / Bearish Specific Metrics"
        ],
        "Daily/Weekly Occurrence Statistics": BASE_METRICS[
            "Daily/Weekly Occurrence Statistics"
        ],
        "Aggregated / Thematic Metrics": BASE_METRICS["Aggregated / Thematic Metrics"],
    },
    "MORDAN": {
        "Volatility & Range Metrics": BASE_METRICS["Volatility & Range Metrics"],
        "High/Low Timing Distribution (per Session)": BASE_METRICS[
            "High/Low Timing Distribution (per Session)"
        ],
        "Intraday Interval High/Low Percentages": BASE_METRICS[
            "Intraday Interval High/Low Percentages"
        ],
        "Bullish / Bearish Specific Metrics": BASE_METRICS[
            "Bullish / Bearish Specific Metrics"
        ],
        "Daily/Weekly Occurrence Statistics": BASE_METRICS[
            "Daily/Weekly Occurrence Statistics"
        ],
        "Aggregated / Thematic Metrics": BASE_METRICS["Aggregated / Thematic Metrics"],
    },
}


def get_metrics_for_profile(profile: str) -> dict:
    if profile not in PROFILE_METRICS:
        raise ValueError(f"Unknown profile: {profile}")
    return PROFILE_METRICS[profile]
