from module.logger.logger import Logging



if __name__ == "__main__":
    logger = Logging().getLogger(__name__)

    logger.info("Hello")