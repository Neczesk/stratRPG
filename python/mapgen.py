#Standard imports
import math
from dataclasses import dataclass
import queue
#Local Imports
import wrappednoise
import db

class MapTile:
	"""This class represents a single space on the map through which entities can move or exist on."""
	xCord: int
	yCord: int
	elevation: int
	precipitation: int
	temperature: int
	tile_type: str
	tile_id: int

	def __init__(self, x, y, e, p, t, id):
		self.xCord = x
		self.yCord = y
		self.elevation = e
		self.precipitation = p
		self.temperature = t
		self.tile_id = id
		if self.elevation >= 90:
			self.tile_type = "mountain"
		elif self.temperature <= 30:
			if self.precipitation <= 30:
				self.tile_type = "tundra"
			if self.precipitation > 30 and self.precipitation <= 70:
				self.tile_type = "boreal"
			if self.precipitation > 70:
				self.tile_type = "marsh"
		elif self.temperature > 30 and self.temperature <= 70:
			if self.precipitation <= 30:
				self.tile_type = "steppe"
			elif self.precipitation > 30 and self.precipitation <= 70:
				self.tile_type = "grassland"
			elif self.precipitation > 70:
				self.tile_type = "temperate_forest"
		elif self.temperature > 70:
			if self.precipitation <= 30:
				self.tile_type = "desert"
			elif self.precipitation > 30 and self.precipitation <= 70:
				self.tile_type = "savannah"
			elif self.precipitation > 70:
				self.tile_type = "tropical_forest"

class MapGraph:
	tile_list: dict
	def __init__(self, mapconfig):
		noise_config = wrappednoise.NoiseConfig(3,1,1)
		map_config = MapConfig(20,11,40.0)
		tile_dict = generate_tile_dict(map_config, noise_config)

		self.edges: Dict[tuple, list[tuple]] = {}
		for tile in tile_dict:
			for x in range (-1,2):
				for y in range(-1,2):
					if (x,y) in tile_dict and ti

	def neighbors(self, coord: tuple) -> list[int]:
		return self.edges[coord]


@dataclass
class MapConfig:
	width: int
	height: int
	sea_level: float

def generate_tile_dict(mapconfig, noiseConfig) -> dict:
	noise = wrappednoise.WrappedNoise(noiseConfig)
	tileDict = dict()
	x = 0
	y = 0
	for i in range(0,mapconfig.width*mapconfig.height):
		
		if x >= mapconfig.width:
			x = 0
			y+=1
		el = noise.noise_at_point(x,y)
		el = wrappednoise.noise_to_percent(el)
		print(y_to_lat_theta(y, mapconfig.height))
		temperature = math.cos(math.radians(y_to_lat_theta(float(y), float(mapconfig.height))))
		temperature = ((temperature + 1.0) * 100.0)/ 2.0
		alt_factor = (el-mapconfig.sea_level)/10.0
		temperature -= alt_factor
		if temperature > 100:
			temperature = 100.0
		if temperature < 0:
			temperature = 0
		tileDict[(x,y)] = MapTile(x,y,el,0,temperature, i)
		if el <= mapconfig.sea_level:
			tileDict[(x,y)].tile_type = "ocean"
		x += 1
	return tileDict

def y_to_lat_theta(y, map_height):
	old_range = map_height-1
	new_range = 360 #range of degrees for cos function, from -90 to 90
	#TODO: Protect against zeroes
	return ((y * new_range)/old_range) + -180

def precipitation_calc(tile_list, tile_id):
	tileX = tile_list[tile_id].xCord
	tileY = tile_list[tile_id].yCord
	startpoint = tileX,tileY #python is strange yo. This is a tuple
	frontier = queue.PriorityQueue()
	frontier.put()

	return precipitation


if __name__ == "__main__":
	config = wrappednoise.NoiseConfig(3, 1, 1)
	map_config = MapConfig(20,11,40.0)
	map_tiles = generate_tile_dict(map_config, config)
	database = db.MapDB()
	for cord, tile in map_tiles.items():
		database.add_tile(tile.tile_id, tile.xCord, tile.yCord, tile.elevation,\
			tile.precipitation, tile.temperature, tile.tile_type)
	database.save_to_file("test.world.db")

