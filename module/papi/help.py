import requests, os, sys, pathlib, json, yaml

# Add module path to sys.path.
modulePath = os.path.abspath(pathlib.Path(__file__).resolve().parents[2])
sys.path.append(modulePath)

from module.papi.auth import Auth

username = "root"
password = "Password77"
baseUrl = "https://91.229.44.253:8080"



class Help(object):
    def __init__(self, auth = None):

        if type(auth) == None:
            _authenticated = False
        else:
            _authenticated = auth.authenticated
        
        if not _authenticated:
            sys.exit(1)

        self.session = auth.session
        self.session.verify = auth.session.verify

        # Get necessary cookies and headers
        self.baseUrl = auth.baseUrl
        self.platformBaseUrl = self.baseUrl + "/platform/"
        self.cookies = auth.cookies
        self.headers = auth.headers

    def list_all_apis(self, filter = None):
        _params = dict(describe="", list="")

        response = self.session.get(url=self.platformBaseUrl, cookies=self.cookies, headers=self.headers, params=_params)
        response.raise_for_status()

        for key,value in json.loads(response.content).items():
            print(key, ": ")
            for api in value:
                if filter:
                    if filter.lower() in api:
                        print(api)

    def list_all_apis_for_version(self, version = 16):
        _params = dict(describe="", list="")
        _url = self.platformBaseUrl + str(version) + "/"

        response = self.session.get(url=_url, cookies=self.cookies, headers=self.headers, params=_params)
        response.raise_for_status()

        for key,value in json.loads(response.content).items():
            print(key, ": ")
            for api in value:
                print(api)

    def list_all_versions_for_a_resouce(self, resourcePath = "protocols/nfs/exports"):
        # _params = dict(describe="", list="")
        _url = self.platformBaseUrl + "versions/" + resourcePath
        print(self.url)

        response = self.session.get(url=_url, cookies=self.cookies, headers=self.headers)
        response.raise_for_status()
        
        for key,value in json.loads(response.content).items():
            print(key, ": ")
            for api in value:
                print(api)

    def documentation_for_a_resource(self, reosurcePath = "protocols/nfs/exports-summary"):
        # _params = {"describe":" ", "json":" "}
        _url = self.platformBaseUrl + reosurcePath + "?describe&json"
        
        # response = self.session.get(url=_url, cookies=self.cookies, headers=self.headers, params=_params)
        response = self.session.get(url=_url, cookies=self.cookies, headers=self.headers)

        response.raise_for_status()

        print(yaml.dump(json.loads(response.content.decode("utf-8"))))

        # print(response.content)

    def list_of_all_resources_for_a_feature(self, reosurcePath = "protocols/nfs/exports"):
        _params = dict(describe="", list="", all="")
        _url = self.platformBaseUrl + reosurcePath

        response = self.session.get(url=_url, cookies=self.cookies, headers=self.headers)
        response.raise_for_status()

        print(type(json.loads(response.content)))
        print(json.loads(response.content))
        

if __name__ == "__main__":

    auth = Auth(username=username, password = password, baseUrl = baseUrl)

    helper = Help(auth=auth)

    # helper.list_all_apis("nfs")
    # helper.list_all_apis_for_version(16)
    # helper.list_all_versions_for_a_resouce()
    helper.documentation_for_a_resource("protocols/nfs/exports")
    # helper.list_of_all_resources_for_a_feature()

        




