"""
Utilities for working with metrics configuration.
Provides helper functions for metrics config management and validation.
"""

from typing import Dict, List, Any, Optional
from config.metrics_config import get_all_metrics, get_metrics_by_category


class MetricsConfigManager:
    """Manager for metrics configuration operations."""

    def __init__(self):
        self._metrics_cache = None

    def get_metrics(self, refresh: bool = False) -> Dict[str, Any]:
        """
        Отримує всі метрики з кешуванням.

        Args:
            refresh: Чи оновлювати кеш

        Returns:
            dict: Словник з усіма метриками
        """
        if self._metrics_cache is None or refresh:
            self._metrics_cache = get_all_metrics()
        return self._metrics_cache

    def get_category_metrics(self, category: str) -> Dict[str, Any]:
        """
        Отримує метрики за категорією.

        Args:
            category: Назва категорії

        Returns:
            dict: Метрики категорії
        """
        return get_metrics_by_category(category)

    def get_available_categories(self) -> List[str]:
        """
        Повертає список доступних категорій.

        Returns:
            list: Список категорій
        """
        categories = set()
        metrics = self.get_metrics()

        for config in metrics.values():
            if isinstance(config, dict) and "category" in config:
                categories.add(config["category"])

        return sorted(list(categories))

    def validate_metric_exists(self, metric_name: str) -> bool:
        """
        Перевіряє, чи існує метрика.

        Args:
            metric_name: Назва метрики

        Returns:
            bool: True якщо метрика існує
        """
        metrics = self.get_metrics()
        return metric_name in metrics

    def get_metric_info(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """
        Отримує інформацію про метрику.

        Args:
            metric_name: Назва метрики

        Returns:
            dict або None: Інформація про метрику
        """
        metrics = self.get_metrics()
        return metrics.get(metric_name)

    def get_metrics_count(self) -> int:
        """
        Повертає кількість метрик.

        Returns:
            int: Кількість метрик
        """
        return len(self.get_metrics())

    def get_metrics_by_profiles(self, profiles: List[str]) -> Dict[str, Any]:
        """
        Фільтрує метрики за профілями.

        Args:
            profiles: Список профілів

        Returns:
            dict: Відфільтровані метрики
        """
        metrics = self.get_metrics()
        filtered = {}

        for metric_name, config in metrics.items():
            if isinstance(config, dict) and "profiles" in config:
                if any(profile in config["profiles"] for profile in profiles):
                    filtered[metric_name] = config

        return filtered

    def get_category_summary(self) -> Dict[str, int]:
        """
        Повертає підсумок метрик за категоріями.

        Returns:
            dict: Словник з кількістю метрик у кожній категорії
        """
        summary = {}
        metrics = self.get_metrics()

        for config in metrics.values():
            if isinstance(config, dict) and "category" in config:
                category = config["category"]
                summary[category] = summary.get(category, 0) + 1

        return summary

    def search_metrics(self, query: str, case_sensitive: bool = False) -> List[str]:
        """
        Пошук метрик за назвою.

        Args:
            query: Пошуковий запит
            case_sensitive: Чи враховувати регістр

        Returns:
            list: Список знайдених назв метрик
        """
        metrics = self.get_metrics()
        results = []

        search_query = query if case_sensitive else query.lower()

        for metric_name in metrics.keys():
            search_target = metric_name if case_sensitive else metric_name.lower()
            if search_query in search_target:
                results.append(metric_name)

        return sorted(results)

    def clear_cache(self) -> None:
        """Очищує кеш метрик."""
        self._metrics_cache = None


def get_metrics_stats() -> Dict[str, Any]:
    """
    Повертає статистику по метриках.

    Returns:
        dict: Статистика метрик
    """
    manager = MetricsConfigManager()

    return {
        "total_metrics": manager.get_metrics_count(),
        "categories": manager.get_available_categories(),
        "category_summary": manager.get_category_summary(),
    }


def validate_metrics_config() -> List[str]:
    """
    Валідує конфігурацію метрик.

    Returns:
        list: Список помилок (порожній якщо все ОК)
    """
    errors = []
    manager = MetricsConfigManager()
    metrics = manager.get_metrics()

    for metric_name, config in metrics.items():
        if not isinstance(config, dict):
            errors.append(
                f"Metric '{metric_name}' has invalid config type: {type(config)}"
            )
            continue

        # Перевіряємо обов'язкові поля
        required_fields = ["category", "profiles"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Metric '{metric_name}' missing required field: {field}")

        # Перевіряємо типи
        if "profiles" in config and not isinstance(config["profiles"], list):
            errors.append(f"Metric '{metric_name}' profiles field must be a list")

    return errors


# Глобальний екземпляр менеджера
metrics_config_manager = MetricsConfigManager()
