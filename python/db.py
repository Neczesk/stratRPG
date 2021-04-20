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
			 UNIQUE(tile_x, tile_y));")

	def add_tile(self, id, x, y, elev, prec, temp, type):
		self.dbcon.execute("INSERT INTO tile VALUES \
			(?, ?, ?, ?, ?, ?, ?)", (id, x, y, elev, prec, temp, type))
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