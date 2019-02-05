''' Predict vegitables code here '''
#imports
# import keras
from keras.models import Model, model_from_json
from keras import applications, optimizers
from keras import backend as K
from keras.applications.mobilenet import MobileNet, preprocess_input
from keras.preprocessing import image
# from keras.layers import Dense, Flatten, Dropout
from keras.callbacks import ModelCheckpoint
import numpy as np
import pandas as pd


def resource_path(file_path) :
    return app.config['basedir'] + file_path

# def mongo_db() :
#     return app.config['pymongo_db'].db

class PredictRawVeggies:

    ###########################################################################
    def __init__(self):
        #Load the model
        self.img_width = 224
        self.img_height = 224

        #get the labels
        df_labels = pd.read_csv("app/models/labels.csv")
        df_labels = df_labels.sort_values(by=['Index'])
        self.labels= list(df_labels['Label'])
        self.num_labels = len(self.labels)
        K.clear_session()
        self.create_model()

        self.model_final._make_predict_function()


    ############################################################################
    def create_model(self):

        json_file = open("app/models/mobilenet_fruit_veggie_arch.json", 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model_final = model_from_json(loaded_model_json)
        self.model_final.load_weights("app/models/mobilenet_fruit_veggie.h5")
        #load the model
#         model = MobileNet(include_top=False, weights="imagenet", input_tensor=Input(shape=(224,224,3)), input_shape=(224,224,3))
#         #disable few layers
#         for layer in model.layers[:5]:
#             layer.trainable = False
#
#         #Add layers
#         x = model.output
#         x = Flatten()(x)
#         x = Dense(128, activation="relu")(x)
#         x = Dropout(0.5)(x)
#         x = Dense(128, activation="relu")(x)
#         x = Dropout(0.2)(x)
#         x = Dense(128, activation="relu")(x)
# #         x = Dropout(0.2)(x)
# #         x = Dense(128, activation="relu")(x)
#         #Add output layer
#         predictions = Dense(53, activation="softmax")(x)
#         #create the final model
#         self.model_final = Model(inputs = model.input, outputs = predictions)
#         #load the weights
#         self.model_final.load_weights("mobilenet_fruit_veggie.h5")
#         # compile the model
#         self.model_final.compile(loss = "categorical_crossentropy", optimizer = optimizers.SGD(lr=0.0001, momentum=0.9), metrics=["accuracy"])

    ######################################################################
    def call_predict(self, images, folder):

        predictions = []
        #predict
        for image_name in images:
            image_path = folder+ "/" + image_name
            print(f"imagepath: {image_path}")
            test_image = image.load_img(image_path, target_size=(224,224), grayscale=False)
            test_image = image.img_to_array(test_image)
            test_image = np.expand_dims(test_image, axis=0)
            test_image = preprocess_input(test_image)
            # print(test_image)
            predict = self.model_final.predict(test_image)

            zip_pred= zip(predict[0], self.labels)

            # if the prediction is high then only senf the value
            match_found = False
            max_pred = max(zip_pred,key=lambda x:x[0])
            if (max_pred[0] > 0.3):
                match_found = True
                predictions.append((image_name, max_pred[1]))

            if(not(match_found)):
                predictions.append((image_name, ""))

        return predictions
