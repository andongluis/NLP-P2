from helper import parsing

def main():


	page_links = [
				  "https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/",
				  # "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/",
				  # "https://www.allrecipes.com/recipe/12720/grilled-salmon-i/"
				  ]




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


		# See if ingredient parsing alright
		for ingred in ingreds:
			print(ingred)
			print(parsing.extract_ingredient(ingred))


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
