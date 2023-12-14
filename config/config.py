import os
from enum import Enum

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVER_PORT = os.getenv("SERVER_PORT", 8083)

upFields = ["fail", "count", "cost", "load_load1", "cpu_util", "tcp_retran", "flowlimitRatio", "limiteCount",
            "exception", "block", "block_rate"]
downFields = []
dataApps = []
field_upOrDown = {
    "cntPercent": "up",
    "uidCntPercent": "up",
}
batchSk = [
    "com.alterShield.release.rolling._batch",
]


class RUNNING_ENV(Enum):
    PROD = 'PROD',
    PRE = 'PRE',
    GARY = 'GARY',
    DEV = 'DEV',
    LOCAL = 'LOCAL'


# Production environment
prodEnvs = ["prod", "PROD", "default", "DEFAULT"]
# Grayscale environment
grayEnvs = ["gray", "GRAY"]
# Pre-release environment
preEnvs = ["pre", "PRE"]
# sim environment
simEnvs = ["sim", "SIM"]
# test environment
testEnvs = ["test", "TEST"]
# development environment
devEnvs = ["dev", "DEV"]
# local environment
localEnvs = ["local", "LOCAL"]


class Config(object):
    ENV_RUN = RUNNING_ENV.LOCAL
    DEBUG = False
    TESTING = False
    BASE_DIR = basedir
    LOG_DIR = os.path.join(basedir, "logs")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # server
    SERVER_PORT = SERVER_PORT

    # biz
    UP_FIELDS = upFields
    DOWN_FIELDS = downFields
    FIELD_UP_OR_DOWN = field_upOrDown
    BATCH_SK = batchSk
    PRE_ENVS = preEnvs
    GARY_ENVS = grayEnvs
    PROD_ENVS = prodEnvs
    SIM_ENVS = simEnvs
    DATA_APPS = dataApps


# prod env
class ProductionConfig(Config):
    @classmethod
    def get_config(cls):
        Config.ENV_RUN = RUNNING_ENV.PROD
        return Config


# dev env
class DevelopmentConfig(Config):
    @classmethod
    def get_config(cls):
        Config.DEBUG = True
        Config.ENV_RUN = RUNNING_ENV.DEV
        return Config


# pre env
class PreConfig(Config):
    @classmethod
    def get_config(cls):
        Config.ENV_RUN = RUNNING_ENV.PRE
        return Config


# local env
class LocalConfig(Config):
    @classmethod
    def get_config(cls):
        Config.DEBUG = True
        Config.TESTING = True
        Config.ENV_RUN = RUNNING_ENV.LOCAL
        return Config


print("——————————————config start")
configs: {str: Config} = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "pre": PreConfig,
    "local": LocalConfig,
    "default": LocalConfig
}
print(f'init config: {configs.keys()}')
print("——————————————config end")
