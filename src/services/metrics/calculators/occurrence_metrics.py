import pandas as pd  # type: ignore
from ..base_metric import BaseMetric


class OccurrenceMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        try:
            daily_data = self.load_timeframe_data(symbol, year, "1d")
            weekly_data = self.load_timeframe_data(symbol, year, "1w")
            if daily_data.empty or weekly_data.empty:
                return self._get_empty_metrics()

            daily_data["weekday"] = pd.to_datetime(daily_data.index).weekday

            high_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
            low_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

            # Додаткові лічильники для bullish/bearish тижнів
            bullish_high_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
            bearish_high_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
            total_weeks = 0
            total_bullish_weeks = 0
            total_bearish_weeks = 0

            for week_start, week_data in weekly_data.iterrows():
                week_high = week_data["High"]
                week_low = week_data["Low"]

                # Parse week start date from range format like "2000-06-05 to 2000-06-11"
                if " to " in str(week_start):
                    week_start_str = str(week_start).split(" to ")[0]
                    week_end_str = str(week_start).split(" to ")[1]
                    week_start_date = pd.to_datetime(week_start_str)
                    week_end_date = pd.to_datetime(week_end_str)
                else:
                    week_start_date = pd.to_datetime(week_start)
                    week_end_date = week_start_date + pd.Timedelta(days=6)

                # Get daily data for this week
                week_mask = (pd.to_datetime(daily_data.index) >= week_start_date) & (
                    pd.to_datetime(daily_data.index) <= week_end_date
                )
                week_daily_data = daily_data[week_mask]

                if len(week_daily_data) == 0:
                    continue

                total_weeks += 1

                week_open = week_data["Open"]
                week_close = week_data["Close"]
                is_bullish_week = week_close > week_open
                is_bearish_week = week_close < week_open

                if is_bullish_week:
                    total_bullish_weeks += 1
                elif is_bearish_week:
                    total_bearish_weeks += 1

                high_days = week_daily_data[week_daily_data["High"] == week_high]
                if not high_days.empty:
                    first_high_day = high_days.iloc[0]
                    high_weekday = first_high_day["weekday"]
                    if high_weekday in high_counts:
                        high_counts[high_weekday] += 1

                        if is_bullish_week:
                            bullish_high_counts[high_weekday] += 1
                        elif is_bearish_week:
                            bearish_high_counts[high_weekday] += 1

                low_days = week_daily_data[week_daily_data["Low"] == week_low]
                if not low_days.empty:
                    first_low_day = low_days.iloc[0]
                    low_weekday = first_low_day["weekday"]
                    if low_weekday in low_counts:
                        low_counts[low_weekday] += 1

            if total_weeks > 0:
                metrics = {
                    "High in Monday": round((high_counts[0] / total_weeks) * 100, 2),
                    "High in Tuesday": round((high_counts[1] / total_weeks) * 100, 2),
                    "High in Wednesday": round((high_counts[2] / total_weeks) * 100, 2),
                    "High in Thursday": round((high_counts[3] / total_weeks) * 100, 2),
                    "High in Friday": round((high_counts[4] / total_weeks) * 100, 2),
                    "Low in Monday": round((low_counts[0] / total_weeks) * 100, 2),
                    "Low in Tuesday": round((low_counts[1] / total_weeks) * 100, 2),
                    "Low in Wednesday": round((low_counts[2] / total_weeks) * 100, 2),
                    "Low in Thursday": round((low_counts[3] / total_weeks) * 100, 2),
                    "Low in Friday": round((low_counts[4] / total_weeks) * 100, 2),
                    # Bullish High metrics
                    "Bullish High in Monday": (
                        round((bullish_high_counts[0] / total_bullish_weeks) * 100, 2)
                        if total_bullish_weeks > 0
                        else 0.0
                    ),
                    "Bullish High in Tuesday": (
                        round((bullish_high_counts[1] / total_bullish_weeks) * 100, 2)
                        if total_bullish_weeks > 0
                        else 0.0
                    ),
                    "Bullish High in Wednesday": (
                        round((bullish_high_counts[2] / total_bullish_weeks) * 100, 2)
                        if total_bullish_weeks > 0
                        else 0.0
                    ),
                    "Bullish High in Thursday": (
                        round((bullish_high_counts[3] / total_bullish_weeks) * 100, 2)
                        if total_bullish_weeks > 0
                        else 0.0
                    ),
                    "Bullish High in Friday": (
                        round((bullish_high_counts[4] / total_bullish_weeks) * 100, 2)
                        if total_bullish_weeks > 0
                        else 0.0
                    ),
                    # Bearish High metrics
                    "Bearish High in Monday": (
                        round((bearish_high_counts[0] / total_bearish_weeks) * 100, 2)
                        if total_bearish_weeks > 0
                        else 0.0
                    ),
                    "Bearish High in Tuesday": (
                        round((bearish_high_counts[1] / total_bearish_weeks) * 100, 2)
                        if total_bearish_weeks > 0
                        else 0.0
                    ),
                    "Bearish High in Wednesday": (
                        round((bearish_high_counts[2] / total_bearish_weeks) * 100, 2)
                        if total_bearish_weeks > 0
                        else 0.0
                    ),
                    "Bearish High in Thursday": (
                        round((bearish_high_counts[3] / total_bearish_weeks) * 100, 2)
                        if total_bearish_weeks > 0
                        else 0.0
                    ),
                    "Bearish High in Friday": (
                        round((bearish_high_counts[4] / total_bearish_weeks) * 100, 2)
                        if total_bearish_weeks > 0
                        else 0.0
                    ),
                }
            else:
                metrics = self._get_empty_metrics()

            return metrics

        except Exception as e:
            print(f"❌ Error calculating occurrence metrics for {symbol}: {e}")
            return self._get_empty_metrics()

    def _get_empty_metrics(self) -> dict:
        return self._get_default_metrics(self._get_metric_names())

    def _get_metric_names(self) -> list[str]:
        """Return list of metric names for this calculator."""
        return [
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
            # Bullish High metrics
            "Bullish High in Monday",
            "Bullish High in Tuesday",
            "Bullish High in Wednesday",
            "Bullish High in Thursday",
            "Bullish High in Friday",
            # Bearish High metrics
            "Bearish High in Monday",
            "Bearish High in Tuesday",
            "Bearish High in Wednesday",
            "Bearish High in Thursday",
            "Bearish High in Friday",
        ]
