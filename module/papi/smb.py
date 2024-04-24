import os, sys, pathlib, json, pathlib, yaml, requests
import logging.config

# Add module path to sys.path.
modulePath = os.path.abspath(pathlib.Path(__file__).resolve().parents[2])
sys.path.append(modulePath)
from module.logconf.logconf import get_log_config
from module.papi.auth import Auth
from module.papi.zone import Zone

# Get logger logging.
logger = logging.getLogger(__name__)

class SMB(object):
    def __init__(self, auth = None, papi_version=None):

        if type(auth) == None:
            _authenticated = False
        else:
            _authenticated = True
        
        if not _authenticated:
            logger.error("Not an authenticated session, quiting")
            sys.exit(1)

        logger.info("Authenticated session!")

        self.auth = auth
        self.session = auth.session
        self.papi_version = papi_version

        # Set URLs
        self.baseUrl = auth.baseUrl
        self.platformBaseUrl = self.baseUrl + "/platform/"
        if not papi_version:
            self.sharesUrl = self.platformBaseUrl + "protocols/smb/shares"
            self.shareSummaryUrl = self.platformBaseUrl + "/protocols/smb/shares-summary"
        else:
            self.sharesUrl = self.platformBaseUrl + str(papi_version) + "/protocols/smb/shares"
            self.shareSummaryUrl = self.platformBaseUrl + str(papi_version) + "/protocols/smb/shares-summary"
        self.namespaceUrl = self.baseUrl + "/namespace"

        # Set cookies and base headers
        self.cookies = auth.cookies
        self.headers = auth.headers
        
    def get_shares_summary(self, zone = "System"):
        _params = dict(zone=zone)
     
        try:
            # response = self.session.get(url = _url, cookies=self.cookies, headers=self.headers)
            _response = self.session.get(url = self.shareSummaryUrl, cookies=self.cookies, headers=self.headers, params=_params)
            _response.raise_for_status()
            logger.debug(f"SMB shares summary for zone: {zone}: " + json.dumps(json.loads(_response.content)))
            
        except Exception as e:
            logger.error("SMB shares summary failed!")
            logger.error(e)
            return False, False
    
        return json.loads(_response.content), True
    
    def get_shares(self, zone = "system"):
        _params = dict(zone=zone)
        
        try:
            # response = self.session.get(url = _url, cookies=self.cookies, headers=self.headers)
            _response = self.session.get(url = self.sharesUrl, cookies=self.cookies, headers=self.headers, params=_params)
            _response.raise_for_status()
            shares = json.loads(_response.content)['shares']
            for share in shares:
                logger.debug( " ".join( ["Share: ", str(share['zid']), str(share['id']), share['path'] ] ) )
            
        except Exception as e:
            logger.error(f"SMB shares list request for zone: {zone} could not be completed!")
            logger.error(e)
            return False, False
        
        return shares, True
    
    def create_share(self, config = False, zone = None):

        if not (config and isinstance(dict, config)):
            configFilePath = os.path.abspath(os.path.join(pathlib.Path(__file__).resolve().parents[2], "conf/papi_objects/create_share.yaml"))

            if configFilePath and os.path.isfile(configFilePath):
                with open(configFilePath, "r") as file:
                    content = file.read()
                try:
                    config = yaml.load(content,Loader=yaml.Loader)
                except Exception as e:
                    logger.error("Configuration for the object could not be obained. Quiting...")
                    return False
                
        # If zone specified in the arguments then overwrite the zone value in the config dictionary.
        _zone =  zone if zone else config['metadata']['zone']
        _zone = _zone.lower()

        print(_zone)

        # Not necessary in OneFS 9.7.
        # _zid = self.lookup_zid(_zone)

        # Request payload type will be of json.
        # This sets the respective header to inform the server that the payload is json formatted string.
        _headers = self.headers
        _headers.update({"Content-Type": "application/json"})
        _data = json.dumps(config['spec'])
        _sharePath = config['spec']['path']
        _url = self.sharesUrl
        _params = {"zone": zone}

        try:
            _response = self.session.post(url=self.sharesUrl, cookies=self.cookies, headers=_headers, params=_params, data=_data)
            _response.raise_for_status()
            logger.info(f"Share named {_sharePath} for path: {_sharePath} has been created!")
        except Exception as e:
            print(_response.url)
            logger.error(f"Share named {_sharePath} for path: {_sharePath} failed!")
            logger.error(e)
            return False

        return True
    
    def delete_share(self, zone = None, id = None):
        if not (zone and id):
            logger.warning("No zone or share name is specified. Quiting...")
            return False
        
        # _zid = self.lookup_zid(zone)

        _url = self.sharesUrl + f"/{str(id)}"
        _params = {"zone": zone}

        try:
            _response = self.session.delete(url=_url, cookies=self.cookies, headers=self.headers, params=_params)
            _response.raise_for_status()
            logger.info(f"Share: {id} in zone: {zone} has been deleted!")
        except Exception as e:
            logger.error(f"Share: {id} in zone: {zone} could not be deleted!")
            logger.error(e)
            return False
        
        return True
    
    def lookup_zid(self, _zone = None):
        
        logger.info(f"Lookup zone id.")
        zone = Zone(self.auth)

        (zones, successful) = zone.get_zones()

        if successful: 
            if zones:
                for z in zones:
                    print(z['name'] , _zone)
                    if z['name'] == _zone:
                        _zid = z['zone_id']
            else:
                logger.info(f"Zones list is empty.")

            logger.info(f"Zones list is completed.")

        else:
            logger.error(f"Could not get zones list!")
            return False
        
        return _zid

if __name__ == "__main__":

    username = "root"
    # username = "papi"
    password = "password"
    baseUrl = "https://IP:8080"
    zone = "zone1"
    log_level = "debug"
    # papi_version = "16"
    papi_version = None
    id = "share15"
    
    # actions = ["shares_summary", "list_shares", "create_share", "delete_share"]
    actions = ["delete_share"]

    # Get the logger.
    logging.config.dictConfig(get_log_config(level=log_level))
    logger = logging.getLogger("module.papi.smb")

    # Instantiate SMB object.
    auth = Auth(username=username, password = password, baseUrl = baseUrl)
    smb = SMB(auth=auth, papi_version=papi_version)

    # Shares summary
    if "shares_summary" in actions:
        logger.info(f"SMB shares for zone: {zone} is requested.")

        (sharesSummary, successful) = smb.get_shares_summary(zone = zone)
        if successful: 
            if sharesSummary:
                logger.info(sharesSummary)
            else:
                logger.info(f"SMB shares summary is empty.")

            logger.info(f"SMB shares summary for zone: {zone} is completed.")
        else:
            logger.error(f"Could not get SMB shares summary!")

    # shares is a list of shares.
    if "list_shares" in actions:
        logger.info(f"SMB list for zone: {zone} is requested.")

        (shares, successful) = smb.get_shares(zone = zone)

        # Display attributes of each export from shares list.
        # list(map(print, [k for k in shares[0].keys()]))

        if successful: 
            if shares:
                for share in shares:
                    logger.info( " ".join( ["Share: ", str(share['zid']), str(share['id']), share['path'] ] ) )
            else:
                logger.info(f"SMB shares list is empty.")

            logger.info(f"SMB shares list for zone: {zone} is completed.")

        else:
            logger.error(f"Could not get SMB shares list!")

    ### Create a share.
    if "create_share" in actions:

        logger.info(f"SMB share creation is requested.")
        successful = smb.create_share(zone=zone)

        if successful: 
            logger.info(f"Share was created!")       
        else:
            logger.error(f"Share creation failed!")

    ### Delete a share.
    if "delete_share" in actions:
        logger.info(f"SMB export deletion is requested.")
        successful = smb.delete_share(zone=zone, id=id)

        if successful: 
            logger.info(f"Share was deleted!")       
        else:
            logger.error(f"Share deletion failed!")


    # Delete session
    logger.info(f"Session deletion was requested.")

    # Check the HTTP response code from delete_session(). If delete_session() gets an exception it sets the status code to False.
    if not auth.delete_session(): 
        logger.warning(f"Could not delete the session!")
    else:
        logger.info(f"Session deletion request was completed.")
