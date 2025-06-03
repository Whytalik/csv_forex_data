from ..base_metric import BaseMetric


class OccurrenceMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        # Load required timeframes
        daily_data = self.load_timeframe_data(symbol, year, "1d")

        metrics = {
            "High in Monday": 0,
            "High in Tuesday": 0,
            "High in Wednesday": 0,
            "High in Thursday": 0,
            "High in Friday": 0,
            "Low in Monday": 0,
            "Low in Tuesday": 0,
            "Low in Wednesday": 0,
            "Low in Thursday": 0,
            "Low in Friday": 0,
        }

        return metrics
