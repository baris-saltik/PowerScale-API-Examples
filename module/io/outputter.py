import os, sys, pathlib, json, pathlib, yaml, requests, datetime
import logging.config

# Add module path to sys.path.
modulePath = os.path.abspath(pathlib.Path(__file__).resolve().parents[2])
sys.path.append(modulePath)

# Get logger logging.
logger = logging.getLogger(__name__)

class Output(object):

    def __init__(self, items):

        self.outputPath = os.path.abspath( os.path.join( pathlib.Path(__file__).resolve().parents[2], "output" ))
        os.makedirs(self.outputPath, exist_ok=True)

        self._items = items
        self._listExportsFile = os.path.abspath(os.path.join(self.outputPath, "list_exports.yaml"))
        self._listSharesFile = os.path.abspath(os.path.join(self.outputPath, "list_shares.yaml"))

    def list_exports(self):

        # Reference to self._items: ["Export: ", export['zone'], str(export['id']), export['paths'][0], ",".join( export['security_flavors']
        _outPut = {}
        _outPut.update({"version": "v1"})

        _spec = {}
        _specItems = []

        _metadata = {}
        
        _outPut["metadata"] = {"zone": self._items[0]["zone"]}

        _now = datetime.datetime.now()
        _date_time = _now.strftime("%m/%d/%YT%H:%M:%S")

        _outPut["metadata"].update({"time": _date_time})
        _outPut["metadata"].update({"status": "success"})

        for i in self._items:
            
            _ = {}
            _["id"] = i["id"]
            _["path"] = i["paths"][0]
            _["security_flavors"] = ["security_flavors"]
            _specItems.append(_)

        _outPut["spec"] = {"exports": _specItems}

        logging.debug(_outPut)

        with open(self._listExportsFile, "w") as file:
            file.write(yaml.dump(_outPut))

        return True

    def list_shares(self):

        # Reference to self._items: ["Share: ", str(share['zid']), str(share['id']), share['path'] ]
        _outPut = {}
        _outPut.update({"version": "v1"})

        _spec = {}
        _specItems = []

        _metadata = {}
        
        _outPut["metadata"] = {"zone": self._items[0]["zid"]}

        _now = datetime.datetime.now()
        _date_time = _now.strftime("%m/%d/%YT%H:%M:%S")

        _outPut["metadata"].update({"time": _date_time})
        _outPut["metadata"].update({"status": "success"})

        for i in self._items:
            
            _ = {}
            _["id"] = i["id"]
            _["path"] = i["path"]
            _specItems.append(_)

        _outPut["spec"] = {"shares": _specItems}

        logging.debug(_outPut)

        with open(self._listSharesFile, "w") as file:
            file.write(yaml.dump(_outPut))

        return True
        # _outPutYaml = yaml.dump(_outputDict)


        




