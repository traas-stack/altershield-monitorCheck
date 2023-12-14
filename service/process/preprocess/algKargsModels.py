from config import CONFIG


class AlgKargsModel:
    """Update, iterate, and configure algorithm parameters"""

    def __init__(self, interval=1000):
        """
        Algorithm parameters are determined based on the service type/metric name
        anormalMinPoints：Anomalies persist in points
        sigma_coef_min：The minimum coefficient of the degree of volatility
        sigma_thresh：The minimum threshold for fluctuations
        zero_ratio_thresh：Proportion of zero values
        metricname_thres：Basic thresholds for each metric name
        """
        self.initAlgKargs(interval)

    def getAlgKargs(self, ):
        return self.alg_kargs

    def updateAlgKargs(self, app, change_type, metric_type, env, detect_windows=4, anormal_windows=1, fieldThresh={}):
        self.updateBySKAndMT(app, change_type, metric_type, env)
        self.updateByRule(detect_windows, anormal_windows, fieldThresh)

    def updateByRule(self, detect_windows, anormal_points, fieldThresh, last_windows=3, interval=1000):
        """
        Parameters are updated through the detection window, number of abnormal points, and manual threshold
        """
        self.alg_kargs["long_std_params"][1] = detect_windows
        self.alg_kargs["long_std_params"][4] = anormal_points
        self.alg_kargs["long_std_params"][3] = last_windows
        self.alg_kargs["multi_quantile_params"][1] = detect_windows
        self.alg_kargs["multi_quantile_params"][2] = anormal_points
        self.alg_kargs["iso_params"][1] = detect_windows
        self.alg_kargs["iso_params"][4] = anormal_points
        self.alg_kargs["iso_params"][3] = last_windows
        self.alg_kargs["interval"] = interval
        for field, thresh in fieldThresh.items():
            if field in self.metricname_params:
                self.metricname_params[field][0] = thresh

    def updateBySKAndMT(self, app, change_type, metric_type, env):
        """
        Parameters can be updated by changing the scenario, indicator type, application, and environment
        """

        # It takes five dots to be able to call the police
        if change_type in CONFIG.BATCH_SK or env in CONFIG.PRE_ENVS + CONFIG.SIM_ENVS + CONFIG.GARY_ENVS:
            self.long_std_params = [100, 7, 2.5, 3, 5]
            self.multi_quantile_params = [100, 7, 5, 0.99, 0.05]
            self.alg_kargs.update({
                "long_std_params": self.long_std_params, "multi_quantile_params": self.multi_quantile_params,
                "metricname_params": self.metricname_params, })

        # When the system class indicator conditions are more stringent
        if metric_type == "system":
            self.long_std_params = [100, 9, 2.5, 5, 7]
            if change_type in CONFIG.BATCH_SK or env in CONFIG.PRE_ENVS + CONFIG.SIM_ENVS + CONFIG.GARY_ENVS:
                self.long_std_params = [100, 8, 2.5, 3, 6]
                self.shake_params = [0.75, 0.65, 0.45, 0.1]
            self.alg_kargs.update({
                "long_std_params": self.long_std_params, "shake_params": self.shake_params})

        # When an app is a data app, the conditions are more stringent
        if app in CONFIG.DATA_APPS:
            self.long_std_params = [100, 9, 2.5, 5, 7]
            if metric_type == "system":
                self.long_std_params = [100, 12, 2.5, 8, 10]
            self.alg_kargs.update({"long_std_params": self.long_std_params})

    def initAlgKargs(self, interval=1000):
        self.metricname_kmeans_params = {
            "fail": [3, 0],
            "successPercent": [2, 0],
            "count": [3, 0],
            "cost": [10, 0],
            "total": [10, 0],
            "load_load1": [15, 0],
            "cpu_util": [20, 0],
            "rcpu_util": [20, 0],
            "pcsw_cswch": [10, 0],
            "pcsw_curtsk": [10, 0],
            "ygc_count": [7, 0],
            "fgc_count": [7, 0],
            "ygc_time": [20, 0],
            "fgc_time": [20, 0],
            "limitFlow": [10, 0],
            "cnt": [3, 0],
            "uidCnt": [3, 0],
            "cntPercent": [0.01, 0],
            "uidCntPercent": [0.01, 0],
        }

        self.metricname_params = {
            "fail": [2, 0.1, 0, 3],
            "successPercent": [95, 0.07, 1, 3],
            "count": [2, 0.1, 0, 3],
            "cost": [60, 0.1, 0, 3],
            "total": [10, 0.1, 1, 3],
            "load_load1": [15, 0.1, 0, 3],
            "load_load15": [15, 0.1, 0, 3],
            "rcpu_util": [20, 0.1, 0, 3],
            "cpu_util": [20, 0.1, 0, 3],
            "success": [10, 0.1, 0, 3],
            "fgc_count": [5, 0.1, 0, 3],
            "ygc_count": [5, 0.1, 0, 3],
            "ygc_time": [2, 0.1, 0, 3],
            "fgc_time": [2, 0.1, 0, 3],
            "tcp_retran": [3, 0.1, 0, 3],
            "pcsw_cswch": [10, 0.1, 0, 3],
            "pcsw_curtsk": [10, 0.1, 0, 3],
            "limitFlow": [100, 0.1, 0, 3],
            "cnt": [3, 0.1, 0, 3],
            "uidCnt": [3, 0.1, 0, 3],
            "cntPercent": [0.05, 0.1, 0, 3],
            "uidCntPercent": [0.05, 0.1, 0, 3],
        }
        """"
        Detection window, value close to zero, number of drops of zero, number of stand-alone units
        """
        self.total_zero_params = [5, 5, 3, 5]
        """
        The coefficient of the degree of fluctuation and the threshold of the degree of fluctuation, 
        if the degree of fluctuation is large, the threshold of STD also needs to be larger
        """
        self.sigma_params = [1, 2]
        """
        During long-time series detection, the K-Sigma reference data window, detection window, 
        threshold, and last number of points do not deviate, and the number of abnormal points does not deviate
        """
        self.long_std_params = [100, 6, 2.5, 3, 4]
        """
        Isolated forest detection The reference data window, detection window, 
        threshold, and last point are not deviated, and the number of abnormal points
        """
        self.iso_params = [100, 6, 0.05, 3, 4]
        """
        Median Offset Reference Data Window, Detection Window, Threshold
        """
        self.median_shift_params = [100, 5, 0.5]
        """
        Median Offset Reference Data Window, Detection Window, Threshold
        """
        self.meanlevel_params = [100, 5, 1.35]
        """
         Whether there is a signal of recovery Maximum recovery limit, minimum recovery limit, 
         fluctuation deviation base, fluctuation coefficient
        """
        self.shake_params = [0.85, 0.7, 0.5, 0.1]
        self.single_anormal_ratio_thresh = 0.35
        """
        Reference data window, detection window, number of anomalies, up_thresh, down_thresh
        """
        self.multi_quantile_params = [100, 6, 4, 0.985, 0.05]

        self.alg_kargs = {
            "sigma_params": self.sigma_params,
            "zero_ratio_thresh": 0.9,
            "metricname_params": self.metricname_params,
            "metricname_kmeans_params": self.metricname_kmeans_params,
            "kde_thresh": 1,
            "total_zero_params": self.total_zero_params,
            "long_std_params": self.long_std_params,
            "iso_params": self.iso_params,
            "median_shift_params": self.median_shift_params,
            "meanlevel_params": self.meanlevel_params,
            "single_anormal_ratio_thresh": self.single_anormal_ratio_thresh,
            "multi_quantile_params": self.multi_quantile_params,
            "shake_params": self.shake_params,
            "extra_range": 1200,
            "interval": interval,
        }

    def decodeBaseKargs(self, ):
        return self.alg_kargs.get("extra_range", 1200), self.alg_kargs.get("interval", 1000)
