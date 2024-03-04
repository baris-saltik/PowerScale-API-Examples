import os, sys, pathlib, json, pathlib, yaml, requests
import logging.config

# Add module path to sys.path.
modulePath = os.path.abspath(pathlib.Path(__file__).resolve().parents[2])
sys.path.append(modulePath)
from module.logconf.logconf import get_log_config
from module.papi.auth import Auth

# Get logger logging.
logger = logging.getLogger(__name__)

class NFS(object):
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
            self.exportsUrl = self.platformBaseUrl + "protocols/nfs/exports"
            self.exportsSummaryUrl = self.platformBaseUrl + "/protocols/nfs/exports-summary"
        else:
            self.exportsUrl = self.platformBaseUrl + str(papi_version) + "/protocols/nfs/exports"
            self.exportsSummaryUrl = self.platformBaseUrl + str(papi_version) + "/protocols/nfs/exports-summary"
        self.cookies = auth.cookies
        self.headers = auth.headers
        
    def get_exports_summary(self, zone = "System"):
        _params = dict(zone=zone)
     
        try:
            # response = self.session.get(url = _url, cookies=self.cookies, headers=self.headers)
            _response = self.session.get(url = self.exportsSummaryUrl, cookies=self.cookies, headers=self.headers, params=_params)
            _response.raise_for_status()
            logger.debug(f"NFS exports summary for zone: {zone}: " + json.dumps(json.loads(_response.content)))
            
        except Exception as e:
            logger.error("NFS Exports summary failed!")
            logger.error(e)
            return False, False
    
        return json.loads(_response.content), True
    
    def get_exports(self, zone = "system"):
        _params = dict(zone=zone)
        
        try:
            # response = self.session.get(url = _url, cookies=self.cookies, headers=self.headers)
            _response = self.session.get(url = self.exportsUrl, cookies=self.cookies, headers=self.headers, params=_params)
            _response.raise_for_status()
            exports = json.loads(_response.content)['exports']
            for export in exports:
                logger.debug( " ".join( ["Export: ", export['zone'], str(export['id']), export['paths'][0], ",".join( export['security_flavors'] ) ] ) )
            
        except Exception as e:
            logger.error(f"NFS exports list request for zone: {zone} could not be completed!")
            logger.error(e)
            return False, False
        
        return exports, True
    
    def create_export(self, config = False, zone = None):
        if not (config and isinstance(dict, config)):
            configFilePath = os.path.abspath(os.path.join(pathlib.Path(__file__).resolve().parents[2], "conf/papi_objects/create_export.yaml"))

            if configFilePath and os.path.isfile(configFilePath):
                with open(configFilePath, "r") as file:
                    content = file.read()
                
                try:
                    config = yaml.load(content,Loader=yaml.Loader)['spec']
                except Exception as e:
                    logger.error("Configuration for the object could not be obained. Quiting...")
                    return False
                
        # If zone specified in the arguments then overwrite the zone value in the config dictionary.
        if zone:
            config['zone'] = zone

        # Request payload type will be of json.
        # This sets the respective header to inform the server that the payload is json formatted string.
        _headers = self.headers
        _headers.update({"Content-Type": "application/json"})
        _data = json.dumps(config)

        try:
            _response = self.session.post(url=self.exportsUrl, cookies=self.cookies, headers=_headers, data=_data)
            _response.raise_for_status()
            logger.info(f"Export for path: {config['paths'][0]} has been created!")
        except Exception as e:
            logger.error(f"Export creation for path: {config['paths'][0]} failed!")
            logger.error(e)
            return False

        return True
    
    def delete_export(self, zone = None, id = None):
        if not (zone and id):
            logger.warning("No zone or export id is specified. Quiting...")
            return False
        
        _url = self.exportsUrl + f"/{str(id)}"

        try:
            _response = self.session.delete(url=_url, cookies=self.cookies, headers=self.headers)
            _response.raise_for_status()
            logger.info(f"Export with id: {id} in zone: {zone} has been deleted!")
        except Exception as e:
            logger.error(f"Export with id: {id} in zone: {zone} could not be deleted!")
            logger.error(e)
            return False
        
        return True


if __name__ == "__main__":

    # username = "root"
    username = "papi"
    # password = "Password77"
    password = "3"
    # baseUrl = "https://91.229.44.253:8080"
    # baseUrl = "https://91.229.44.232:8080"
    # baseUrl = "https://192.168.184.141:8080"
    baseUrl = "https://192.168.184.144:8080"
    zone = "zone1"
    log_level = "info"
    papi_version = 16
    # papi_version = None
    id = "2"
    
    # actions = ["exports_summary", "list_exports", "create_export", "delete_export"]
    actions = ["delete_export"]

    # Get the logger.
    logging.config.dictConfig(get_log_config(level=log_level))
    logger = logging.getLogger("module.papi.nfs")

    # Instantiate NFS object.
    auth = Auth(username=username, password = password, baseUrl = baseUrl)
    nfs = NFS(auth=auth, papi_version=papi_version)

    # Exports summary
    logger.info(f"NFS exports for zone: {zone} is requested.")
    if "exports_summary" in actions:

        (exportsSummary, successful) = nfs.get_exports_summary(zone = zone)
        if successful: 
            if exportsSummary:
                logger.info(exportsSummary)
            else:
                logger.info(f"NFS summary is empty.")

            logger.info(f"NFS exports summary for zone: {zone} is completed.")
        else:
            logger.error(f"Could not get NFS exports summary!")

    # exports is a list of exports.
    if "list_exports" in actions:

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


    ### Create an export.
    if "create_export" in actions:

        logger.info(f"NFS export creation is requested.")
        successful = nfs.create_export(zone=zone)

        if successful: 
            logger.info(f"Export was created!")       
        else:
            logger.error(f"Export creation failed!")

    logger.info(f"Session deletion was requested.")

    ### Delete an export.
    if "delete_export" in actions:
        
        logger.info(f"NFS export deletion is requested.")
        successful = nfs.delete_export(zone=zone, id=id)

        if successful: 
            logger.info(f"Export was deleted!")       
        else:
            logger.error(f"Export deletion failed!")

    logger.info(f"Session deletion was requested.")

    # Check the HTTP response code from delete_session(). If delete_session() gets an exception it sets the status code to False.
    if not auth.delete_session(): 
        logger.warning(f"Could not delete the session!")
    else:
        logger.info(f"Session deletion request was completed.")
