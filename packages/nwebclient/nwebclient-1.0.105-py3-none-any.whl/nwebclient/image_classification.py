# based on https://medium.com/@draj0718/image-classification-and-prediction-using-transfer-learning-3cf2c736589d

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
import sklearn.metrics as metrics
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.applications import VGG16


# Haengt mit der verwendeten Neuronalen Netz zusammen
IMAGE_SHAPE = [224, 224]


def build_model(num_classes=3):
    vgg = VGG16(input_shape = (224,224,3), weights = 'imagenet', include_top = False)
    for layer in vgg.layers:
        layer.trainable = False
    x = Flatten()(vgg.output)
    x = Dense(128, activation = ‘relu’)(x) 
    x = Dense(64, activation = ‘relu’)(x) 
    x = Dense(num_classes, activation = ‘softmax’)(x) 
    model = Model(inputs = vgg.input, outputs = x)
    model.compile(loss=’categorical_crossentropy’, optimizer=’adam’, metrics=[‘accuracy’])
    return model

def train(epochs = 5, batch_size=32, num_classes=3):
    model = build_model()
    
    trdata = ImageDataGenerator()
    train_data_gen = trdata.flow_from_directory(directory="train",target_size=(224,224), shuffle=False, class_mode='categorical')
    tsdata = ImageDataGenerator()
    test_data_gen = tsdata.flow_from_directory(directory="test", target_size=(224,224),shuffle=False, class_mode='categorical')

    training_steps_per_epoch = np.ceil(train_data_gen.samples / batch_size)
    validation_steps_per_epoch = np.ceil(test_data_gen.samples / batch_size)
    model.fit_generator(train_data_gen, steps_per_epoch = training_steps_per_epoch, validation_data=test_data_gen, validation_steps=validation_steps_per_epoch,epochs=epochs, verbose=1)
    print(‘Training Completed!’)

    Y_pred = model.predict(test_data_gen, test_data_gen.samples / batch_size)
    val_preds = np.argmax(Y_pred, axis=1)
    import sklearn.metrics as metrics
    val_trues =test_data_gen.classes
    from sklearn.metrics import classification_report
    print(classification_report(val_trues, val_preds))

    keras_file=”Model.h5"
    tf.keras.models.save_model(model,keras_file)

def predict(img_path):
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.applications.vgg16 import preprocess_input, decode_predictions
    import numpy as np
    #load saved model
    model = load_model(‘Model.h5’) 
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds=model.predict(x)
    # create a list containing the class labels
    class_labels = [‘Apple’,’Banana’,’Orange’]
    # find the index of the class with maximum score
    pred = np.argmax(preds, axis=-1)
    # print the label of the class with maximum score
    print(class_labels[pred[0]])

    