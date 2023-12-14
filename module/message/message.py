class Message:
    def __init__(
            self, verdict='PASS',  resultCode=0, abnormalMsg="", rootCauseMsg="", supportMsg="", costTime=0
    ):
        self.verdict = verdict
        self.resultCode = resultCode
        self.abnormalMsg = abnormalMsg
        self.rootCauseMsg = rootCauseMsg
        self.supportMsg = supportMsg
        self.costTime = costTime

    def updateMessage(self, ):
        """Update based on existing information"""
        pass

    def __repr__(self):
        return "verdict: {}, resultCode: {}, algorithmMessage: {}, rootCauseMsg: {}, supportMessage: {}".format(
            self.verdict, self.resultCode, self.abnormalMsg, self.rootCauseMsg, self.supportMsg)

    def to_dict(self):
        return {
            'verdict': self.verdict,
            'resultCode': self.resultCode,
            'algorithmMessage': self.abnormalMsg,
            'rootCauseMsg': self.rootCauseMsg,
            'costTime': self.costTime
        }


class AbnormalMessage:
    def __init__(self, ):
        pass


class RCAMessage:
    def __init__(self):
        pass
