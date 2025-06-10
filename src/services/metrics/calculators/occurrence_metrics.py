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
            total_weeks = 0

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

                high_days = week_daily_data[week_daily_data["High"] == week_high]
                if not high_days.empty:
                    first_high_day = high_days.iloc[0]
                    high_weekday = first_high_day["weekday"]
                    if high_weekday in high_counts:
                        high_counts[high_weekday] += 1

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
                    "PDH Probability": round(
                        self._calculate_pdh_probability(daily_data), 2
                    ),
                    "PDL Probability": round(
                        self._calculate_pdl_probability(daily_data), 2
                    ),
                    "PD Levels Probability": round(
                        self._calculate_pd_levels_probability(daily_data), 2
                    ),
                }
            else:
                metrics = self._get_empty_metrics()

            return metrics

        except Exception as e:
            print(f"❌ Error calculating occurrence metrics for {symbol}: {e}")
            return self._get_empty_metrics()

    def _get_empty_metrics(self) -> dict:
        """Return empty metrics structure"""
        return {
            "High in Monday": 0.0,
            "High in Tuesday": 0.0,
            "High in Wednesday": 0.0,
            "High in Thursday": 0.0,
            "High in Friday": 0.0,
            "Low in Monday": 0.0,
            "Low in Tuesday": 0.0,
            "Low in Wednesday": 0.0,
            "Low in Thursday": 0.0,
            "Low in Friday": 0.0,
            "PDH Probability": 0.0,
            "PDL Probability": 0.0,
            "PD Levels Probability": 0.0,
        }

    def _calculate_pdh_probability(self, daily_data: pd.DataFrame) -> float:
        """Calculate probability that previous day high (PDH) is taken out"""
        if len(daily_data) < 2:
            return 0.0

        pdh_taken_count = 0
        total_days = 0

        for i in range(1, len(daily_data)):
            prev_day_high = daily_data.iloc[i - 1]["High"]
            current_day_high = daily_data.iloc[i]["High"]

            if current_day_high > prev_day_high:
                pdh_taken_count += 1
            total_days += 1

        return (pdh_taken_count / total_days * 100) if total_days > 0 else 0.0

    def _calculate_pdl_probability(self, daily_data: pd.DataFrame) -> float:
        """Calculate probability that previous day low (PDL) is taken out"""
        if len(daily_data) < 2:
            return 0.0

        pdl_taken_count = 0
        total_days = 0

        for i in range(1, len(daily_data)):
            prev_day_low = daily_data.iloc[i - 1]["Low"]
            current_day_low = daily_data.iloc[i]["Low"]

            if current_day_low < prev_day_low:
                pdl_taken_count += 1
            total_days += 1

        return (pdl_taken_count / total_days * 100) if total_days > 0 else 0.0

    def _calculate_pd_levels_probability(self, daily_data: pd.DataFrame) -> float:
        """Calculate probability that BOTH PDH AND PDL are taken out"""
        if len(daily_data) < 2:
            return 0.0

        both_levels_taken_count = 0
        total_days = 0

        for i in range(1, len(daily_data)):
            prev_day_high = daily_data.iloc[i - 1]["High"]
            prev_day_low = daily_data.iloc[i - 1]["Low"]
            current_day_high = daily_data.iloc[i]["High"]
            current_day_low = daily_data.iloc[i]["Low"]

            # Both PDH AND PDL must be taken (changed from OR to AND)
            if current_day_high > prev_day_high and current_day_low < prev_day_low:
                both_levels_taken_count += 1
            total_days += 1

        return (both_levels_taken_count / total_days * 100) if total_days > 0 else 0.0
