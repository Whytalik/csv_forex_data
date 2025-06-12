"""
Service for handling profile-specific metrics operations.
Handles filtering, grouping, and validation of metrics for different profiles.
"""

from typing import Dict, List, Set
from config.metrics_config import METRICS_CONFIG


class MetricsProfileService:
    """Service for managing profile-specific metrics operations."""

    VALID_PROFILES = ["Whytalik", "Mordan", "Infobase"]

    def __init__(self):
        self._metrics_config = METRICS_CONFIG

    def get_metrics_for_profile(self, profile: str) -> Dict[str, List[str]]:
        """
        Повертає метрики для конкретного профілю, згруповані за категоріями.

        Args:
            profile: Назва профілю ('Whytalik', 'Mordan', 'Infobase')

        Returns:
            dict: Словник з категоріями та списками метрик
        """
        self._validate_profile(profile)

        result = {}
        for metric_name, config in self._metrics_config.items():
            if profile in config["profiles"]:
                category = config["category"]
                if category not in result:
                    result[category] = []
                result[category].append(metric_name)

        return result

    def group_metrics_by_category(self, flat_metrics: dict) -> dict:
        """
        Групує плоскі метрики за категоріями.

        Args:
            flat_metrics: Словник метрик у плоскому форматі

        Returns:
            dict: Згруповані метрики за категоріями
        """
        grouped = {}

        for metric_name, value in flat_metrics.items():
            category = self._get_metric_category(metric_name)

            if category not in grouped:
                grouped[category] = {}

            grouped[category][metric_name] = value

        return grouped

    def get_all_categories(self) -> List[str]:
        """
        Повертає список всіх доступних категорій метрик.

        Returns:
            list: Відсортований список категорій
        """
        categories = set()
        for config in self._metrics_config.values():
            categories.add(config["category"])
        return sorted(list(categories))

    def get_profiles_for_metric(self, metric_name: str) -> List[str]:
        """
        Повертає список профілів, для яких доступна дана метрика.

        Args:
            metric_name: Назва метрики

        Returns:
            list: Список профілів
        """
        if metric_name not in self._metrics_config:
            return []
        return self._metrics_config[metric_name]["profiles"]

    def is_metric_available_for_profile(self, metric_name: str, profile: str) -> bool:
        """
        Перевіряє, чи доступна метрика для конкретного профілю.

        Args:
            metric_name: Назва метрики
            profile: Назва профілю

        Returns:
            bool: True якщо метрика доступна
        """
        if metric_name not in self._metrics_config:
            return False
        return profile in self._metrics_config[metric_name]["profiles"]

    def get_all_metrics_for_profile(self, profile: str) -> Set[str]:
        """
        Повертає множину всіх метрик для конкретного профілю.

        Args:
            profile: Назва профілю

        Returns:
            set: Множина назв метрик
        """
        self._validate_profile(profile)

        metrics_set = set()
        for metric_name, config in self._metrics_config.items():
            if profile in config["profiles"]:
                metrics_set.add(metric_name)

        return metrics_set

    def filter_profile_properties(self, profile_data: dict, profile: str) -> dict:
        """
        Фільтрує властивості профілю, залишаючи тільки дозволені метрики.

        Args:
            profile_data: Дані профілю
            profile: Назва профілю

        Returns:
            dict: Відфільтровані дані
        """
        self._validate_profile(profile)

        allowed_metrics = self.get_all_metrics_for_profile(profile)
        filtered_data = {}

        for key, value in profile_data.items():
            if isinstance(value, (int, float)):
                if key in allowed_metrics:
                    filtered_data[key] = value
                else:
                    print(
                        f"🔄 Filtered out metric '{key}' for profile '{profile}' (not in config)"
                    )
            else:
                filtered_data[key] = value

        return filtered_data

    def filter_profile_metrics_by_category(
        self, profile_metrics: dict, profile: str
    ) -> dict:
        """
        Фільтрує метрики профілю за категоріями.

        Args:
            profile_metrics: Метрики згруповані за категоріями
            profile: Назва профілю

        Returns:
            dict: Відфільтровані метрики за категоріями
        """
        self._validate_profile(profile)

        allowed_metrics_by_category = self.get_metrics_for_profile(profile)
        filtered_metrics = {}

        for category, metrics_dict in profile_metrics.items():
            if category in allowed_metrics_by_category:
                filtered_category_metrics = {}
                allowed_metrics_for_category = set(
                    allowed_metrics_by_category[category]
                )

                for metric_name, value in metrics_dict.items():
                    if isinstance(value, (int, float)):
                        if metric_name in allowed_metrics_for_category:
                            filtered_category_metrics[metric_name] = value
                        else:
                            print(
                                f"🔄 Filtered out metric '{metric_name}' in category '{category}' for profile '{profile}' (not in config)"
                            )
                    else:
                        filtered_category_metrics[metric_name] = value

                if filtered_category_metrics:
                    filtered_metrics[category] = filtered_category_metrics
            else:
                print(
                    f"🔄 Filtered out entire category '{category}' for profile '{profile}' (not in config)"
                )

        return filtered_metrics

    def _validate_profile(self, profile: str) -> None:
        """Валідує назву профілю."""
        if profile not in self.VALID_PROFILES:
            raise ValueError(
                f"Unknown profile: {profile}. Available profiles: {', '.join(self.VALID_PROFILES)}"
            )

    def _get_metric_category(self, metric_name: str) -> str:
        """Повертає категорію метрики або 'Other' якщо не знайдено."""
        if metric_name in self._metrics_config:
            return self._metrics_config[metric_name]["category"]
        return "Other"


# Глобальний екземпляр сервісу
metrics_profile_service = MetricsProfileService()
