import pandas as pd
import numpy as np
import timestamp


def time_lag_pair(signal_ref, signal_eval, max_lag=4, freq="1min"):
    """Calculates the time lag between two Pandas dataframes of time series
    data by finding the time offset that maximizes the correlation R2. Requires
    two DataFrames, indexed by time, with overlapping timestamps. Matching is
    done within the function.

    Parameters
    ----------
    df: DataFrame
        Pandas DataFrame indexed by date-time, with two columns of data
        (assumed to be the same type of measurement, each from a different
        mast).

    Returns
    -------
    lag: integer
        Number of time steps to apply to df2 to minimize lag with df1. NaN
        indicates insufficient overlapping data for a correlation.
    r2before: float
        R-squared value of a correlation between df1 and df2 before the time
        offset is applied. NaN indicates insufficient overlapping data for a
        correlation.
    r2after: float
        R-squared value of a correlation between df1 and df2 after the time
        offset is applied. NaN indicates insufficient overlapping data for a
        correlation.
    r2benefit: float
        R-squared benefit of applying the suggested lag. NaN indicates
        insufficient overlapping data for a correlation.
    """

    times, freq, _, _ = timestamp.get_times(
        signal_ref, signal_eval, return_extra=True)

    # interal parameters of algorithm
    df = pd.concat([signal_ref, signal_eval], axis=1)
    df = timestamp.get_continuous_ts(df, times)
    xmax = df[df.columns[0]].quantile(0.995)
    ymax = df[df.columns[1]].quantile(0.995)
    slope = ymax / xmax
    tol = 8
    rangex = 4

    freq_min = timestamp.get_freq_min(freq)
    max_lag = int(max_lag * 60 / freq_min)

    df = df.resample(freq).mean().interpolate(method="polynomial", order=2)
    dfshifted = df.copy()

    if len(df) > 0 and not (np.isnan(df.corr().iloc[0, 1] ** 2)):
        df_clean = df[
            (df[df.columns[1]] > (slope * df[df.columns[0]] - ymax / tol))
            & (df[df.columns[1]] < (slope * df[df.columns[0]] + ymax / tol))
        ]
        r2before = df_clean.corr().iloc[0, 1] ** 2

        r2lagged = [0.0 for i in range(-max_lag, max_lag, 1)]

        for offset in range(-max_lag, max_lag, 1):
            dfshifted.iloc[:, 1] = df.iloc[:, 1].shift(offset)
            dfshifted_clean = dfshifted[
                (
                    dfshifted[dfshifted.columns[1]]
                    > (slope * dfshifted[dfshifted.columns[0]] - ymax / tol)
                )
                & (
                    dfshifted[dfshifted.columns[1]]
                    < (slope * dfshifted[dfshifted.columns[0]] + ymax / tol)
                )
                & (dfshifted[dfshifted.columns[0]] > xmax / rangex)
                & (dfshifted[dfshifted.columns[0]] < xmax - (xmax / rangex))
            ]
            r2lagged[offset + max_lag] = dfshifted_clean.corr().iloc[0, 1] ** 2

        r2after = max(r2lagged)
        r2benefit = r2after - r2before
        lag = -max_lag + r2lagged.index(r2after)

    else:
        lag = np.nan
        r2before = np.nan
        r2after = np.nan
        r2benefit = np.nan
    if freq_min == 15:
        lag = lag / 4
    if freq_min == 5:
        lag = lag / 12
    if freq_min == 1:
        lag = lag / 60
    return lag * 60, r2before, r2after, r2benefit


def shift_hourly_min(df, lag, freq_min=1, initial_freq_min=15):
    """
    lag in hours (0.5 equals 30min)
    """

    if freq_min == 15:
        shifts = lag / 60 * 4
    if freq_min == 5:
        shifts = lag / 60 * 12
    if freq_min == 1:
        shifts = lag / 60 * 60

    freq = get_freq_str(freq_min)
    initial_freq = get_freq_str(initial_freq_min)

    resampled_data = (
        df.resample(freq).mean().fillna(
            method="ffill").fillna(method="bfill")
    )
    shifted_data = resampled_data.shift(int(shifts))
    shifted_data = (
        shifted_data.resample(initial_freq).mean().fillna(
            method="ffill").fillna(method="bfill")
    )

    return shifted_data


def get_freq_str(freq_min):

    if freq_min < 60:
        return f'{freq_min}T'
    elif freq_min == 60:
        return 'H'
    elif freq_min % 60 == 0:
        return f'{freq_min // 60}H'
    elif freq_min % (24 * 60) == 0:
        return f'{freq_min // (24 * 60)}D'
    else:
        return f'{freq_min}T'
