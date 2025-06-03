from pathlib import Path
import pandas as pd  # type: ignore
import logging
from ..base_metric import BaseMetric
from config.sessions_config import SESSIONS
from services.utils import is_time_in_session


class SessionDistributionMetrics(BaseMetric):
    def __init__(self, timeframes_dir: Path):
        super().__init__(timeframes_dir)
        # Create cache directory in the parent of timeframes_dir
        data_dir = timeframes_dir.parent
        self.cache_dir = data_dir / "metrics" / "session_distribution"
        self.cache_dir.mkdir(parents=True, exist_ok=True)  # Setup logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def calculate(self, symbol: str, year: str) -> dict:
        self.logger.info(
            f"Starting session distribution calculation for {symbol} {year}"
        )

        # Check for cached intermediate data first
        intermediate_cache_file = (
            self.cache_dir / f"{symbol}_{year}_daily_session_data.csv"
        )

        if intermediate_cache_file.exists():
            self.logger.info(
                f"Loading cached intermediate data from {intermediate_cache_file}"
            )
            try:
                daily_session_df = pd.read_csv(
                    intermediate_cache_file, parse_dates=["trading_date"]
                )
                self.logger.info(f"Loaded {len(daily_session_df)} cached daily records")
            except Exception as e:
                self.logger.warning(
                    f"Failed to load intermediate cache: {e}. Recalculating..."
                )
                daily_session_df = self._prepare_daily_session_data(
                    symbol, year, intermediate_cache_file
                )
        else:
            # Prepare daily session data from 5-minute data
            daily_session_df = self._prepare_daily_session_data(
                symbol, year, intermediate_cache_file
            )

        if daily_session_df.empty:
            self.logger.warning(f"No daily session data available for {symbol} {year}")
            return self._create_empty_metrics()

        # Calculate session distribution from cached/prepared data
        return self._calculate_session_percentages(daily_session_df)

    def _prepare_daily_session_data(
        self, symbol: str, year: str, cache_file: Path
    ) -> pd.DataFrame:
        """
        Prepare daily session data from 5-minute data and cache it.
        Returns DataFrame with columns: trading_date, daily_high_session, daily_low_session
        """
        self.logger.info(f"Preparing daily session data for {symbol} {year}")

        # Load 5-minute data for detailed session analysis
        self.logger.info(f"Loading 5-minute data for {symbol} {year}")
        five_minute_data = self.load_timeframe_data(symbol, year, "5m")

        if five_minute_data.empty:
            self.logger.warning(f"No 5-minute data found for {symbol} {year}")
            return pd.DataFrame()

        self.logger.info(f"Processing {len(five_minute_data)} 5-minute data points")

        # Group by trading day (since trading day starts at 21:00)
        self.logger.info("Grouping data by trading days")
        daily_groups = {}

        for timestamp, row in five_minute_data.iterrows():
            # Determine which trading day this data belongs to
            if timestamp.time() >= pd.Timestamp("21:00").time():
                # After 21:00 = next trading day
                trading_date = (timestamp + pd.Timedelta(days=1)).date()
            else:
                # Before 21:00 = current trading day
                trading_date = timestamp.date()

            if trading_date not in daily_groups:
                daily_groups[trading_date] = []
            daily_groups[trading_date].append((timestamp, row))

        total_days = len(daily_groups)
        self.logger.info(f"Found {total_days} trading days to process")

        # Process each trading day to find session highs/lows
        daily_results = []
        processed_days = 0

        for trading_date, day_data in daily_groups.items():
            if not day_data:
                continue

            processed_days += 1
            if processed_days % 50 == 0:  # Log progress every 50 days
                self.logger.info(f"Processed {processed_days}/{total_days} days")

            # Calculate session highs and lows for this day
            session_highs = {}
            session_lows = {}
            out_of_session_high = None
            out_of_session_low = None

            for timestamp, row in day_data:
                session_found = False

                for session_name, session_times in SESSIONS.items():
                    if is_time_in_session(timestamp.time(), session_times):
                        # Update session high/low
                        if session_name not in session_highs:
                            session_highs[session_name] = row["High"]
                            session_lows[session_name] = row["Low"]
                        else:
                            session_highs[session_name] = max(
                                session_highs[session_name], row["High"]
                            )
                            session_lows[session_name] = min(
                                session_lows[session_name], row["Low"]
                            )
                        session_found = True
                        break

                if not session_found:
                    # Out of session data
                    if out_of_session_high is None:
                        out_of_session_high = row["High"]
                        out_of_session_low = row["Low"]
                    else:
                        out_of_session_high = max(out_of_session_high, row["High"])
                        out_of_session_low = min(out_of_session_low, row["Low"])

            # Find which session had the daily high and low
            all_highs = dict(session_highs)
            all_lows = dict(session_lows)

            if out_of_session_high is not None:
                all_highs["Out of Session"] = out_of_session_high
                all_lows["Out of Session"] = out_of_session_low

            daily_high_session = "Unknown"
            daily_low_session = "Unknown"

            if all_highs:
                # Find session with highest high
                max_session = max(all_highs.items(), key=lambda x: x[1])
                daily_high_session = max_session[0]

                # Find session with lowest low
                min_session = min(all_lows.items(), key=lambda x: x[1])
                daily_low_session = min_session[
                    0
                ]  # Store this day's results with all session highs/lows
            result = {
                "trading_date": trading_date,
                "daily_high_session": daily_high_session,
                "daily_low_session": daily_low_session,
                "daily_high_value": max_session[1] if all_highs else None,
                "daily_low_value": min_session[1] if all_lows else None,
            }

            # Add all session highs and lows
            for session_name in SESSIONS.keys():
                result[f"{session_name}_high"] = session_highs.get(session_name, None)
                result[f"{session_name}_low"] = session_lows.get(session_name, None)

            # Add out of session data
            result["Out_of_Session_high"] = out_of_session_high
            result["Out_of_Session_low"] = out_of_session_low

            daily_results.append(result)

        # Create DataFrame from results
        daily_session_df = pd.DataFrame(daily_results)

        # Cache the intermediate data
        self.logger.info(f"Caching intermediate data to {cache_file}")
        try:
            daily_session_df.to_csv(cache_file, index=False)
            self.logger.info(
                f"Successfully cached {len(daily_session_df)} daily records"
            )
        except Exception as e:
            self.logger.error(f"Failed to cache intermediate data: {e}")

        return daily_session_df

    def _calculate_session_percentages(self, daily_session_df: pd.DataFrame) -> dict:
        """
        Calculate session distribution percentages from prepared daily session data.
        """
        self.logger.info("Calculating session distribution percentages")

        total_days = len(daily_session_df)
        self.logger.info(f"Processing {total_days} trading days")

        # Count occurrences of each session
        high_counts = {
            "Asia": 0,
            "Frankfurt": 0,
            "London": 0,
            "Lunch": 0,
            "NY": 0,
            "Out of Session": 0,
        }
        low_counts = high_counts.copy()

        # Count from prepared data
        for _, row in daily_session_df.iterrows():
            daily_high_session = row["daily_high_session"]
            daily_low_session = row["daily_low_session"]

            if daily_high_session in high_counts:
                high_counts[daily_high_session] += 1
            if daily_low_session in low_counts:
                low_counts[daily_low_session] += 1

        # Calculate percentages
        metrics = {}
        for session_name in SESSIONS.keys():
            high_percentage = (
                round((high_counts[session_name] / total_days) * 100, 2)
                if total_days > 0
                else 0
            )
            low_percentage = (
                round((low_counts[session_name] / total_days) * 100, 2)
                if total_days > 0
                else 0
            )

            metrics[f"Daily High in {session_name} %"] = high_percentage
            metrics[f"Daily Low in {session_name} %"] = low_percentage

        metrics["Daily High in Out of Session %"] = (
            round((high_counts["Out of Session"] / total_days) * 100, 2)
            if total_days > 0
            else 0
        )
        metrics["Daily Low in Out of Session %"] = (
            round((low_counts["Out of Session"] / total_days) * 100, 2)
            if total_days > 0
            else 0
        )

        self.logger.info(f"Session distribution calculation completed")

        # Log summary of results
        self.logger.info("Session Distribution Summary:")
        for session in SESSIONS.keys():
            high_pct = metrics.get(f"Daily High in {session} %", 0)
            low_pct = metrics.get(f"Daily Low in {session} %", 0)
            self.logger.info(f"  {session}: High {high_pct}%, Low {low_pct}%")

        out_high_pct = metrics.get("Daily High in Out of Session %", 0)
        out_low_pct = metrics.get("Daily Low in Out of Session %", 0)
        self.logger.info(f"  Out of Session: High {out_high_pct}%, Low {out_low_pct}%")

        return metrics

    def _create_empty_metrics(self) -> dict:
        """Create empty metrics when no data is available"""
        metrics = {}
        for session_name in SESSIONS.keys():
            metrics[f"Daily High in {session_name} %"] = 0
            metrics[f"Daily Low in {session_name} %"] = 0

        metrics["Daily High in Out of Session %"] = 0
        metrics["Daily Low in Out of Session %"] = 0

        return metrics

    def clear_cache(self, symbol: str = None, year: str = None):
        """Clear cached results. If symbol and year are provided, clears specific cache file."""
        if symbol and year:
            cache_file = self.cache_dir / f"{symbol}_{year}_session_distribution.csv"
            if cache_file.exists():
                cache_file.unlink()
                self.logger.info(f"Cleared cache for {symbol} {year}")
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*.csv"):
                cache_file.unlink()
            self.logger.info("Cleared all session distribution cache files")

    def get_session_comparison_metrics(self, daily_session_df: pd.DataFrame) -> dict:
        """
        Calculate comparison metrics between sessions using cached session data.
        Returns percentages for when one session breaks another session's high/low.
        """
        if daily_session_df.empty:
            return {}

        metrics = {}
        session_names = list(SESSIONS.keys())

        for i, session1 in enumerate(session_names):
            for j, session2 in enumerate(session_names):
                if i >= j:  # Avoid duplicate comparisons and self-comparison
                    continue

                # Count when session2 breaks session1's high
                session1_high_col = f"{session1}_high"
                session2_high_col = f"{session2}_high"

                if (
                    session1_high_col in daily_session_df.columns
                    and session2_high_col in daily_session_df.columns
                ):
                    valid_data = daily_session_df.dropna(
                        subset=[session1_high_col, session2_high_col]
                    )
                    if not valid_data.empty:
                        breaks_high = (
                            valid_data[session2_high_col]
                            > valid_data[session1_high_col]
                        ).sum()
                        total_days = len(valid_data)
                        percentage = (
                            round((breaks_high / total_days) * 100, 2)
                            if total_days > 0
                            else 0
                        )
                        metrics[f"{session2}-{session1} High %"] = percentage

                # Count when session2 breaks session1's low
                session1_low_col = f"{session1}_low"
                session2_low_col = f"{session2}_low"

                if (
                    session1_low_col in daily_session_df.columns
                    and session2_low_col in daily_session_df.columns
                ):
                    valid_data = daily_session_df.dropna(
                        subset=[session1_low_col, session2_low_col]
                    )
                    if not valid_data.empty:
                        breaks_low = (
                            valid_data[session2_low_col] < valid_data[session1_low_col]
                        ).sum()
                        total_days = len(valid_data)
                        percentage = (
                            round((breaks_low / total_days) * 100, 2)
                            if total_days > 0
                            else 0
                        )
                        metrics[f"{session2}-{session1} Low %"] = percentage

        return metrics

    def get_directional_metrics(self, daily_session_df: pd.DataFrame) -> dict:
        """
        Calculate directional metrics using cached session data.
        """
        if daily_session_df.empty:
            return {}

        metrics = {}
        session_names = list(SESSIONS.keys())

        for i, session1 in enumerate(session_names):
            for j, session2 in enumerate(session_names):
                if i >= j:  # Avoid duplicate comparisons and self-comparison
                    continue

                session1_high_col = f"{session1}_high"
                session1_low_col = f"{session1}_low"
                session2_low_col = f"{session2}_low"
                session2_high_col = f"{session2}_high"

                # Bullish: session2 breaks session1's low (takes liquidity below and moves up)
                if all(
                    col in daily_session_df.columns
                    for col in [session1_low_col, session2_low_col]
                ):
                    valid_data = daily_session_df.dropna(
                        subset=[session1_low_col, session2_low_col]
                    )
                    if not valid_data.empty:
                        bullish_breaks = (
                            valid_data[session2_low_col] < valid_data[session1_low_col]
                        ).sum()
                        total_days = len(valid_data)
                        percentage = (
                            round((bullish_breaks / total_days) * 100, 2)
                            if total_days > 0
                            else 0
                        )
                        metrics[f"Bullish {session2}-{session1} Low %"] = percentage

                # Bearish: session2 breaks session1's high (takes liquidity above and moves down)
                if all(
                    col in daily_session_df.columns
                    for col in [session1_high_col, session2_high_col]
                ):
                    valid_data = daily_session_df.dropna(
                        subset=[session1_high_col, session2_high_col]
                    )
                    if not valid_data.empty:
                        bearish_breaks = (
                            valid_data[session2_high_col]
                            > valid_data[session1_high_col]
                        ).sum()
                        total_days = len(valid_data)
                        percentage = (
                            round((bearish_breaks / total_days) * 100, 2)
                            if total_days > 0
                            else 0
                        )
                        metrics[f"Bearish {session2}-{session1} High %"] = percentage

        return metrics
