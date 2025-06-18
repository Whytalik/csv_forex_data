import pandas as pd  # type: ignore
from ..base_metric import BaseMetric
from config.pairs_config import PAIRS
from utils.session_utils import get_session_range


class VolatilityMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        try:
            daily_data = self.load_timeframe_data(symbol, year, "1d")
            weekly_data = self.load_timeframe_data(symbol, year, "1w")
            five_minute_data = self.load_timeframe_data(symbol, year, "5m")
            pip_factor = PAIRS[symbol.upper()]["pip_factor"]

            if daily_data.empty or weekly_data.empty:
                return self._get_default_metrics(self._get_metric_names())

            # Calculate daily metrics
            daily_range = round(
                ((daily_data["High"] - daily_data["Low"]) * pip_factor).mean(), 2
            )
            daily_body_size = round(
                (abs(daily_data["Close"] - daily_data["Open"]) * pip_factor).mean(), 2
            )

            # Calculate weekly metrics
            weekly_range = round(
                ((weekly_data["High"] - weekly_data["Low"]) * pip_factor).mean(), 2
            )
            weekly_body_size = round(
                (abs(weekly_data["Close"] - weekly_data["Open"]) * pip_factor).mean(), 2
            )

            # Calculate session ranges
            asia_range = get_session_range("Asia", five_minute_data, symbol)
            frankfurt_range = get_session_range("Frankfurt", five_minute_data, symbol)
            london_range = get_session_range("London", five_minute_data, symbol)
            lunch_range = get_session_range("Lunch", five_minute_data, symbol)
            ny_range = get_session_range("NY", five_minute_data, symbol)

            # Calculate daily ranges for each weekday
            weekday_ranges = {}
            for weekday in range(5):
                try:
                    weekday_mask = pd.to_datetime(daily_data.index).weekday == weekday
                    weekday_data = daily_data[weekday_mask]

                    if not weekday_data.empty:
                        daily_ranges = (
                            weekday_data["High"] - weekday_data["Low"]
                        ) * pip_factor
                        weekday_ranges[weekday] = round(daily_ranges.mean(), 2)
                    else:
                        print(f"Warning: No data found for weekday {weekday}")
                        weekday_ranges[weekday] = 0
                except Exception as e:
                    print(f"Error processing weekday {weekday}: {e}")
                    weekday_ranges[weekday] = 0

            avg_monday_range = weekday_ranges[0]
            avg_tuesday_range = weekday_ranges[1]
            avg_wednesday_range = weekday_ranges[2]
            avg_thursday_range = weekday_ranges[3]
            avg_friday_range = weekday_ranges[4]

            metrics = {
                "Average Daily Range (pips)": daily_range,
                "Average Daily Body Size (pips)": daily_body_size,
                "Average Weekly Range (pips)": weekly_range,
                "Average Weekly Body Size (pips)": weekly_body_size,
                "Average Asia Range": asia_range,
                "Average Frankfurt Range": frankfurt_range,
                "Average London Range": london_range,
                "Average Lunch Range": lunch_range,
                "Average NY Range": ny_range,
                "Average Monday Range": avg_monday_range,
                "Average Tuesday Range": avg_tuesday_range,
                "Average Wednesday Range": avg_wednesday_range,
                "Average Thursday Range": avg_thursday_range,
                "Average Friday Range": avg_friday_range,
            }

            return metrics

        except Exception as e:
            print(f"Error calculating volatility metrics for {symbol}: {e}")
            return self._get_default_metrics(self._get_metric_names())

    def _get_metric_names(self) -> list[str]:
        """Return list of metric names for this calculator."""
        return [
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
        ]
