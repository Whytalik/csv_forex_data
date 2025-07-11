from pathlib import Path
import pandas as pd  # type: ignore
import logging
from ..base_metric import BaseMetric
from config.sessions_config import SESSIONS
from utils.session_utils import is_time_in_session


class SessionDistributionMetrics(BaseMetric):
    def __init__(self, timeframes_dir: Path):
        super().__init__(timeframes_dir)
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
        five_minute_data = self.load_timeframe_data(symbol, year, "5m")

        if five_minute_data.empty:
            self.logger.warning(f"No 5-minute data found for {symbol} {year}")
            return pd.DataFrame()

        self.logger.info(f"Loaded {symbol} {year}: {len(five_minute_data):,} 5m points")

        # Group by trading day (since trading day starts at 21:00)
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
        self.logger.info(f"Found {total_days:,} trading days to process")

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

            # Find which session had the and low
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
                low_counts[daily_low_session] += 1  # Calculate percentages
        metrics = {}
        for session_name in SESSIONS.keys():
            high_percentage = (
                self.round_metric((high_counts[session_name] / total_days) * 100)
                if total_days > 0
                else 0.0
            )
            low_percentage = (
                self.round_metric((low_counts[session_name] / total_days) * 100)
                if total_days > 0
                else 0.0
            )

            metrics[f"Daily High in {session_name} %"] = high_percentage
            metrics[f"Daily Low in {session_name} %"] = low_percentage

        metrics["Daily High in Out of Session %"] = (
            self.round_metric((high_counts["Out of Session"] / total_days) * 100)
            if total_days > 0
            else 0.0
        )
        metrics["Daily Low in Out of Session %"] = (
            self.round_metric((low_counts["Out of Session"] / total_days) * 100)
            if total_days > 0
            else 0.0
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
        else:  # Clear all cache files
            for cache_file in self.cache_dir.glob("*.csv"):
                cache_file.unlink()
            self.logger.info("Cleared all session distribution cache files")

    def get_session_comparison_metrics(self, daily_session_df: pd.DataFrame) -> dict:
        """
        Calculate comparison metrics between sessions using cached session data.
        Returns percentages for when one session breaks another session's high/low
        considering chronological order - once a level is broken, subsequent sessions
        cannot break it again.
        """
        if daily_session_df.empty:
            return {}

        metrics = {}
        # Define chronological order of sessions throughout the trading day
        session_order = ["Asia", "Frankfurt", "London", "Lunch", "NY", "Out of Session"]

        for i, session1 in enumerate(session_order):
            for j, session2 in enumerate(session_order):
                if j <= i:  # Only consider sessions that come AFTER session1
                    continue

                # Count when session2 breaks session1's high (and it hasn't been broken yet)
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
                        # Check if session2 breaks session1's high AND
                        # no intermediate session has already broken it
                        breaks_count = 0

                        for _, row in valid_data.iterrows():
                            session1_high = row[session1_high_col]
                            session2_high = row[session2_high_col]

                            # Check if session2 breaks session1's high
                            if session2_high > session1_high:
                                # Check if any intermediate session already broke it
                                already_broken = False
                                for k in range(
                                    i + 1, j
                                ):  # Check sessions between session1 and session2
                                    intermediate_session = session_order[k]
                                    intermediate_high_col = (
                                        f"{intermediate_session}_high"
                                    )

                                    if (
                                        intermediate_high_col
                                        in daily_session_df.columns
                                    ):
                                        intermediate_high = row.get(
                                            intermediate_high_col
                                        )
                                        if (
                                            pd.notna(intermediate_high)
                                            and intermediate_high > session1_high
                                        ):
                                            already_broken = True
                                            break

                                if not already_broken:
                                    breaks_count += 1

                        total_days = len(valid_data)
                        percentage = (
                            self.round_metric((breaks_count / total_days) * 100)
                            if total_days > 0
                            else 0.0
                        )
                        metrics[f"{session2}-{session1} High %"] = percentage

                # Count when session2 breaks session1's low (and it hasn't been broken yet)
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
                        # Check if session2 breaks session1's low AND
                        # no intermediate session has already broken it
                        breaks_count = 0

                        for _, row in valid_data.iterrows():
                            session1_low = row[session1_low_col]
                            session2_low = row[session2_low_col]

                            # Check if session2 breaks session1's low
                            if session2_low < session1_low:
                                # Check if any intermediate session already broke it
                                already_broken = False
                                for k in range(
                                    i + 1, j
                                ):  # Check sessions between session1 and session2
                                    intermediate_session = session_order[k]
                                    intermediate_low_col = f"{intermediate_session}_low"

                                    if intermediate_low_col in daily_session_df.columns:
                                        intermediate_low = row.get(intermediate_low_col)
                                        if (
                                            pd.notna(intermediate_low)
                                            and intermediate_low < session1_low
                                        ):
                                            already_broken = True
                                            break

                                if not already_broken:
                                    breaks_count += 1

                        total_days = len(valid_data)
                        percentage = (
                            self.round_metric((breaks_count / total_days) * 100)
                            if total_days > 0
                            else 0.0
                        )
                        metrics[f"{session2}-{session1} Low %"] = percentage

        return metrics

    def get_directional_metrics(self, daily_session_df: pd.DataFrame) -> dict:
        if daily_session_df.empty:
            return {}

        metrics = {}
        session_order = ["Asia", "Frankfurt", "London", "Lunch", "NY", "Out of Session"]

        for i, session1 in enumerate(session_order):
            for j, session2 in enumerate(session_order):
                if j <= i:
                    continue

                session1_high_col = f"{session1}_high"
                session1_low_col = f"{session1}_low"
                session2_low_col = f"{session2}_low"
                session2_high_col = f"{session2}_high"

                if all(
                    col in daily_session_df.columns
                    for col in [session1_low_col, session2_low_col]
                ):
                    valid_data = daily_session_df.dropna(
                        subset=[session1_low_col, session2_low_col]
                    )
                    if not valid_data.empty:
                        breaks_count = 0

                        for _, row in valid_data.iterrows():
                            session1_low = row[session1_low_col]
                            session2_low = row[session2_low_col]

                            if session2_low < session1_low:
                                already_broken = False
                                for k in range(i + 1, j):
                                    intermediate_session = session_order[k]
                                    intermediate_low_col = f"{intermediate_session}_low"

                                    if intermediate_low_col in daily_session_df.columns:
                                        intermediate_low = row.get(intermediate_low_col)
                                        if (
                                            pd.notna(intermediate_low)
                                            and intermediate_low < session1_low
                                        ):
                                            already_broken = True
                                            break

                                if not already_broken:
                                    breaks_count += 1

                        total_days = len(valid_data)
                        percentage = (
                            self.round_metric((breaks_count / total_days) * 100)
                            if total_days > 0
                            else 0.0
                        )
                        metrics[f"Bullish {session2}-{session1} Low %"] = percentage

                if all(
                    col in daily_session_df.columns
                    for col in [session1_high_col, session2_high_col]
                ):
                    valid_data = daily_session_df.dropna(
                        subset=[session1_high_col, session2_high_col]
                    )
                    if not valid_data.empty:
                        breaks_count = 0

                        for _, row in valid_data.iterrows():
                            session1_high = row[session1_high_col]
                            session2_high = row[session2_high_col]

                            if session2_high > session1_high:
                                already_broken = False
                                for k in range(i + 1, j):
                                    intermediate_session = session_order[k]
                                    intermediate_high_col = (
                                        f"{intermediate_session}_high"
                                    )

                                    if (
                                        intermediate_high_col
                                        in daily_session_df.columns
                                    ):
                                        intermediate_high = row.get(
                                            intermediate_high_col
                                        )
                                        if (
                                            pd.notna(intermediate_high)
                                            and intermediate_high > session1_high
                                        ):
                                            already_broken = True
                                            break

                                if not already_broken:
                                    breaks_count += 1

                        total_days = len(valid_data)
                        percentage = (
                            self.round_metric((breaks_count / total_days) * 100)
                            if total_days > 0
                            else 0.0
                        )
                        metrics[f"Bearish {session2}-{session1} High %"] = percentage

        return metrics

    def get_directional_session_distribution(
        self, daily_session_df: pd.DataFrame
    ) -> dict:
        """
        Calculate directional session distribution metrics (Bullish/Bearish Daily High/Low per session).
        Returns percentages of when daily high/low occurs in specific sessions during bullish/bearish days.
        """
        if daily_session_df.empty:
            return {}

        self.logger.info("Calculating directional session distribution percentages")

        # Add a column to determine if day is bullish or bearish
        daily_session_df["is_bullish"] = False
        daily_session_df["is_bearish"] = False

        for idx, row in daily_session_df.iterrows():
            # If daily data has Open/Close, use it to determine direction
            # For daily df from 5min data, create a simple condition
            if all(col in daily_session_df.columns for col in ["Open", "Close"]):
                daily_session_df.at[idx, "is_bullish"] = row["Close"] > row["Open"]
                daily_session_df.at[idx, "is_bearish"] = row["Close"] < row["Open"]
            else:
                # Approximate direction using session data
                # If highest value is later in the day than lowest, consider it bullish
                sessions_order = [
                    "Asia",
                    "Frankfurt",
                    "London",
                    "Lunch",
                    "NY",
                    "Out of Session",
                ]
                high_session_idx = (
                    sessions_order.index(row["daily_high_session"])
                    if row["daily_high_session"] in sessions_order
                    else -1
                )
                low_session_idx = (
                    sessions_order.index(row["daily_low_session"])
                    if row["daily_low_session"] in sessions_order
                    else -1
                )

                # If we have both indices, compare them
                if high_session_idx >= 0 and low_session_idx >= 0:
                    daily_session_df.at[idx, "is_bullish"] = (
                        high_session_idx > low_session_idx
                    )
                    daily_session_df.at[idx, "is_bearish"] = (
                        high_session_idx < low_session_idx
                    )

        # Filter bullish and bearish days
        bullish_days = daily_session_df[daily_session_df["is_bullish"]]
        bearish_days = daily_session_df[daily_session_df["is_bearish"]]

        total_bullish = len(bullish_days)
        total_bearish = len(bearish_days)

        self.logger.info(
            f"Found {total_bullish} bullish days and {total_bearish} bearish days"
        )

        metrics = {}

        # Process all sessions including Out of Session
        all_sessions = list(SESSIONS.keys()) + ["Out of Session"]

        # Calculate bullish metrics
        if total_bullish > 0:
            # Count occurrences of each session producing high/low in bullish days
            bullish_high_counts = {session: 0 for session in all_sessions}
            bullish_low_counts = {session: 0 for session in all_sessions}

            for _, row in bullish_days.iterrows():
                daily_high_session = row["daily_high_session"]
                daily_low_session = row["daily_low_session"]

                if daily_high_session in bullish_high_counts:
                    bullish_high_counts[daily_high_session] += 1
                if daily_low_session in bullish_low_counts:
                    bullish_low_counts[daily_low_session] += 1

            # Calculate percentages
            for session_name in all_sessions:
                high_percentage = self.round_metric(
                    (bullish_high_counts[session_name] / total_bullish) * 100
                )
                low_percentage = self.round_metric(
                    (bullish_low_counts[session_name] / total_bullish) * 100
                )

                metrics[f"Bullish Daily High in {session_name} %"] = high_percentage
                metrics[f"Bullish Daily Low in {session_name} %"] = low_percentage
        else:
            # Set default values if no bullish days
            for session_name in all_sessions:
                metrics[f"Bullish Daily High in {session_name} %"] = 0.0
                metrics[f"Bullish Daily Low in {session_name} %"] = 0.0

        # Calculate bearish metrics
        if total_bearish > 0:
            # Count occurrences of each session producing high/low in bearish days
            bearish_high_counts = {session: 0 for session in all_sessions}
            bearish_low_counts = {session: 0 for session in all_sessions}

            for _, row in bearish_days.iterrows():
                daily_high_session = row["daily_high_session"]
                daily_low_session = row["daily_low_session"]

                if daily_high_session in bearish_high_counts:
                    bearish_high_counts[daily_high_session] += 1
                if daily_low_session in bearish_low_counts:
                    bearish_low_counts[daily_low_session] += 1

            # Calculate percentages
            for session_name in all_sessions:
                high_percentage = self.round_metric(
                    (bearish_high_counts[session_name] / total_bearish) * 100
                )
                low_percentage = self.round_metric(
                    (bearish_low_counts[session_name] / total_bearish) * 100
                )

                metrics[f"Bearish Daily High in {session_name} %"] = high_percentage
                metrics[f"Bearish Daily Low in {session_name} %"] = low_percentage
        else:
            # Set default values if no bearish days
            for session_name in all_sessions:
                metrics[f"Bearish Daily High in {session_name} %"] = 0.0
                metrics[f"Bearish Daily Low in {session_name} %"] = 0.0

        # Log summary
        self.logger.info("Directional Session Distribution Summary:")
        for session in all_sessions:
            bullish_high = metrics.get(f"Bullish Daily High in {session} %", 0)
            bullish_low = metrics.get(f"Bullish Daily Low in {session} %", 0)
            bearish_high = metrics.get(f"Bearish Daily High in {session} %", 0)
            bearish_low = metrics.get(f"Bearish Daily Low in {session} %", 0)
            self.logger.info(
                f"  {session}: Bullish High {bullish_high}%, Low {bullish_low}%, Bearish High {bearish_high}%, Low {bearish_low}%"
            )

        return metrics
