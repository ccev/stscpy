# stscpy (SwiftTileServerCachePY)

Very basic wrapper for Flo's tileserver (https://github.com/123FLO321/SwiftTileserverCache/).

#### `pip install stscpy`

```py
from tileserver import Tileserver

server = Tileserver("https://tiles.map.com") # initialize your tileserver with a base url

staticmap = server.staticmap(style="osm-bright", zoom=15) # create a static map
staticmap.add_marker(url="https://cdn.url.com/image.png", lat=12.345, lon=98.765) # add a marker
staticmap.add_circle(fill_color="#ffffff60", stroke_color="#ffffff", radius=80, lat=12.345, lon=98.765) # add a circle

from shapely.geometry import Polygon
poly = Polygon((...)) # make sure it's (lat, lon) not the other way around
staticmap.add_polygon(polygon=poly, fill_color="#ffffff60", stroke_color="#ffffff") # add a polygon
staticmap.add_polygon(path=[(1.23, 2.34), ...], fill_color="#ffffff60", stroke_color="#ffffff") # or without shapely

staticmap.auto_position() # set base zoom, latitude and longitude based on circles/markers/polygons

print(staticmap.get_url()) # get an URL to the Static Map (using pregenerate)
staticmap.get_image().show() # Returns the map as an PIL Image, then displays it
import json
print(json.dumps(staticmap.get_dict(), indent=4)) # print the Static Map as JSON



multimap = server.multistaticmap() # create a multistaticmap

multimap.grid[0].add_staticmap(staticmap) # add a staticmap to the first grid-field
multimap.grid[0].add_staticmap(server.staticmap(...), "bottom") # add another staticmap below

multimap.add_field("right") # Add another grid-field to the right
multimap.grid[1].add_staticmap(server.staticmap(...))) # create a staticmap in the 2nd field
multimap.grid[1].maps[0].add_marker(...) # add a marker to that staticmap

print(multimap.get_url()) # get_url(), get_image(), get_dict() are the same for multistaticmaps and staticmaps
```
