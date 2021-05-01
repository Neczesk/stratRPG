import os
import sqlite3
from dataclasses import dataclass
from pathvalidate import is_valid_filename

@dataclass
class MapConfig:
	width: int
	height: int
	sea_level: float
	mountain_level: float
	num_continents: int
	num_mnts_per_continent: int
	wetness: float
	roughness: float
	subtiles: int


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
			INTEGER NOT NULL, tile_y INTEGER NOT NULL, tile_elevation DOUBLE NOT NULL,\
			 tile_precipitation INTEGER, tile_temp INTEGER, tile_type TEXT, \
			 tile_mv_cost FLOAT, UNIQUE(tile_x, tile_y));")

		self.dbcon.execute("CREATE TABLE subtile (subtile_id INTEGER PRIMARY KEY, subtile_x\
			INTEGER NOT NULL, subtile_y INTEGER NOT NULL, subtile_elevation DOUBLE NOT NULL,\
			subtile_type TEXT NOT NULL, subtile_mv_mod DOUBLE, tile_id INTEGER, FOREIGN KEY (tile_id) REFERENCES tile (tile_id), UNIQUE(subtile_x, subtile_y));")

	def add_tile(self, id, x, y, elev, prec, temp, type, mv_cost):
		self.dbcon.execute("INSERT INTO tile VALUES \
			(?, ?, ?, ?, ?, ?, ?, ?)", (id, x, y, elev, prec, temp, type, mv_cost))
		self.dbcon.commit()
		#TODO: Error checking

	def add_subtile(self, id, x, y, elev, type, mv_mod, tile_id):
		self.dbcon.execute("INSERT INTO subtile VALUES \
			(?,?,?,?,?,?,?)",(id, x, y, elev, type, mv_mod, tile_id))
		self.dbcon.commit()

	def save_to_file(self, path):
		if os.path.exists(path):
			os.remove(path)
		if is_valid_filename(path) and path.endswith(".world.db"):
			file = sqlite3.connect(path)
			self.dbcon.backup(file)
		else:
			print("error with file path")

	def close(self):
		self.dbcon.close()

class ConfigDB:
	def __init__(self, path="../config/map_settings.db"):
		self.dbcon = sqlite3.connect(path)

	def get_base_mv_cost(self, terrain) -> float:
		cur = self.dbcon.execute("SELECT type_base_mv_cost FROM tile_types WHERE\
		 type_name = ?;", (terrain,))
		results = list()
		for row in cur:
			results.append(row[0])
		if len(results) > 1 :
			print ("too many results for movement cost query")
		return results[0]

	def get_type_color(self, t_type) -> str:
		cur = self.dbcon.execute("SELECT type_img_color FROM tile_types WHERE\
			type_name = ?;", (t_type,))
		results = list()
		for row in cur:
			results.append(row[0])
		if len(results) > 1:
			print ("too many results for color query")
		if len(results) == 0:
			print("no results found")
			print(t_type)
		return results[0]

	def get_subtile_type_color(self, t_type) -> str:
		cur = self.dbcon.execute("SELECT subtile_color FROM subtile_types WHERE\
			subtile_type = ?;", (t_type,))
		results = list()
		for row in cur:
			results.append(row[0])
		if len(results) > 1:
			print ("too many results for color query")
		if len(results) == 0:
			print("no results found")
			print(t_type)
		return results[0]


	def get_script_config(self, script):
		cur = self.dbcon.execute("SELECT script_width, script_height, \
			script_sea_level, script_mountain_level, script_num_continents, \
			script_num_mnts_per_continent, script_wetness, script_roughness, \
			script_subtiles FROM map_scripts \
			WHERE script_name = ?;", (script,))
		rows = list()
		for row in cur:
			rows.append(row)
		if len(rows) > 1:
			print("too many results for map_script query")
		results = rows[0]

		return MapConfig(results[0], results[1], results[2], results[3],\
			results[4], results[5], results[6], results[7], results[8])

	def close(self):
		self.dbcon.close()

def main():
	condb = ConfigDB()
	print(condb.get_base_mv_cost("mountain"))

if __name__ == '__main__':
	main()

