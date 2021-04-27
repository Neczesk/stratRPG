#Standard imports
import math
from dataclasses import dataclass
import queue
import statistics

#Local Imports
import wrappednoise
import db
import helper
import texgen

class MapTile:
	"""This class represents a single space on the map through which entities can move or exist on."""
	xCord: int
	yCord: int
	elevation: int
	precipitation: float
	temperature: float
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
		self.tile_type = "Unassigned"

	def calculate_type(self) -> str:
		if self.temperature <= 30:
			if self.precipitation <= 30:
				tile_type = "tundra"
			if self.precipitation > 30 and self.precipitation <= 70:
				tile_type = "boreal"
			if self.precipitation > 70:
				tile_type = "marsh"
		elif self.temperature > 30 and self.temperature <= 70:
			if self.precipitation <= 30:
				tile_type = "steppe"
			elif self.precipitation > 30 and self.precipitation <= 70:
				tile_type = "grassland"
			elif self.precipitation > 70:
				tile_type = "temperate_forest"
		elif self.temperature > 70:
			if self.precipitation <= 30:
				tile_type = "desert"
			elif self.precipitation > 30 and self.precipitation <= 70:
				tile_type = "savannah"
			elif self.precipitation > 70:
				tile_type = "tropical_forest"

		# if self.precipitation == 0:
		# 	tile_type = "test_no_prec"

		return tile_type

class MapGraph:
	tile_dict: dict
	def __init__(self, mapconfig):
		self.noise_config = wrappednoise.NoiseConfig\
		(mapconfig.octaves,mapconfig.freq,mapconfig.exp, \
			mapconfig.persistence)
		self.map_config = mapconfig
		self.tile_dict = self.generate_tile_dict(self.map_config, \
			self.noise_config)

		self.edges: Dict[tuple, list[tuple]] = {}
		self.generate_edges()
		
		prec_dict = self.precipitation_calc()
		for tile in self.tile_dict:
			self.tile_dict[tile].precipitation = prec_dict[tile]

		self.noise_modify_prec()
		self.noise_modify_temp()

		for coord, tile in self.tile_dict.items():
			if tile.tile_type == "Unassigned":
					tile.tile_type = tile.calculate_type()

		texgen.draw_mountain_map(self.tile_dict,\
				"mountain_map.png",self.map_config.width, \
				self.map_config.height, 50)

	def generate_edges(self):
		for coord, tile in self.tile_dict.items():
			self.edges[coord] = list()
			for y in range(-1,2):
				for x in range(-1,2):
					# print("Checking: " + str(x) + ", " + str(y))
					if (coord[0]+x, coord[1]+y) in self.tile_dict and\
					 (coord[0]+x, coord[1]+y) != coord:
						if self.tile_dict[coord[0]+x, \
						coord[1]+y].tile_type != "mountain":
							self.edges[coord].append((coord[0]+x, \
								coord[1]+y))

	def noise_modify_prec(self):
		prec_noise_config = wrappednoise.NoiseConfig\
		(map_config.prec_octaves, map_config.prec_freq, 1, \
			map_config.prec_persistence)
		prec_noise = wrappednoise.WrappedNoise(prec_noise_config)
		texgen.noise_visualize(prec_noise, self.map_config.width, self.map_config.height, 50, "prec_noise.png")

		for coord, tile in self.tile_dict.items():
			prec_mod = prec_noise.noise_at_point(coord[0], coord[1])
			prec_mod = helper.linearConversion(prec_mod, -1, 1, -30, 30)
			if abs(prec_mod) > 15:
				print("big noise mod")
			tile.precipitation += prec_mod
			tile.precipitation = helper.clamp(tile.precipitation, 0, 100)

	def noise_modify_temp(self):
		temp_noise_config = wrappednoise.NoiseConfig\
		(map_config.temp_octaves, map_config.temp_freq, 1,\
			map_config.temp_persistence)
		temp_noise = wrappednoise.WrappedNoise(temp_noise_config)

		for coord, tile in self.tile_dict.items():
			temp_mod = temp_noise.noise_at_point(coord[0], coord[1])
			temp_mod = helper.linearConversion(temp_mod, -1, 1, -30, 30)
			tile.temperature += temp_mod
			tile.temperature = helper.clamp(tile.temperature, 0, 100)



	def neighbors(self, coord: tuple) -> list[tuple]:
		return self.edges[coord]

	def precipitation_calc(self) -> dict:
		"""This function returns a dict of precipitation values using coordinates as keys.
		The algorithm starts by adding all ocean tiles to a queue, then removing the tiles that
		border land tiles. Then each tile neighboring one of the coastal ocean tiles has its distance
		to the ocean calculated and that tile is added to the queue. Then neighbors of those tiles and
		so forth. This seemed more performant than the main branch, where a path is found using dijkstra's
		algorithm to any ocean tile for every land tile.

		This actually did end up being roughly 4 times as fast for n = 20,000"""
		oceans = queue.Queue()
		q = queue.Queue()
		distance_dict = dict()

		#Get all ocean tiles
		for coord, tile in self.tile_dict.items():
			distance_dict[coord] = math.inf
			if tile.tile_type == "ocean":
				oceans.put(coord)
				distance_dict[coord] = 0

		#Loop through all ocean tiles and add ones that have at least one non-ocean neighbor to a new queue
		while not oceans.empty():
			coastal = False
			current = oceans.get()
			neighbors = self.neighbors((current))
			for neighbor in neighbors:
				if self.tile_dict[neighbor].tile_type != "ocean":
					coastal = True
					break
			if coastal:
				q.put(current)

		while not q.empty():
			current = q.get()
			neighbors = self.neighbors((current))
			for neighbor in neighbors:
				if self.tile_dict[neighbor].tile_type != "ocean":
					new_distance = distance_dict[current] + (self.tile_dict[neighbor].elevation-self.map_config.sea_level)
					if neighbor not in distance_dict or new_distance < distance_dict[neighbor]:
						distance_dict[neighbor] = new_distance
						q.put(neighbor)

		distance_scaling = 2.0 # This variable is used to scale the distances exponentially, 
								#increasing the weight of higher altitudes on the precipitation calculation
		distance_cutoff_percent = 0.5 #This variable sets a limit for 0 precipitation 
										#in terms of percentage of highest elevation on map
		for coord, distance in distance_dict.items():
			distance_dict[coord] = pow(distance_dict[coord], distance_scaling)
		distance_list = distance_dict.values()

		max_distance = max(distance_list)
		max_distance *= distance_cutoff_percent
		prec_dict = dict()
		for coord, distance in distance_dict.items():
			prec_dict[coord] = helper.linearConversion(distance, 0, max_distance, 0, 100)
			prec_dict[coord] = max(0,100 - prec_dict[coord])

		return prec_dict

	def temperature_calc(self, latitude, altitude) -> float:
		temperature = math.cos(math.radians(y_to_lat_theta(float(latitude), float(self.map_config.height))))
		temperature = helper.linearConversion(temperature, -1, 1, 0, 100)
		alt_factor = (altitude-self.map_config.sea_level)/2
		alt_factor = pow(alt_factor, 2)
		if altitude-self.map_config.sea_level < 0:
			alt_factor *= -1
		temperature -= alt_factor

		if temperature > 100:
			temperature = 100.0
		if temperature < 0:
			temperature = 0

		return temperature



	def generate_tile_dict(self, mapconfig, noiseConfig) -> dict:
		settings = db.ConfigDB()
		noise = wrappednoise.WrappedNoise(noiseConfig)
		tileDict = dict()
		x = 0
		y = 0
		base_noise = noise.produce_noise_list_percent(mapconfig.width,\
		 mapconfig.height)
		adjusted_noise = \
		noise.transform_noise_list(base_noise, 40, statistics.pstdev(base_noise))
		for i in range(0,mapconfig.width*mapconfig.height):
			
			if x >= mapconfig.width:
				x = 0
				y+=1
			el = adjusted_noise[i]
			temperature = self.temperature_calc(y,el)
			tileDict[(x,y)] = MapTile(x,y,el,0,temperature, i, 0)
			tileDict[(x,y)].tile_mv_cost = settings.get_base_mv_cost(tileDict[(x,y)].tile_type)
			if el <= mapconfig.sea_level:
				tileDict[(x,y)].tile_type = "ocean"
			if el >= mapconfig.mountain_level:
				tileDict[(x,y)].tile_type = "mountain"
			x += 1
		return tileDict








def y_to_lat_theta(y, map_height):
	old_range = map_height-1
	new_range = 360 #range of degrees for cos function, from -90 to 90
	#TODO: Protect against zeroes
	return ((y * new_range)/old_range) + -180




if __name__ == "__main__":
	settings_db = db.ConfigDB()
	map_config = settings_db.get_script_config("test")
	new_map = MapGraph(map_config)
	database = db.MapDB()
	type_list = texgen.tile_dict_to_type_lists(new_map.tile_dict, \
		map_config.width, map_config.height)
	color_list = list()
	for row in type_list:
		color_list.append(texgen.type_list_to_color_list(row))
	# print(color_list)
	texgen.draw_terrain_map(color_list, "map.png", 50)
	texgen.draw_height_map(new_map.tile_dict, "heightmap.png",map_config.width, map_config.height, 50)
	texgen.create_physical_map("map.png", "heightmap.png", "phys_map.png")
	for cord, tile in new_map.tile_dict.items():
		database.add_tile(tile.tile_id, tile.xCord, tile.yCord, tile.elevation,\
			tile.precipitation, tile.temperature, tile.tile_type, tile.tile_mv_cost)
	database.save_to_file("test.world.db")

