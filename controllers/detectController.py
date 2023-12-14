from flask_restful import Resource, request
from loguru import logger

from module.message.message import Message
from service.batchMonitorDetectService import BatchMonitorDetect
from util.responseUtil import response_filter

# Service Define
batchMonitorDetectService = BatchMonitorDetect()


class BatchMonitorDetectController(Resource):
    @response_filter
    def post(self):
        try:
            # Batch monitoring and verification service entrance
            result = batchMonitorDetectService.detect(request.get_json())
        except Exception as e:
            logger.error(f'system Exception: {e}')
            return Message(verdict='FAIL', abnormalMsg="System Error", resultCode=-1, rootCauseMsg="System Error")
        return result
