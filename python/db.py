import os
import sqlite3
from pathvalidate import is_valid_filename

class MapDB:
	def __init__(self, path=""):
		if path == "":
			self.dbcon = sqlite3.connect(':memory:')
		elif is_valid_filename(path) and path.endswith(".world.db"):
			source = sqlite3.connect(path)
			self.dbcon = sqlite3.connect(':memory:')
			source.backup(self.dbcon)
		else:
			#TODO: Implement errors and error handling for the database initialization
			print("error detected")

		self.dbcon.execute("CREATE TABLE tile (tile_id INTEGER PRIMARY KEY, tile_x \
			INTEGER NOT NULL, tile_y INTEGER NOT NULL, tile_elevation float NOT NULL,\
			 tile_precipitation INTEGER, tile_temp INTEGER, tile_type TEXT, \
			 tile_mv_cost FLOAT, UNIQUE(tile_x, tile_y));")

	def add_tile(self, id, x, y, elev, prec, temp, type, mv_cost):
		self.dbcon.execute("INSERT INTO tile VALUES \
			(?, ?, ?, ?, ?, ?, ?, ?)", (id, x, y, elev, prec, temp, type, mv_cost))
		self.dbcon.commit()
		#TODO: Error checking

	def save_to_file(self, path):
		if os.path.exists(path):
			os.remove(path)
		if is_valid_filename(path) and path.endswith(".world.db"):
			file = sqlite3.connect(path)
			self.dbcon.backup(file)
		else:
			print("error with file path")

class ConfigDB:
	def __init__(self, path="../config/map_settings.db"):
		self.dbcon = sqlite3.connect(path)

	def get_base_mv_cost(self, terrain) -> float:
		cur = self.dbcon.execute("SELECT type_base_mv_cost FROM tile_types WHERE type_name = ?;", (terrain,))
		results = list()
		for row in cur:
			results.append(row[0])
		if len(results) > 1 :
			print ("too many results for movement cost query")
		return results[0]

def main():
	condb = ConfigDB()
	print(condb.get_base_mv_cost("mountain"))

if __name__ == '__main__':
	main()

