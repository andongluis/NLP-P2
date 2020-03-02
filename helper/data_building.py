# Functions for building data structures and reading in stuff from csv files
# Class objects too

import pandas as pd
import random
import os
import copy
from . import parsing
from itertools import chain



def find_food_group(food_string, food_dicts):
    # Go through food group database, find corresponding food group
    # If no corresponding group found, might need to make a default food group (or exit error)

    food_group = None
    for d in food_dicts.values():
        if food_string in d:
            return d[food_string]
    if not food_group:
        return food_string

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

        if self.quantity != 0:
            res = f"{self.quantity} "
            if self.measurement != "unit":
                res += f"{self.measurement} "
            for i in self.qualifiers:
                res += i + " "
            res += self.orig_name
        else:
            res = ""
            for i in self.qualifiers:
                res += i + " "
            res += self.orig_name
            res += ", to taste"
        return res


    def is_quality(self, quality):
        # Check if ingredient is quality (vegetarian, vegan, healthy, gluten-free, lactose-free)
        # Return bool
        if self.food_group in self.fg_db:
            if quality in self.fg_db[self.food_group]:
                return self.fg_db[self.food_group][quality]
        return False


    def multiply_quantity(self, quant=2):
        # Multiply ingredient quantity by quant
        # Returns nothing
        self.quantity *= quant
        return self

        # NOTE: Victor said this one might be tricky, so will likely need more debugging


    def make_quality(self, quality, food_dicts):
        if quality == 'healthy' and (self.food_group == 'condiment_group' or self.food_group == 'sweetener'):
            self = self.multiply_quantity(0.4)
        elif quality == 'unhealthy':
            if (self.food_group == 'sweetener' or self.food_group == 'fats' or
                                         (self.food_group in self.fg_db and
                                          self.fg_db[self.food_group]['food super group'] == 'fats')):
                self = self.multiply_quantity(1.25)
            elif self.food_group == 'vegetable':
                self = self.multiply_quantity(0.5)
        elif quality[:7] == 'country':
            if not self.is_quality(quality) and self.orig_name not in self.sub_dict[quality]:
                if quality in self.sub_dict:
                    if self.food_group in self.fg_db:
                        if self.food_group in self.sub_dict[quality].values() or \
                                self.fg_db[self.food_group]['food super group'] in self.sub_dict[quality].values():
                            list_of_options = [k for k, v in self.sub_dict[quality].items() if v == self.food_group or
                                               v == self.fg_db[self.food_group]['food super group']]
                            if len(list_of_options) > 0:
                                choice = random.choice(list_of_options)
                                self.food_group = find_food_group(choice, food_dicts)
                                self.orig_name = choice
                    else:
                        if self.food_group in self.sub_dict[quality].values():
                            list_of_options = [k for k, v in self.sub_dict[quality].items() if v == self.food_group]
                            if len(list_of_options) > 0:
                                choice = random.choice(list_of_options)
                                self.food_group = find_food_group(choice, food_dicts)
                                self.orig_name = choice
        else:
            if not self.is_quality(quality):
                if quality in self.sub_dict:
                    if self.orig_name in self.sub_dict[quality]:
                        self.orig_name = self.sub_dict[quality][self.orig_name]
                        self.food_group = find_food_group(self.orig_name, food_dicts)
                    elif self.food_group in self.sub_dict[quality]:
                        self.orig_name = self.sub_dict[quality][self.food_group]
                        self.food_group = find_food_group(self.food_group, food_dicts)
                else:
                    if self.food_group in self.fg_db:
                        found = False
                        while not found and self.fg_db[self.food_group]['food super group'] != self.food_group:
                            if quality+' substitute' in self.fg_db[self.food_group]:
                                found = True
                                self.orig_name = self.fg_db[self.food_group][quality+' substitute']
                                self.food_group = find_food_group(self.orig_name, food_dicts)
                            else:
                                self.food_group = self.fg_db[self.food_group]['food super group']
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

        quant_dict = parsing.get_quantities_step(orig_str)

        ingred_dict = parsing.get_ingredients_step(quant_dict["string"], ingred_list)



        self.placeholder_string = ingred_dict["string"]
        self.ingred_placeholders = ingred_dict["placeholders"]
        self.quant_placeholders = quant_dict["placeholders"]
        self.tools = parsing.get_tools(self.placeholder_string)
        self.methods = parsing.get_methods(self.placeholder_string)

        

    def __repr__(self):
        my_str = self.placeholder_string

        for place_key, ingred in self.ingred_placeholders.items():
            # print(ingred)
            my_str = my_str.replace(place_key, ingred["ingredient"].orig_name)


        for quant_key, quant in self.quant_placeholders.items():
            my_str = my_str.replace(quant_key, str(quant["quantity"]))

        return my_str.strip().capitalize()

    def __str__(self):
        return self.__repr__()

    def verbose_print(self):
        print(f"Orig String: {self.orig_string}")
        print(f"Tools: {self.tools}")
        print(f"Methods: {self.methods}")
        print(f"Placeholder str: {self.placeholder_string}")
        print(f"Ingred Placeholder dict: {self.ingred_placeholders}")
        print(f"Quant Placeholder dict: {self.quant_placeholders}")



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

def make_quality(quality, ingred_list, food_dicts):
    if quality == 'double':
        return [ing.multiply_quantity(2) for ing in ingred_list]
    elif quality == 'half':
        return [ing.multiply_quantity(1/2) for ing in ingred_list]
    else:
        if any(not ing.is_quality(quality) for ing in ingred_list):
            return [ing.make_quality(quality, food_dicts) for ing in ingred_list]
    return ingred_list

def slap_some_meat_on_there(ingred_list):
    for ing in ingred_list:
        ing_copy = copy.copy(ing)
        if ing_copy.food_group in ing_copy.fg_db:
            if ing_copy.food_group == 'meat':
                return False
            while ing_copy.fg_db[ing_copy.food_group]['food super group'] != ing_copy.food_group:
                ing_copy.food_group = ing_copy.fg_db[ing_copy.food_group]['food super group']
            if ing_copy.food_group == 'meat':
                return False
    return True

def make_fg_db():
    '''
    :param paths: list of paths for excel files, each containing a food group hierarchy
    :return: dictionary of dictionaries, each containing all properties and values as key-value pairs
                for each food group
    '''
    path_list = ['csv', 'substitutions', 'food_groups']
    paths = [l + '/' + d for l in path_list for d in os.listdir(l)]
    fg_dicts = {}
    fg_substitutions = {}
    fg_groups = {}
    for path in paths:
        if path[:3] == 'csv':
            df = pd.read_csv(path, encoding='latin1')
            print(path)
            print(list(df))
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
            if path[14:21] == 'country':
                fg_substitutions[path[14:-4]] = pd.Series(df.group.values, index=df.name).to_dict()
            else:
                fg_substitutions[path[14:-4]] = pd.Series(df.substitute.values, index=df.name).to_dict()
    return fg_groups, fg_dicts, fg_substitutions


def multiply_step(step, multiplier):
    for place_key, placeholder_dict in step.quant_placeholders.items():
        step.quant_placeholders[place_key]["quantity"] *= multiplier

    step.verbose_print()
    return step