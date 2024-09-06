import pandas as pd


def get_times(signal1: pd.Series, signal2: pd.Series, list_signals=None, return_extra=False):
    """_summary_

    Args:
        signal1 (pd.Series): _description_
        signal2 (pd.Series): _description_
    """
    start_date = get_start_date(signal1, signal2, list_signals)
    end_date = get_start_date(signal1, signal2, list_signals)
    freq = get_freq(signal1, signal2)
    times = pd.date_range(start=start_date, end=end_date, freq=freq)
    if return_extra:
        return times, freq, start_date, end_date
    return times


def get_start_date(signal1: pd.Series, signal2: pd.Series, list_signals=None):
    """Return lowest starting date

    Args:
        signal1 (pd.Series): _description_
        signal2 (pd.Series): _description_
        list_signals (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    if list_signals is None:
        signal1 = sanitize_index(signal1)
        signal2 = sanitize_index(signal2)
        return min(signal1.index[0], signal2.index[0])
    out = None
    for signal in list_signals:
        signal = sanitize_index(signal)
        if out is None:
            out = signal.index[0]
        else:
            if signal.index[0] < out:
                out = signal.index[0]
    return out


def get_end_date(signal1: pd.Series, signal2: pd.Series, list_signals=None):
    if list_signals is None:
        signal1 = sanitize_index(signal1)
        signal2 = sanitize_index(signal2)
        return max(signal1.index[-1], signal2.index[-1])
    out = None
    for signal in list_signals:
        signal = sanitize_index(signal)
        if out is None:
            out = signal.index[-1]
        else:
            if signal.index[-1] > out:
                out = signal.index[-1]
    return out


def get_freq(signal1: pd.Series, signal2: pd.Series, list_signals=None):
    if list_signals is None:
        signal1 = sanitize_index(signal1)
        signal2 = sanitize_index(signal2)
        freq1 = pd.infer_freq(signal1)
        freq2 = pd.infer_freq(signal1)
        freq1_min = get_freq_min(freq1)
        freq2_min = get_freq_min(freq2)
        return freq1 if freq1_min < freq2_min else freq2
    freq = None
    for signal in list_signals:
        signal = sanitize_index(signal)
        if freq is None:
            freq = pd.infer_freq(signal)
            freq_min = get_freq_min(freq)
        else:
            freq_ = pd.infer_freq(signal)
            freq_min_ = get_freq_min(freq)
            if freq_min_ < freq_min:
                freq = freq_
                freq_min = freq_min_
    return freq


def get_freq_min(freq):
    return (
        pd.to_timedelta(
            pd.tseries.frequencies.to_offset(freq)
        ).total_seconds()
        / 60
    )


def get_continuous_ts(df, times):
    df_times = pd.DataFrame(index=times)
    df = df[~df.index.duplicated(keep='first')]
    df = pd.concat([df_times, df], axis=1)
    df = df.loc[df_times.index[0]:df_times.index[-1]]

    df.index = df.index.rename('TS')
    return df


def sanitize_index(signal: pd.Series):
    signal = signal.loc[~signal.index.isna()]
    if signal.empty:
        raise ValueError('Signal did not contain any index')
    if not isinstance(signal.index[0], pd.Timestamp):
        raise ValueError('Signal index are not pd.Timestamp')
    return signal.sort_index()
