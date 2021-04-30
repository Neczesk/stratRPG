#Standard imports
import math
from dataclasses import dataclass
import queue
import statistics
import decimal
import random

#Local Imports
import wrappednoise
import db
import helper
import texgen

class MapTile:
	"""This class represents a slightly larger region of the map, with a single climate."""
	def __init__(self, x, y, e, p, t, id, mv_cost):
		self.xCord = x
		self.yCord = y
		self.elevation = e
		self.precipitation = p
		self.temperature = t
		self.tile_id = id
		self.tile_mv_cost = mv_cost
		self.tile_type = "Unassigned"

	def calculate_type(self, settings) -> str:
		if self.elevation > settings.mountain_level:
			return "mountain"
		if self.elevation < settings.sea_level:
			return "ocean"
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
		else:
			print("error determining tile type")
			print(self.temperature)
			print(self.precipitation)

		# if self.precipitation == 0:
		# 	tile_type = "test_no_prec"

		return tile_type

	def change_type(self, new_type):
		self.tile_type = new_type
		settings = db.ConfigDB()
		self.mv_cost = settings.get_base_mv_cost(new_type)
		settings.close()

class MapSubTile:
	"""This class represents the smallest, indivisible points on the map. Entities can move through these subtiles and structures can exist on them."""
	def __init__(self, noise, tile, x, y, id):
		self.subcoord = (x,y)
		self.globalcoord = ((tile.xCord*5 + x), (tile.yCord*5 + y))
		self.elevation = noise.noise_at_point(float(self.globalcoord[0]), float(self.globalcoord[1]))
		self.subtile_type = "Unassigned"
		self.parent = tile
		self.id = id
		self.mv_mod = 0

class MapGraph:


	def __init__(self, mapconfig):
		self.tile_dict = dict()
		self.subtile_dict = dict()
		self.subtile_coord_max = 4
		self.noise_config = wrappednoise.NoiseConfig\
		(mapconfig.octaves,mapconfig.freq,mapconfig.exp, \
			mapconfig.persistence)
		self.map_config = mapconfig
		self.tile_dict = self.generate_tile_dict(self.map_config, \
			self.noise_config)

		self.edges: Dict[tuple, list[tuple]] = {}
		self.generate_edges()

		self.subtile_edges: Dict[tuple, list[tuple]] = {}
		self.generate_subtile_edges()
		# print(self.subtile_edges)
		
		prec_dict = self.precipitation_calc()
		for tile in self.tile_dict:
			self.tile_dict[tile].precipitation = prec_dict[tile]

		self.noise_modify_prec()
		self.noise_modify_temp()

		for coord, tile in self.tile_dict.items():
			if tile.tile_type == None:
				print("tile type is none before")
			if tile.tile_type == "Unassigned":
				new_type = tile.calculate_type(self.map_config)
				tile.change_type(new_type)
			if tile.tile_type == None:
				print("tile type is none after")

		for coord, tile in self.subtile_dict.items():
			new_type = self.calculate_subtile_type(tile)
			print(new_type)
			tile.subtile_type = new_type

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

	def generate_subtile_edges(self):
		for coord, subtile in self.subtile_dict.items():
			self.subtile_edges[coord] = list()
			for y in range(-1,2):
				for x in range(-1,2):
					# print("Checking: " + str(x) + ", " + str(y))
					if (coord[0]+x, coord[1]+y) in self.subtile_dict and\
					 (coord[0]+x, coord[1]+y) != coord:
						self.subtile_edges[coord].append((coord[0]+x, \
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
			if abs(temp_mod) > 30:
				print("abs temp mod exceeds 30")
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
		tile_dict = dict()
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
			tile_dict[(x,y)] = MapTile(x,y,el,0,temperature, i, 0)
			tile_dict[(x,y)].tile_mv_cost = settings.get_base_mv_cost(tile_dict[(x,y)].tile_type)
			if el <= mapconfig.sea_level:
				tile_dict[(x,y)].tile_type = "ocean"
			if el >= mapconfig.mountain_level:
				tile_dict[(x,y)].tile_type = "mountain"
			x += 1
		id = 0
		for coord, tile in tile_dict.items():
			for y in range(0, 5):
				for x in range(0,5):
					new_subtile = MapSubTile(noise, tile, x, y, i)
					self.subtile_dict[new_subtile.globalcoord] = new_subtile
					i += 1
		return tile_dict

	def check_coastal_subtile(self, subtile) -> bool:
		border_direction = None
		if subtile.subcoord[0] == 0 and subtile.subcoord[1] == 0:
			border_direction = "northwest"
		elif subtile.subcoord[0] == self.subtile_coord_max and subtile.subcoord[1] == 0:
			border_direction = "northeast"
		elif subtile.subcoord[0] == 0 and subtile.subcoord[1] == self.subtile_coord_max:
			border_direction = "southwest"
		elif subtile.subcoord[0] == self.subtile_coord_max and subtile.subcoord[1] == self.subtile_coord_max:
			border_direction = "southeast"
		elif subtile.subcoord[0] == 0:
			border_direction = "west"
		elif subtile.subcoord[0] == self.subtile_coord_max:
			border_direction = "east"
		elif subtile.subcoord[1] == 0:
			border_direction = "north"
		elif subtile.subcoord[1] == self.subtile_coord_max:
			border_direction = "south"
		else:
			return False
		tile = subtile.parent
		neighbor_coords = self.neighbors((tile.xCord, tile.yCord))
		ocean_neighbor_coords = [coord for coord in neighbor_coords if self.tile_dict[coord].tile_type == "ocean"]
		if len(ocean_neighbor_coords) == 0:
			return False
		directions = [tuple(map(lambda x, y: x - y, coord, (tile.xCord, tile.yCord))) for coord in ocean_neighbor_coords]
		dir_dict = {
			"northwest": (-1,-1),
			"north": (0, -1),
			"northeast": (1,-1),
			"west": (-1,0),
			"east": (1,0),
			"southwest": (-1,1),
			"south": (0,1),
			"southeast": (1,1)
		}
		if dir_dict.get(border_direction, "none") in directions:
			return True

	def get_subtile_neighbors(self, subtile) -> dict:
		return self.subtile_edges[subtile.globalcoord]

	def calc_desert_type(self, subtile) -> str:
		"""Random number for now, should eventually use a groundwater noise generator"""
		groundwater = random.randrange(30)
		if groundwater >= 28:
			return "oasis_desert"
		if self.check_coastal_subtile(subtile):
			return "coastal_desert"
		if (subtile.elevation - self.map_config.sea_level) > 25:
			return "badlands_desert"
		else:
			return "sandy_desert"

	def calc_savannah_type(self, subtile) -> str:
		groundwater = random.randrange(30)
		if groundwater >= 28:
			return "oasis_savannah"
		sub_prec = subtile.parent.precipitation + random.randrange(-10, 10)
		if sub_prec > 20:
			return "woodlands_savannah"
		if sub_prec > 10:
			return "serengeti_savannah"
		else:
			return "dry_savannah"

	def calc_tropical_rainforest_type(self, subtile) -> str:
		if (subtile.elevation - self.map_config.sea_level) > 30:
			return "cloud_rainforest"
		sub_prec = subtile.parent.precipitation + random.randrange(-10, 10)
		if sub_prec > 95:
			return "swamp_rainforest"
		else:
			return "base_rainforest"

	def calc_temperate_forest_type(self, subtile) -> str:
		if self.check_coastal_subtile(subtile):
			return "rainforest_temperate"
		if (subtile.elevation - self.map_config.sea_level) > 30:
			return "conifer_forest"
		else:
			return "deciduous_forest"

	def calc_grassland_type(self, subtile) -> str:
		if (subtile.elevation - self.map_config.sea_level) > 35:
			return "moors_grassland"
		sub_prec = subtile.parent.precipitation + random.randrange(-10, 10)
		if sub_prec > 50:
			return "meadow_grassland"
		else:
			return "prairie_grassland"

	def calc_steppe_type(self, subtile) -> str:
		neighboring_subtiles = [self.subtile_dict[coord] for coord in self.get_subtile_neighbors(subtile)]
		print(len(neighboring_subtiles))
		mean_el = statistics.mean([sub.elevation for sub in neighboring_subtiles])
		if subtile.elevation > mean_el:
			return "badlands_steppe"
		else:
			return "grasslands_steppe"

	def calc_marsh_type(self, subtile) -> str:
		if self.check_coastal_subtile(subtile):
			return "salt_marsh"
		if (subtile.parent.temperature + random.randrange(-10,10)) > 20:
			return "grassy_marsh"
		else:
			return "swamp_marsh"

	def calc_boreal_type(self, subtile) -> str:
		if (subtile.elevation - self.map_config.sea_level) > 30:
			return "spruce_forest"
		else:
			return "boreal_pine_forest"

	def calc_tundra_type(self, subtile) -> str:
		if subtile.parent.temperature < 10:
			return "glacier"
		if subtile.parent.precipitation < 10:
			return "cold_desert_tundra"
		else:
			return "base_tundra"

	def calc_mountain_type(self, subtile) -> str:
		if subtile.elevation > 95:
			return "glacier"
		if subtile.parent.temperature > 20:
			return "tropical_alpine"
		else:
			return "alpine"

	def calc_ocean_type(self, subtile) -> str:
		if (subtile.elevation - self.map_config.sea_level) > -10:
			return "shelf_ocean"
		if (subtile.elevation - self.map_config.sea_level) > -30:
			return "ocean"
		else:
			return "trench"

	switcher = {
		"ocean": calc_ocean_type,
		"mountain": calc_mountain_type,
		"tundra": calc_tundra_type,
		"boreal": calc_boreal_type,
		"marsh": calc_marsh_type,
		"steppe": calc_steppe_type,
		"grassland": calc_grassland_type,
		"desert": calc_desert_type,
		"temperate_forest": calc_temperate_forest_type,
		"savannah": calc_savannah_type,
		"tropical_forest": calc_tropical_rainforest_type
	}

	def calculate_subtile_type(self, subtile) -> str:
		"""Uses arguments to determine the subtile's type. Returns a type string"""
		"""This uses a dictionary of lambdas. Each defined function is used depending on the climate type of the parent tile."""
		return self.switcher.get(subtile.parent.tile_type, "Unassigned")(self, subtile)



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
	# print(new_map.tile_dict)
	color_list = list()
	for row in type_list:
		color_list.append(texgen.type_list_to_color_list(row))
	# print(color_list)
	new_map.check_coastal_subtile(new_map.subtile_dict[105, 29])
	texgen.draw_terrain_map(color_list, "map.png", 50)
	type_list = texgen.subtile_dict_to_type_lists(new_map.subtile_dict, map_config.width*new_map.subtile_coord_max, map_config.height*new_map.subtile_coord_max)
	subtile_color_list = list()
	for row in type_list:
		subtile_color_list.append(texgen.subtile_type_list_to_color_list(row))
	texgen.draw_terrain_map(subtile_color_list, "subtile.png", 10)
	texgen.draw_height_map(new_map.tile_dict, "heightmap.png",map_config.width, map_config.height, 50)
	texgen.create_physical_map("map.png", "heightmap.png", "phys_map.png")
	for cord, tile in new_map.tile_dict.items():
		database.add_tile(tile.tile_id, tile.xCord, tile.yCord, tile.elevation,\
			tile.precipitation, tile.temperature, tile.tile_type, tile.tile_mv_cost)
	for coord, subtile in new_map.subtile_dict.items():
		database.add_subtile(subtile.id, subtile.globalcoord[0], subtile.globalcoord[1], subtile.elevation, subtile.subtile_type, subtile.mv_mod, subtile.parent.tile_id)
	database.save_to_file("test.world.db")
	database.close()
	settings_db.close()


