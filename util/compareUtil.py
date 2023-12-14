import copy
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler


def detect_mean_shift(arr1, arr2):
    mean1 = np.nanmean(arr1)
    mean2 = np.nanmean(arr2)
    return 2 * (mean1 - mean2) / (mean1 + mean2 + 1e-5)


def detect_median_shift(arr1, arr2):
    mean1 = np.nanmedian(arr1)
    mean2 = np.nanmedian(arr2)
    return 2 * (mean1 - mean2) / (mean1 + mean2 + 1e-5)


def detect_mean_shift_multi(arr1, arr2):
    mean1 = np.nanmean(arr1, axis=1)
    mean2 = np.nanmean(arr2, axis=1)
    return 2 * (mean1 - mean2) / (mean1 + mean2 + 1e-5)


def detect_median_shift_multi(arr1, arr2):
    mean1 = np.nanmedian(arr1, axis=1)
    mean2 = np.nanmedian(arr2, axis=1)
    return 2 * (mean1 - mean2) / (mean1 + mean2 + 1e-5)


def value_sensitive_normalize(arr: np.ndarray, min_quantile=0, max_quantile=0.975):
    lower = np.quantile(arr, min_quantile)
    upper = np.quantile(arr, max_quantile)
    if upper < 50:
        upper = 20 + (upper / 50) * 30
    if 110 < upper < 10000:
        upper = upper * 1.05
    elif 10000 <= upper:
        upper = upper * 1.1
    return (arr - lower) / (upper - lower + 1e-3)


def IsolationForestPredict(values, contamination=0.01):
    """false is abnormal, true is normal"""
    clf = IsolationForest(contamination=contamination, random_state=42).fit(values)
    clf_result = clf.predict(values)
    return clf_result != -1


def anormal_region_func(history_values, history_ts, contamination=0.01, isMulti=False):
    """Aperiodic time series can be treated in this way, and the data will be faltten"""
    history_values_c = copy.deepcopy(history_values)
    history_values_c[np.isnan(history_values_c)] = np.nanmedian(history_values_c)
    clf_result_up = history_values_c > np.quantile(history_values_c, 0.995)
    clf_result_down = history_values_c < np.quantile(history_values_c, 0.01)
    clf_result = clf_result_up | clf_result_down
    unanormal_values, unanormal_ts = history_values_c[~clf_result], history_ts[~clf_result]
    return unanormal_values, unanormal_ts


def normalize(arr):
    """Normalization"""
    min_max_scaler = MinMaxScaler().fit(arr)
    return min_max_scaler.transform(arr).flatten()


def disturbArr(arr):
    scale = np.random.normal(0, 1, size=(len(arr),)) / 100 + 1
    return arr * scale


def period_region_multi(history_values, history_ts, ts_min, ts_max, extra_range=600, period=86400, interval=1,
                        isPlot=False):
    """
    Delineate the time range, periodically delineate the historical data within the delineation range,
    and obtain the data of the same period
    """
    assert ts_min - ts_min + 2 * extra_range * interval < period * interval,\
        "The period period must be larger than the time series range"
    if history_values.shape[1] < 100:
        return [], [], False
    history_values[np.isnan(history_values)] = 0
    # history_idx is []
    history_ts_c = history_ts + (ts_max + extra_range * interval - history_ts) // (period * interval) * (
            period * interval)
    history_idx = np.argwhere(
        (history_ts_c >= ts_min - extra_range * interval) & (history_ts_c <= ts_max + extra_range * interval)).flatten()

    reference_valuess, reference_tss, reference_range = [], [], []
    l = 0

    for i in np.argwhere(np.diff(history_idx) != 1).flatten():
        reference_range.append([history_idx[l], history_idx[i]])
        l = i + 1
    if len(history_idx) == 0:
        return [], [], False
    reference_range.append([history_idx[l], history_idx[len(history_idx) - 1]])

    for l, r in reference_range:
        if len(history_values) != 0:
            reference_valuess.append(history_values[:, l:r - 1])
            reference_tss.append(history_ts[l:r - 1])

    if isPlot:
        plt.figure(figsize=(16, 2))
        plt.plot(history_values.T)

        for l, r in reference_range:
            if len(history_values) != 0:
                plt.vlines(l, np.min(history_values), np.max(history_values), "red")
                plt.vlines(r - 1, np.min(history_values), np.max(history_values), "red")
        plt.title("period_region_multi")
        plt.show()

    # Determine whether the data of the period is similar
    lens = len(reference_valuess)
    dis_list = []
    cycle, uncycle = True, False
    for ts1_idx in range(lens):
        ts1_c = reference_valuess[ts1_idx]
        for ts2_idx in range(ts1_idx + 1, lens):
            ts2_c = reference_valuess[ts2_idx]
            if ts1_c.shape[1] * 0.6 > ts2_c.shape[1]: continue
            min_lens = min(ts1_c.shape[1], ts2_c.shape[1])
            if min_lens <= 5: continue
            coef = np.corrcoef(ts1_c[:, :min_lens], ts2_c[:, :min_lens])
            coef = np.mean(coef[coef <= 0.99])
            dis_list.append(coef)
    cycle = True if np.nanmean(np.abs(dis_list)) > 0.4 else False

    # Multi-terminal data is randomly selected to determine whether it is periodic
    for ts_idx in range(lens):
        dis_list = []
        ts2_c = reference_valuess[ts_idx]
        for _ in range(10):
            min_lens = ts2_c.shape[1]
            ts1_idx = np.random.randint(min_lens, history_values.shape[1])
            ts1_c = history_values[ts1_idx - ts2_c.shape[1]:ts1_idx]
            if min_lens <= 5: continue
            coef = np.corrcoef(ts1_c[:, :min_lens], ts2_c[:, :min_lens])
            coef = np.mean(coef[coef <= 0.99])
            dis_list.append(coef)
        uncycle = True if np.nanmean(np.abs(dis_list)) > 0.5 and sum(np.abs(dis_list) > 0.3) > 0.9 * len(
            dis_list) else False
        if uncycle:
            break

    use_all_flag = True if uncycle or (not cycle) else False  # Whether to use global data
    return reference_valuess, reference_tss, use_all_flag


def zerofill(st, ed, values, ts, interval=1000, fillValue=0):
    """Populate the data to zero"""
    # Sort by time
    if len(values) < int(st / 60 * interval * 0.5):
        tmp_ts = list(set(range(int(st), int(ed) + 1, 60 * interval)) - set(ts))
        tmp_v = [fillValue for i in range(len(tmp_ts))]

        if isinstance(values, list) and isinstance(ts, list):
            values += tmp_v
            ts += tmp_ts
            values = np.array(values)
            ts = np.array(ts)
        else:
            values = np.append(values, tmp_v)
            ts = np.append(ts, tmp_ts)
        sort_index = np.argsort(ts)
        values, ts = values[sort_index], ts[sort_index]

    return values, ts

