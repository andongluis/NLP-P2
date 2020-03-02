# NLP-P2

Team Members: Quinn Shim, Alexander Einarsson, Andong Luis Li Zhao

## Requirements

TODO: Make requirements txt


## Overview

In this project, we created a recipe transformer. The transformations that we allow are:
- Vegetarian
- Un-vegetarian
- Healthy
- Unhealthy
- Swedish
- Mexican
- Gluten-free
- Double amount
- Halve amount


## How it works

The general flow of how our project works is as follows:

1. Take in an input url from allrecipes
2. Scrape the website through BeautifulSoup
3. Obtain the ingredients and the steps from the website (we use a mixture of noun chunking and regular expressions to accomplpish this task)
4. Load in our pre-built food groups, methods, and tools data structures
5. Obtain the qualities (e.g. vegetarian, gluten-free) for our ingredients by linking them to our pre-built food groups
6. Ask for a transformation input
7. Transform the ingredients (and steps, if needed be) based on the input (using our pre-built data structures for substitutions)
8. Print the transformed recipe