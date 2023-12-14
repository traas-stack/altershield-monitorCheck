from service.process.postprocess.algorithmDetect import *
from service.process.postprocess.bizUtil import *
from service.process.preprocess.algKargsModels import AlgKargsModel


def getAlgKargs(bizParams: BizParams) -> BizParams:
    """Generate algorithm parameters and update algorithm parameters through some parameter configurations"""
    changeStart, changeEnd, period, dsid, servers, unservers, app, ldc, \
        fields, metricType, changeType, tags, env, isTest, isPlot, isPrint, \
        bizAlgKargs, datasourceKargs, algKargs, configId, traceId = bizParams.decodeBizParams()
    detect_windows, anormal_windows, fieldThresh = bizParams.decodeBizAlgKargs()

    algKargsModel = AlgKargsModel()
    algKargsModel.updateAlgKargs(app, changeType, metricType, env, detect_windows, anormal_windows, fieldThresh)
    bizParams.algKargsModel = algKargsModel
    return bizParams


def getAtomicAlgKargs(bizParams: AtomicParams) -> BizParams:
    """Generate algorithm parameters and update algorithm parameters through some parameter configurations"""
    change_series, support_series, changeStart, changeEnd, period, app, isTest, isPlot, isPrint, \
        bizAlgKargs, datasourceKargs, algKargsModel, configId, traceId = bizParams.decodeBizParams()
    detect_windows, anormal_windows, fieldThresh = bizParams.decodeBizAlgKargs()

    algKargsModel = AlgKargsModel()
    algKargsModel.updateAlgKargs(app, "default", "default", "default", detect_windows, anormal_windows, fieldThresh)
    bizParams.algKargsModel = algKargsModel
    return bizParams


def bizDetectRouter(bizParams: BizParams):
    """Generate according to business parameters"""
    routerDict = {
        # Only used by business parties that provide data
        "statisticMultiByAtomic": statisticMultiByAtomic,
    }
    detectRouterType = bizParams.getDetectRouterType()
    if detectRouterType not in routerDict:
        return True, [], {"error": "No algorithm available"}
    func = routerDict[detectRouterType]
    return func(bizParams)


def statisticMultiByAtomic(bizParams: AtomicParams):
    """
    for-tags: multiple field + custom（Short timing + long timing verification），Verification based on statistics and kde
    :return:
    """
    change_series, support_series, changeStart, changeEnd, period, app, isTest, isPlot, isPrint, \
        bizAlgKargs, datasourceKargs, algKargsModel, configId, traceId = bizParams.decodeBizParams()

    # Determine whether the incoming data exists
    dataTypes = ["detect", "long"]
    dataType_prepared_dict = {dataType: change_series.is_prepared_by_dataType(dataType) for dataType in dataTypes}
    # Start short-series detection "obtain abnormal object collection and its characteristic information"
    abnormalCollections_short, abnormalFeas_short = shortDetectMulti(change_series, changeStart, changeEnd, configId,
                                                                     algKargsModel, isTest, isPlot=isPlot)
    # Start long-term detection
    abnormalCollections_long, abnormalFeas_long = longDetectMulti(change_series, changeStart, changeEnd, configId,
                                                                  algKargsModel, isTest, isPlot=isPlot)

    abnormalCollections_dict = {"detect": abnormalCollections_short, "long": abnormalCollections_long}
    abnormalFeas_dict = {"detect": abnormalFeas_short, "long": abnormalFeas_long}

    decisionModule = DecisionModule()
    verdict, abnormalCollections, abnormalMsgs, _ = decisionModule.moduleDecision(abnormalCollections_dict,
                                                                                  abnormalFeas_dict,
                                                                                  dataType_prepared_dict)

    return verdict, abnormalCollections, abnormalMsgs
