from module.seriesDS.changeSeries import ChangeSeries
from service.features.kdeFeatures import *
from service.features.statisticFeatures import *
from service.process.postprocess.decisionModule import DecisionModule
from service.process.preprocess.algKargsModels import AlgKargsModel
from loguru import logger


def multiDataPreprocess(change_values, change_ts, changeStart, changeEnd, field, isPlot):
    """Preprocess data for short time series"""
    if isPlot:
        plt.figure(figsize=(16, 2))
        for change_value in change_values:
            plt.plot(np.array(change_value))
        plt.legend([field])
        plt.show()
    change_select_values, unchanged_select_values, change_select_ts, unchanged_select_ts = splitChangeData(
        change_values,
        change_ts,
        changeStart,
        changeEnd
    )
    return change_select_values, unchanged_select_values, change_select_ts, unchanged_select_ts


def shortDetectMulti(change_series: ChangeSeries, changeStart, changeEnd, configId, alg_kargs_model: AlgKargsModel,
                     isTest=False, isPlot=False, ):
    """Short-time series detection"""
    logger.info("[shortDetectMulti detect][configId={}]".format(configId))
    # Extract the change validity interval and note that the incoming data is time-ordered
    abnormalCollections, abnormalFeas = [], {}
    for field in change_series.get_fields_by_dataType(dataType="detect"):
        # Confirm whether the data is complete
        if not change_series.is_prepared_by_field(field, ["detect"]):
            logger.error("[reDataControlByField error][field={}][configId={}]".format(field, configId))
            continue
        change_values = np.array(change_series.get_values_by_field(field, dataType="detect"))
        change_ts = change_series.get_ts_by_field(field, dataType="detect")
        change_select_values, unchanged_select_values, change_select_ts, unchanged_select_ts = multiDataPreprocess(
            change_values, change_ts, changeStart, changeEnd, field, isPlot)
        abnormal_collections, abnormal_feas = calBackFeaturesMulti(change_series, unchanged_select_values,
                                                                   unchanged_select_ts, change_select_values,
                                                                   change_select_ts, field, alg_kargs_model)
        abnormalCollections.extend(abnormal_collections)
        abnormalFeas.update(abnormal_feas)
    return abnormalCollections, abnormalFeas


def longDetectMulti(change_series: ChangeSeries, changeStart, changeEnd, configId, alg_kargs_model: AlgKargsModel,
                    isTest=False, isPlot=False, ):
    """Long-time series detection"""

    logger.info("[longDetectMulti detect][configId={}]".format(configId))
    # Extract the change validity interval and note that the incoming data is time-ordered
    abnormalCollections, abnormalFeas = [], {}
    for field in change_series.get_fields_by_dataType(dataType="long"):
        # Confirm whether the data is complete
        if not change_series.is_prepared_by_field(field, ["long"]):
            logger.error("[reDataControlByField error][field={}][configId={}]".format(field, configId))
            continue
        change_values = np.array(change_series.get_values_by_field(field, dataType="long"))
        change_ts = change_series.get_ts_by_field(field, dataType="long")
        change_select_values, unchanged_select_values, change_select_ts, unchanged_select_ts = multiDataPreprocess(
            change_values, change_ts, changeStart, changeEnd, field, isPlot)
        abnormal_collections, abnormal_feas = calBackFeaturesMulti(change_series, unchanged_select_values,
                                                                   unchanged_select_ts, change_select_values,
                                                                   change_select_ts, field, alg_kargs_model)
        abnormalCollections.extend(abnormal_collections)
        abnormalFeas.update(abnormal_feas)

    return abnormalCollections, abnormalFeas


def calculateFeaturesMulti(
        field, values_before_change, ts_before_change, values_after_change, ts_after_change,
        isTest=False, isPlot=False, isIsoforest=False, isKde=True, extra_range=1200, interval=1000, alg_kargs={}):
    """Noise is filtered from a statistical point of view"""

    # Calculation of features
    statisticFeaturesMulti = StatisticFeaturesMulti()
    features = statisticFeaturesMulti.getFeaturesMulti(values_after_change, values_before_change, field,
                                                       referLength=100, isIsoforest=isIsoforest, alg_kargs=alg_kargs)
    if isKde:
        kde_long_scores, std_long_scores = get_anormalValue_scores_multi(
            values_after_change, ts_after_change, values_before_change, ts_before_change,
            extra_range=extra_range, interval=interval, isPlot=isPlot
        )
    else:
        kde_long_scores = [[2] for i in range(len(values_after_change))]
        std_long_scores = [0] * len(values_after_change)
    features.update({
        "kde_scores": kde_long_scores,
        "kde_long_scores": kde_long_scores,
        "std_long_scores": std_long_scores,
    })
    return features


def calBackFeaturesMulti(change_series: ChangeSeries, unchanged_select_values, unchanged_select_ts, change_select_values,
                         change_select_ts, field, alg_kargs_model: AlgKargsModel):
    """Compute data from the history of the time series itself"""
    extra_range, interval = alg_kargs_model.decodeBaseKargs()
    alg_kargs = alg_kargs_model.getAlgKargs()
    # Calculation of features
    features = calculateFeaturesMulti(
        field, unchanged_select_values, unchanged_select_ts, change_select_values, change_select_ts,
        isTest=False, isPlot=False, extra_range=extra_range, interval=interval, alg_kargs=alg_kargs,
        isKde=True
    )

    # The decision of statistical features
    decisionModule = DecisionModule()
    unabnormalFlags = decisionModule.isSingleAnormalMulti(features, alg_kargs)
    abnormal_combines = [combines for idx, combines in enumerate(change_series.get_metainfo_by_field(field)) if
                         not unabnormalFlags[idx]]
    abnormal_feas = {"&&".join(combines): getIdxFeatures(features, idx) for idx, combines in
                     enumerate(change_series.get_metainfo_by_field(field)) if not unabnormalFlags[idx]}
    return abnormal_combines, abnormal_feas


def splitChangeData(change_values, change_ts, changeStart, changeEnd):
    """Filter by change time"""
    if len(change_values.shape) >= 2:
        change_select_values, unchanged_select_values = change_values[:, change_ts >= changeEnd], \
            change_values[:, change_ts < changeStart]
        change_select_ts, unchanged_select_ts = change_ts[change_ts >= changeEnd], change_ts[change_ts < changeStart]
    else:
        change_select_values, unchanged_select_values = change_values[change_ts >= changeEnd], change_values[
            change_ts < changeStart]
        change_select_ts, unchanged_select_ts = change_ts[change_ts >= changeEnd], change_ts[change_ts < changeStart]
    return change_select_values, unchanged_select_values, change_select_ts, unchanged_select_ts


def getIdxFeatures(features, idx):
    """Associates multi-dimensional features with tags in a specified order"""
    return {
        "std_socres": features["std_socres"][idx],
        "std_mean": features["std_mean"][idx],
        "sigma_coef": features["sigma_coef"][idx],
        "shake_thres": features["shake_thres"][idx],
        "shake_level": features["shake_level"][idx],
        "median_shift": features["median_shift"][idx],
        "mean_level": features["mean_level"][idx],
        "zero_ratio": features["zero_ratio"][idx],
        "detect_result": features["detect_results"][idx],
        "trend": features["trends"][idx],
        "iso_flags": features["iso_flags"][idx],
        "thresh_flags": features["thresh_flags"][idx],
        "mean_level_before": features["mean_level_before"][idx],
        "mean_level_after": features["mean_level_after"][idx],
        "mean_level_change": features["mean_level_change"][idx],
        "kde_scores": features["kde_scores"][idx],
        "kde_long_scores": features["kde_long_scores"][idx],
        "std_long_scores": features["std_long_scores"][idx],
        "cpu_lower_flag": features["cpu_lower_flags"][idx],
        "successPercent_higher_flag": features["successPercent_higher_flags"][idx],
        "total_smaller_flag": features["total_smaller_flags"][idx],
        "field": features["field"],
        "refer_values": features["refer_values"][idx],
        "detect_values": features["detect_values"][idx],
        "abnormal_idx": features["abnormal_idxs"][idx]
    }
