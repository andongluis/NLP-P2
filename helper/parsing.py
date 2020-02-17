'''Functions regarding scraping and parsing data'''



import requests
from bs4 import BeautifulSoup

from functools import reduce
from operator import concat


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



def get_nutritional_value(soup):
	# TODO: Takes in Soup content, returns list of nutritional values
	# (can be dict, depending on what you find most expressive/useful)

	# IGNORE FOR NOW

	return []



def get_tools(step):
	# TOOD: Take in a step string, return a list of tools for cooking that are used in this step
	return []