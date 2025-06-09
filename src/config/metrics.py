
# Конфіг метрик - для кожної метрики вказано в яких профілях вона доступна
METRICS_CONFIG = {
    # Volatility & Range Metrics
    "Average Daily Range (pips)": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Average Daily Body Size (pips)": {
        "category": "Volatility & Range Metrics", 
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Average Weekly Range (pips)": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Average Weekly Body Size (pips)": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Average Asia Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Average Frankfurt Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Average London Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Average Lunch Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik"]
    },
    "Average NY Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Average Monday Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Infobase"]
    },
    "Average Tuesday Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Infobase"]
    },
    "Average Wednesday Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Infobase"]
    },
    "Average Thursday Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Infobase"]
    },
    "Average Friday Range": {
        "category": "Volatility & Range Metrics",
        "profiles": ["Whytalik", "Infobase"]
    },
    
    # High/Low Timing Distribution (per Session)
    "Daily High in Asia %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Daily High in Frankfurt %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Daily High in London %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Daily High in Lunch %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik"]
    },
    "Daily High in NY %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Daily High in Out of Session %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Mordan", "Infobase"]
    },
    "Daily Low in Asia %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Daily Low in Frankfurt %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Daily Low in London %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Daily Low in NY %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Daily Low in Lunch %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Whytalik"]
    },
    "Daily Low in Out of Session %": {
        "category": "High/Low Timing Distribution (per Session)",
        "profiles": ["Mordan", "Infobase"]
    },    
    # Intraday Interval High/Low Percentages
    "Frankfurt-Asia High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Frankfurt-Asia Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan"]
    },
    "London-Asia High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "London-Asia Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "London-Frankfurt High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan"]
    },
    "London-Frankfurt Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Lunch-Asia High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik"]
    },
    "Lunch-Asia Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik"]
    },
    "Lunch-London High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik"]
    },
    "Lunch-London Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik"]
    },
    "Lunch-Frankfurt High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik"]
    },
    "Lunch-Frankfurt Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik"]
    },
    "NY-Asia High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "NY-Asia Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "NY-Frankfurt High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan"]
    },
    "NY-Frankfurt Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan"]
    },
    "NY-London High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "NY-London Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "NY-Lunch High %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik"]
    },
    "NY-Lunch Low %": {
        "category": "Intraday Interval High/Low Percentages",
        "profiles": ["Whytalik"]
    },    
    # Bullish / Bearish Specific Metrics
    "Bullish Frankfurt-Asia Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Bullish London-Asia Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Bullish London-Frankfurt Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Bullish Lunch-Asia Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik"]
    },
    "Bullish Lunch-Frankfurt Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik"]
    },
    "Bullish Lunch-London Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik"]
    },
    "Bullish NY-Asia Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Bullish NY-Frankfurt Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Bullish NY-London Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Bullish NY-Lunch Low %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik"]
    },
    "Bearish Frankfurt-Asia High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Bearish London-Asia High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Bearish London-Frankfurt High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Bearish Lunch-Asia High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik"]
    },
    "Bearish Lunch-Frankfurt High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik"]
    },
    "Bearish Lunch-London High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik"]
    },
    "Bearish NY-Asia High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Bearish NY-Frankfurt High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "Bearish NY-London High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Bearish NY-Lunch High %": {
        "category": "Bullish / Bearish Specific Metrics",
        "profiles": ["Whytalik"]
    },    
    # Daily/Weekly Occurrence Statistics
    "High in Monday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "High in Tuesday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "High in Wednesday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "High in Thursday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "High in Friday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Low in Monday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Low in Tuesday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Low in Wednesday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Low in Thursday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "Low in Friday": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
    "PDH Probability": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "PDL Probability": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan"]
    },
    "PD Levels Probability": {
        "category": "Daily/Weekly Occurrence Statistics",
        "profiles": ["Whytalik", "Mordan"]
    },
    
    # Aggregated / Thematic Metrics
    "Date Range": {
        "category": "Aggregated / Thematic Metrics",
        "profiles": ["Whytalik", "Mordan", "Infobase"]
    },
}


def get_metrics_for_profile(profile: str) -> dict:
    """
    Отримати метрики для конкретного профілю
    
    Args:
        profile: Назва профілю ("Whytalik", "Mordan", "Infobase")
    
    Returns:
        dict: Словник метрик згрупованих по категоріях
    """
    if profile not in ["Whytalik", "Mordan", "Infobase"]:
        raise ValueError(f"Unknown profile: {profile}. Available profiles: Whytalik, Mordan, Infobase")
    
    result = {}
    
    # Проходимо по всіх метриках і збираємо ті, що доступні для профілю
    for metric_name, config in METRICS_CONFIG.items():
        if profile in config["profiles"]:
            category = config["category"]
            if category not in result:
                result[category] = []
            result[category].append(metric_name)
    
    return result


def get_all_categories() -> list:
    """
    Отримати список всіх категорій метрик
    
    Returns:
        list: Список унікальних категорій
    """
    categories = set()
    for config in METRICS_CONFIG.values():
        categories.add(config["category"])
    return sorted(list(categories))


def get_profiles_for_metric(metric_name: str) -> list:
    """
    Отримати список профілів, для яких доступна метрика
    
    Args:
        metric_name: Назва метрики
    
    Returns:
        list: Список профілів
    """
    if metric_name not in METRICS_CONFIG:
        return []
    return METRICS_CONFIG[metric_name]["profiles"]


def is_metric_available_for_profile(metric_name: str, profile: str) -> bool:
    """
    Перевірити, чи доступна метрика для профілю
    
    Args:
        metric_name: Назва метрики
        profile: Назва профілю
    
    Returns:
        bool: True якщо метрика доступна для профілю
    """
    if metric_name not in METRICS_CONFIG:
        return False
    return profile in METRICS_CONFIG[metric_name]["profiles"]
