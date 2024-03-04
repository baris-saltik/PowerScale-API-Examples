import os, logging.config, yaml, pathlib

def get_log_config(maxBytes = 3000, backupCount = 3, level = "DEBUG"):
        
        level = level.upper()

        loggingBaseDirectory = os.path.abspath(os.path.join(pathlib.Path(__file__).resolve().parents[2],"log"))
        os.makedirs(loggingBaseDirectory, exist_ok=True)

        loggingConfigFile = os.path.abspath(os.path.join(pathlib.Path(__file__).resolve().parents[2], "conf", "logging", "logging.yaml"))
        print(loggingBaseDirectory)
        print(loggingConfigFile)

        defaultConfigDict = {
            "version": 1,
            "formatters": {
                "generic": {
                    "format": "%(asctime)s %(levelname)-8s %(name)-18s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },

            "handlers": {
                "main": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "generic",
                    "filename": os.path.join(loggingBaseDirectory, "main.log"),
                    "maxBytes": maxBytes,
                    "backupCount": backupCount
                },

                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "generic",
                    "stream": "ext://sys.stdout"
                },

                "auth": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "generic",
                    "filename": os.path.join(loggingBaseDirectory, "auth.log"),
                    "maxBytes": maxBytes,
                    "backupCount": backupCount
                },      
            },

            "loggers": {
                "papi_cli": {
                    "level": "DEBUG",
                    "propagate": False,
                    "handlers": ["main", "console"]
                },
                
                # For modules when they are started invididually.
                "__main__": {
                    "level": "DEBUG",
                    "propagate": False,
                    "handlers": ["main", "console"]
                },

                "module.papi.auth": {
                    "level": "DEBUG",
                    "propagate": False,
                    "handlers": ["auth", "console"]
                },

                "module.papi.nfs": {
                    "level": "DEBUG",
                    "propagate": False,
                    "handlers": ["auth", "console"]
                },
            },

            "root": {
                "level": "DEBUG",
                "handlers": ["main", "console"],
            }

        }
 
        # Read the log file and turn it into a dictionary.
        if os.path.exists(loggingConfigFile) and os.path.isfile(loggingConfigFile):
            try:
                with open(loggingConfigFile, "r") as File:
                        content = File.read()
                
                configDict = yaml.load(content, Loader=yaml.Loader)

            except Exception as e:
                print("Logging file could not be opened! Loading default logging config...")
                print(e)
                configDict = defaultConfigDict
        else:
             configDict = defaultConfigDict  

        # Set maxBytes, backupCount and filename parameters for each log handler and level for all handlers.
        for handlerConfig in configDict["handlers"].values():
             handlerConfig["level"] = level
             if handlerConfig["class"] == "logging.handlers.RotatingFileHandler":
                  handlerConfig["maxBytes"] = maxBytes
                  handlerConfig["backupCount"] = backupCount
                  handlerConfig["filename"] = os.path.join( loggingBaseDirectory, handlerConfig["filename"] )

        return configDict


if __name__ == "__main__":
    
    logConfig = get_log_config()
    print(yaml.dump(logConfig, default_flow_style=False))