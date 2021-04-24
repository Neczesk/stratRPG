from PIL import Image, ImageDraw, ImageColor, ImageChops

import db
import helper

def tile_dict_to_type_lists(tile_dict, width, height) -> list:
	output = list()
	x=0
	y=0

	for y in range(0,height):
		row = list()
		for x in range(width):
			row.append(tile_dict[(x,y)].tile_type)
		output.append(row)
	return output

def type_list_to_color_list(type_list) -> list:
	settings_db = db.ConfigDB()
	output = list()
	for t in type_list:
		output.append("#" + settings_db.get_type_color(t))
	return output

def draw_terrain_map(color_lists, path, scale):
	with Image.new("RGB",(len(color_lists[0])*scale, len(color_lists)* scale)) as im:
		draw = ImageDraw.Draw(im)
		for y,row in enumerate(color_lists):
			for x,tile in enumerate(row):
				
				draw.rectangle([(x*scale, y*scale), \
					((x+1)*scale, (y+1)*scale)], ImageColor.getrgb(tile))
		im.save(path, "PNG")

def draw_mountain_map(tile_dict, path, width, height, scale):
	with Image.new("RGB",(width*scale, height*scale)) as im:
		draw = ImageDraw.Draw(im)
		for coord, tile in tile_dict.items():
			if tile.tile_type == "mountain":
				draw.rectangle([(coord[0]*scale, coord[1]*scale), \
					((coord[0]+1)*scale, (coord[1]+1)*scale)], ImageColor.getrgb("#FFFFFF"))
			else:
				draw.rectangle([(coord[0]*scale, coord[1]*scale), \
					((coord[0]+1)*scale, (coord[1]+1)*scale)], ImageColor.getrgb("#000000"))
		im.save(path, "PNG")

def draw_height_map(tile_dict, path, width, height, scale):
	with Image.new("RGB",(width*scale, height*scale)) as im:
		draw = ImageDraw.Draw(im)
		for coord, tile in tile_dict.items():
			el = round(tile.elevation, -1)
			value = int(el)
			# value = 100 - value
			draw.rectangle([(coord[0]*scale, coord[1]*scale), \
				((coord[0]+1)*scale, (coord[1]+1)*scale)], ImageColor.getrgb("hsv(0,0%,"+str(value)+"%)"))
		im.save(path, "PNG")

def create_physical_map(terrain_map_path, height_map_path, path):
	with Image.open(terrain_map_path) as terrain_map:
		with Image.open(height_map_path) as height_map:
			im = ImageChops.hard_light(terrain_map, height_map)
			im.save(path, "PNG")
