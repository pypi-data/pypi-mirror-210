import json
import urllib.request

import pandas as pd


class Client(object):
    def __init__(self, base):
        self.BASE = base

    def get_report(self, experiments):
        BASE = self.BASE

        r = urllib.request.urlopen(
            f"{BASE}/analysis/mlexperiments/epochs/search",
            data=json.dumps({"experiments": experiments}).encode('utf8'),
            context=ssl._create_unverified_context()
        )
        r = json.loads(r.read())
        report = pd.DataFrame.from_dict(r['values'])
        report = report[['experiment', 'experiment_id', 'seed', 'epoch'] + [x for x in r['metrics'] if x not in ('experiment', 'epoch')]]
        parameters = r['parameters']
        # parameters = pd.DataFrame.from_dict(parameters)
        parameters = pd.DataFrame.from_dict(parameters, orient='index')
        parameters['experiment_id'] = [int(x) for x in parameters.index]
        return report, parameters
