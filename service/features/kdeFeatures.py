from scipy import stats
from util.compareUtil import *


def get_anormalValue_scores_multi(change_select_values, change_select_ts, history_values, history_ts, extra_range=300,
                                  interval=1000, alg_kargs={}, isPlot=False):
    """Select appropriate data for calculation based on periodic properties"""
    period_valuess, period_tss, use_all_flag = period_region_multi(
        history_values, history_ts,
        change_select_ts[0], change_select_ts[-1],
        extra_range=extra_range, interval=interval, isPlot=isPlot
    )
    # data preparation
    refer_x_lens, refer_y_lens = history_values.shape
    empty_array = [[] for i in range(refer_x_lens)]
    refer_values = np.array(empty_array)
    for period_values in period_valuess:
        """If there are a small number of null values, perform simple filling processing"""
        if np.isnan(period_values).sum() <= 0.1 * period_values.shape[1]:
            period_values[np.isnan(period_values)] = np.nanmean(period_values)
        else:
            continue
        if period_values.shape[1] < 10:
            continue
        refer_values = np.append(refer_values, period_values, axis=1)

    history_refer_values = np.mean(history_values, axis=0)

    # 计算特征
    if history_values.shape[1] > 10:
        anormal_history_values, anormal_history_ts = anormal_region_func(history_refer_values, history_ts,
                                                                         contamination=0.001, isMulti=True)
    else:
        anormal_history_values, anormal_history_ts = np.array([[]]), np.array([[]])

    anormal_scores = [[2] for i in range(refer_x_lens)]
    if not use_all_flag and refer_values.shape[1] > 5:
        anormal_scores = []
        """Loop to obtain the abnormal score of kde"""
        for refer_value, change_select_value in zip(refer_values, change_select_values):
            if refer_value[refer_value != 0].shape[0] > 5:
                kdeFeatures = KDEFeatures()
                anormal_score = kdeFeatures.getKdeScoresSingle(change_select_value, refer_value[refer_value != 0])

            else:
                anormal_score = [2] * len(change_select_values)
            anormal_scores.append(anormal_score)

    """The default sigma score is zero"""
    unall_sigma_scores, all_sigma_scores = [[0] for i in range(refer_x_lens)], [[0] for i in range(refer_x_lens)]
    if refer_values.shape[0] > 5:
        unall_sigma_scores = np.abs(change_select_values - np.mean(refer_values)) / (np.std(refer_values) + 1)

    if anormal_history_values.shape[0] > 5:
        all_sigma_scores = np.abs(change_select_values - np.mean(anormal_history_values)) / (
                    np.std(anormal_history_values) + 1)

    """Merge the information and take the one with the larger sigma anomaly score"""
    sigma_scores = np.where(np.max(unall_sigma_scores) >= np.max(all_sigma_scores), unall_sigma_scores,
                            all_sigma_scores)
    sigma_scores = np.mean(sigma_scores, axis=1) if len(sigma_scores) > 0 else [0] * refer_x_lens
    return anormal_scores, sigma_scores


class KDEModelNotReady(Exception): pass


class KDEFeatures:

    def __init__(self, ):
        pass

    def getFeaturesSingle(self, detect_values, reference_values):
        return {"kde_scores": self.getKdeScoresSingle(detect_values, reference_values)}

    def getFeaturesMulti(self, detect_values, reference_values):
        return {"kde_scores": self.getKdeScoresMulti(detect_values, reference_values)}

    def getKdeScoresSingle(self, detect_values, reference_values):
        """Train a kde model and detect a single time series"""
        try:
            if len(detect_values) == 0 or len(reference_values) == 0: return [-1]

            arr, detect_values = self.listToArray(detect_values, reference_values)
            """Filter out continuous deviation points and maximum deviation points"""
            arr = self.outlierFilter(arr)
            step = self.getStep(arr)
            """Perturb the original data"""
            values_c, arr_c = self.disturb(detect_values, arr, step)
            """Solve kde fraction"""
            if len(arr) <= 1 or len(set(arr)) <= 1: return [-1]
            d_score = self.kdeDetect(values_c, arr_c)
            return d_score

        except np.linalg.LinAlgError:
            raise KDEModelNotReady()

    def getKdeScoresMulti(self, detect_values, reference_values):
        """Train a kde model and loop through the detection matrix data"""
        try:
            if len(detect_values) == 0 or len(reference_values) == 0: return [[-1]]
            arr, detect_valuess = self.listToArray(detect_values, reference_values)
            """Filter out continuous deviation points and maximum deviation points"""
            arr = self.outlierFilter(arr)
            step = self.getStep(arr)
            """Loop detection kde score"""
            d_scores = []
            for values in detect_valuess:
                """Perturb the original data"""
                values_c, arr_c = self.disturb(values, arr, step)
                if len(arr_c) <= 1 or len(set(arr_c)) <= 1:
                    d_score = [-1]
                else:
                    d_score = self.kdeDetect(values_c, arr_c)
                d_scores.append(d_score)
            return d_scores

        except np.linalg.LinAlgError:
            raise KDEModelNotReady()

    def listToArray(self, detect_values, reference_values):
        arr = np.array(reference_values) if isinstance(reference_values, list) else reference_values
        values = np.array(detect_values) if isinstance(detect_values, list) else detect_values
        """Specifically for the situation where 0 exists in the success rate reference data"""
        if np.sum(arr == 0) < len(arr) * 0.1: arr = arr[arr != 0]
        return arr, values

    def outlierFilter(self, arr):
        """
        Due to the short-term mutation points in historical data, year-on-year failure will occur.
        If the deviation points are removed, the same period in history will result.
        """
        coef1 = 0.98 if len(arr) > 500 else 0.85  # Points to be filtered need to consider continuity
        coef2 = 0.98 if len(arr) > 500 else 0.95  # Explicit points to be eliminated
        outlier_point = np.where(arr > np.quantile(arr, coef1))[0]
        outlier_idx = np.array([True] * len(arr))
        outlier_list = (np.where(arr > np.quantile(arr, coef2))[0]).tolist()
        if len(outlier_point) >= 2:
            left = outlier_point[0]
            tmp, cnt = [left], 0
            for right in outlier_point[1:]:
                if right - left <= 2:
                    cnt += 1
                    tmp.append(right)
                else:
                    if cnt <= 10:
                        outlier_list.extend(tmp)
                    cnt = 1
                    tmp = [right]
                left = right
            if cnt <= 10:
                outlier_list.extend(tmp)
        """Eliminate non-continuous outliers"""
        outlier_idx[outlier_list] = False

        arr = arr[outlier_idx]
        return arr

    def getStep(self, arr):
        median = np.median(arr)
        return (median or 1) * 0.01

    def disturb(self, detect_values, refer_values, step):
        """Slightly perturb the data"""
        # Disturbance
        values, arr = detect_values + step, refer_values + step
        # Disturbance
        arr = disturbArr(refer_values)
        # Normalized
        lower, upper = np.quantile(arr, 0), np.quantile(arr, 0.975)
        arr = (arr - lower) / (upper - lower + 1e-2) + 1
        values = (values - lower) / (upper - lower + 1e-2) + 1
        return values, arr

    def kdeDetect(self, detect_values, refer_values):
        m = stats.gaussian_kde(refer_values, bw_method="silverman")
        percentile = m.evaluate(detect_values) + 0.000000001
        bw = (len(refer_values) * 3 / 4.) ** (-1. / 5)
        th = - np.log10(bw / 100) * 2.
        d_score = - np.log10(percentile) - th
        d_score[d_score <= 0] = 0
        return d_score
