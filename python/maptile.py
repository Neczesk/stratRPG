#local imports
import db

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