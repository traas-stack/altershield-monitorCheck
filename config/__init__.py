import os

from config.config import configs

# Global configuration, acquisition method：CONFIG.ENV_RUN
CONFIG = configs[os.getenv("FLASK_ENV", "local")]
