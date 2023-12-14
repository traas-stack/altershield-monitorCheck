from pydantic import BaseModel
from typing import List, Dict

from util.compareUtil import zerofill


class BaseKeySeries(BaseModel):
    tagStr: str = "default"
    field: str = "default"
    dsId: str = "default"
    series: Dict[int, float] = {}

    def getMetaInfo(self, start, end):
        times, values = zip(*[[i, j] for i, j in self.series.items()])
        fillValue = 100 if self.field == "successPercent" else 0
        values, times = zerofill(start, end, values, times, fillValue=fillValue)
        return "".join([self.dsId, self.tagStr, self.field]), self.dsId, self.tagStr, self.field, \
            times, values


class BaseSeriesList(BaseModel):
    series: List[Dict[int, float]] = []


class BaseKeySeriesList(BaseModel):
    keySeriesList: List[BaseKeySeries] = []

    def getBaseKeySeriesList(self, ):
        return self.keySeriesList

    def getLens(self):
        return len(self.keySeriesList)
