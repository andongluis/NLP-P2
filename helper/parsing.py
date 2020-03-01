'''Functions regarding scraping and parsing data'''


import requests
from bs4 import BeautifulSoup

from functools import reduce
from operator import concat

import re
from fractions import Fraction
from copy import deepcopy

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
    if not ingreds:
        # LIKELY DID NOT WORK, GONNA TRY NEW METHOD
        ingred_tags = soup.find_all(class_="ingredients-item-name")
        ingreds = [ingred_tag.get_text() for ingred_tag in ingred_tags]
        ingreds = [ingred.strip() for ingred in ingreds if ingred != "" and ingred != 'Add all ingredients to list']
    return ingreds


def get_preptime(soup):
    # Takes in soup content, returns dict = {"": ,"":, ":"}, where keys are type of activity, value is datetime
    prep_tags = soup.find_all(class_="prepTime__item")
    time_tags = [prep_tag.find_all("time")[0] for prep_tag in prep_tags if prep_tag.find_all("time")]
    time_dict = {time_tag['itemprop']: time_tag['datetime'] for time_tag in time_tags}
    if not time_dict:
        prep_tags = soup.find_all(class_="recipe-meta-item")
        prep_dict = {tag.find(class_="recipe-meta-item-header").get_text().strip()[:-1] : tag.find(class_="recipe-meta-item-body").get_text().strip() for tag in prep_tags}
        time_dict = {key + "Time": time for key, time in prep_dict.items() if key in ["prep", "cook", "total"]}
    return time_dict


def get_steps(soup):
    # Takes in Soup content, returns list of steps as string
    steps_tags = soup.find_all(class_="recipe-directions__list--item")
    steps = [steps_tag.get_text().strip() for steps_tag in steps_tags]
    
    if not steps:
        steps_tags = soup.find_all(class_="instructions-section-item")
        # print(steps_tags)
        steps = [steps_tag.find(class_="section-body").get_text().strip() for steps_tag in steps_tags]
    steps = reduce(concat, [step.split(". ") for step in steps if step != ""])        
    return steps



MEASUREMENTS = ["cup", "pound", "can", "teaspoon", "tablespoon",
                "ounce", "clove", "package", "pinch", "container", "slice"]

MEASUREMENTS.extend([meas + "s" for meas in MEASUREMENTS])


def get_measurement(in_string):
    for measurement in MEASUREMENTS:
        if measurement + " " in in_string:
            return measurement
    return None


QUALIFIERS = ["grated", "chopped", "crushed", "minced", "beaten", "cooled", "sliced",
              "dried", "patty", "patties", "baked", "freshly", "fresh", "semisweet", "sweet",
              "extra-virgin", "extra virgin", "virgin", "dry", "finely", "unsalted",
              "mashed", "day-old", "small", "frozen", "kosher", "shredded", "lean"]


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

        # Further split by ",", "and", and "or"

        post_comma_list = re.split(", |and |or ", comma_portion)
        # print(post_comma_list)
        quals.extend(post_comma_list)

    # Get common qualifiers
    for qual in QUALIFIERS:
        if qual in in_string and qual not in quals:
            quals.append(qual)
            in_string = in_string.replace(qual + " ", "")


    quals = [qual.strip() for qual in quals if qual.strip() != ""]

    return quals, in_string


def extract_ingredient(in_string):
    '''
    return list of following dict(s):
    [{food_group: "",
     quantity: float,
     measurement: "",
     qualifiers: ["", ""]}]

     It is a list bc there might be weirdd instances where there are two ingredients listed in one entry
     (most often salt and pepper)
     NOTE: If some unspecified quantity (e.g. "to taste"), put 0. Might need to alter this depending on what we see
    '''
    ingred_dict = {"food_group": "",
                   "quantity": None,
                   "measurement": "",
                   "qualifiers": []}


    # Parsing in casee of the weird fraction case
    in_string = in_string.replace(u"½", u"1/2")
    in_string = in_string.replace(u"¾", u"3/4")
    in_string = in_string.replace(u"⅓", u"1/3")
    in_string = in_string.replace(u"¼", u"1/4")

    # in_string = in_string.replace(u"\u2009", u" ")
    in_string = in_string.replace(u"⅔", u"2/3")
    in_string = in_string.replace(u"⅛", u"1/8")
    # in_string = in_string.replace(u"¼", u"1/4")    



    # To taste:
    if "to taste" in in_string:
        # quantity is to taste
        in_string = in_string.replace("to taste", "")
        # Leave quantity as 0 just as placeholder value
        quantity = 0
    elif "as needed" in in_string:
        # quantity is to taste
        in_string = in_string.replace("as needed", "")
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



    ingred_split = in_string.split("and")

    if len(ingred_split) == 1:

        # obtain food group:
        ingred_dict["food_group"] = in_string.lower()

        return [ingred_dict]
    else:
        return_lst = []
        for ingred in ingred_split:
            ingred_dict_i = deepcopy(ingred_dict)
            ingred_dict_i["food_group"] = ingred.lower().strip()
            return_lst.append(ingred_dict_i)

        return return_lst



def get_nutritional_value(soup):
    # TODO: Takes in Soup content, returns list of nutritional values
    # (can be dict, depending on what you find most expressive/useful)

    # IGNORE FOR NOW

    return []


TOOLS = ["saucepan", "wok", "skillet", "baking dish", "pot", "pan", "oven", "stove",
        "bowl", "knife", "spoon", "fork", "tongs", "spatula", "grater", "board", "can opener",
        "peeler", "masher", "blender", "whisk", "pin", "colander", "press", "ladle",
        "thermometer", "glove", "mit", "scissors", "grill", "measuring cup", "measuring spoon",
        "spinner", "cutter", "shear", "rod", "stockpot", "wrap", "plastic wrap", "grate",
        "platter", "foil", "brush", "tablespoon", "teaspoon", "hammer", "boil", "chop", "chopping"]
TOOLS.extend([t + "s" for t in TOOLS])

def get_tools(step):
    for tool in TOOLS:
        if tool + " " in step:
            # covers edge cases where tools aren't specified
            if tool == "tablespoon" or tool == "teaspoon":
                return "measuring spoon"
            if tool == "boil":
                return "pot"
            if tool == "chop":
                return "knife"
            return tool
    return None
    # TOOD: Take in a step string, return a list of tools for cooking that are used in this step

METHODS = ["sauté", "boil", "broil", "poach", "sear", "steam", "shop", "grate", "mince", "shake",
            "squeeze", "crush", "grill", "fry", "simmer", "roast", "bast", "brown", "brine", "blanch",
            "barbecue", "bake", "carmelize", "croquette", "cure", "deglaze", "dredge", "ferment", "fillet",
            "frost", "garnish", "glaze", "pressure cook", "pasturize", "pickle", "smoke", "tenderize", "zest"]

def get_method(step):
    for method in METHODS:
        if method + " " in step:
            return method
    return None

import spacy
from fuzzywuzzy import fuzz
from spacy.lang.en.stop_words import STOP_WORDS
NLP = spacy.load("en_core_web_sm")
NOT_USEFUL_NOUNS = set()


import re

def get_chunks(str):
    return [chunk.text for chunk in NLP(str).noun_chunks if chunk.text not in STOP_WORDS and chunk.text not in NOT_USEFUL_NOUNS]


def ingredient_match(candidate, ingredients):
    # candidate_str will likely be either substring of an ingredient name
    # or a set substring of the ingredient+qualifiers


    return [ingred for ingred in ingredients if fuzz.token_set_ratio(candidate, ingred.orig_name) == 100]


def extract_number(string):
    # NOTE: fractions
    
    lst = [int(s) for s in string.split() if s.isdigit()]
    return lst[0] if lst else None


def find_all_str(phrase, string):
    return [(m.start(), m.start() + len(string) )for m in re.finditer(phrase, string)]





COMMON_GARBAGE = ["cook ", "season ", "mix ", "melt ", "pour ", "the "]
def remove_common_noise(string):
    for garbage in COMMON_GARBAGE:
        if string.startswith(garbage):
            string = string.replace(garbage, "")
    return string

def get_ingred_sub(ingred, ingred_list, ingred_sub_list):
    index = ingred_list.index(ingred)
    if ingred != ingred_sub_list[index]:
        return ingred_sub_list[index]
    return ingred

def get_ingredients_step(step, ingred_list):
    # Return a dict with the following:
    """
    {"string": string with placeholder values replacing ingredient strings
     "placeholders": {
                        placeholder_string: {"ingredient": str,
                                             "quantity": float,
                                            }
                        ... 
                     }
        
    }


    to do list:
    - try ignoring noun chunks, doing a simple "contains" for each of the ingredients we have,
    if it is contained, then we know we ought to be looking for that ingredient in that string.
    the next step would be to identify what part of the string has that ingredient, and additional
    words before/after it (e.g. half of the potatoes, sliced cheese)

    - try other noun chunkings (e.g. nltk)


    - do both: contains-ing and noun chunking to try to match things up


    - dealing with numbers: make sure to store/remove the number (or ignore it)


    -briefly looking at victors code, it seems like there is no easy way of parsing ingreds from step
    
    - so, might just need to put in a lott of work into parsing this

    - have an mvp asap so that quinn can begin working on printing

    """
    # print(step)


    step = step.lower()


    ### Noun Chunking Approach

    # Noun chunk string
    noun_chunks = get_chunks(" ".join(step.split()[1:]))
    print(noun_chunks)

    noun_chunks = [remove_common_noise(chunk) for chunk in noun_chunks]
    print(noun_chunks)


    counter = 0


    placeholders = {}



    # For each noun chunk
    
    for noun_chunk in noun_chunks:
        matches = ingredient_match(noun_chunk, ingred_list)

        # TODO: HANDLE QUANTITIES PROPERLY
        quant = extract_number(noun_chunk)

        # print(matches)
        if len(matches) > 0:
            match = matches[0]
            placehold_id = f"<{counter}>"
            counter += 1
            placeholders[placehold_id] = {"ingredient": match, "quantity": quant}
            step = step.replace(noun_chunk, placehold_id)

    # print(placeholders)
    # print(step)


    ### Contains Approach

    # # For each ingredient:
    for ingred in ingred_list:

        # Try find entire phrase, if found, great
        if ingred.orig_name in step:
            placehold_id = f"<{counter}>"
            counter += 1

            # TODO: HANDLE QUANTITIES PROPERLY
            quant = None

            placeholders[placehold_id] = {"ingredient": ingred, "quantity": quant}
            step = step.replace(ingred.orig_name, placehold_id)

            counter += 1

        # else:
        #     # Use find for each stringsplit in ingred in the step,

        #     nouns = [chunk.text for chunk in NLP(ingred.orig_name) if chunk.pos_ == "NOUN"]
        #     # print(ingred.orig_name)
        #     # print(nouns)
        #     for noun in nouns:
        #         if noun in step:
        #             placehold_id = f"<{counter}>"
        #             counter += 1

        #             # TODO: HANDLE QUANTITIES PROPERLY
        #             quant = None

        #             placeholders[placehold_id] = {"ingredient": ingred, "quantity": quant}
        #             step = step.replace(noun, placehold_id)

        #             counter += 1

    # print('************************\n************************\nprinting placeholders')
    # print(placeholders)
    # print('************************\n************************\nprinting step')
    # print(step)

    return {"string": step, "placeholders": placeholders}

