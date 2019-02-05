import requests
import pandas as pd
# import config
import os
import glob
import itertools
from app import app, config
# from boto.s3.connection import S3Connection

def getAPIkeys():
    Spoonacular_API_key = []

    Spoonacular_API_key.append(os.environ.get('Spoonacular_API_key1') if os.environ.get('Spoonacular_API_key2') else config.Spoonacular_API_key1)
    Spoonacular_API_key.append(os.environ.get('Spoonacular_API_key2') if os.environ.get('Spoonacular_API_key2') else config.Spoonacular_API_key2)
    Spoonacular_API_key.append(os.environ.get('Spoonacular_API_key3') if os.environ.get('Spoonacular_API_key2') else config.Spoonacular_API_key3)
    Spoonacular_API_key.append(os.environ.get('Spoonacular_API_key4') if os.environ.get('Spoonacular_API_key2') else config.Spoonacular_API_key4)

    # print(Spoonacular_API_key)

    return Spoonacular_API_key

# getAPIkeys()
'''
Get the remaining limit
'''
def getremainigAPIcalls():

    #loop through API keys
    Spoonacular_API_key = getAPIkeys()
    for key in Spoonacular_API_key:
        #make tiny request
        response = requests.post("https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/cuisine",
        headers={
            "X-RapidAPI-Key": key,
            "Content-Type": "application/x-www-form-urlencoded"
            },
            params={
            "ingredientList": "",
            "title": ""
            }
            )
        try:
            calls_remaning = response.headers['X-RateLimit-requests-Remaining']
            tiny_calls_remaning = response.headers['x-ratelimit-tinyrequests-remaining']
            print(f"Request calls remailing = {calls_remaning} Tiny calls remailing = {tiny_calls_remaning}")
        except:
            print("move on")

        #Return the key only if there are calls remainig
        if (int(calls_remaning) > 0):
            return key
    # print(Spoonacular_API_key[0])
    return False #Spoonacular_API_key[0] #only for today
# print(getremainigAPIcalls())

'''
getRecipeByUrl : query spoonacular API with the link
Return: Return the request
'''
def getRecipeByUrl(url):
    #Add payload
    payload = {
        'fillIngredients': True,
        'url': url,
        'limitLicense': True,
        'number': 2,
        'ranking': 1
    }
    # Check if any limit left
    key = getremainigAPIcalls()
    if (key):
        api_key = key
    else:
        return None

    endpoint = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/extract"
    headers={ "X-RapidAPI-Key": api_key  }
    #send the request
    result = requests.get(endpoint, params=payload, headers=headers)
    return result


'''
getRecipe : get the recipe and send it to the routes
cuisine: string
ingredients: list
Return: Return the request'''
def getRecipes(cuisine, link):

    info = {}
    #make a API call and get the recipe
    result = getRecipeByUrl(link)
    # print(result.json())

    if(result):
        #store the information
        cuisines = result.json()['cuisines'] if result.json()['cuisines'] else [cuisine]
        try:
            info = {'title': result.json()['title'],
                    'sourceUrl': result.json()['sourceUrl'],
                    'cookingMinutes': result.json()['cookingMinutes'],
                    'preparationMinutes': result.json()['preparationMinutes'],
                    'image': result.json()['image'],
                    'instructions': result.json()['instructions'],
                    'ingredients' : [key['originalString'] for key in result.json()['extendedIngredients']],
                    'servings': result.json()['servings'],
                    'diets': result.json()['diets'],
                    'cuisine': cuisines,
                    'course' : course
                    }
        except:
            # pass
            print("Recipe not found")
    return info

'''
getLinksFromcsv
return the list of recepies
'''
def getLinksFromcsv(cuisine="Indian", ingredients=[]):
    #make everything lower case
    ingredients= [x.lower().strip() for x in ingredients]
    cuisine = cuisine.lower().strip()

    #get the ingredients whoes recipes we have saved
    df = pd.read_csv(os.path.join('recipes', 'recipes.csv'), skipinitialspace=True)
    df.columns = map(str.lower, df.columns)
    df.fillna(value=" ", inplace=True)

    #get the synonyms and append to ingredients
    syn_df = pd.read_csv(os.path.join('recipes', 'synonyms.csv'), skipinitialspace=True)
    syn_df.columns = map(str.lower, syn_df.columns)
    syn_df.fillna(value="", inplace=True)
    # print(syn_df)

    #if syninym found append to ingredient
    for ingredient in ingredients:
        try:
            ingredients.extend(syn_df[ingredient].tolist())
        except:
            pass
    ingredients=list(filter(None, ingredients))
    print(ingredients)
    # print(df[cuisine])

    recipe_links_list = []
    for ingredient in ingredients:
        new_list = []
        #find the recipes
        try:
            new_list = df[cuisine][df[cuisine].str.contains(ingredient)].tolist()
        except:
            print("not found")

        recipe_links_list = [x for x in itertools.chain.from_iterable(itertools.zip_longest(recipe_links_list,new_list)) if x]

    # print(recipe_links_list)
    return recipe_links_list
# getLinksFromcsv('Italian', ['mushroom','corn','tomato'])
#
'''
findRecipesDBorAPI() NOT USED
'''
def findRecipesDBorAPI(cuisine, ingredients):
    #Get the links
    recipe_links = getLinksFromcsv(cuisine, ingredients)
    # If cuisine name not present insert
    if (mongo_db()['cuisine']
                .find({"cuisine_name": cuisine})
                .count() == 0):
        print(f"inserted {cuisine}")
        mongo_db()['cuisine'].insert({"cuisine_name":cuisine})

    for link in recipe_links:
        if (mongo_db()['recipes']
                    .find({"sourceUrl": link})
                    .count() == 0):
            print(f"inserted {cuisine}")
            mongo_db()['cuisine'].insert({"cuisine_name":cuisine})

'''
getdict()
Testing
'''
def getdict():
    return [{'title': 'spinach corn sandwich',
    'sourceUrl': 'https://hebbarskitchen.com/spinach-corn-sandwich-recipe/',
    'cookingMinutes': 10,
    'image': 'https://spoonacular.com/recipeImages/1047695-556x370.jpg',
    'instructions': 'Instructionsfirstly, in a large tawa heat 1 tsp butter and saute 2 tbsp onion.',
    'ingredients': ['1 tsp butter', '2 tbsp onion finely chopped', '1 cup palak / spinach finely chopped']},
    {'title': 'spinach corn sandwich',
    'sourceUrl': 'https://hebbarskitchen.com/spinach-corn-sandwich-recipe/',
    'cookingMinutes': 10,
    'image': 'https://hebbarskitchen.com/wp-content/uploads/mainPhotos/onion-tomato-chutney-recipe-tomato-onion-chutney-recipe-1.jpeg',
    'instructions': 'Instructionsfirstly, in a large tawa heat 1 tsp butter and saute 2 tbsp onion.',
    'ingredients': ['1 tsp butter', '2 tbsp onion finely chopped', '1 cup palak / spinach finely chopped']}]
# print(config.Spoonacular_API_key2)
