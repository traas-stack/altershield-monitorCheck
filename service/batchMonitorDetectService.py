import time
from loguru import logger
from module.message.message import Message
from module.seriesDS.changeSeries import ChangeSeries
from module.seriesDS.seriesRequests.baseSeriesRequest import BaseKeySeriesList
from service.process.postprocess.bizDetect import getAtomicAlgKargs, bizDetectRouter
from service.process.postprocess.bizUtil import AtomicParams


class BatchMonitorDetect:

    # Detect services
    def detect(self, request_json: dict) -> Message:
        # 1、Convertor Request To Input Param
        try:
            # 1.1、Encode to dict
            format_dict = encodeToDict(query=request_json)

            # 1.2、Format params
            change_series = format_dict['change_series']
            app = format_dict['app']
            changeStart = format_dict['changeStart']
            changeEnd = format_dict['changeEnd']
            period = format_dict['period']
            bizAlgKargs = format_dict['bizAlgKargs']
            datasourceKargs = format_dict['datasourceKargs']
            isTest = format_dict['isTest']
            isPlot = format_dict['isPlot']
            isPrint = format_dict['isPrint']
        except Exception as e:
            logger.exception(f'Convertor Request To Input Param Error. e = {e}')
            return Message(verdict='FAIL', abnormalMsg="Parameter parsing failed", resultCode=-1, rootCauseMsg="Parameter parsing failed")

        # 2、Atomic predict tasks
        return atomic_predict(
            change_series, None, app, changeStart, changeEnd, period, bizAlgKargs, datasourceKargs, traceId='default',
            configId='default',
            isPlot=isPlot, isPrint=isPrint, isTest=isTest
        )


# Atomic predict tasks
def atomic_predict(change_series, support_series, app, changeStart, changeEnd, period, bizAlgKargs,
                   datasourceKargs, traceId="default", configId="default",
                   isPlot=False, isPrint=False, isTest=False,
                   ) -> Message:
    """
    A generalized execution function for change risk identification, which can accept multiple data inputs
    """
    if bizAlgKargs is None:
        bizAlgKargs = {}
    if datasourceKargs is None:
        datasourceKargs = {}

    # Build business parameters
    bizParams = AtomicParams(
        change_series, support_series, changeStart, changeEnd, period, app, bizAlgKargs, datasourceKargs,
        isTest, isPlot, isPrint, traceId, configId,
    )
    bizParams = getAtomicAlgKargs(bizParams)

    # detect router
    start_time = time.time()
    verdict, anormalCollections, anormalMsgs = bizDetectRouter(bizParams)
    end_time = time.time()

    # Summarize the results of the verification analysis and provide the return information
    abnormalMsg = ""
    for index, msg in enumerate(anormalMsgs.values()):
        abnormalMsg += f"{index + 1}、{msg}; \n"
    return Message(verdict='PASS' if verdict else 'FAIL', abnormalMsg=abnormalMsg,
                   rootCauseMsg="", costTime=end_time - start_time)


def encodeToDict(query: dict):
    """
    Encapsulates the data to the specified algorithm parameters with partial checks
    """
    app = query.get("app", "default")
    changeStart = query.get("changeStart", -1)
    changeEnd = query.get("changeEnd", -1)
    period = query.get("period", -1)

    bizAlgKargs = query.get("bizAlgKargs", {})
    detect_series = BaseKeySeriesList(**query.get("detectSeries", {}))
    long_series = BaseKeySeriesList(**query.get("longSeries", {}))
    change_series = ChangeSeries()
    supportData_series = ChangeSeries()
    if detect_series.getLens() > 0:
        change_series.decodeOuterJson(changeStart - 86400 * 2 * 60000, period, detect_series, dataType="detect")
    if long_series.getLens() > 0:
        change_series.decodeOuterJson(changeStart - 86400 * 2 * 60000, period, long_series, dataType="long")
    assert (changeStart != -1) & (changeEnd != -1) & (period != -1)
    return {
        "app": app, "change_series": change_series, "bizAlgKargs": bizAlgKargs, "datasourceKargs": {},
        "support_series": supportData_series,
        "changeStart": changeStart, "changeEnd": changeEnd, "period": period,
        "isTest": False, "isPlot": False, "isPrint": False
    }
