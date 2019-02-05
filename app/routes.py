
from flask import jsonify, render_template, url_for, request, redirect
import json
import os
import glob
# from models import PredictRawVeggies
import pandas as pd
# from recipes import getRecipes, getdict, getLinksFromcsv
from random import shuffle
from app import app
from app import models, recipes, mongodb

# app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
my_pred = models.PredictRawVeggies()

def mongo_db() :
    return app.config['pymongo_db'].db

# # Define routes ###############################################################
@app.route("/",  methods=['GET', 'POST'])
def index():
    print("upload click")
    if request.method == 'POST':
        if request.files.get('file'):
#
            images = request.files.getlist("file") #convert multidict to dict
            print(f"Images: {images}")
            # Remove all the files
            files = glob.glob("app/" +app.config['UPLOAD_FOLDER']+'/*')
            # print(files)
            for f in files:
                os.remove(f)

            filenames = []
            #save the image
            for image in images:     #image will be the key
                # create a path to the uploads folder
                filepath = os.path.join("app/", app.config['UPLOAD_FOLDER'], image.filename)
                image.save(filepath)
                filenames.append(image.filename)
                print(filenames)

            predictions = my_pred.call_predict(filenames, "app/" +app.config['UPLOAD_FOLDER'])

        return jsonify({'result': 'success', 'predictions': predictions})
    else:
        # Get the cusines from the file list
        cuisines_list = [cuisine['cuisine_name'] for cuisine in mongo_db()['cuisine'].find({},{ "_id": 0, "cuisine_name": 1 })]
        print(cuisines_list)

    return render_template('index.html', cuisines = cuisines_list)

#####################################################################################
# Define routes ###############################################################
@app.route("/find_recipe", methods=['POST'])
def find_recipe():
    data = {"success": False}
    if request.method == 'POST':
        print("find_recipe")
        print("-------------------------------------")
        data = request.get_json()
        ingredients = [word for line in data['ingredients'] for word in line.split()]
        cuisine = data['cuisine']
        print(f'cuisine {cuisine}')
        #Get the links
        recipes_list = mongodb.selectRecipes(cuisine, ingredients)
        # print(recipe_links)
        #
        #if any recipe found retun success
        for recipe in recipes_list:
            if bool(recipe):
                return jsonify({'data': render_template('recipes.html', object_list=recipes_list)})

        return json.dumps({ "error": "Cannot find the recipe" }), 500

# ###########################################################################
# ###########################################################################
print(__name__)
if __name__ == '__main__':
    app.run(debug=True)
