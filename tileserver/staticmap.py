from .errors import MissingArgument, EndpointError, UnknownStyle

import json
import math
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import quote_plus

def convert_to_dict(dic):
    final = {}
    for k, v in dic.items():
        if k == "tileserver":
            continue
        if v is None or v == []:
            continue
        if isinstance(v, list) and k != "path":
            if isinstance(v[0], dict):
                v = [convert_to_dict(o) for o in v].copy()
            else:
                v = [convert_to_dict(o.__dict__) for o in v].copy()
        if isinstance(v, StaticMap):
            v = convert_to_dict(v.get_dict())
        final[k] = v
    return final

class _MapObject:
    def arg_check(self, arguments, kwargs):
        for argument in arguments:
            if not argument in kwargs.keys():
                raise MissingArgument(argument)

class Marker(_MapObject):
    def __init__(self, **kwargs):
        self.arg_check(["url", "lat", "lon"], kwargs)
        self.url = str(kwargs.get("url"))
        self.latitude = float(kwargs.get("lat"))
        self.longitude = float(kwargs.get("lon"))
        self.height = kwargs.get("height", 32)
        self.width = kwargs.get("width", 32)
        self.x_offset = kwargs.get("x_offset")
        self.y_offset = kwargs.get("y_offset")

class Circle(_MapObject):
    def __init__(self, **kwargs):
        self.arg_check(["fill_color", "stroke_color", "radius", "lat", "lon"], kwargs)
        self.stroke_width = kwargs.get("stroke_width", 1)
        self.fill_color = kwargs.get("fill_color")
        self.stroke_color = kwargs.get("stroke_color")
        self.radius = kwargs.get("radius")
        self.latitude = kwargs.get("lat")
        self.longitude = kwargs.get("lon")

class Polygon(_MapObject):
    def __init__(self, **kwargs):
        if kwargs.get("polygon") is not None:
            kwargs["path"] = []
            for lat, lon in kwargs["polygon"].exterior.coords:
                kwargs["path"].append([lat, lon])

        self.arg_check(["fill_color", "stroke_color", "path"], kwargs)
        self.stroke_width = kwargs.get("stroke_width", 1)
        self.fill_color = kwargs.get("fill_color")
        self.stroke_color = kwargs.get("stroke_color")
        self.path = kwargs.get("path")

class _BaseMap:
    @property
    def __type(self):
        if isinstance(self, StaticMap):
            return "staticmap"
        else:
            return "multistaticmap"

    def get_dict(self):
        return convert_to_dict(self.__dict__)

    def get_url(self, regeneratable=False):
        regen = "&regeneratable=true" if regeneratable else ""
        endpoint = self.tileserver.base_url + self.__type + "?pregenerate=true" + regen
        result = requests.post(endpoint, json=self.get_dict())

        if "error" in result.text:
            raise EndpointError(result.json().get("reason", "Unknown Tileserver error"))
        finished_url = self.tileserver.base_url + self.__type + "/pregenerated/" + result.text
        requests.get(finished_url)
        return finished_url

    def get_image(self):
        endpoint = self.tileserver.base_url + self.__type
        result = requests.post(endpoint, json=self.get_dict())

        return Image.open(BytesIO(result.content))

class StaticMap(_BaseMap):
    def __init__(self, tileserver, **kwargs):
        self.tileserver = tileserver

        self.style = str(kwargs.get("style", "osm-bright"))
        self.latitude = float(kwargs.get("lat", 0))
        self.longitude = float(kwargs.get("lon", 0))
        self.zoom = float(kwargs.get("zoom", 18))
        self.width = int(kwargs.get("width", 1000))
        self.height = int(kwargs.get("height", 500))
        self.scale = kwargs.get("scale", 1)
        self.format = kwargs.get("format")
        self.bearing = kwargs.get("bearing")
        self.pitch = kwargs.get("pitch")

        if not self.style in self.tileserver.styles:
            raise UnknownStyle(self.style)

    def center(self):
        center = {"lat": self.latitude, "lon": self.longitude}
        return center

    def add_marker(self, **kwargs):
        marker = Marker(**kwargs)
        try:
            self.markers.append(marker)
        except AttributeError:
            self.markers = [marker]

    def add_circle(self, **kwargs):
        circle = Circle(**kwargs)
        try:
            self.circles.append(circle)
        except AttributeError:
            self.circles = [circle]

    def add_polygon(self, **kwargs):
        polygon = Polygon(**kwargs)
        try:
            self.polygons.append(polygon)
        except AttributeError:
            self.polygons = [polygon]
    
    def auto_position(self, margin=1.06, default_zoom=17.5):
        objs = []
        try:
            objs += [(c.latitude, c.longitude) for c in self.circles]
        except AttributeError:
            pass
        try:
            objs += [(m.latitude, m.longitude) for m in self.markers]
        except AttributeError:
            pass
        try:
            objs += [(p[0], p[1]) for p in [p.path for p in self.polygons][0]]
        except AttributeError:
            pass
            
        if objs == []:
            return

        lats = [obj[0] for obj in objs]
        lons = [obj[1] for obj in objs]
        
        min_lat = min(lats)
        max_lat = max(lats)
        min_lon = min(lons)
        max_lon = max(lons)

        ne = [max_lat, max_lon]
        sw = [min_lat, min_lon]   

        ne = [c * margin for c in ne]
        sw = [c * margin for c in sw]

        if ne == sw:
            self.zoom = default_zoom
            self.latitude = lats[0]
            self.longitude = lons[0]
            return
        
        self.latitude = min_lat + ((max_lat - min_lat) / 2)
        self.longitude = min_lon + ((max_lon - min_lon) / 2)

        def latRad(lat):
            sin = math.sin(lat * math.pi / 180)
            rad = math.log((1 + sin) / (1 - sin)) / 2
            return max(min(rad, math.pi), -math.pi) / 2

        def zoom(px, fraction):
            return round(math.log((px / 256 / fraction), 2), 2)

        lat_fraction = (latRad(ne[0]) - latRad(sw[0])) / math.pi

        angle = ne[1] - sw[1] 
        if angle < 0:
            angle += 360
        lon_fraction = angle / 360

        self.zoom = min(zoom(self.height, lat_fraction), zoom(self.width, lon_fraction))

    def get_long_url(self, *, shorten=False, regeneratable=False, generate=False):
        first_url = self.base_url + "staticmap/"