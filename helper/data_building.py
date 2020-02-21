# Functions for building data structures and reading in stuff from csv files
# Class objects too
import pandas as pd
import parsing


from parsing import *

class FoodGroup:
	# Should really only be called when creating the init food group database
	def __init__(self, food_str, super_food_group=None, attr_dict={}):

		self.name = food_str

		self.super_food_group = super_food_group
		if super_food_group:
			# inherited stuff, should do stuff here
			pass

		# should use attr_dict to fill these out or something
		self.qualities = attr_dict
		# self.healthy = False
		# self.vegetarian = False
		# self.lactose_free = False
		# self.gluten_free = False
		# self.vegan = False
		# self.substitutes = [] # maybe consider not having substitutes, might be a lot of work

class Ingredient:

	def __init__(self, in_string):
		# in_string is "raw" string from 

		# Parse/Extract things
		str_dict = parsing.extract_ingredient(in_string)

		# Find FoodGroup
		self.food_group = data_building.find_food_group(str_dict["food_group"])

		# Extract quantities
		self.quantity = str_dict["quantity"]

		# Extract type of measurement
		self.measurement = str_dict["measurement"]

		# Extract qualifiers
		self.qualifiers = str_dict["qualifiers"]


	def is_quality(self, quality):
		# Check if ingredient is quality (vegetarian, vegan, healthy, gluten, lactose)
		# Return bool
		if quality in self.food_group.qualities:
			return self.food_group.qualities[quality]
		return False


	def multiply_quantity(self, quant=2):
		# Multiply ingredient quantity by quant
		# Returns nothing
		self.quantity *= quant

		# NOTE: Victor said this one might be tricky, so will likely need more debugging


	def make_quality(self, quality):
		# Makes an ingredient a specific type of quality

		# NOTE: might have to think about how to do this for e.g. flours
		# Do we create an "alternate" food gorup where the main difference is we add gluten-free?
		# Do we just look for a substitute thing that has that alternate quality

		# Return nothing
		return


class Step:

	def __init__(self, method, ingredients):
		# 
		pass



class RecipeObject:

	def __init__(self, url_link):

		soup = parsing.get_page(page_link)

		print("TITLE")
		title_text = parsing.get_title(soup)
		print(title_text)
		self.orig_title = title_text


		print("\nINGREDIENTS")
		ingreds = parsing.get_ingredients(soup)
		print(ingreds)
		# Make ingredient list
		self.ingred_list = []


		# Get Prep Time
		print("\nPREP TIME")
		time_dict = parsing.get_preptime(soup)
		print(time_dict)
		self.time_dict = time_dict

		# Get Steps
		print("\nSTEPS")
		steps = parsing.get_steps(soup)
		print(steps)
		# Make steps list(have ingredients in these link to ones in ingredient list)
		self.steps = []

	

def make_fg_db(paths=["food_groups/meat.xlsx", "food_groups/carbs.xlsx"]):
	'''
	:param paths: list of paths for excel files, each containing a food group hierarchy
	:return: dictionary of dictionaries, each containing all properties and values as key-value pairs
				for each food group
	'''
	fg_dataframes = {}
	for path in paths:
		df = pd.read_excel(path, sheet_name=None)
		for k, v in df.items():
			fg_dataframes[k] = {}
			for index, row in v.iterrows():
				prop = row['property']
				val = row['value']
				if val == 'TRUE' or val == 'true':
					val = True
				elif val == 'FALSE' or val == 'false':
					val = False
				fg_dataframes[k][prop] = val
	return fg_dataframes



def find_food_group(food_str, fg_db):

	# Go through food group database, find corresponding food group
	# If no corresponding group found, might need to make a default food group (or exit error)

	return FoodGroup("blank")

