from helper import parsing

def main():


	page_links = ["https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/",
				  "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/"]




	for page_link in page_links:

		soup = parsing.get_page(page_link)


		print("TITLE")
		title_text = parsing.get_title(soup)
		print(title_text)


		print("\nINGREDIENTS")
		ingreds = parsing.get_ingredients(soup)
		print(ingreds)


		# Get Prep Time
		print("\nPREP TIME")
		time_dict = parsing.get_preptime(soup)
		print(time_dict)

		# Get Steps
		print("\nSTEPS")
		steps = parsing.get_steps(soup)
		print(steps)


		'''


		# some id's:
		# - lst_ingredients_1
		# - lst_ingredients_2

		class="list-ingredients-1"
		class="list-ingredients-2"
		sections: 
		class="recipe-directions"
		class = "directions--section__steps"
		class="prepTime"
		class="prepTime__item"

		class="recipe-directions__list"
		class="recipe-directions__list--item"


		'''

if __name__ == "__main__":
	main()
