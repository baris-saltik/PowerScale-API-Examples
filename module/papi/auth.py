import requests, os, sys, pathlib, json, re
import logging.config

# Add module path to sys.path.
modulePath = os.path.abspath(pathlib.Path(__file__).resolve().parents[2])
sys.path.append(modulePath)
from module.logconf.logconf import get_log_config

# Initiate logging.
logging.config.dictConfig(get_log_config())
logger = logging.getLogger(__name__)

class Auth(object):

    def __init__(self, username, password, baseUrl, ca_cert_file_name = "FileOrbisTrustServices.crt"):

        self.auhtenticated = False
        self.username = username
        self.password = password
        self.baseUrl = baseUrl
        self.sessionUrl = baseUrl + "/session/1/session"
        ca_cert_file_path = os.path.abspath(os.path.join(pathlib.Path(__file__).resolve().parents[2], "conf", "ca_certificates", ca_cert_file_name))
        # sessionIdRex = re.compile(r"isisessid=(.*?);")

        _headers = {"Content-Type": "application/json"}
        _data = json.dumps(dict(username=self.username, password=self.password, services=["platform", "namespace"]))


        self.session = requests.Session()
        self.session.verify = ca_cert_file_path

        try:
            response = self.session.post(url=self.sessionUrl, headers=_headers, data=_data)
            response.raise_for_status()
            self.auhtenticated = True
            logger.info(f"Authentication succeeded for user: {self.username}!")
        except Exception as e:
            logger.error(f"Authentication failed for user: f{self.username}!")
            logger.error(e)
            sys.exit()


        # self.sessionId = sessionIdRex.search(response.headers["Set-Cookie"]).group(1)
        # self.csrfToken = response.headers["X-CSRF-Token"]

        self.isisessid = response.cookies.get("isisessid")
        self.isicsrf = response.cookies.get("isicsrf")

        self.cookies = dict(isisessid=self.isisessid)
        self.headers = {"X-CSRF-Token": self.isicsrf}
        self.referer = {'referer': self.baseUrl}
        self.headers.update(self.referer)

    def get_session_info(self):
        try:
            response = self.session.get(url=self.sessionUrl, cookies=self.cookies, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Session information for {self.isisessid}: {json.loads(response.content)}")
        except Exception as e:
            logger.error(f"Session info could not be acquired for session id: f{self.isisessid}")
            logger.error(e)
            return (False, False)

        return(json.loads(response.content), response.status_code)
    
    def delete_session(self):
        try:
            response = self.session.delete(url=self.sessionUrl, cookies=self.cookies, headers=self.headers)
            response.raise_for_status()
            logger.debug(f"Session was deleted for session id: {self.isisessid}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response status code: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Session could not be deleted for {self.isisessid}")
            logger.error(e)
            return False


if __name__ == "__main__":
    
    logger = logging.getLogger("module.papi.auth")
    # logger.info(f"Logging test module.papi.auth")

    auth = Auth(username="root", password = "Password77", baseUrl="https://91.229.44.253:8080")
    print(auth.get_session_info())
    print("#" * 100)
    print(auth.delete_session())



