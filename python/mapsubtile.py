class MapSubTile:
	"""This class represents the smallest, indivisible points on the map. Entities can move through these subtiles and structures can exist on them."""
	def __init__(self, elevation, tile, x, y, id):
		self.subcoord = (x,y)
		self.globalcoord = ((tile.xCord*5 + x), (tile.yCord*5 + y))
		self.elevation = elevation
		self.subtile_type = "Unassigned"
		self.parent = tile
		self.id = id
		self.mv_mod = 0