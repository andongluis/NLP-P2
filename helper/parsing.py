'''Functions regarding scraping and parsing data'''


import requests
from bs4 import BeautifulSoup

from functools import reduce
from operator import concat

import re
from fractions import Fraction


def get_page(page_url):
    # Returns BeautifulSoup content for page_url
    page = requests.get(page_url)
    return BeautifulSoup(page.content, 'html.parser')   


def get_title(soup):
    # Takes in Soup content, returns title as string
    return soup.find_all("title")[0].get_text()



def get_ingredients(soup):
    # Takes in Soup content, returns list of ingredients as string
    ingred_tags = soup.find_all(class_="recipe-ingred_txt")
    ingreds = [ingred_tag.get_text() for ingred_tag in ingred_tags]
    ingreds = [ingred for ingred in ingreds if ingred != "" and ingred != 'Add all ingredients to list']
    return ingreds


def get_preptime(soup):
    # Takes in soup content, returns dict = {"": ,"":, ":"}, where keys are type of activity, value is datetime
    prep_tags = soup.find_all(class_="prepTime__item")
    time_tags = [prep_tag.find_all("time")[0] for prep_tag in prep_tags if prep_tag.find_all("time")]
    time_dict = {time_tag['itemprop']: time_tag['datetime'] for time_tag in time_tags}
    return time_dict


def get_steps(soup):
    # Takes in Soup content, returns list of steps as string
    steps_tags = soup.find_all(class_="recipe-directions__list--item")
    steps = [steps_tag.get_text() for steps_tag in steps_tags]
    steps = reduce(concat, [step.split(". ") for step in steps if step != ""])
    return steps



MEASUREMENTS = ["cup", "pound", "can", "teaspoon", "tablespoon",
                "ounce", "clove"]

MEASUREMENTS.extend([meas + "s" for meas in MEASUREMENTS])



def get_measurement(in_string):
    for measurement in MEASUREMENTS:
        if measurement + " " in in_string:
            return measurement
    return None


QUALIFIERS = ["grated", "chopped", "crushed", "minced", "beaten", "cooled", "sliced"]


def get_qualifiers(in_string):

    quals = []

    # Obtain stuff within parenthesis
    in_parenth = re.search("\(([^\)]+)\)", in_string)

    # deal with parenthesis somehow

    if in_parenth:
        group = in_parenth.group(1)
        # remove parenthesis from string
        in_string = in_string.replace(" (" + group + ")", "")

        quals.append(group)

    # Get stuff after comma
    split_comma = in_string.split(", ", 1)
    # print(split_comma)
    if len(split_comma) > 1:
        comma_portion = split_comma[1]

        # remove parenthesis from string
        # print(in_string)
        # print(comma_portion)
        in_string = in_string.replace(", " + comma_portion, "")
        # print(in_string)

        quals.append(comma_portion)

    # Get common qualifiers
    for qual in QUALIFIERS:
        if qual in in_string and qual not in quals:
            quals.append(qual)
            in_string = in_string.replace(qual + " ", "")

    return quals, in_string


def extract_ingredient(in_string):
    '''
    return following dict:
    {food_group: "",
     quantity: float,
     measurement: "",
     qualifiers: ["", ""]}
     NOTE: If some unspecified quantity (e.g. "to taste"), put 0. Might need to alter this depending on what we see

     ['1 1/2 pounds salmon fillets', 'lemon pepper to taste', 'garlic powder to taste', 'salt to taste',
     '1/3 cup soy sauce', '1/3 cup brown sugar', '1/3 cup water', '1/4 cup vegetable oil']

     ['3/4 cup white sugar', '1/3 cup all-purpose flour', '1/4 teaspoon salt', '2 cups milk', '3 egg yolks, beaten', 
     '2 tablespoons butter', '1 1/4 teaspoons vanilla extract', '1 (9 inch) baked pastry shell, cooled', '4 bananas, sliced']

     ['1 pound sweet Italian sausage', '3/4 pound lean ground beef', '1/2 cup minced onion', '2 cloves garlic, crushed',
     '1 (28 ounce) can crushed tomatoes', '2 (6 ounce) cans tomato paste', '2 (6.5 ounce) cans canned tomato sauce',
     '1/2 cup water', '2 tablespoons white sugar', '1 1/2 teaspoons dried basil leaves', '1/2 teaspoon fennel seeds',
     '1 teaspoon Italian seasoning', '1 1/2 teaspoons salt, divided, or to taste', '1/4 teaspoon ground black pepper',
     '4 tablespoons chopped fresh parsley', '12 lasagna noodles', '16 ounces ricotta cheese', '1 egg',
     '3/4 pound mozzarella cheese, sliced', '3/4 cup grated Parmesan cheese']

    '''
    ingred_dict = {"food_group": "",
                   "quantity": None,
                   "measurement": "",
                   "qualifiers": []}


    # To taste:
    if "to taste" in in_string:
        # quantity is to taste
        in_string = in_string.replace("to taste", "")
        # Leave quantity as 0 just as placeholder value
        quantity = 0
    else:
        # just placeholder value, horrible notation but ill make it prettier when i have more willpower 
        quantity = -1


    # Obtain qualifiers
    qualifiers, in_string = get_qualifiers(in_string)

    ingred_dict["qualifiers"] = qualifiers

    # Obtain quantity
    quant_string = re.search('(\d+\s?\d*?\/?\d*? )', in_string)
    if quant_string:
        quant_string = quant_string.group(0)
    in_string = in_string.replace(quant_string, "")
    if quantity != 0:
        quantity = float(sum(Fraction(s) for s in quant_string.split()))

    ingred_dict["quantity"] = quantity


    # Obtain measurement
    measurement = get_measurement(in_string)
    if not measurement:
        print(f"no measurement found in string {in_string}, gonna put 'unit' as default")
        measurement = "unit"
    else:
        in_string = in_string.replace(measurement + " ", "")
    ingred_dict["measurement"] = measurement



    # obtain food group:
    ingred_dict["food_group"] = in_string


    return ingred_dict



def get_nutritional_value(soup):
    # TODO: Takes in Soup content, returns list of nutritional values
    # (can be dict, depending on what you find most expressive/useful)

    # IGNORE FOR NOW

    return []



def get_tools(step):
    # TOOD: Take in a step string, return a list of tools for cooking that are used in this step
    return []