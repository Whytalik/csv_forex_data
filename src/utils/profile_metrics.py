"""
Legacy profile metrics utilities.
This module is kept for backward compatibility.
New code should import from services.metrics_profile_service directly.
"""

# Import all functionality from the new metrics profile service
from services.metrics_profile_service import metrics_profile_service


# Re-export functions for backward compatibility
def get_metrics_for_profile(profile: str):
    """Legacy wrapper for get_metrics_for_profile."""
    return metrics_profile_service.get_metrics_for_profile(profile)


def group_metrics_by_category(flat_metrics: dict):
    """Legacy wrapper for group_metrics_by_category."""
    return metrics_profile_service.group_metrics_by_category(flat_metrics)


def get_all_metrics_for_profile(profile: str):
    """Legacy wrapper for get_all_metrics_for_profile."""
    return metrics_profile_service.get_all_metrics_for_profile(profile)


def filter_profile_metrics_by_category(profile_metrics: dict, profile: str):
    """Legacy wrapper for filter_profile_metrics_by_category."""
    return metrics_profile_service.filter_profile_metrics_by_category(
        profile_metrics, profile
    )


def filter_profile_properties(profile_data: dict, profile: str):
    """Legacy wrapper for filter_profile_properties."""
    return metrics_profile_service.filter_profile_properties(profile_data, profile)


# Export for compatibility
__all__ = [
    "get_metrics_for_profile",
    "group_metrics_by_category",
    "get_all_metrics_for_profile",
    "filter_profile_metrics_by_category",
    "filter_profile_properties",
]
