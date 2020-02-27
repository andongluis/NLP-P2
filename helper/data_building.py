# Functions for building data structures and reading in stuff from csv files
# Class objects too

import pandas as pd
from . import parsing
from itertools import chain



def find_food_group(food_string, food_dicts):
    # Go through food group database, find corresponding food group
    # If no corresponding group found, might need to make a default food group (or exit error)

    food_group = None
    for d in food_dicts.values():
        if food_string in d:
            food_group = d[food_string]
    if not food_group:
        return food_string
    return food_group

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

    def __repr__(self):
        return f"Name: {self.name}, Super Group: {self.super_food_group}, Qualities: {self.qualities}"

    def __str__(self):
        return self.__repr__()

class Ingredient:

    def __init__(self, str_dict, recipe_obj):
        
        # Substitution dictionaries
        self.sub_dict = recipe_obj[2]
        
        # Food group dictionaries
        self.fg_db = recipe_obj[1]
        
        # Food group maps
        self.fg_maps = recipe_obj[0]

        # Original string name
        self.orig_name = str_dict["food_group"]

        # Find FoodGroup
        self.food_group = find_food_group(self.orig_name, recipe_obj[0])

        # Extract quantities
        self.quantity = str_dict["quantity"]

        # Extract type of measurement
        self.measurement = str_dict["measurement"]

        # Extract qualifiers
        self.qualifiers = str_dict["qualifiers"]

    def __repr__(self):
        return f"Name: {self.orig_name}, Quantity: {self.quantity} {self.measurement}, Qualifiers: {self.qualifiers}\n"

    def __str__(self):
        return self.__repr__()


    def is_quality(self, quality):
        # Check if ingredient is quality (vegetarian, vegan, healthy, gluten-free, lactose-free)
        # Return bool
        if self.food_group in self.fg_db:
            if quality in self.fg_db[self.food_group]:
                return self.fg_db[self.food_group][quality]
        return True


    def multiply_quantity(self, quant=2):
        # Multiply ingredient quantity by quant
        # Returns nothing
        self.quantity *= quant

        # NOTE: Victor said this one might be tricky, so will likely need more debugging


    def make_quality(self, quality):
        if not self.is_quality(quality):
            if quality in self.sub_dict:
                if self.orig_name in self.sub_dict[quality]:
                    self.orig_name = self.sub_dict[quality][self.orig_name]
            else:
                print('No default substitution for '+quality+' given.')
        # Makes an ingredient a specific type of quality

        # NOTE: might have to think about how to do this for e.g. flours
        # Do we create an "alternate" food gorup where the main difference is we add gluten-free?
        # Do we just look for a substitute thing that has that alternate quality

        # Return nothing
        return self


class Step:

    def __init__(self, orig_str, ingred_list):
        # 
        self.orig_string = orig_str
        place_dict = parsing.get_ingredients_step(step, ingred_list)
        self.placeholder_string = place_dict["string"]
        self.placeholders = place_dict["placeholders"]



class RecipeObject:

    def __init__(self, url_link):

        soup = parsing.get_page(url_link)

        self.food_group_dict = make_fg_db()

        print("TITLE")
        title_text = parsing.get_title(soup)
        print(title_text)
        self.orig_title = title_text


        print("\nINGREDIENTS")
        ingreds = parsing.get_ingredients(soup)
        print(ingreds)
        # Make ingredient list
        print(type(ingreds))
        ingred_list = list(chain.from_iterable([parsing.extract_ingredient(in_string) for in_string in ingreds]))

        self.ingred_list = [Ingredient(ingred) for ingred in ingred_list ]


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
        self.steps = [Step(step) for step in steps]



def make_fg_db(paths=["csv/meats.csv","csv/pasta_group.csv","substitutions/gluten-free.csv",
                      "food_groups/meat.xlsx", "food_groups/carbs.xlsx", "food_groups/fats.xlsx",
                      "food_groups/dairy.xlsx"]):
    '''
    :param paths: list of paths for excel files, each containing a food group hierarchy
    :return: dictionary of dictionaries, each containing all properties and values as key-value pairs
                for each food group
    '''
    binary = ['gluten', 'healthy', 'vegetarian']
    categorical = ['style']
    fg_dicts = {}
    fg_substitutions = {}
    fg_groups = {}
    for path in paths:
        if path[:3] == 'csv':
            df = pd.read_csv(path, encoding='latin1')
            fg_groups[path[4:-4]] = pd.Series(df.group.values, index=df.name).to_dict()
        elif path[-4:] == "xlsx":
            df = pd.read_excel(path, sheet_name=None)
            for k, v in df.items():
                fg_dicts[k] = {}
                for index, row in v.iterrows():
                    prop = row['property']
                    val = row['value']
                    if val == 'TRUE' or val == 'true':
                        val = True
                    elif val == 'FALSE' or val == 'false':
                        val = False
                    fg_dicts[k][prop] = val
        elif path[-3:] == "csv":
            df = pd.read_csv(path, encoding='latin1')
            fg_substitutions[path[14:-4]] = pd.Series(df.substitute.values, index=df.name).to_dict()
    return fg_groups, fg_dicts, fg_substitutions