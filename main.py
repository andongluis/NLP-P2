from helper import parsing, data_building, printing
import pathlib


from helper.data_building import Ingredient

from itertools import chain

def main():


    page_links = [
                  "https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/",
                  "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/",
                  "https://www.allrecipes.com/recipe/12720/grilled-salmon-i/",
                  "https://www.allrecipes.com/recipe/229960/shrimp-scampi-with-pasta/",
                  "https://www.allrecipes.com/recipe/8302/banana-chocolate-chip-cake/",
                  "https://www.allrecipes.com/recipe/59661/spinach-enchiladas/",
                  "https://www.allrecipes.com/recipe/216564/swedish-meatballs-svenska-kottbullar/",
                  "https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/",
                  "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/",
                  "https://www.allrecipes.com/recipe/218120/hearty-meat-lasagna/"
                  ]


    '''
    NOTE: Some recipe parsing fails, such as :

    "https://www.allrecipes.com/recipe/45736/chicken-tikka-masala/",
    '''

    # while True:
    #     url = input("Enter URL: ")

    #     # need to make full list of transformations available
    #     transformation = input("Select transformation:\n1. Vegetarian\n2. Double\n3. Exit")
        
    #     if transformation == 3:
    #         break
        
    #     # parse for these
    #     try:
    #         # may also check that the url is for allrecipes.com/is a recipe page
    #         soup = parsing.get_page(url)
    #     except:
    #         print("Invaled url")
    #         continue
    #     title_text = parsing.get_title(soup)
    #     ingreds = parsing.get_ingredients(soup)
    #     time_dict = parsing.get_preptime(soup)
    #     steps = parsing.get_steps(soup)

    #     #transform them and call printing
    #     #printing.printTransformed(...)



    for page_link in page_links:

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

        print(str_dicts)

        continue

        ingred_list = [Ingredient(str_dict, db) for str_dict in str_dicts]

        print('Before deglutenizing step')

        print(ingred_list)

        print(steps)

        # Testing deglutenizer

        ingred_list = [ing.make_quality('gluten-free') for ing in ingred_list]

        print('After deglutenizing step')

        print(ingred_list)

        [parsing.get_ingredients_step(step, ingred_list) for step in steps]

        # prints using final printing function
        printing.printTransformed(title_text, ingred_list, time_dict, steps, page_link)
        
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





if __name__ == "__main__":
    main()
