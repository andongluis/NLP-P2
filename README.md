# NLP-P2

Team Members: Alexander Einarsson, Andong Luis Li Zhao, Quinn Shim

## Requirements

Installation requirements are specified in the `requirements.txt` file.

## Overview

In this project, we created a recipe transformer. The transformations that we allow are to make things:
- Vegetarian
- Un-vegetarian
- Healthy
- Unhealthy
- Swedish
- Mexican
- Gluten-free
- Double amount
- Halve amount

## Running this program

To run this program, you should be in the same directory as `main.py`. Then, you would run the command
```python main.py <URL_INPUT> ```
If no url is given, a default url will be used from the predetermined list.

## How it works

The general flow of how our project works is as follows:

1. Take in an input url from allrecipes. The expected format of the recipes is:
`"https://www.allrecipes.com/recipe/<RECIPE_ID>/<NAME_OF_RECIPE>/"`
(NOTE: Theoretically, the parser should work for the old allrecipes format and the new one.)
2. Scrape the website through BeautifulSoup
3. Obtain the ingredients and the steps from the website (we use a mixture of noun chunking and regular expressions to accomplpish this task)
4. Load in our pre-built food groups, methods, and tools data structures
5. Obtain the qualities (e.g. vegetarian, gluten-free) for our ingredients by linking them to our pre-built food groups
6. Ask for a transformation input
7. Transform the ingredients (and steps, if needed be) based on the input (using our pre-built data structures for substitutions)
8. Print the transformed recipe
9. Exit or return to step 6


## Some comments

- When doubling/halving recipes, we (if parsed correctly) also double/halve the capacity of pans (e.g. 9x12 inch pans) because we take into account that the previous pan would've been too big or too small for the new amount