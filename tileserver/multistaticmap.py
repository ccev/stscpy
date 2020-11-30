from .errors import EndpointError, WrongDirection
from .staticmap import StaticMap, _BaseMap, convert_to_dict

import requests

def check_direction(grid, direction):
    if len(grid) == 0:
        allowed = ["first"]
        default = "first"
    else:
        allowed = ["right", "bottom"]
        default = "right"

    if direction == "":
        return default
    else:
        if not direction in allowed:
            raise WrongDirection(direction, allowed)
        return direction

class MultiField:
    def __init__(self, direction: str):
        self.direction = direction
        self.maps = []
    
    def add_staticmap(self, staticmap: StaticMap, direction=""):
        direction = check_direction(self.maps, direction)
        self.maps.append({"direction": direction, "map": staticmap})

class MultiStaticMap(_BaseMap):
    def __init__(self, tileserver):
        self.tileserver = tileserver
        self.grid = [MultiField("first")]

    def add_field(self, direction=""):
        direction = check_direction(self.grid, direction)
        self.grid.append(MultiField(direction))