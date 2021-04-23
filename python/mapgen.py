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
		(mapconfig.octaves,mapconfig.freq,mapconfig.exp)
		self.map_config = mapconfig
		self.tile_dict = self.generate_tile_dict(self.map_config, self.noise_config)

		self.edges: Dict[tuple, list[tuple]] = {}

		self.generate_edges()
		ocean_present = False
		for tile in self.tile_dict:
			if self.tile_dict[tile].tile_type == "ocean":
				ocean_present = True
		if ocean_present:
			for tile in self.tile_dict:
				self.tile_dict[tile].precipitation = self.precipitation_calc(self.tile_dict, tile)
				if self.tile_dict[tile].tile_type == "Unassigned":
					self.tile_dict[tile].tile_type = self.tile_dict[tile].calculate_type()
		texgen.draw_mountain_map(self.tile_dict,\
				"mountain_map.png",self.map_config.width, self.map_config.height, 50)

	def generate_edges(self):
		for coord, tile in self.tile_dict.items():
			self.edges[coord] = list()
			for y in range(-1,2):
				for x in range(-1,2):
					# print("Checking: " + str(x) + ", " + str(y))
					if (coord[0]+x, coord[1]+y) in self.tile_dict and (coord[0]+x, coord[1]+y) != coord:
						if self.tile_dict[coord[0]+x, coord[1]+y].tile_type != "mountain":
							self.edges[coord].append((coord[0]+x, coord[1]+y))
						
					# else:
					# 	print("not added: " + str((coord[0]+ x, coord[1]+y)))
			# if len(self.edges[coord]) < 8:
			# 				print(coord)
			# 				print(self.edges[coord])





	def neighbors(self, coord: tuple) -> list[int]:
		return self.edges[coord]

	def precipitation_calc(self, tile_dict, tile_coord) -> float:
		"""This function uses pathfinding to find the adjusted distance--
		ie the total elevation of all tiles intervening--
		and that adjusted distance is then used to generate a precipitation rating
		between 0-100"""
		if tile_dict[tile_coord].tile_type == "ocean":
			return 100
		elif tile_dict[tile_coord].tile_type == "mountain":
			return 0
		startpoint = tile_coord
		#The following block is an implementation of Dijkstra's algorithm. The exit condition
		#is finding any ocean tile
		frontier = queue.PriorityQueue()
		frontier.put((0, startpoint))
		came_from = dict()
		cost_so_far = dict()
		came_from[startpoint] = None
		cost_so_far[startpoint] = 0

		nearest_ocean_coord: tuple
		i = 0
		while not frontier.empty():
			i+= 1
			if i >= self.map_config.width*self.map_config.height:
				print("loop ran more than " + str(i) + " times")
				break
			current = frontier.get()
			current = current[1]

			# print(current)
			if tile_dict[current].tile_type == "ocean":
				nearest_ocean_coord = current
				break
			for neighbor in self.neighbors(current):
				if len(self.neighbors(current)) < 8:
					if current[0] != 0 and current[0] != self.map_config.width-1 and current[1] != 0 and current[1] != self.map_config.height-1:
						print(str(current) + " " + str(len(self.neighbors(current))))
						print("Neighbors: " + str(self.neighbors(current)))
				new_cost = cost_so_far[current] + self.tile_dict[neighbor].elevation
				if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
					cost_so_far[neighbor] = new_cost
					priority = new_cost
					frontier.put((priority, neighbor))
					came_from[neighbor] = current

		path = []

		try: 
			current = nearest_ocean_coord
		except:
			print(tile_dict[tile_coord].elevation)
			print(tile_coord)
			print("invalid nearest ocean")
			if tile_coord == (199,99):
				texgen.draw_mountain_map(tile_dict,\
				"mountain_map.png",self.map_config.width, self.map_config.height, 50)
			return 0

		distance = 0
		i=0
		while current != startpoint:
			i+= 1
			if i >= 100:
				break
			path.append(current)
			distance += self.tile_dict[current].elevation
			if current not in came_from:
				print("path error")
				print(tile_coord)
				# print(path)
				# print(came_from)
				texgen.draw_mountain_map(tile_dict,"mountain_map.png",self.map_config.width, self.map_config.height, 50)
			current = came_from[current]
		neighbor_ocean = list()
		for neighbor in self.neighbors(tile_coord):
			if self.tile_dict[neighbor].tile_type == "ocean":
				neighbor_ocean.append(neighbor)
		if len(neighbor_ocean) > 0 and nearest_ocean_coord not in neighbor_ocean:
			print("current" + str(tile_coord))
			print("neighboring ocean: " + str(neighbor_ocean))
			print("found ocean: " + str(nearest_ocean_coord))
			print("path: " + str(path))


		max_distance = 10000 #This is currently just an initial number. Once map sizes are decided upon this should scale with map size
		precipitation = 100 - helper.linearConversion(distance, 0,1000,0,100)
		if precipitation < 0:
			precipitation = 0
		elif precipitation > 100:
			precipitation = 100
		return precipitation

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
	for cord, tile in new_map.tile_dict.items():
		database.add_tile(tile.tile_id, tile.xCord, tile.yCord, tile.elevation,\
			tile.precipitation, tile.temperature, tile.tile_type, tile.tile_mv_cost)
	database.save_to_file("test.world.db")

