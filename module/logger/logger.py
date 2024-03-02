import logging
import logging.config
import os, sys, pathlib



class Logging(object):
    def __init__(self):

        _loggingBaseDirectory = os.path.abspath(os.path.join(os.getcwd(), "log"))

        self.loggingConfigDict = {
            "version": 1,
            "formatters": {
                "generic": {
                    "format": "%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },

            "handlers": {
                "main": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "generic",
                    "filename": os.path.join(_loggingBaseDirectory, "main"),
                    "maxBytes": 1000,
                    "backupCount": 3
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "generic",
                    "stream": "ext://sys.stdout"
                }
                
            },

            "loggers": {
                "main": {
                    "level": "DEBUG",
                    "propagate": False,
                    "handlers": ["main", "console"]
                },
                
                # For modules when they are started invididually.
                "__main__": {
                    "level": "DEBUG",
                    "propagate": False,
                    "handlers": ["main", "console"]
                }
            },

            "root": {
                "level": "DEBUG",
                "handlers": ["main", "console"],
            }

        }
 
        logging.config.dictConfig(self.loggingConfigDict)

    def get_logger(self, name = "__main__"):
        self.logger = logging.getLogger(name) 

        


if __name__ == "__main__":
    
    loggerObj = Logging()
    loggerObj.get_logger("__main__")
    logger = loggerObj.logger

    logger.info("Hello")
