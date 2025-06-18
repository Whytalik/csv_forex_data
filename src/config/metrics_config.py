from .metrics.levels_metrics import LEVELS_METRICS
from .metrics.occurrence_statistics_metrics import (
    OCCURRENCE_STATISTICS_METRICS,
    BULLISH_OCCURRENCE_STATISTICS_METRICS,
    BEARISH_OCCURRENCE_STATISTICS_METRICS,
)
from .metrics.range_metrics import (
    VOLATILITY_RANGE_METRICS,
    SESSIONS_RANGE_METRICS,
    WEEKDAY_RANGE_METRICS,
)
from .metrics.session_timing_distribution_metrics import (
    SESSION_TIMING_DISTRIBUTION_METRICS,
    BULLISH_SESSION_TIMING_DISTRIBUTION_METRICS,
    BEARISH_SESSION_TIMING_DISTRIBUTION_METRICS,
)
from .metrics.sessions_interactions import (
    SESSION_INTERACTION_METRICS,
    BULLISH_SESSION_INTERACTIONS_METRICS,
    BEARISH_SESSION_INTERACTIONS_METRICS,
)


def get_all_metrics():
    all_metrics = {}
    all_metrics.update(LEVELS_METRICS)
    all_metrics.update(OCCURRENCE_STATISTICS_METRICS)
    all_metrics.update(BULLISH_OCCURRENCE_STATISTICS_METRICS)
    all_metrics.update(BEARISH_OCCURRENCE_STATISTICS_METRICS)
    all_metrics.update(VOLATILITY_RANGE_METRICS)
    all_metrics.update(SESSIONS_RANGE_METRICS)
    all_metrics.update(WEEKDAY_RANGE_METRICS)
    all_metrics.update(SESSION_TIMING_DISTRIBUTION_METRICS)
    all_metrics.update(BULLISH_SESSION_TIMING_DISTRIBUTION_METRICS)
    all_metrics.update(BEARISH_SESSION_TIMING_DISTRIBUTION_METRICS)
    all_metrics.update(SESSION_INTERACTION_METRICS)
    all_metrics.update(BULLISH_SESSION_INTERACTIONS_METRICS)
    all_metrics.update(BEARISH_SESSION_INTERACTIONS_METRICS)

    return all_metrics


def get_metrics_by_category(category: str = None):
    """
    Повертає метрики за категорією.

    Args:
        category: 'levels', 'occurrence', 'range', 'timing', 'interactions', або None для всіх

    Returns:
        dict: Відфільтровані метрики
    """
    if category == "levels":
        return LEVELS_METRICS.copy()
    elif category == "occurrence":
        metrics = {}
        metrics.update(OCCURRENCE_STATISTICS_METRICS)
        metrics.update(BULLISH_OCCURRENCE_STATISTICS_METRICS)
        metrics.update(BEARISH_OCCURRENCE_STATISTICS_METRICS)
        return metrics
    elif category == "range":
        metrics = {}
        metrics.update(VOLATILITY_RANGE_METRICS)
        metrics.update(SESSIONS_RANGE_METRICS)
        metrics.update(WEEKDAY_RANGE_METRICS)
        return metrics
    elif category == "timing":
        metrics = {}
        metrics.update(SESSION_TIMING_DISTRIBUTION_METRICS)
        metrics.update(BULLISH_SESSION_TIMING_DISTRIBUTION_METRICS)
        metrics.update(BEARISH_SESSION_TIMING_DISTRIBUTION_METRICS)
        return metrics
    elif category == "interactions":
        metrics = {}
        metrics.update(SESSION_INTERACTION_METRICS)
        metrics.update(BULLISH_SESSION_INTERACTIONS_METRICS)
        metrics.update(BEARISH_SESSION_INTERACTIONS_METRICS)
        return metrics
    else:
        return get_all_metrics()


# Глобальна змінна для конфігурації метрик
METRICS_CONFIG = get_all_metrics()

# Для зворотної сумісності та простого доступу
ALL_METRICS = get_all_metrics()
