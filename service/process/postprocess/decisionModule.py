import numpy as np
from loguru import logger

from service.process.postprocess.bizUtil import anormalInfo2msg


class DecisionModule:
    def __init__(self, ):
        pass

    def isSingleAnormal(self, features, alg_kargs):
        """false is abnormal, true is normal"""
        detect_values = features.get("detect_values", np.array([20, 20, 20, 20]))
        field = features.get("field", "default")
        env = features.get("env", "default")
        oslens = features.get("oslens", 1)
        std_scores = features.get("std_scores", [4])
        std_score = np.mean(std_scores[-5:])
        sigma_coef = features.get("sigma_coef", 0.1)
        shake_thres = features.get("shake_thres", 2)
        kde_scores = features.get("kde_scores", [4])
        iso_flags = features.get("iso_flags", [])
        detect_result = features.get("detect_result", [])
        thresh_flag = features.get("thresh_flag", False)
        needShakeFlag = alg_kargs.get("needShakeFlag", True)
        needTotalZeroFlag = alg_kargs.get("needTotalZeroFlag", True)

        # Determine the degree of the drop of zero
        totalZeroFlag = self.totalZeroByOSAndEnv(detect_values, field, env, alg_kargs, oslens)
        totalZeroFlag &= needTotalZeroFlag
        # Judgment analysis is performed based on KDE values
        value_flag = np.mean(kde_scores) >= 0 and (
                np.mean(kde_scores[-5:]) < 0.8 or np.mean(kde_scores[-2:]) < 0.7)
        # Judgment analysis is carried out by whether it falls back or not
        shake_flag = (np.max(std_scores) - std_scores)[-1] > shake_thres * np.max(std_scores)
        shake_flag &= needShakeFlag
        # When judging the comparison of scores with thresholds
        long_std_params = alg_kargs.get("long_std_params", [100, 5, 2.5, 2, 3])

        anormal_points_flag = (std_scores[0] != 4) and self.abnormalPointsByThreshWindows(std_scores,
                                                                                          long_std_params[1],
                                                                                          long_std_params[2],
                                                                                          long_std_params[4])
        unanormal_pointus_flag = (std_scores[0] != 4) and self.unabnormalPointsByThreshWindows(std_scores,
                                                                                               long_std_params[3],
                                                                                               long_std_params[2])
        # If the scores are true
        multi_quantile_params = alg_kargs.get("multi_quantile_params",
                                              [100, 5, 3, 0.99, 0.05])
        isoFlag = self.abnormalPointsByWindows(detect_result, multi_quantile_params[1], multi_quantile_params[2]) | \
                  self.abnormalPointsByWindows(iso_flags, multi_quantile_params[1], multi_quantile_params[2])
        """
        Isolated forest detection. The reference data window, detection window, threshold, 
        and last point are not deviated, and the number of abnormal points is not deviated
        """
        iso_params = alg_kargs.get("iso_params", [100, 5, 0.05, 3, 4])
        isoFlag2 = field in ("cost", "total", "fail", "count") and (
            np.all(iso_flags[-(iso_params[3] + 3):]))
        # Judgment of the degree of fluctuation
        sigma_params = alg_kargs.get("sigma_params", [1, 2])
        sigma_flag = np.abs(std_score) < sigma_params[1] + 1 * np.log10(max(sigma_coef, sigma_params[0]))

        return shake_flag | value_flag | sigma_flag | thresh_flag | anormal_points_flag | unanormal_pointus_flag | isoFlag | isoFlag2

    def isSingleAnormalMulti(self, features, alg_kargs):
        std_scores = features.get("std_socres", [[10]])
        sigma_coefs = features.get("sigma_coef", [0.1])
        median_shifts = features.get("median_shift", [999])
        mean_levels = features.get("mean_level", [10])
        threshFlags = features.get("thresh_flags", [False])
        detect_results = features.get("detect_results", [[False]])
        std_long_coefs = features.get("std_long_scores", [0.1 for i in detect_results])
        kde_long_scores = features.get("kde_long_scores", [[10] for i in detect_results])
        kde_scores = features.get("kde_scores", [[10] for i in detect_results])
        mean_levels_before = features.get("mean_level_before", [10])
        zero_ratios = features.get("zero_ratio", [0 for i in detect_results])
        successPercent_higher_flags = features.get("successPercent_higher_flags", [False for i in detect_results])
        field = features.get("field", "default")

        sigma_params = alg_kargs.get("sigma_params", [1, 2])
        """
        During long-time series detection, the K-Sigma reference data window, detection window, threshold, 
        and last number of points do not deviate, and the number of abnormal points does not deviate
        """
        long_std_params = alg_kargs.get("long_std_params", [100, 5, 2.5, 2, 3])
        multi_quantile_params = alg_kargs.get("multi_quantile_params", [100, 5, 3, 0.99, 0.05])
        if field == "cost":
            multi_quantile_params = alg_kargs.get("multi_quantile_params", [100, 8, 3, 0.99, 0.05])

        flag_list = []
        for values in zip(
                std_scores, sigma_coefs, kde_long_scores, std_long_coefs, kde_scores, median_shifts, mean_levels,
                threshFlags, detect_results, mean_levels_before, zero_ratios, successPercent_higher_flags
        ):
            std_score, sigma_coef, kde_long_score, std_long_coef, kde_score, median_shift, \
                mean_level, threshFlag, detect_result, mean_level_before, zero_ratio, successPercent_higher_flag = values
            std_score_mean = np.mean(std_score[-5:])

            flag1Thresh1, flag1Thresh2 = sigma_params[1] + 2 * np.log10(max(sigma_coef, sigma_params[0])), sigma_params[
                1] + 2 * np.log10(max(std_long_coef, sigma_params[0]))
            flag1Thresh = np.min([4.5, np.max([flag1Thresh1, flag1Thresh2])])
            flag1 = np.abs(std_score_mean) < flag1Thresh
            flag2 = 0 <= np.mean(std_score[-5:]) < 1 or 0 <= np.mean(kde_long_score[-5:]) < 1
            flag3 = self.unabnormalPointsByThreshWindows(std_score, long_std_params[3], long_std_params[2]) or \
                    self.abnormalPointsByThreshWindows(std_score, long_std_params[1], long_std_params[2],
                                                       long_std_params[4])
            flag4 = median_shift < min(0.05, 7 / max(mean_level, 10))
            flag5 = self.abnormalPointsByWindows(detect_result, multi_quantile_params[1], multi_quantile_params[2])
            flag6 = mean_level / (mean_level_before + 1e-3) < self._ipFunction(mean_level_before, 5, 0.5,
                                                                               0.1) if "Percent" not in field else False
            flag7 = (field == "fail") & (zero_ratio < 0.75) & successPercent_higher_flag
            flag = flag1 or flag2 or flag3 or flag4 or flag5 or flag6 or threshFlag or flag7

            flag_list.append(flag)
        return flag_list

    def totalZeroByOSAndEnv(self, detect_values, field, env, alg_kargs, oslens):
        total_zero_params = alg_kargs.get("total_zero_params", [5, 5, 3, 3])
        return field in ("cost", "total") and np.sum(detect_values[-total_zero_params[0]:] <= total_zero_params[1]) >= \
            total_zero_params[2] and ("SIM" == env or oslens <= total_zero_params[3])

    def abnormalPointsByThreshWindows(self, detect_values, detect_windows, thresh, abnormal_points):
        """
        The number of points greater than the threshold (number of anomalies) in the detection window
        is less than the number of anomalies
        """
        if len(detect_values) == 0:
            return False
        logger.debug("abnormalPointsByThreshWindows, {}, {}, {}, {}".format(len(detect_values[-detect_windows:]),
                                                                            detect_values[-detect_windows:], thresh,
                                                                            abnormal_points))
        return np.sum(detect_values[-detect_windows:] >= thresh) < abnormal_points

    def abnormalPointsByWindows(self, detect_values, detect_windows, abnormal_points):
        """
        The number of anomalies in the detection window is less than the number of anomalies
        """
        if len(detect_values) == 0:
            return False
        logger.debug("abnormalPointsByWindows, {}, {}, {}".format(len(detect_values[-detect_windows:]),
                                                                  detect_values[-detect_windows:], abnormal_points))
        return (len(detect_values[-detect_windows:]) - np.sum(detect_values[-detect_windows:])) < abnormal_points

    def unabnormalPointsByThreshWindows(self, detect_values, detect_windows, thresh):
        """
        The number of anomalies in the detection window is less than the number of anomalies
        """
        logger.debug("unabnormalPointsByThreshWindows, {}, {}, {}".format(len(detect_values[-detect_windows:]),
                                                                          detect_values[-detect_windows:], thresh))
        return np.all(detect_values[-detect_windows:] <= thresh)

    def _ipFunction(self, x, A, B, C):
        """Inverse proportional function"""
        if x < 0.5:
            return A
        return A / (x ** B) + C

    def moduleDecision(self, abnormalCollections_dict, abnormalFeas_dict, dataType_prepared_dict):
        """Composition decisions for modules"""
        noisemsg_by_dataType = {"detect": "The change group is not abnormal",
                                "long": "Background group noise reduction"}
        ac_dict = {}
        for dataType, abnormalCollections in abnormalCollections_dict.items():
            if abnormalCollections is None:
                continue
            for i in abnormalCollections:
                # dsId$&$tagStr$&$field
                i_str = "$&$".join(i)
                if i_str not in ac_dict:
                    ac_dict[i_str] = {"detect": None, "long": None}
                ac_dict[i_str][dataType] = True if dataType_prepared_dict[dataType] else None
        # If it triggers and does not appear, it is noise reduction
        for dataType in ["detect", "long"]:
            abnormalCollections = abnormalCollections_dict.get(dataType, [])
            if abnormalCollections is None or not dataType_prepared_dict[dataType]:
                continue
            for i in abnormalCollections:
                i_str = "$&$".join(i)
                ac_dict[i_str][dataType] = False

        # Information output
        return_msg, return_feas = {}, {}
        return_abnormalCollections = []
        abnormalCollections = abnormalCollections_dict["detect"]
        abnormalFeas = abnormalFeas_dict["detect"]
        for i_str, dataType_values in ac_dict.items():
            # i = ['dsId', 'tagStr1', 'tagStr2...', 'field']
            i = i_str.split("$&$")
            metricName_str = "$&$".join(
                ["$=$".join(["dsId", i[0]]), "$&$".join(i[1:-1]), "$=$".join(["metric", i[-1]])])
            metricName_list = metricName_str.split("$&$")
            # If there is a group that does noise reduction, it will be noise reduction
            unabnormal_flag = np.any([ii for ii in dataType_values.values() if ii is not None])
            print(dataType_values)
            noise_msg = "&&".join(
                [noisemsg_by_dataType.get(dataType, "") for dataType, value in dataType_values.items() if
                 value is True])
            if not unabnormal_flag:
                return_feas[metricName_str] = {"detectMsg": list(abnormalFeas.values())[0]}

                app = "null"
                metricType = "null"
                for metricName in metricName_list:
                    if metricName.startswith("app"):
                        app = metricName.split("$=$")[1]
                    if metricName.startswith("dsId"):
                        metricType = metricName.split("$=$")[1]
                abornalMsg = anormalInfo2msg(app, metricType, abnormalFeas, abnormalCollections)
                return_msg.update(abornalMsg)
                return_abnormalCollections.append(metricName_str)
            else:
                noise_msg = {i_str: "Noise cancellation information: {}".format(noise_msg)}
                return_msg.update(noise_msg)
        """
        If multiple costs are abnormal, the system will receive an alarm, 
        or if there are still alarms after the time-consuming filtering, the system will directly report the alarm
        """
        nameFilter = ["cost"]
        anormalflag = (len(return_abnormalCollections) >= 2) or (
                len([i for i in return_abnormalCollections if i[2] not in nameFilter]) > 0)
        return not anormalflag, return_abnormalCollections, return_msg, return_feas
