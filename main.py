from loguru import logger
from config import CONFIG
from config.logger import init_logger
from controllers import app

if __name__ == '__main__':
    init_logger()
    logger.info("app start on port:{}", CONFIG.SERVER_PORT)
    app.run(host='0.0.0.0', port=CONFIG.SERVER_PORT)
