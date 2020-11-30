import requests
from .staticmap import StaticMap
from .multistaticmap import MultiStaticMap

class Tileserver:
    def __init__(self, base_url: str):
        if not "http" in base_url:
            base_url = "http://" + base_url
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url

    @property
    def styles(self):
        return [style["id"] for style in requests.get(self.base_url + "styles").json()]

    def staticmap(self, **kwargs):
        return StaticMap(self, **kwargs)

    def multistaticmap(self, **kwargs):
        return MultiStaticMap(self)