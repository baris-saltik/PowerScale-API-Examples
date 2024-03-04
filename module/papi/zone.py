import os, sys, pathlib, json, pathlib, yaml, requests
import logging.config

# Add module path to sys.path.
modulePath = os.path.abspath(pathlib.Path(__file__).resolve().parents[2])
sys.path.append(modulePath)
from module.logconf.logconf import get_log_config
from module.papi.auth import Auth

# Get logger logging.
logger = logging.getLogger(__name__)

class Zone(object):
    def __init__(self, auth = None, papi_version=None):

        if type(auth) == None:
            _authenticated = False
        else:
            _authenticated = True
        
        if not _authenticated:
            logger.error("Not an authenticated session, quiting")
            sys.exit(1)

        logger.info("Authenticated session!")

        self.session = auth.session
        self.session.verify = auth.session.verify
        self.papi_version = papi_version

        # Get necessary cookies and headers
        self.baseUrl = auth.baseUrl
        self.platformBaseUrl = self.baseUrl + "/platform/"
        if not papi_version:
            self.zonesUrl = self.platformBaseUrl + "/zones"
            self.zonesSummaryUrl = self.platformBaseUrl + "/zones-summary"
        else:
            self.zonesUrl = self.platformBaseUrl + str(papi_version) + "/zones"
            self.zonesSummaryUrl = self.platformBaseUrl + str(papi_version) + "/zones-summary"
        self.cookies = auth.cookies
        self.headers = auth.headers

    def get_zones_summary(self):
        
        try:
            # response = self.session.get(url = _url, cookies=self.cookies, headers=self.headers)
            _response = self.session.get(url = self.zonesSummaryUrl, cookies=self.cookies, headers=self.headers)
            _response.raise_for_status()
            logger.debug(f"Zones summary: " + json.dumps(json.loads(_response.content)))
            
        except Exception as e:
            logger.error("Zones summary failed!")
            logger.error(e)
            return False, False
    
        return json.loads(_response.content), True

if __name__ == "__main__":

    username = "root"
    # password = "Password77"
    password = "3"
    # baseUrl = "https://91.229.44.253:8080"
    # baseUrl = "https://91.229.44.232:8080"
    baseUrl = "https://192.168.184.141:8080"
    # baseUrl = "https://192.168.184.144:8080"
    zone = "zone1"
    log_level = "info"
    # papi_version = 16
    papi_version = None
    id = "2"
    
    # actions = ["zones_summary", "list_zones"]
    actions = ["zones_summary"]

    # Get the logger.
    logging.config.dictConfig(get_log_config(level=log_level))
    logger = logging.getLogger("module.papi.zone")

    # Instantiate Zone object.
    auth = Auth(username=username, password = password, baseUrl = baseUrl)
    zone = Zone(auth=auth, papi_version=papi_version)

    # Zones summary
    logger.info(f"Zones summary is requested.")
    if "zones_summary" in actions:

        (zonesSummary, successful) = zone.get_zones_summary()
        if successful: 
            if zonesSummary:
                logger.info(zonesSummary)
            else:
                logger.info(f"Zones summary is empty.")

            logger.info(f"Zones summary is completed.")
        else:
            logger.error(f"Could not get Zones summary!")

    # exports is a list of exports.
    if "list_zones" in actions:

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