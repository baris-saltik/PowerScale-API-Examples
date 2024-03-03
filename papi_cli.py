import logging.config, sys, argparse
from module.logconf.logconf import get_log_config
from module.papi.auth import Auth

parser = argparse.ArgumentParser(description="Collective PowerScale API calls to automate defined operations",
                               epilog="Thanks for using the program!")

parser.add_argument("-u", "--username", action="store", required=True)
parser.add_argument("-p", "--password", action="store", required=True)
parser.add_argument("-b", "--baseUrl", action="store", required=True)

# Following should be enabled and the next parse_args([...]) should be commented out in production.
# args = parser.parse_args()
args = parser.parse_args(["--username", "root", "--password", "Password77", "--baseUrl", "https://91.229.44.253:8080"])

username = args.username
password = args.password
baseUrl = args.baseUrl

# Initaite logging.
logging.config.dictConfig(get_log_config())
logger = logging.getLogger("papi_cli")
logger.info(f"PowerScale CLI started...")

logger.info(f"Authenticating the user {username}...")

auth = Auth(username = username, password = password, baseUrl = baseUrl)
if not auth.auhtenticated:
    logger.error(f"Authentication failed for user: {username}, quiting!")
    sys.exit(1)

logger.info(f"Authentication was completed.")


## Get the session info
logger.info(f"Session info was requested.")
(sessionInfo, statusCode) = auth.get_session_info()

# Check the HTTP response code from get_session_info(). If get_session_info() gets an exception it sets the status code to False.
if not statusCode: 
    logger.warning(f"Could not get the session info!")
else:
    logger.info(f"Session info request was compeleted.")


## Delete the session
logger.info(f"Session deletion was requested.")

# Check the HTTP response code from delete_session(). If delete_session() gets an exception it sets the status code to False.
if not auth.delete_session(): 
    logger.warning(f"Could not delete the session!")
else:
    logger.info(f"Session deletion request was completed.")



