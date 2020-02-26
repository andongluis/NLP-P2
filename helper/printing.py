# Printing function(s) for output

# for printing when final transformations are done
def printTransformed(title, ingrediants, prep_time, steps, url):

    print("{} - source : {}".format(title, url))

    # if prep time is given
    if prep_time:
        print("\nPreparation time:")
        print("Total: {}".format(prep_time["totalTime"][2:]))
        print("Prep: {}".format(prep_time["prepTime"][2:]))
        print("Cooking: {}".format(prep_time["cookTime"][2:]))
        # do each type of time it'll take

    # next:
        # print count: [quantity] descriptor name
        # maybe create getters in databuild
    print("\nIngredients:")
    count = 0
    for i in ingrediants:
        print("{}. {}".format(count+1, i))
        count+=1
    
    print("\n Steps:")
    count = 0
    for s in steps:
        print("{}. {}".format(count+1, s))
        count+= 1
    
