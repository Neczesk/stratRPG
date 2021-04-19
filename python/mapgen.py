

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

	def __init__(self, x, y, e, p, t):
		self.xCord = x
		self.yCord = y
		self.elevation = e
		self.precipitation = p
		self.temperature = t
		if self.elevation >= 90:
			self.tile_type = "mountain"
		elif self.temperature <= 30:
			if self.precipitation <= 30:
				self.tile_type = "tundra"
			if self.precipitation > 30 and self.precipitation <= 70:
				self.tile_type = "boreal"
			if self.precipitation > 70:
				self.tile_type = "marsh"
		elif self.temperature > 30:
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


def generate_tile_list(width, height, noiseConfig):
	noise = wrappednoise.WrappedNoise(noiseConfig)
	print(noise.noise_at_point(10, 20))
	tileList = []
	x = 0
	y = 0
	for i in range(0,width*height):
		
		if x >= width:
			x = 0
			y+=1
		el = noise.noise_at_point(x,y) + 1.0
		el = el * 50
		tileList.append(MapTile(x,y,el,0,0))
		x += 1
	return tileList

if __name__ == "__main__":
	config = wrappednoise.NoiseConfig(8, .008, 1)
	map_tiles = generate_tile_list(40,20, config)
	database = db.MapDB()
	for i in range(len(map_tiles)):
		database.add_tile(i, map_tiles[i].xCord, map_tiles[i].yCord, map_tiles[i].elevation,\
			map_tiles[i].precipitation, map_tiles[i].temperature, map_tiles[i].tile_type)
	database.save_to_file("test.world.db")