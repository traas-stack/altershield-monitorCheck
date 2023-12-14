from enum import Enum


class MetricType(Enum):

    @staticmethod
    def get_metric_type_2_name():
        return {metricType: metricName for metricName, metricTypes in MetricType.metricName2metricType.value.items() for
                metricType in metricTypes}

    metricName2metricType = {
        "error错误": ["errorApp", "errorServer", "errorPod"],
        "cethread": ["ceThreadApp", "cethreadServer"],
        "rpc-service": ["serviceApp", "serviceServer"],
        "rpc-sal": ["salApp", "salServer"],
        "pv": ["pvApp"],
        "缓存Cal": ["calApp", "calServer"],
        "数据库Dal": ["dalApp", "dalServer"],
        "消息1": ["msgsubApp", "msgsubServer", "msghubPod"],
        "消息2": ["msgpubApp", "msgpubServer", "msgpubPod"],
        "系统监控": ["systemServer", "systemPod"],
        "堆内监控": ["jvmgcServer", "jvmgcPod"]
    }

    tableType2MetricType = {
        "app": [
            'errorApp', 'mosnerrorApp', 'odperrorApp', 'ceThreadApp', 'serviceApp',
            'salApp', 'mosnserviceApp', 'mosnsalApp', 'pvApp', 'calApp', 'dalApp', 'msgsubApp',
            'msgpubApp'
        ],
        "server": [
            'errorServer', 'serviceServer', 'calServer', 'salServer', 'dalServer', 'msgpubServer',
            'msgsubServer', 'mosnserviceServer', 'mosnsalServer', 'mosnerrorServer', 'cethreadServer',
            'mosnmsgsubServer', 'mosnmsgpubServer', 'systemServer', 'jvmgcServer'
        ],
        "POD": [
            'errorServer', 'serviceServer', 'calServer', 'salServer', 'dalServer', 'msgpubServer',
            'msgsubServer', 'mosnserviceServer', 'mosnsalServer', 'mosnerrorServer', 'cethreadServer',
            'mosnmsgsubServer', 'mosnmsgpubServer', 'systemServer', 'jvmgcServer'
        ],
    }

    metricType2Fields = {
        # App level interface
        "errorApp": ["count"],
        "ceThreadApp": ["count"],
        "serviceApp": ["total", "fail", "cost", "successPercent"],
        "salApp": ["total", "fail", "cost", "successPercent"],
        "pvApp": ["total", "fail", "cost", "successPercent"],
        "calApp": ["total", "fail", "cost", "successPercent"],
        "dalApp": ["total", "fail", "cost", "successPercent"],
        "msgsubApp": ["total", "fail", "cost", "successPercent"],
        "msgpubApp": ["total", "fail", "cost", "successPercent"],
        # Server level interface
        "errorServer": ["count"],
        "serviceServer": ["total", "fail", "cost", "successPercent"],
        "calServer": ["total", "fail", "cost", "successPercent"],
        "salServer": ["total", "fail", "cost", "successPercent"],
        "dalServer": ["total", "fail", "cost", "successPercent"],
        "msgpubServer": ["total", "fail", "cost", "successPercent"],
        "msgsubServer": ["total", "fail", "cost", "successPercent"],
        "cethreadServer": ["total", "fail", "cost", "successPercent"],
        "systemServer": ["cpu_util", "mem_util", "load_load1"],
        "jvmgcServer": ["fgc_count", "ygc_count", "fgc_time", "ygc_time"],
        # Pod level interface
        "errorPod": ["count"],
        "servicePod": ["total", "fail", "cost", "successPercent"],
        "calPod": ["total", "fail", "cost", "successPercent"],
        "salPod": ["total", "fail", "cost", "successPercent"],
        "dalPod": ["total", "fail", "cost", "successPercent"],
        "msgpubPod": ["total", "fail", "cost", "successPercent"],
        "msgsubPod": ["total", "fail", "cost", "successPercent"],
        "cethreadPod": ["total", "fail", "cost", "successPercent"],
        "systemPod": ["cpu_util", "mem_util", "load_load1"],
        "jvmgcPod": ["fgc_count", "ygc_count", "fgc_time", "ygc_time"],
    }


if __name__ == '__main__':
    print(MetricType.get_metric_type_2_name())
