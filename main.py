
import sys

from helper import parsing, data_building, printing
from helper.data_building import Ingredient, Step

from itertools import chain

def main(page_link):
    '''
    NOTE: Some recipe parsing fails, such as :

    "https://www.allrecipes.com/recipe/45736/chicken-tikka-masala/",
    '''

    soup = parsing.get_page(page_link)


    print("TITLE")
    title_text = parsing.get_title(soup)
    print(title_text)


    print("\nINGREDIENTS")
    ingreds = parsing.get_ingredients(soup)
    print(ingreds)

    # db = data_building.make_fg_db()

    # Get Prep Time
    print("\nPREP TIME")
    time_dict = parsing.get_preptime(soup)
    print(time_dict)

    # Get Steps
    print("\nSTEPS")
    steps = parsing.get_steps(soup)
    print(steps)

    # See if ingredient parsing alright


    # Parse/Extract things
    str_dicts = list(chain.from_iterable([parsing.extract_ingredient(in_string) for in_string in ingreds]))

    # print(str_dicts)

    db = data_building.make_fg_db()

    ingred_list = [Ingredient(str_dict, db) for str_dict in str_dicts]

    steps_list = [Step(step, ingred_list) for step in steps]

    valid = False
    valid_transformations = {
        'v': 'vegetarian',
        'nv': 'non-vegetarian',
        'h': 'healthy',
        'u': 'unhealthy',
        'gf': 'gluten-free',
        's': 'country_swedish',
        'm': 'country_mexican',
        'd': 'double',
        'ha': 'half',
        'q': 'quit',
    }
    while not valid:
        transformation = input('Choose how you want to transform the recipe:'
                               '\nv = vegetarian'
                               '\nnv = non-vegetarian'
                               '\nh = healthy'
                               '\nu = unhealthy'
                               '\ngf = gluten-free'
                               '\ns = swedish'
                               '\nm = mexican'
                               '\nd = double'
                               '\nha = half'
                               '\nq = quit\n')
        if transformation in valid_transformations:
            quality = valid_transformations[transformation]
            # valid = True
        else:
            print('Invalid transformation.')
            continue


        if quality == "quit":
            return

        print('Before transformation step')

        print(ingred_list)

        print(steps_list)

        # Testing transformation
        ingred_list = data_building.make_quality(quality, ingred_list)


        # Transform step quantity if necessary:
        if quality == "double" or quality == "half":
            if quality == "double":
                multiplier = 2
            else:
                multiplier = 0.5
            steps_list = [data_building.multiply_step(step, multiplier) for step in steps_list]

        print('After transformation step')

        print(ingred_list)

        print(steps_list)

        if quality == 'non-vegetarian':
            should_slap_meat = data_building.slap_some_meat_on_there(ingred_list)
            if should_slap_meat:
                steps_list.append(Step('Slap a 20 ounce steak on there raw.', ingred_list))

        # [parsing.get_ingredients_step(step, ingred_list, post_sub_ingred_list) for step in steps]

        # prints using final printing function
        printing.printTransformed(title_text, ingred_list, time_dict, steps_list, page_link)
    


if __name__ == "__main__":
    '''
    Pipeline of project:

    0. Build datasets from stored csv files

    1. INPUT: Get url from user

    2. Parse website

    3. Make data objects

    4. INPUT: Get transformation from user

    5. Transform data based on user input

    6. Print transformed data

    7. Return to 4 or Exit
    '''
    page_links = [
                    "https://www.allrecipes.com/recipe/258170/easy-white-chocolate-ganache/",
                  #  "https://www.allrecipes.com/recipe/33647/chocolate-ganache/",
                  #"https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/",
                  # "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/",
                  # "https://www.allrecipes.com/recipe/12720/grilled-salmon-i/",
                  # "https://www.allrecipes.com/recipe/229960/shrimp-scampi-with-pasta/",
                  # "https://www.allrecipes.com/recipe/8302/banana-chocolate-chip-cake/",
                  # "https://www.allrecipes.com/recipe/59661/spinach-enchiladas/",
                  # "https://www.allrecipes.com/recipe/216564/swedish-meatballs-svenska-kottbullar/",
                  # "https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/",
                  # "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/",
                  # "https://www.allrecipes.com/recipe/218120/hearty-meat-lasagna/"
                  ]

    if len(sys.argv) < 2:
        print("Function should be called: python main.py <allrecipes url>")
        print("however, this will continue on some test url")
        url = page_links[0]
    else:
        url = sys.argv[1]

    main(url)
