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


TOOLS = ["sauce pan", "wok", "skillet", "baking dish", "pot", "pan", "oven", "stove",
        "bowl", "knife", "spoon", "fork", "tongs", "spatula", "grater", "board", "can opener",
        "peeler", "masher", "blender", "whisk", "pin", "colander", "press", "ladle",
        "thermometer", "glove", "mit", "scissors", "grill", "measuring cup", "measuring spoon",
        "spinner", "cutter", "shear", "rod", "stockpot", "wrap", "plastic wrap", "grate",
        "platter", "foil", "brush", "tablespoon", "teaspoon", "hammer", "boil", "chop", "chopping",
        "bowl"]
TOOLS.extend([t + "s" for t in TOOLS])

def get_tools(step):
    step_tools = []
    for tool in TOOLS:
        if tool + " " in step or "tool" + "," in step:
            # covers edge cases where tools aren't specified
            if tool == "tablespoon" or tool == "teaspoon":
                step_tools.append("measuring spoon")
            if tool == "boil":
                step_tools.append("pot")
            if tool == "chop":
                step_tools.append("knife")
            step_tools.append(tool)
    return step_tools
    # TOOD: Take in a step string, return a list of tools for cooking that are used in this step

METHODS = ["sauté", "boil", "broil", "poach", "sear", "steam", "shop", "grate", "mince", "shake",
            "squeeze", "crush", "grill", "fry", "simmer", "roast", "bast", "brown", "brine", "blanch",
            "barbecue", "bake", "carmelize", "croquette", "cure", "deglaze", "dredge", "ferment", "fillet",
            "frost", "garnish", "glaze", "pressure cook", "pasturize", "pickle", "smoke", "tenderize", "zest",
            "mix"]

def get_methods(step):
    step_methods = []
    for method in METHODS:
        if method + " " in step:
            step_methods.append(method)
    return step_methods

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




def find_all_str(phrase, string):
    return [(m.start(), m.start() + len(string) )for m in re.finditer(phrase, string)]




COMMON_GARBAGE = ["cook ", "season ", "mix ", "melt ", "pour ", "the ", "<100> ", "<101> ",
                  "> ", "teaspoons ",
                  "tablespoons ", "teaspoon ", "tablespoon "]
END_GARBAGE = [" mixture"]
def remove_common_noise(string):
    for garbage in COMMON_GARBAGE:
        if string.startswith(garbage):
            string = string.replace(garbage, "")
    for garbage in END_GARBAGE:
        if string.endswith(garbage):
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
                                            }
                        ... 
                     }
    }

    """
    step = step.lower()

    counter = 0
    placeholders = {}

     ### Noun Chunking Approach
    # Noun chunk string
    noun_chunks = get_chunks(" ".join(step.split()[1:]))
    # print(noun_chunks)
    noun_chunks = [remove_common_noise(chunk.strip()) for chunk in noun_chunks]

    # print(noun_chunks)

    # For each noun chunk 
    for noun_chunk in noun_chunks:
        matches = ingredient_match(noun_chunk, ingred_list)
        if len(matches) > 0:
            match = matches[0]
            placehold_id = f"<{counter}>"
            counter += 1
            placeholders[placehold_id] = {"ingredient": match}
            step = step.replace(noun_chunk, placehold_id)

    ### Contains Approach
    # For each ingredient:
    for ingred in ingred_list:

        # Try find entire phrase, if found, great
        if ingred.orig_name + " " in step or ingred.orig_name + "," in step:
            placehold_id = f"<{counter}>"
            placeholders[placehold_id] = {"ingredient": ingred}
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




NUM_DICT = {

    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,

}

def get_quantities_step(in_string):
    # Get placeholder dict for quantities, similar to ingredients above

    # To avoid doublin temperatures or times, lazy solution
    if "degree" in in_string or "minute" in in_string or "seconds" in in_string or "inch" in in_string:
        return {"string": in_string, "placeholders": {}}

    counter = 100
    placeholders = {}

    # Parsing in casee of the weird fraction case
    in_string = in_string.replace(u"½", u"1/2")
    in_string = in_string.replace(u"¾", u"3/4")
    in_string = in_string.replace(u"⅓", u"1/3")
    in_string = in_string.replace(u"¼", u"1/4")

    # in_string = in_string.replace(u"\u2009", u" ")
    in_string = in_string.replace(u"⅔", u"2/3")
    in_string = in_string.replace(u"⅛", u"1/8")
    # in_string = in_string.replace(u"¼", u"1/4")    



    # Dimensions of pans:
    dimen_str = re.search('(\d+x\d+)', in_string)
    if dimen_str:
        dimen_str = dimen_str.group(0)

        dimens = dimen_str.split("x")
        
        # placehold_id = f"<{counter}>"
        # counter += 1
        # in_string = in_string.replace(dimens[0] + "x", placehold_id + "x")
        # placeholders[placehold_id] = {"quantity": float(dimens[0])}

        placehold_id = f"<{counter}>"
        counter += 1
        in_string = in_string.replace("x" + dimens[1], "x" + placehold_id)
        placeholders[placehold_id] = {"quantity": float(dimens[1])}


    # Fractions and numbers
    quant_strs = re.findall('(\d+\s?\d*?\/?\d*? )', in_string)

    # For each fraction
    for quant_str in quant_strs:
        placehold_id = f"<{counter}>"
        counter += 1
        placeholders[placehold_id] = {"quantity": float(sum(Fraction(s) for s in quant_str.split()))}
        in_string = in_string.replace(quant_str, placehold_id + " ")



    # Strings 
    # Ignore for now


    # print(in_string)
    # print(placeholders)


    return {"string": in_string, "placeholders": placeholders}

