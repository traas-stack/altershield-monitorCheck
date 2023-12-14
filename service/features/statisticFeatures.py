from util.compareUtil import *
from config import CONFIG


class StatisticFeaturesMulti:

    def __init__(self, ):
        pass

    def getFeaturesMulti(self, detect_values, refer_values, field, referLength=100, max_quantile=0.995, extra_range=300,
                         interval=1000, alg_kargs={}, isIsoforest=False, isTest=False):
        """Change timing characteristics obtained from fixed data"""
        min_quantile = 0 if field in ["count", "fail", "cost"] else 0.05
        upOrDown = CONFIG.FIELD_UP_OR_DOWN.get(field, "upDown")
        """Isolated forests are extremely time-consuming and need to be adjusted to simple statistical methods"""
        iso_flags = self.getIsoforestFeaturesMulti(refer_values, detect_values, alg_kargs, isIsoforest)
        """Filter values with large deviations"""
        refer_values, notzero_refer_values = self.deleteOutlierMulti(refer_values, field, min_quantile, max_quantile,
                                                                     alg_kargs)
        # The proportion of data that is zero
        zero_ratio = self.getZeroRatioFeaturesMulti(detect_values, refer_values)
        # Analyze deviations
        detect_results = self.getOutilerFeaturesMulti(detect_values, refer_values, notzero_refer_values, max_quantile,
                                                      min_quantile, upOrDown, alg_kargs)
        # Analyze volatility
        std_socres, sigma_coef = self.getStdFeaturesMulti(detect_values, refer_values, referLength, upOrDown, alg_kargs)
        # Judging the degree of recovery based on the degree of volatility
        shake_level, shake_thres = self.getShakeFeaturesMulti(std_socres, sigma_coef, alg_kargs)
        # Water level changes
        median_shift, trends = self.getMeanShiftFeaturesMulti(detect_values, refer_values, alg_kargs)
        mean_level = self.getMeanLevelFeaturesMulti(detect_values, alg_kargs)
        mean_level_before = np.mean(refer_values, axis=1)
        mean_level_after = np.max(detect_values, axis=1)
        mean_level_change = mean_level_after / np.where(mean_level_before > 10, mean_level_before, 10)
        mean_level_change = np.where(mean_level_change > 1, mean_level_change - 1, 1 - mean_level_change)
        # Threshold feature
        thresh_flags = self.getThreshFeaturesMulti(detect_values, refer_values, field, alg_kargs)
        # Find the index of the first exception
        abnormal_idxs = np.argmax(std_socres >= 3, axis=1)
        return {
            "std_socres": std_socres,
            "std_mean": np.mean(std_socres[:, -5:], axis=1),
            "sigma_coef": sigma_coef,
            "shake_thres": shake_thres,
            "shake_level": shake_level,
            "median_shift": median_shift,
            "mean_level": mean_level,
            "zero_ratio": zero_ratio,
            "detect_results": detect_results,
            "trends": trends,
            "iso_flags": iso_flags,
            "thresh_flags": thresh_flags,
            "detect_values": detect_values,
            "refer_values": refer_values,
            "mean_level_before": mean_level_before,
            "mean_level_after": mean_level_after,
            "mean_level_change": mean_level_change,
            "cpu_lower_flags": self.isCpuLower(detect_values, field),
            "successPercent_higher_flags": self.isSuccessPercentHigher(detect_values, field),
            "total_smaller_flags": self.isTotalSmaller(detect_values, field),
            "field": field,
            "abnormal_idxs": abnormal_idxs
        }

    def getIsoforestFeaturesMulti(self, refer_values, detect_values, alg_kargs, isIsoforest=False):
        """
        Returns the characteristic information provided by the isolated forest, false means abnormal, true means normal

        Isolated forest detection: Reference data window, detection window, threshold, last point number do not deviate,
        number of abnormal points
        """
        iso_params = alg_kargs.get("iso_params", [100, 5, 0.05, 1, 4])
        iso_scores = [[False, False, False, False, False, False, ] for i in refer_values]
        if isIsoforest:
            iso_scores = IsolationForestPredict(np.append(refer_values, detect_values, axis=0), )
            iso_scores = iso_scores[-iso_params[1]:]
        return iso_scores

    def getMeanShiftFeaturesMulti(self, detect_values, refer_values, alg_kargs):
        """Returns the average degree of deviation"""
        median_shift_params = alg_kargs.get("median_shift_params", [100, 5, 0.5])
        median_shift = detect_mean_shift_multi(detect_values[:, -median_shift_params[1]:], refer_values)
        trends = np.where(median_shift >= 0, "up", "down")
        median_shift = abs(median_shift)
        return median_shift, trends

    def getMeanLevelFeaturesMulti(self, detect_values, alg_kargs):
        """Return average water level"""
        meanlevel_params = alg_kargs.get("meanlevel_params", [100, 5, 1.5])
        mean_level = np.mean(detect_values[:, -meanlevel_params[1]:], axis=1)
        return mean_level

    def deleteOutlierMulti(self, refer_values, field, min_quantile, max_quantile, alg_kargs):
        """Filter values with large deviations"""
        change_window = alg_kargs.get("change_window", 5)
        control_detect_flag = alg_kargs.get("control_detect_flag", False)
        quantile_min, quantile_max = np.quantile(refer_values, min_quantile), np.quantile(refer_values, max_quantile)
        sparse_flag = np.sum(np.all(refer_values == 0, axis=0)) > 0.7 * refer_values.shape[1]
        """Only when the indicators are sparse and not count can the 0-picking process be performed."""
        if sparse_flag and field != "count":
            notzero_refer_values = refer_values[:, np.all(refer_values != 0, axis=0)]
            notzero_refer_values = refer_values if notzero_refer_values.shape[1] == 0 else notzero_refer_values
        else:
            notzero_refer_values = refer_values
        refer_mean = np.mean(refer_values)
        refer_values_c = np.where(refer_values > quantile_max, refer_mean, refer_values)
        refer_values_c = np.where(refer_values_c < quantile_min, refer_mean, refer_values)
        # Prevent the last few points of the control group from being replaced
        refer_values_c[:, -change_window:] = refer_values[:, -change_window:]
        return refer_values, notzero_refer_values

    def getOutilerFeaturesMulti(self, detect_values, refer_values, notzero_refer_values, max_quantile, min_quantile,
                                upOrDown="upDown", alg_kargs={}):
        """Values with larger deviations are false"""
        outiler_points = 5
        notzero_refer_values_lens = len(notzero_refer_values[0])
        multi_quantile_params = alg_kargs.get("multi_quantile_params",
                                              [100, 4, 2, 0.99, 0.05])
        control_detect_flag = alg_kargs.get("control_detect_flag", False)
        if control_detect_flag:
            quantile_max_axis, quantile_min_axis = np.max(refer_values, axis=1), np.min(refer_values, axis=1)
        else:
            max_quantile, min_quantile = multi_quantile_params[3], multi_quantile_params[4]
            quantile_max_axis1, quantile_min_axis1 = np.quantile(refer_values, max_quantile, axis=1), np.quantile(
                refer_values, min_quantile, axis=1)
            quantile_max_axis2, quantile_min_axis2 = np.quantile(notzero_refer_values, np.max(
                [0.5, max_quantile - outiler_points / notzero_refer_values_lens]), axis=1), np.quantile(
                notzero_refer_values, min_quantile, axis=1)
            quantile_max_axis, quantile_min_axis = np.max([quantile_max_axis1, quantile_max_axis2], axis=0), np.min(
                [quantile_min_axis1, quantile_min_axis2], axis=0)

        """The true value of detect_result indicates normal"""
        if upOrDown == "up":
            detect_results = (detect_values.T <= quantile_max_axis).T
        elif upOrDown == "down":
            detect_results = (detect_values.T >= quantile_min_axis).T
        else:
            detect_results = ((detect_values.T <= quantile_max_axis) & (
                    detect_values.T >= quantile_min_axis)).T

        return detect_results

    def getStdFeaturesMulti(self, detect_values, refer_values, referLength=100, upOrDown="upDown", alg_kargs={}):
        """Returns the multiple and volatility of the standard deviation"""
        control_detect_flag = alg_kargs.get("control_detect_flag", False)
        change_window = alg_kargs.get("change_window", 5)
        refer_values_c = refer_values[:, -change_window:] if control_detect_flag else refer_values
        refer_mean, refer_std = np.mean(refer_values_c, axis=1), np.std(refer_values_c, axis=1)
        detect_mean, detect_std = np.nanmean(detect_values, axis=1), np.std(detect_values, axis=1)
        floor = np.where(refer_mean * 0.1 > 1, 1, detect_mean * 0.05 + 0.01)
        refer_mean, refer_std = np.nanmean(refer_values_c[:, -referLength:], axis=1), np.std(
            refer_values_c[:, -referLength:], axis=1)
        if upOrDown == "up":
            std_socres1 = (detect_values - refer_mean[:, np.newaxis]) / (
                    refer_std[:, np.newaxis] + floor[:, np.newaxis])
            std_socres1 = np.where(std_socres1 > 0, std_socres1, 0)
            std_socres2 = (detect_values - refer_mean[:, np.newaxis]) / (
                    refer_std[:, np.newaxis] + floor[:, np.newaxis])
            std_socres2 = np.where(std_socres2 > 0, std_socres2, 0)
        elif upOrDown == "down":
            std_socres1 = (detect_values - refer_mean[:, np.newaxis]) / (
                    refer_std[:, np.newaxis] + floor[:, np.newaxis])
            std_socres1 = np.abs(np.where(std_socres1 < 0, std_socres1, 0))
            std_socres2 = (detect_values - refer_mean[:, np.newaxis]) / (
                    refer_std[:, np.newaxis] + floor[:, np.newaxis])
            std_socres2 = np.abs(np.where(std_socres2 < 0, std_socres2, 0))
        else:
            std_socres1 = np.abs(detect_values - refer_mean[:, np.newaxis]) / (
                    refer_std[:, np.newaxis] + floor[:, np.newaxis])
            std_socres2 = np.abs(detect_values - refer_mean[:, np.newaxis]) / (
                    refer_std[:, np.newaxis] + floor[:, np.newaxis])
        std_socres = np.min(np.concatenate([std_socres1[:, np.newaxis, ], std_socres2[:, np.newaxis]], axis=1), axis=1)
        sigma_coef = refer_mean / (refer_std + floor)
        return std_socres, sigma_coef

    def getShakeFeaturesMulti(self, std_scores, sigma_coef, alg_kargs={}):
        """
        Return to recovery level
        The recovery super parameters are obtained based on the degree of fluctuation.
        """
        #
        shake_params = alg_kargs.get("shake_params", [0.85, 0.7, 0.5, 0.1])
        sigma_coef_log = (shake_params[2] + np.log10(sigma_coef) * 0.1)
        sigma_coef_log_max = np.where(sigma_coef_log <= shake_params[1], shake_params[1], sigma_coef_log)
        shake_thres = np.where(sigma_coef_log_max <= shake_params[0], sigma_coef_log_max, shake_params[0])
        # The degree of recovery is judged by the fluctuation score
        shake_level = (np.max(std_scores, axis=1)[:, np.newaxis] - std_scores)[-1] / (
                np.max(std_scores, axis=1)[:, np.newaxis] + 1)
        return shake_level, shake_thres

    def getZeroRatioFeaturesMulti(self, detect_values, refer_values):
        """Returns the ratio of the value zero"""
        refer_x_lens, refer_y_lens = refer_values.shape
        detect_x_lens, detect_y_lens = detect_values.shape
        zero_ratio = (np.sum(detect_values == 0, axis=1) + np.sum(refer_values == 0, axis=1)) / (
                refer_y_lens + detect_y_lens)
        return zero_ratio

    def isSuccessPercentHigher(self, detect_values, field):
        """
        Determine whether the success rate indicator is greater than 95, which is used to trigger other conditions.
        """
        successHigherFlag = [False for _ in detect_values]
        if field == "successPercent":
            successHigherFlag = np.sum(detect_values[:, -5:] >= 95, axis=1) >= 3
        return successHigherFlag

    def isTotalSmaller(self, detect_values, field):
        """Determine whether the flow rate is less than 20 for triggering other logic"""
        smallerFlag = [False for _ in detect_values]
        if field == "total":
            smallerFlag = np.sum(detect_values[:, -5:] <= 20, axis=1) >= 3
        return smallerFlag

    def isCpuLower(self, detect_values, field):
        """Determine whether the cpu is less than 60 for triggering other logic"""
        cpuLowerFlag = [False for _ in detect_values]
        if field == "cpu_util":
            # detect_values_mean = np.mean(detect_values, axis=0)
            cpuLowerFlag = np.sum(detect_values[:, -5:] <= 60, axis=1) >= 3
        return cpuLowerFlag

    def getThreshFeaturesMulti(self, detect_values, refer_values, field, alg_kargs):
        """
        Noise reduction for specific fields, for multi-dimensional arrays, only for the same indicators
        """
        metric_name_threes = {
            "fail": [15, 0.1, 0, 5],
            "successPercent": [95, 0.07, 1, 5],
            "count": [10, 0.1, 0, 5],
            "cost": [50, 0.1, 0, 3],
            "total": [10, 0.1, 1, 5],
            "load_load1": [20, 0.1, 0, 5],
            "load_load15": [20, 0.1, 0, 5],
            "rcpu_util": [20, 0.1, 0, 5],
            "cpu_util": [20, 0.1, 0, 5],
            "success": [10, 0.1, 0, 5],
            "fgc_count": [10, 0.1, 0, 5],
            "ygc_count": [10, 0.1, 0, 3],
            "ygc_time": [20, 0.1, 0, 3],
            "fgc_time": [20, 0.1, 0, 3],
            "tcp_retran": [3, 0.1, 0, 3],
            "pcsw_cswch": [10, 0.1, 0, 3],
            "pcsw_curtsk": [10, 0.1, 0, 3],
            "limitFlow": [100, 0.1, 0, 3]
        }
        metric_name_threes = alg_kargs.get("metricname_params", metric_name_threes)
        meanlevel_params = alg_kargs.get("meanlevel_params", [100, 5, 1.5])
        level_thresh = meanlevel_params[2]

        thresh = metric_name_threes.get(field, [10, 0.1, 0, 3])
        median_shift_thresh = thresh[1]
        detect_windows = thresh[3]
        median_shift = detect_median_shift_multi(detect_values[:, -detect_windows:], refer_values)
        median_shift = np.abs(median_shift)
        median_level = np.mean(detect_values[:, -detect_windows:], axis=1) / np.where(
            np.median(refer_values, axis=1) >= np.median(detect_values, axis=1) * 0.1, np.median(refer_values, axis=1),
            np.median(detect_values, axis=1) * 0.1)

        threshFlags = [False for i in median_shift]
        # If total is increasing, no alarm will be issued
        if field == "total" and (median_shift > 0).all():
            threshFlags = [True for i in median_shift]

        """
        The water level is less than the water level change threshold 
        or
        The last two points are both less than the alarm threshold
        or 
        The current value multiple is less than the multiple threshold
        """
        if thresh[2] == 0:
            threshFlags = (median_shift <= median_shift_thresh) | (
                    (detect_values[:, -2:] <= thresh[0]).all(axis=1) | (median_level <= level_thresh))
        elif thresh[2] == 1:
            threshFlags = (median_shift <= median_shift_thresh) | ((detect_values[:, -2:] > thresh[0]).all(axis=1))

        return threshFlags
