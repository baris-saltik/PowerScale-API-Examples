import logging.config
from module.logconf.logconf import get_log_config
from module.papi.auth import Auth

if __name__ == "__main__":
    # Initaite logging.
    logging.config.dictConfig(get_log_config())
    print(__name__)
    logger = logging.getLogger(__name__)
    logger.info(f"Execution starts!")

    auth = Auth(username="root", password = "Password77", baseUrl="https://91.229.44.253:8080")
    print(auth.get_session_info())
    print("#" * 100)
    print(auth.delete_session())
