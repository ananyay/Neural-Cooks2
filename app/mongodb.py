from app import app, recipes
import pandas as pd
import os
import re

COLLECTION_NAME = 'recipes'

def mongo_db() :
    return app.config['pymongo_db'].db

def remove_Recipes():
    mongo_db()[COLLECTION_NAME].remove()
    return

def insert_recipe(record, cuisine, recreate_db = False ):
    """
        Inserts population data into database
        clears existing data if recreate_db = True
    """
    if (recreate_db):
        remove_Recipes()
    # Convert it to Json
    try:
        records ={
        'title': 'spinach corn sandwich',
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
        'ingredients': ['1 tsp butter', '2 tbsp onion finely chopped', '1 cup palak / spinach finely chopped'],
        'cuisine': ['Indian'],
        'type': ['main'],
        'numofhits':10
        }
        # Insert only if place does not exist
        # if (mongo_db()['population']
        #             .find({"place_id": location.raw["place_id"]})
        #             .count() == 0):
        #     print(records)
        #     mongo_db()['population'].insert(records)
        # else:
        #     print("updating")
        # mongo_db()['population'].update({"place_id": records["place_id"]},
        #     records, upsert=True)
        mongo_db()[COLLECTION_NAME].insert(records)
        print("Inserted record please check ...")
    except Exception as e:
        print(e)


# InsertRecipes in to DB
def insertRecipe(cuisine):
    #Get the links
    df = pd.read_csv(os.path.join('app', 'recipes', cuisine + '.csv'), skipinitialspace=True)
    # If cuisine name not present insert
    if (mongo_db()['cuisine']
                .find({"cuisine_name": cuisine})
                .count() == 0):
        print(f"inserted {cuisine}")
        mongo_db()['cuisine'].insert({"cuisine_name":cuisine})


    # Iterate  through DataFrame and get recipe for each link from spoonacular
    for index, row in df.iterrows():
        if (mongo_db()['recipes']
                    .find({"sourceUrl": row['link']})
                    .count() == 0):
            print(f"inserted course:{row['course']} link:{row['link']}")
            # return

            result = recipes.getRecipeByUrl(row['link'])
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
                            'ingredients' : [{"aisle": key['aisle'],"originalString": key['originalString']} for key in result.json()['extendedIngredients']],
                            'servings': result.json()['servings'],
                            'diets': result.json()['diets'],
                            'cuisine': [cuisine.lower() for cuisine in cuisines],
                            'course' : row['course'],
                            'nutrition': row['nutrition']
                            }
                    print(info['title'])
                    mongo_db()['recipes'].insert(info)
                except Exception as e:
                    # pass
                    print(e)
        else:
            print("All recipes are present")


# Selects the recipes and send it to flask app
# #returns a list
def selectRecipes(cuisine, ingredients):
    recipes = []

    for ingredient in ingredients:
        if (cuisine == ""):
            print(f"cuisine is empty {ingredients}")
            results = mongo_db()['recipes'].find({'ingredients.originalString' :{'$regex' : ingredient, '$options' : 'i'}})
        else:
            results = mongo_db()['recipes'].find({
                    '$and': [
                    {'cuisine': {"$in": [re.compile(cuisine, re.IGNORECASE)]}},
                    {'ingredients.originalString' :{'$regex' : ingredient, '$options' : 'i'}}
                    ]
                    })


        for result in results:
            nutrition = ""
            if "nutrition" in result:
                nutrition = result['nutrition']
            print(f'nutrition {nutrition}')

            info = {'title': result['title'],
                    'sourceUrl': result['sourceUrl'],
                    'cookingMinutes': result['cookingMinutes'],
                    'preparationMinutes': result['preparationMinutes'],
                    'image': result['image'],
                    'instructions': result['instructions'],
                    'ingredients' : [key['originalString'] for key in result['ingredients']],
                    'servings': result['servings'],
                    'diets': result['diets'],
                    'nutrition' : nutrition,
                    # 'cuisine': [cuisine.lower() for cuisine in cuisines],
                    'course' : result['course']
                    }
            recipes.append(info)
            # print(result['title'])

    recipes1 = [i for n, i in enumerate(recipes) if i not in recipes[n + 1:]]

    for r in recipes1:
        print(r['title'])

    return recipes1

# selectRecipes('', ['kiwi'])

# insertRecipe("vegetarian")
