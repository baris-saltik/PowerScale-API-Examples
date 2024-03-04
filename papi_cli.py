"""
Success status code is evaluated in here. Respective module provides responses and response codes.

"""


import logging.config, sys, argparse
from module.logconf.logconf import get_log_config
from module.papi.auth import Auth
from module.papi.nfs import NFS

parser = argparse.ArgumentParser(description="Collective PowerScale API calls to automate defined operations",
                               epilog="Thanks for using the program!")

parser.add_argument("-u", "--username", action="store", required=True)
parser.add_argument("-p", "--password", action="store", required=True)
parser.add_argument("-b", "--baseUrl", action="store", required=True)
parser.add_argument("-z", "--zone", action="store", required=True)
parser.add_argument("-f", "--feature", action="store", choices=["nfs","cifs","quota","snap"], required=True)
parser.add_argument("-a", "--action", action="store", choices=["list","create", "delete"], required=True)
parser.add_argument("-c", "--config", action="store" , help="/path/to/yaml/config_file.yaml", required=False)
parser.add_argument("-i", "--id", action="store" , help="Id an export or snapshot or name of a share.", required=False)
parser.add_argument("-v", "--version", action="store", help="Papi Version", default=None, required=False)
parser.add_argument("-l", "--log_level", action="store" , choices=["critical", "error", "warning", "info", "debug"], default="info", required=False)


# Following should be enabled and the next parse_args([...]) should be commented out in production.
# args = parser.parse_args()
args = parser.parse_args(["--username", "root",
                          "--password", "3",
                          # "--password", "Password77",
                          # "--baseUrl", "https://91.229.44.232:8080",
                          # "--baseUrl", "https://91.229.44.253:8080",
                          "--baseUrl", "https://192.168.184.141:8080",
                          "--zone", "system",
                          "--feature", "nfs",
                          "--action", "delete",
                          "--config", False,
                          "--id", "9",
                          "--version", None
                          ]
                          )

username = args.username
password = args.password
baseUrl = args.baseUrl
zone = args.zone
feature = args.feature.lower()
action = args.action.lower()

try:
    config = action.config 
except Exception:
    config = False

log_level = args.log_level.lower()
papi_version = args.version
id = args.id

# Initaite logging.
# get_log_config() method returns logging config dictionary.
logging.config.dictConfig(get_log_config(level=log_level))
logger = logging.getLogger("papi_cli")
logger.info(f"PowerScale CLI started...")

logger.info(f"Authenticating the user {username}...")

# Get authenticated.
auth = Auth(username = username, password = password, baseUrl = baseUrl)

if not auth.authenticated:
    logger.error(f"Authentication failed for user: {username}, quiting!")
    sys.exit(1)

logger.info(f"Authentication was completed.")

## Get the session info
logger.info(f"Session info was requested.")
(sessionInfo, successful) = auth.get_session_info()
logger.info(f"Session information: {sessionInfo}")

# Check the HTTP response code from get_session_info(). If get_session_info() gets an exception it sets the status code to False.
if not successful: 
    logger.warning(f"Could not get the session info!")
else:
    logger.info(f"Session info request was compeleted.")


################ NFS Operations #####################
if feature == "nfs":
    # Instantiate NFS object
    nfs = NFS(auth=auth, papi_version=papi_version)

    if action == "list":
        # Get NFS Exports.
        logger.info(f"NFS exports for zone: {zone} is requested.")

        # exports is a list of exports.
        (exports, successful) = nfs.get_exports(zone = zone)

        # Display attributes of each export from exports list.
        # list(map(print, [k for k in exports[0].keys()]))
        if successful: 
            if exports:
                for export in exports:
                    logger.info( " ".join( ["Export: ", export['zone'], str(export['id']), export['paths'][0], ",".join( export['security_flavors'] ) ] ) )
            else:
                logger.info(f"NFS exports list is empty.")

            logger.info(f"NFS exports list for zone: {zone} is completed.")
        else:
            logger.error(f"Could not get NFS exports list!")

    elif action == "create":
        # Create an NFS Export.
        logger.info(f"NFS export creation in zone: {zone} is requested.")
        successful = nfs.create_export(config=config, zone=zone)

        if successful: 
            logger.info(f"Export was created!")       
        else:
            logger.error(f"Export creationg failed!")

    elif action == "delete":
        logger.info(f"NFS export deletion for id: {id} is requested.")
        successful = nfs.delete_export(zone=zone, id=id)

        if successful: 
            logger.info(f"Export was deleted!")       
        else:
            logger.error(f"Export deletion failed!")


## Delete the session
logger.info(f"Session deletion was requested.")

# Check the HTTP response code from delete_session(). If delete_session() gets an exception it sets the status code to False.
if not auth.delete_session(): 
    logger.warning(f"Could not delete the session!")
else:
    logger.info(f"Session deletion request was completed.")
