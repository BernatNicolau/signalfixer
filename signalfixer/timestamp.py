import pandas as pd
from typing import Union, List


def get_times(signal: Union[pd.Series, pd.DataFrame, List[pd.Series], List[pd.DataFrame]], return_extra=False):
    """_summary_

    Args:
        signal (Union[pd.Series, pd.DataFrame, List[pd.Series], List[pd.DataFrame]]): Signal or list of Signals. Signal can be pd.Series or pd.DataFrame.
        return_extra (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    start_date = get_start_date(signal)
    end_date = get_start_date(signal)
    freq = get_freq(signal)
    times = pd.date_range(start=start_date, end=end_date, freq=freq)
    if return_extra:
        return times, freq, start_date, end_date
    return times


def get_start_date(signal: Union[pd.Series, pd.DataFrame, List[pd.Series], List[pd.DataFrame]]):
    """Return lowest starting date

    Args:
        signal (pd.Series): _description_

    Returns:
        _type_: _description_
    """

    out = None
    if (isinstance(signal, pd.Series)) or (isinstance(signal, pd.DataFrame)):
        signal = sanitize_index(signal)
        if out is None:
            out = signal.index[0]
        else:
            if signal.index[0] < out:
                out = signal.index[0]

    for signal_ in signal:
        signal_ = sanitize_index(signal_)
        if out is None:
            out = signal_.index[0]
        else:
            if signal_.index[0] < out:
                out = signal_.index[0]
    return out


def get_end_date(signal: Union[pd.Series, pd.DataFrame, List[pd.Series], List[pd.DataFrame]]):
    out = None
    if (isinstance(signal, pd.Series)) or (isinstance(signal, pd.DataFrame)):
        signal = sanitize_index(signal)
        if out is None:
            out = signal.index[-1]
        else:
            if signal.index[-1] > out:
                out = signal.index[-1]
    else:
        for signal_ in signal:
            signal_ = sanitize_index(signal_)
            if out is None:
                out = signal_.index[-1]
            else:
                if signal_.index[-1] > out:
                    out = signal_.index[-1]
    return out


def get_freq(signal: Union[pd.Series, pd.DataFrame, List[pd.Series], List[pd.DataFrame]]):

    out = None
    freq_min_ref = None
    if (isinstance(signal, pd.Series)) or (isinstance(signal, pd.DataFrame)):
        signal = sanitize_index(signal)
        freq = pd.infer_freq(signal)
        freq_min = get_freq_min(freq)
        if out is None:
            out = freq
            freq_min_ref = freq_min
        else:
            if freq_min < freq_min_ref:
                out = freq
                freq_min_ref = freq_min
    else:
        for signal_ in signal:
            signal_ = sanitize_index(signal_)
            freq = pd.infer_freq(signal_)
            freq_min = get_freq_min(freq)
            if out is None:
                out = freq
                freq_min_ref = freq_min
            else:
                if freq_min < freq_min_ref:
                    out = freq
                    freq_min_ref = freq_min
    return out


def get_freq_min(freq):
    return (
        pd.to_timedelta(
            pd.tseries.frequencies.to_offset(freq)
        ).total_seconds()
        / 60
    )


def get_continuous_ts(signal: Union[pd.Series, pd.DataFrame]):
    """Ensures continuous index

    Args:
        df (pd.DataFrame): _description_
        times (pd.Series): _description_

    Returns:
        pd.Series: _description_
    """
    times = get_times(signal)
    df_times = pd.DataFrame(index=times)
    signal = signal[~signal.index.duplicated(keep='first')]
    signal = pd.concat([df_times, signal], axis=1)
    signal = signal.loc[df_times.index[0]:df_times.index[-1]]

    return signal


def sanitize_index(signal: Union[pd.Series, pd.DataFrame]):
    """Removes NaN and sorts index

    Args:
        signal (pd.Series): Index must be pd.Timestamp

    Raises:
        ValueError: Signal did not contain any index
        ValueError: Signal index are not pd.Timestamp

    Returns:
        pd.Series: Same input with sanitized index
    """
    signal = signal.loc[~signal.index.isna()]
    if signal.empty:
        raise ValueError('Signal did not contain any index')
    if not isinstance(signal.index[0], pd.Timestamp):
        raise ValueError('Signal index are not pd.Timestamp')
    return signal.sort_index()
