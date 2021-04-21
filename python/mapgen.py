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
	tile_mv_cost: float
	def __init__(self, x, y, e, p, t, id, mv_cost):
		self.xCord = x
		self.yCord = y
		self.elevation = e
		self.precipitation = p
		self.temperature = t
		self.tile_id = id
		self.tile_mv_cost = mv_cost

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
	tile_dict: dict
	def __init__(self, mapconfig):
		self.noise_config = wrappednoise.NoiseConfig(3,1,1)
		self.map_config = mapconfig
		self.tile_dict = generate_tile_dict(self.map_config, self.noise_config)

		self.edges: Dict[tuple, list[tuple]] = {}

		for tile in self.tile_dict:
			self.edges[tile] = list()
			for x in range (-1,2):
				for y in range(-1,2):
					if (tile[0]+x, tile[1]+y) in self.tile_dict and tile != (tile[0]+x,tile[1]+y) and self.tile_dict[tile].tile_type != "mountain":
						self.edges[tile].append((tile[0]+x,tile[1]+y))

		for coord, tile in self.tile_dict:
			tile.precipitation


	def neighbors(self, coord: tuple) -> list[int]:
		return self.edges[coord]

	def precipitation_calc(self, tile_list, tile_id):
		tileX = tile_list[tile_id].xCord
		tileY = tile_list[tile_id].yCord
		startpoint = tileX,tileY #python is strange yo. This is a tuple
		frontier = queue.PriorityQueue()
		frontier.put(0, startpoint)
		came_from = dict()
		cost_so_far = dict()
		came_from[startpoint] = null
		cost_so_far[startpoint] = 0
		nearest_ocean_coord: tuple

		while not frontier.empty():
			current = frontier.get()

			if tile_list[current[1]].tile_type == "ocean":
				nearest_ocean_coord = current[1]
				break
			for next in self.neighbors(current[1]):
				new_cost = cost_so_far[current[1]] + self.tile_dict[next].elevation
				if next not in cost_so_far or new_cost < cost_so_far[next]:
					cost_so_far[next] = new_cost
					priority = new_cost
					frontier.put(priority, next)
					came_from[next] = current[1]

		path = []
		current = nearest_ocean_coord
		distance = 0
		while current != startpoint:
			path.append(current)
			distance += self.tile_dict[current].elevation


		max_distance = 1000 #This is currently just an initial number. Once map sizes are decided upon this should scale with map size
		precipitation = 100 - distance/10
		return precipitation



@dataclass
class MapConfig:
	width: int
	height: int
	sea_level: float

def generate_tile_dict(mapconfig, noiseConfig) -> dict:
	settings = db.ConfigDB()
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
		temperature = math.cos(math.radians(y_to_lat_theta(float(y), float(mapconfig.height))))
		temperature = ((temperature + 1.0) * 100.0)/ 2.0
		alt_factor = (el-mapconfig.sea_level)/10.0
		temperature -= alt_factor
		if temperature > 100:
			temperature = 100.0
		if temperature < 0:
			temperature = 0
		tileDict[(x,y)] = MapTile(x,y,el,0,temperature, i, 0)
		tileDict[(x,y)].tile_mv_cost = settings.get_base_mv_cost(tileDict[(x,y)].tile_type)
		if el <= mapconfig.sea_level:
			tileDict[(x,y)].tile_type = "ocean"
		x += 1
	return tileDict

def y_to_lat_theta(y, map_height):
	old_range = map_height-1
	new_range = 360 #range of degrees for cos function, from -90 to 90
	#TODO: Protect against zeroes
	return ((y * new_range)/old_range) + -180




if __name__ == "__main__":
	map_config = MapConfig(20,11,40.0)
	new_map = MapGraph(map_config)
	database = db.MapDB()
	for cord, tile in new_map.tile_dict.items():
		database.add_tile(tile.tile_id, tile.xCord, tile.yCord, tile.elevation,\
			tile.precipitation, tile.temperature, tile.tile_type, tile.tile_mv_cost)
	database.save_to_file("test.world.db")

