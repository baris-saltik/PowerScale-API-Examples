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

# Initaite logging.
logging.config.dictConfig(get_log_config())
logger = logging.getLogger("powerscale_cli")
logger.info(f"PowerScale CLI started...")

auth = Auth(username=args.username, password = args.password, baseUrl = args.baseUrl)
if not auth.auhtenticated:
    # logger.error(f"Authentication failed for user: {username}, quiting!")
    sys.exit(1)

# logger.info(f"Authentication succeeded for user: {username}!")

