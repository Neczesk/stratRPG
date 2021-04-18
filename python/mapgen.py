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
				self.tile_type "tundra"
			if self.precipitation > 30 and self.precipitation <= 70:
				self.tile_type "boreal"
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


def mapgen(width, height, noiseConfig):
	noisy = OpenSimplex(int(time.time()))
	tileList = []
	x = 0
	y = 0
	for i in range(0,width*height):
		if x >= width:
			x = 0
			y++
		tileList[i] = MapTile(x,y,0,0,0)
