from typing import Tuple, TypeVar
from dataclasses import dataclass
from module.seriesDS.seriesRequests.baseSeriesRequest import *

T = TypeVar("T")


@dataclass
class BaseChangeSeries:

    def __init__(self, ):
        self.detectSeries: Tuple(List[int], List[float]) = []
        self.longSeries: Tuple[List[int], List[float]] = []
        self.dataTypeToSeries = {
            "detect": self.detectSeries, "long": self.longSeries
        }

    def add_series(self, values, ts, dataType="detect", nearby_length=50):
        if dataType in ["detect"]:
            values, ts = values[-nearby_length:], ts[-nearby_length:]

        self.dataTypeToSeries[dataType].append(tuple([ts, values]))

    def is_prepared(self, dataType):
        return len(self.dataTypeToSeries[dataType]) > 0

    def get_values(self, dataType="detect", idx=0):
        return [self.dataTypeToSeries[dataType][idx][1]]

    def get_ts(self, dataType="detect", idx=0):
        return [self.dataTypeToSeries[dataType][idx][0]]

    def get_values_array(self, dataType="detect"):
        return [i[1] for i in self.dataTypeToSeries[dataType]]

    def get_ts_array(self, dataType="detect"):
        return [i[0] for i in self.dataTypeToSeries[dataType]]


@dataclass
class ChangeSeries:

    def __init__(self, ):
        self.data_status: int = -1
        dataTypes = ["detect", "long"]
        # 
        self.fieldsByDataType: Dict[str, List[str]] = {k: [] for k in dataTypes}
        self.metricNamesByDataType: Dict[str, List[str]] = {k: [] for k in dataTypes}
        self.metainfoStrsByDataType: Dict[str, List[str]] = {k: [] for k in dataTypes}
        self.metainfoByDataType: Dict[str, List[str]] = {k: [] for k in dataTypes}
        self.metricNameByFieldByDataType: Dict[str, Dict[str, List[str]]] = {k: {} for k in dataTypes}
        # MetricName 纬度的时许数据
        self.seriesByMetricName: Dict[str, BaseChangeSeries] = {}
        self.metainfoByMetricNameByDataType: Dict[str, Dict[str, List[str]]] = {k: {} for k in dataTypes}
        self.metainfoByFieldByDataType: Dict[str, Dict[str, List[str]]] = {k: {} for k in dataTypes}
        self.metainfoStrByFieldByDataType: Dict[str, Dict[str, List[str]]] = {k: {} for k in dataTypes}

    def add_series(self, metricName, dsId, tagStr, field, change_values, change_ts, dataType="detect",
                   nearby_length=50):
        metainfoStr = "$&$".join([dsId, tagStr, field])
        if field not in self.fieldsByDataType[dataType]:
            self.fieldsByDataType[dataType].append(field)
            self.metricNameByFieldByDataType[dataType][field] = []
            self.metainfoByFieldByDataType[dataType][field] = []
            self.metainfoStrByFieldByDataType[dataType][field] = []

        if metricName not in self.metricNamesByDataType[dataType] and (dataType == "detect"):
            self.seriesByMetricName[metricName] = BaseChangeSeries()

        if metricName not in self.metricNamesByDataType[dataType]:
            self.metricNamesByDataType[dataType].append(metricName)
            self.metainfoByMetricNameByDataType[dataType][metricName] = []
            self.metricNameByFieldByDataType[dataType][field].append(metricName)

        if metainfoStr not in self.metainfoStrsByDataType[dataType]:
            self.metainfoStrsByDataType[dataType].append(metainfoStr)
            self.metainfoByDataType[dataType].append([dsId, tagStr, field])
            self.metainfoByMetricNameByDataType[dataType][metricName].append([dsId, tagStr, field])
            self.metainfoByFieldByDataType[dataType][field].append([dsId, tagStr, field])
            self.metainfoStrByFieldByDataType[dataType][field].append(metainfoStr)
        self.seriesByMetricName[metricName].add_series(change_values, change_ts, dataType, nearby_length)

    def get_values_by_metricName(self, metricName, dataType="detect"):
        return [j for j in self.seriesByMetricName[metricName].get_values_array(dataType)]

    def get_tsMatrix_by_metricName(self, metricName, dataType="detect"):
        return [j for j in self.seriesByMetricName[metricName].get_ts(dataType)]

    def get_ts_by_metricName(self, metricName, dataType="detect"):
        return [j for j in self.seriesByMetricName[metricName].get_ts(dataType)][0]

    def get_values_by_field(self, field, dataType="detect"):
        return [j for metricName in self.metricNameByFieldByDataType["detect"][field] for j in
                self.seriesByMetricName[metricName].get_values_array(dataType)]

    def get_tsMatrix_by_field(self, field, dataType="detect"):
        return [j for metricName in self.metricNameByFieldByDataType["detect"][field] for j in
                self.seriesByMetricName[metricName].get_ts(dataType)]

    def get_ts_by_field(self, field, dataType="detect"):
        return [j for metricName in self.metricNameByFieldByDataType["detect"][field] for j in
                self.seriesByMetricName[metricName].get_ts(dataType)][0]

    def is_prepared_by_metricName(self, metricName, dataTypes):
        return all([self.seriesByMetricName[metricName].is_prepared(dataType) for dataType in dataTypes])

    def is_prepared_by_field(self, field, dataTypes):
        return all([self.seriesByMetricName[metricName].is_prepared(dataType) for metricName in
                    self.metricNameByFieldByDataType["detect"][field] for dataType in dataTypes])

    def is_prepared_by_dataType(self, dataType):
        return any([self.seriesByMetricName[metricName].is_prepared(dataType)
                    for field in self.fieldsByDataType[dataType] for metricName in
                    self.metricNameByFieldByDataType[dataType][field]
                    ])

    def get_field_by_metricName(self, metricName, dataType="detect"):
        return self.metainfoByMetricNameByDataType[dataType][metricName][0][2]

    def get_tagStr_by_metricName(self, metricName, dataType="detect"):
        return self.metainfoByMetricNameByDataType[dataType][metricName][0][1]

    def get_dsId_by_metricName(self, metricName, dataType="detect"):
        return self.metainfoByMetricNameByDataType[dataType][metricName][0][0]

    def get_fields_by_dataType(self, dataType="detect"):
        return self.fieldsByDataType[dataType]

    def get_metricNames_by_dataType(self, dataType="detect"):
        return self.metricNamesByDataType[dataType]

    def get_metainfoStrs_by_dataType(self, dataType="detect"):
        return self.metainfoStrsByDataType[dataType]

    def get_metainfoStrs_by_metricName(self, metricName, dataType="detect"):
        return self.metainfoByMetricNameByDataType[dataType][metricName]

    def get_metainfo_by_metricName(self, metricName, dataType="detect"):
        return self.metainfoByMetricNameByDataType[dataType][metricName]

    def get_metainfo_by_dataType(self, dataType="detect"):
        return self.metainfoByDataType[dataType]

    def get_metainfo_by_field(self, field, dataType="detect"):
        return self.metainfoByFieldByDataType[dataType][field]

    def get_metainfoStrs_by_field(self, field, dataType="detect"):
        return self.metainfoStrByFieldByDataType[dataType][field]

    def decodeOuterJson(self, start, end, baseKeySeriesList: BaseKeySeriesList, dataType="detect", nearby_length=50):
        """Parse the specified data into this structure"""
        for baseKeySeries in baseKeySeriesList.keySeriesList:
            metric_name, dsId, tagStr, field, change_ts, change_values = baseKeySeries.getMetaInfo(start, end)
            self.add_series(metric_name, dsId, tagStr, field, change_values, change_ts, dataType,
                            nearby_length=nearby_length)

    def decode(self, ):
        pass
