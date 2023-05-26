import os
import requests
import urllib.parse


class api():

    def __init__(self, target=None, token=None, base='v1'):

        self.base = f'https://treasuremap.space/api/{base}'
        self.target = target

        if token is None:
            self.token = os.getenv('GWTM_API_TOKEN')
        else:
            self.token = token

        self.request = None


    def _build_url(self):
        assert self.target is not None, 'Target cannot be None'
        self.url = '{}/{}'.format(self.base, self.target)


    def _post(self, r_json):
        self._build_url()
        data = r_json['data'] if 'data' in r_json.keys() else None
        files = r_json['files'] if 'files' in r_json.keys() else None
        d_json = r_json['d_json'] if 'd_json' in r_json.keys() else None
        self.request = requests.post(self.url, json=d_json, data=data, files=files)
        return self.request


    def _get(self, r_json, urlencode=False):
        self._build_url()
        d_json = r_json['d_json'] if 'd_json' in r_json.keys() else None
        if urlencode:
            self.url = f"{self.url}?{urllib.parse.urlencode(d_json)}"
            self.request = requests.get(self.url)
        else:
            self.request = requests.get(self.url, json=d_json)
        return self.request


    def _put(self, r_json):
        self._build_url()
        d_json = r_json['d_json']
        self.request = requests.put(self.url, json=d_json)
        return self.request


    def _delete(self, r_json):
        self._build_url()
        d_json = r_json['d_json']
        self.request = requests.delete(self.url, json=d_json)
        return self.request
