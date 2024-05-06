import os
import json
import healpy as hp
from pathlib import Path

CACHE_TYPES = [
    "json",
    "fits"
]

class TMCache():

    def __init__(self, filename: str=None, cache_type=None):
        if cache_type not in CACHE_TYPES:
            raise ValueError(f"Invalid Cache Type: {cache_type}")

        self.cache_home = os.path.join(f"{Path.home()}", ".tmcache")
        self._set_cache_home()
        self.cache_path = os.path.join(self.cache_home, filename)
        self.cache_type = cache_type

        self.get_dict = {
            "json" : self._get_cached_json,
            "fits" : self._get_cached_fits
        }

        self.put_dict = {
            "json" : self._put_cached_json,
            "fits" : self._put_cached_fits
        }


    def get(self, **kwargs):
        if os.path.exists(self.cache_path):
            return self.get_dict[self.cache_type](**kwargs)
        else:
            return None


    def put(self, payload, overwrite=False, **kwargs):
        if not os.path.exists(self.cache_path) or overwrite:
            self.put_dict[self.cache_type](payload=payload, **kwargs)


    def _set_cache_home(self):
        if not os.path.exists(self.cache_home):
            os.makedirs(self.cache_home)


    def _get_cached_json(self, **kwargs):
        try:
            with open(self.cache_path, "r") as input_file:
                payload = json.load(input_file)
            return payload
        except:  # noqa: E722
            raise Exception("Error reading json cache")


    def _get_cached_fits(self, **kwargs):
        try:
            skymap = hp.read_map(self.cache_path)
            return skymap
        except:  # noqa: E722
            raise Exception("Error in reading cached fits file")


    def _put_cached_json(self, payload, **kwargs):
        try:
            with open(self.cache_path, "w") as output_file:
                json.dump(payload, output_file)
        except:  # noqa: E722
            raise Exception("Error in writing payload cache to json")

    
    def _put_cached_fits(self, payload, **kwargs):
        try:
            hp.write_map(self.cache_path, payload, **kwargs)
        except:  # noqa: E722
            raise Exception("Error in writing skymap cache")
