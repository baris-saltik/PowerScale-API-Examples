import requests, os, sys, pathlib, json
import logging.config

# Add module path to sys.path.
modulePath = os.path.abspath(pathlib.Path(__file__).resolve().parents[2])
sys.path.append(modulePath)
from module.logconf.logconf import get_log_config

# Get logger.
logger = logging.getLogger(__name__)

class Auth(object):

    def __init__(self, username, password, baseUrl, ca_cert = "CACertFile.crt"):

        self.authenticated = False
        self.username = username
        self.password = password
        self.baseUrl = baseUrl
        self.sessionUrl = baseUrl + "/session/1/session"
        ca_cert_file_path = os.path.abspath(os.path.join(pathlib.Path(__file__).resolve().parents[2], "conf", "ca_certificates", ca_cert))

        _headers = {"Content-Type": "application/json"}
        _data = json.dumps(dict(username=self.username, password=self.password, services=["platform", "namespace"]))


        self.session = requests.Session()
        self.session.verify = ca_cert_file_path
        # Uncomment following to disable ca certification verification.
        # self.session.verify = False

        try:
            response = self.session.post(url=self.sessionUrl, headers=_headers, data=_data)
            print(response.url)
            response.raise_for_status()
            self.authenticated = True
            logger.info(f"Authentication succeeded for user: {self.username}!")
        except Exception as e:
            logger.error(f"Authentication failed for user: {self.username}!")
            logger.error(e)
            sys.exit()

        self.isisessid = response.cookies.get("isisessid")
        self.isicsrf = response.cookies.get("isicsrf")

        # Create necessary cookies and headers
        self.cookies = dict(isisessid=self.isisessid)
        self.headers = {"X-CSRF-Token": self.isicsrf}
        self.referer = {'referer': self.baseUrl}
        self.headers.update(self.referer)

    def get_session_info(self):
        try:
            response = self.session.get(url=self.sessionUrl, cookies=self.cookies, headers=self.headers)
            response.raise_for_status()
            logger.debug(f"Session information: {json.loads(response.content)}")
            
        except Exception as e:
            logger.error(f"Session info could not be acquired for session id: f{self.isisessid}")
            logger.error(e)
            return False, False

        return(json.loads(response.content), True)
    
    def delete_session(self):
        try:
            response = self.session.delete(url=self.sessionUrl, cookies=self.cookies, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Session was deleted for session id: {self.isisessid}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response status code: {response.status_code}")
            
        except Exception as e:
            logger.error(f"Session could not be deleted for {self.isisessid}")
            logger.error(e)
            return False

        return True

if __name__ == "__main__":

    log_level = "info"
    
    logging.config.dictConfig(get_log_config(level=log_level))
    logger = logging.getLogger("module.papi.auth")
    # logger.info(f"Logging test module.papi.auth")

    auth = Auth(username="user", password = "password", baseUrl="https://IP:8080")
    print(auth.get_session_info())
    print("#" * 100)
    print(auth.delete_session())



