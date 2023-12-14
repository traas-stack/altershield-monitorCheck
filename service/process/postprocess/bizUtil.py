from module.enums.metricType import MetricType
from module.seriesDS.changeSeries import ChangeSeries
from service.process.preprocess.algKargsModels import AlgKargsModel


class BizParams:

    def __init__(self,
                 changeStart, changeEnd, period, dsid, servers, unservers, app, changeType,
                 ldc, fields, metricType, tags, env, bizAlgKargs, datasourceKargs,
                 isTest, isPlot, isPrint, traceId, configId
                 ) -> None:
        self.changeStart = changeStart
        self.changeEnd = changeEnd
        self.period = period
        self.dsid = dsid
        self.servers = servers
        self.unservers = unservers
        self.app = app
        self.ldc = ldc
        self.fields = fields
        self.metricType = metricType
        self.changeType = changeType
        self.tags = tags
        self.env = env
        # 
        self.isTest = isTest
        self.isPlot = isPlot
        self.isPrint = isPrint
        # 
        self.bizAlgKargs = bizAlgKargs
        self.datasourceKargs = datasourceKargs
        self.algKargsModel = AlgKargsModel()
        #
        self.configId = configId  # 某一个批次的记录
        self.traceId = traceId  # 单次调用的记录

    def encodeBizParams(self, ):
        """
        changeStart, changeEnd, period, dsid, servers, unservers, app, ldc, \
        fields, metricType, changeType, tags, env, isTest, isPlot, isPrint, \
        bizAlgKargs, datasourceKargs, algKargsModel, configId, traceId = bizParams.decodeBizParams()
        """
        pass

    def decodeBizParams(self, ):
        return self.changeStart, self.changeEnd, self.period, self.dsid, self.servers, self.unservers, self.app, \
            self.ldc, self.fields, self.metricType, self.changeType, self.tags, self.env, \
            self.isTest, self.isPlot, self.isPrint, \
            self.bizAlgKargs, self.datasourceKargs, self.algKargsModel, self.configId, self.traceId

    def decodeBizAlgKargs(self, ):
        detect_windows = self.bizAlgKargs.get("detect_windows", 4)
        anormal_windows = self.bizAlgKargs.get("anormal_windows", 1)
        fieldThresh = self.bizAlgKargs.get("fieldThresh", {})
        return detect_windows, anormal_windows, fieldThresh

    def getDetectRouterType(self, ):
        return self.bizAlgKargs.get("detectRouterType", "statisticMulti")


class AtomicParams:

    def __init__(self,
                 change_series: ChangeSeries, support_series: ChangeSeries, changeStart, changeEnd, period, app,
                 bizAlgKargs, datasourceKargs,
                 isTest, isPlot, isPrint, traceId, configId
                 ) -> None:
        self.change_series = change_series
        self.support_series = support_series
        self.changeStart = changeStart
        self.changeEnd = changeEnd
        self.period = period
        self.app = app
        # 
        self.isTest = isTest
        self.isPlot = isPlot
        self.isPrint = isPrint
        # 
        self.bizAlgKargs = bizAlgKargs
        self.datasourceKargs = datasourceKargs
        self.algKargsModel = AlgKargsModel()
        #
        self.configId = configId  # 某一个批次的记录
        self.traceId = traceId  # 单次调用的记录

    def encodeBizParams(self, ):
        """
        change_series, support_series, changeStart,changeEnd, period, app, isTest, isPlot, isPrint, \
            bizAlgKargs, datasourceKargs, algKargsModel, configId, traceId = bizParams.decodeBizParams()
        """
        pass

    def decodeBizParams(self, ):
        return self.change_series, self.support_series, self.changeStart, self.changeEnd, self.period, self.app, \
            self.isTest, self.isPlot, self.isPrint, \
            self.bizAlgKargs, self.datasourceKargs, self.algKargsModel, self.configId, self.traceId

    def decodeBizAlgKargs(self, ):
        detect_windows = self.bizAlgKargs.get("detect_windows", 4)
        anormal_windows = self.bizAlgKargs.get("anormal_windows", 1)
        fieldThresh = self.bizAlgKargs.get("fieldThresh", {})
        return detect_windows, anormal_windows, fieldThresh

    def getDetectRouterType(self, ):
        return self.bizAlgKargs.get("detectRouterType", "statisticMulti")


def anormalInfo2msg(app, metricType, abnormalFeas, abnormalCollections):
    """Convert data into anomaly information"""
    fieldName = MetricType.get_metric_type_2_name().get(metricType, metricType)
    abnormalNames = ["&&".join(i) for i in abnormalCollections]
    abornalMsg = {}
    for metricName, feas in abnormalFeas.items():
        dsid, tagStr, field = metricName.split("&&")
        if metricName not in abnormalNames:
            continue
        trend = feas["trend"]
        mean_level = feas["mean_level"]
        mean_level_before = feas["mean_level_before"]
        trend = "上涨" if trend == "up" else "下跌"
        detail_info = "; ".join(tagStr.replace("$=$", "=").split("$&$"))
        abornalMsg[metricName] = "{} 应用的指标 {}-{} 从变更前 {:.2f} {}到变更后 {:.2f} - [详细信息：{}]".format(
            app, fieldName, field, mean_level_before, trend, mean_level, detail_info)
    return abornalMsg
