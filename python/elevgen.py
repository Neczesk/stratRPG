#Standard library
import math
import statistics
import random

#local imports
import wrappednoise
import helper
import db
import texgen

def generate_elevation_list(mapconfig, subtileratio) -> list:
	noise_config = wrappednoise.NoiseConfig(8, 0.01, 0.5, 0.5, 1)
	noise = wrappednoise.WrappedNoise(noise_config)
	# noise.conf.freq *= (1/subtileratio) #This should convert this to a subtile elevation list, which can then be averaged if needed for a tile elevation list
	output = list()
	for y in range(0,mapconfig.height*subtileratio):
		for x in range(0,mapconfig.width*subtileratio):
			percent = noise.noise_at_point(x, y)
			if percent > 1 or percent < -1:
				print("noise outside bounds")
			percent = helper.linearConversion(percent, -1, 1, 0, 100)
			output.append(percent)

	return output

def generate_tile_elevation_list(subtile_elevations, subtileratio) -> list:
	output = list()
	i = 0
	while i < len(subtile_elevations):
		k = i + int(math.pow(subtileratio, 2))
		next_tile = subtile_elevations[i:k]
		mean = statistics.mean(next_tile)
		output.append(mean)
		i += subtileratio

	return output


class continent:
	def __init__(self, origin):
		self.all_tiles = set()
		self.origin = origin
		self.all_tiles.add(origin)
		self.all_subtiles = set()

	def add_tile(self, new_tile):
		self.all_tiles.add(new_tile)

	def tiles_to_subtiles(self, subtileratio) -> list:
		subtiles = set()
		for tile in self.all_tiles:
			for y in range(subtileratio):
				for x in range(subtileratio):
					subtile = ((tile[0]*subtileratio + x),(tile[1]*subtileratio + y))
					subtiles.add(subtile)
		# print(len(self.all_tiles))
		# print(len(subtiles))
		# print(self.all_tiles)
		return subtiles

	def grow_continent(self, generations):
		for i in range(generations):
			new_tiles = set()
			for tile in self.all_tiles:
				for y in range(-1,2):
					for x in range(-1,2):
					# print("Checking: " + str(x) + ", " + str(y))
						if (tile[0]+x, tile[1]+y) != tile:
							new_tiles.add((tile[0]+x, tile[1]+y))
			self.all_tiles.update(new_tiles)



def generate_new_subtile_elevation_dict(mapconfig) -> dict:
	length = mapconfig.width * mapconfig.height * int((math.pow(mapconfig.subtiles, 2)))
	output = dict()
	for y in range(mapconfig.height*mapconfig.subtiles):
		for x in range(mapconfig.width * mapconfig.subtiles):
			output[(x,y)] = 0
	continents = list()
	for i in range(mapconfig.num_continents):
		continents.append(create_continent((random.randrange(int(mapconfig.width/2)) + int(mapconfig.width/4), random.randrange(int(mapconfig.height/2)) + int(mapconfig.height/4)), random.randrange(10,20)))
		continents[i].all_subtiles = continents[i].tiles_to_subtiles(mapconfig.subtiles)
		new_elevations = raise_continent_to_elevation(continents[i], 50)
		output.update(new_elevations)
	return output

def raise_continent_to_elevation(continent, elevation) -> dict:
	output = dict()
	for subtile in continent.all_subtiles:
		output[subtile] = elevation
	# print(len(output))
	# print(output)
	return output

def create_continent(origin, size):
	new_continent = continent(origin)
	new_continent.origin = origin
	current = origin
	old_heading = (0,1) #Right now it defaults to having placed the startpoint going north. This will be randomly generated at some point
	new_heading = (0,0)
	for i in range(size):
		heading = random.randrange(0,8) #this integer represents a heading relative to old_heading. 0 = left, 1-2 = forward, 3 = right
		if heading < 2:
			new_heading = (old_heading[1], old_heading[0]*-1)
			current = helper.add_coordinates(current, new_heading)
		elif heading < 6:
			new_heading = old_heading
			current = helper.add_coordinates(current, new_heading)
		else:
			new_heading = (old_heading[1]*-1, old_heading[0])
			current = helper.add_coordinates(current, new_heading)
		if current[0] < 0:
			print("continent tile out of bounds")
		new_continent.add_tile(current)
	new_continent.grow_continent(1)
	return new_continent


def main():
	settings = db.ConfigDB()
	mapconfig = settings.get_script_config("test")
	settings.close()
	el_dict = generate_new_subtile_elevation_dict(mapconfig)
	# print(len(el_dict))
	texgen.draw_elevation_map(el_dict, "elev_map.png", mapconfig.width*mapconfig.subtiles, mapconfig.height*mapconfig.subtiles, 20)
	# print(el_dict)



if __name__ == '__main__':
	main()
