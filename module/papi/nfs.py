import requests, os, sys, pathlib, json
import logging.config

# Add module path to sys.path.
modulePath = os.path.abspath(pathlib.Path(__file__).resolve().parents[2])
sys.path.append(modulePath)
from module.logconf.logconf import get_log_config
from module.papi.auth import Auth

# Initiate logging.
logging.config.dictConfig(get_log_config())
logger = logging.getLogger(__name__)

class NFS(object):
    def __init__(self, auth = None):

        if type(auth) == None:
            _authenticated = False
        else:
            _authenticated = auth.authenticated
        
        if not _authenticated:
            logger.error("Not an authenticated session, quiting")
            sys.exit(1)

        logger.info("Authenticated session!")

        self.session = auth.session
        self.session.verify = auth.session.verify

        # Get necessary cookies and headers
        self.baseUrl = auth.baseUrl
        self.platformBaseUrl = self.baseUrl + "/platform/"
        self.cookies = auth.cookies
        self.headers = auth.headers
        
    def get_exports_summary(self, zone = "System"):
        _params = dict(zone=zone)
        _url = self.platformBaseUrl + "16" + "/protocols/nfs/exports-summary"
        
        try:
            
            # response = self.session.get(url = _url, cookies=self.cookies, headers=self.headers)
            response = self.session.get(url = _url, cookies=self.cookies, headers=self.headers, params=_params)
            print(response.url)
            response.raise_for_status()
            return json.loads(response.content)
        except Exception as e:
            print(e)
            return False
    
    def get_exports(self, zone = "system"):
        _params = dict(zone=zone)
        _url = self.platformBaseUrl + "16" + "/protocols/nfs/exports"
        
        try:
            # response = self.session.get(url = _url, cookies=self.cookies, headers=self.headers)
            response = self.session.get(url = _url, cookies=self.cookies, headers=self.headers, params=_params)
            print(response.url)
            response.raise_for_status()

            exports = json.loads(response.content)['exports']
            return exports

            #exports = {}
            #for exportObj in json.loads(response.content)['exports']:
            #    _export = {"id": exportObj["id"], "path": exportObj['paths'][0], "zone": exportObj['zone']}
            #    exports.update(_export)
                # print(f"{exportObj['id']} {exportObj['paths'][0]} {exportObj['zone']}")
            
            #print(exports)

        except Exception as e:
            print(e)
            return False
        
        
if __name__ == "__main__":

    username = "root"
    password = "Password77"
    baseUrl = "https://91.229.44.253:8080"

    auth = Auth(username=username, password = password, baseUrl = baseUrl)
    nfs = NFS(auth=auth)
    print(nfs.get_exports())
    # print(nfs.get_exports_summary())



