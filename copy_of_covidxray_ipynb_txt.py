# -*- coding: utf-8 -*-
"""Copy of covidxray.ipynb.txt

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vhqm5V2u-ViHnKJZu3SFCelGXWV3OXvd

### **Importing the Libraries**
"""

import tensorflow as tf
import pandas as pd
import random
from imutils import paths
from tensorflow.keras.applications import VGG16, VGG19, Xception
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import cv2
import os
import seaborn as sns
import time
from keras.layers import Input, Lambda, Dense, Flatten,BatchNormalization,Dropout

"""**Google Drive Mounting**"""

from google.colab import drive
drive.mount('/content/drive')

"""### **Importing Data**"""

path_ = list(paths.list_images('/content/drive/MyDrive/ml ass/dataset'))
X = []
Y = []
for path in path_:
    # Set Class label
    y = path.split(os.path.sep)[-2]
    #print(y)
    # Grayscale the image and reshape
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (512, 512))
    # update the data and labels lists, respectively
    X.append(image)
    Y.append(y)

# Normalize images
X = np.array(X) / 255.0
Y = np.array(Y)
print('Number of training images: ', len(X))
print('Number of training images: ', len(Y))
#print(Y)
# Plot example patient scan
W = 8
L = 1
fig, axes = plt.subplots(L, W, figsize = (17,17))
axes = axes.ravel() 
n = 138

for i in np.arange(0, W * L):
    index = np.random.randint(0, n)    
    axes[i].imshow( X[index] )
    axes[i].set_title(Y[index])

#one-hot encoding on the labels
lb = LabelBinarizer()
Y = lb.fit_transform(Y)
Y = tf.keras.utils.to_categorical(Y)

"""### **Splitting the data**"""

# split training and test data

(X_train, x_test, Y_train, y_test) = train_test_split(X, Y,test_size=0.20)

(x_train, x_valid, y_train, y_valid) = train_test_split(X_train, Y_train,test_size=0.20)

"""### **Data Augmentation**"""

Datagen= tf.keras.preprocessing.image.ImageDataGenerator(featurewise_center=True,featurewise_std_normalization=True,
                            rotation_range=20,width_shift_range=0.2,height_shift_range=0.2,horizontal_flip=True)

"""### **Different CNN Algorithm Structure**

**1. VGG16**
"""

def Covid_model():
    input_img = tf.keras.layers.Input(shape=(512, 512, 3))
    baseModel = VGG16(weights="imagenet", include_top=False,
	  input_tensor=tf.keras.layers.Input(shape=(512, 512, 3)))

    # Make all pre-trained layers from VGG19 non-trainable 
    for layer in baseModel.layers[:-3]:
        layer.trainable = False
    x = baseModel.output
    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Dropout(0.25)(x)

    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    

    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Dropout(0.25)(x)

    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.5)(x)

    x = tf.keras.layers.Dense(2, activation='softmax')(x)
  
    
    covid_model = tf.keras.models.Model(baseModel.input, x)
    adagrad=tf.keras.optimizers.Adagrad(lr=0.001)
    covid_model.compile(optimizer=adagrad, loss='binary_crossentropy',metrics=["accuracy"])
    return covid_model

"""**Fitting the VGG16 model**"""

model = Covid_model()
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', verbose=1,patience=10,mode='max',restore_best_weights=True)
covid= model.fit_generator(Datagen.flow(x_train, y_train, batch_size=8),steps_per_epoch=len(x_train) / 8,validation_data=(x_valid, y_valid), epochs=5,callbacks = [early_stopping])

"""### **Prediction and value calculation**"""

tic=time.clock()
y_pred = model.predict(x_test, batch_size=8)
toc=time.clock()
y_pred = np.argmax(y_pred, axis=1)
y_true = np.argmax(y_test, axis=1)

predicted_metrics = model.evaluate(x_test, y_test, batch_size=8, verbose=0)

for name, value in zip(model.metrics_names, predicted_metrics):
  print(name, ': ', value)

acc=predicted_metrics[1]
print(classification_report(y_pred, y_true,target_names=lb.classes_))

cm = confusion_matrix(y_pred, y_true)

sensitivity = cm[0, 0] / (cm[0, 0] + cm[0, 1])
specificity = cm[1, 1] / (cm[1, 0] + cm[1, 1])
time1=toc-tic

"""###**2. VGG19**"""

def Covid_model2():
    input_img = tf.keras.layers.Input(shape=(512, 512, 3))
    baseModel = VGG19(weights="imagenet", include_top=False,
	  input_tensor=tf.keras.layers.Input(shape=(512, 512, 3)))

    # Make all pre-trained layers from VGG19 non-trainable 
    for layer in baseModel.layers[:-3]:
        layer.trainable = False
    x = baseModel.output
    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Dropout(0.25)(x)

    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    

    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Dropout(0.25)(x)

    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.5)(x)

    x = tf.keras.layers.Dense(2, activation='softmax')(x)
  
    
    covid_model = tf.keras.models.Model(baseModel.input, x)
    adagrad=tf.keras.optimizers.Adagrad(lr=0.001)
    covid_model.compile(optimizer=adagrad, loss='binary_crossentropy',metrics=["accuracy"])
    return covid_model

"""##**Model fittting**"""

model2 = Covid_model()
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy',verbose=1,patience=10,mode='max',restore_best_weights=True)
covid2= model2.fit_generator(Datagen.flow(x_train, y_train, batch_size=8),steps_per_epoch=len(x_train) / 8,validation_data=(x_valid, y_valid), epochs=5,callbacks = [early_stopping])

"""**pridiction**"""

tic=time.clock()
y_pred2 = model.predict(x_test, batch_size=8)
toc=time.clock()
y_pred2 = np.argmax(y_pred2, axis=1)
y_true2 = np.argmax(y_test, axis=1)

predicted_metrics2 = model.evaluate(x_test, y_test, batch_size=8, verbose=0)

for name, value in zip(model2.metrics_names, predicted_metrics2):
  print(name, ': ', value)

print(classification_report(y_pred2, y_true2,target_names=lb.classes_))

acc2=predicted_metrics2[1]
cm2 = confusion_matrix(y_pred2, y_true2)

sensitivity2 = cm2[0, 0] / (cm2[0, 0] + cm2[0, 1])
specificity2 = cm2[1, 1] / (cm2[1, 0] + cm2[1, 1])
    
time2=toc-tic

"""###**3. Xception**"""

def Covid_model3():
    input_img = tf.keras.layers.Input(shape=(512, 512, 3))
    baseModel = Xception(weights="imagenet", include_top=False,
	  input_tensor=tf.keras.layers.Input(shape=(512, 512, 3)))

     
    for layer in baseModel.layers[:-3]:
        layer.trainable = False
    x = baseModel.output
    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Dropout(0.25)(x)

    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    

    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Dropout(0.25)(x)

    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.5)(x)

    x = tf.keras.layers.Dense(2, activation='softmax')(x)
  
    
    covid_model = tf.keras.models.Model(baseModel.input, x)
    adagrad=tf.keras.optimizers.Adagrad(lr=0.001)
    covid_model.compile(optimizer=adagrad, loss='binary_crossentropy',metrics=["accuracy"])
    return covid_model

model3 = Covid_model3()
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', verbose=1,patience=10,mode='max',restore_best_weights=True)
covid= model3.fit_generator(Datagen.flow(x_train, y_train, batch_size=8),steps_per_epoch=len(x_train) / 8, validation_data=(x_valid, y_valid), epochs=5,callbacks = [early_stopping])

tic=time.clock()
y_pred3 = model3.predict(x_test, batch_size=8)
toc=time.clock()
y_pred3 = np.argmax(y_pred3, axis=1)
y_true3 = np.argmax(y_test, axis=1)


predicted_metrics3 = model3.evaluate(x_test, y_test,batch_size=8, verbose=0)

for name, value in zip(model3.metrics_names, predicted_metrics3):
  print(name, ': ', value)

print(classification_report(y_pred3, y_true,target_names=lb.classes_))
cm3 = confusion_matrix(y_pred, y_true)

acc3=predicted_metrics3[1]

sensitivity3 = cm3[0, 0] / (cm3[0, 0] + cm3[0, 1])
specificity3 = cm3[1, 1] / (cm3[1, 0] + cm3[1, 1])
time3=toc-tic

"""###**Accuracy comparision**"""

a=['VGG16','VGG19','Xception']
b=[acc,acc2,acc3]

fig=sns.barplot(x=a,y=b)
fig.set(xlabel='Model', ylabel='Accuracy')
plt.title("Model Vs Accuracy")
plt.ylim(0,1)
plt.show()

"""###**confusion matrix**"""

plt.figure(figsize=(5,4))
sns.heatmap(cm, annot=True, fmt="d")
plt.title('Confusion matrix of VGG16')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')

plt.figure(figsize=(5,4))
sns.heatmap(cm2, annot=True, fmt="d")
plt.title('Confusion matrix of VGG19')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')

plt.figure(figsize=(5,4))
sns.heatmap(cm3, annot=True, fmt="d")
plt.title('Confusion matrix of Xception')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')

"""###**Accuracy and loss of test and validation data at different Epoch**

##
"""

z=[2,5,10,20,40,60,80,100]
accura=[]
los=[]
accura1=[]
los1=[]
for epoch in (z):
  covid21= model2.fit_generator(Datagen.flow(x_train, y_train, batch_size=8),steps_per_epoch=len(x_train) / 8,validation_data=(x_valid, y_valid), epochs=epoch,callbacks = [early_stopping])
  y_pred21 = model2.predict(x_test, batch_size=8)
  y_pred21 = np.argmax(y_pred21, axis=1)
  y_true21 = np.argmax(y_test, axis=1)
  predicted_metrics21 = model2.evaluate(x_test, y_test, batch_size=8, verbose=0)
  predicted_metrics211 = model2.evaluate(x_valid, y_valid, batch_size=8, verbose=0)
  loss21=predicted_metrics21[0]
  acc21=predicted_metrics21[1]
  loss211=predicted_metrics211[0]
  acc211=predicted_metrics211[1]
  los.append(loss21)
  accura.append(acc21)

  los1.append(loss211)
  accura1.append(acc211)

"""##**Accuracy Vs Epoch**"""

a1,=plt.plot(z,accura,color='r')
a2,=plt.plot(z,accura1,color='b')
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.legend([a1,a2],['train_acc','val_acc'])
plt.show()

"""##**Loss Vs Epoch**"""

a1,=plt.plot(z,los,color='r')
a2,=plt.plot(z,los1,color='b')
plt.xlabel('epochs')
plt.ylabel('loss accuracy')
plt.legend([a1,a2],['train_loss','val_loss'])
plt.show()

"""##**Time of prediction**"""

time_=[time1,time2,time3]
time_

fig=sns.barplot(x=a,y=time_)
fig.set(xlabel='Model', ylabel='time of prediction')
plt.title("Model Vs time of prediction")
plt.show()

def Covid_model():
    input_img = tf.keras.layers.Input(shape=(512, 512, 3))
    baseModel = VGG19(weights="imagenet", include_top=False,
	  input_tensor=tf.keras.layers.Input(shape=(512, 512, 3)))

    # Make all pre-trained layers from VGG19 non-trainable (Don't train existing weights)
    for layer in baseModel.layers[:-3]:
        layer.trainable = False
    

    #x = baseModel.output
    #x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    #x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    #x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    #x = tf.keras.layers.Dropout(0.25)(x)

    #x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    #x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    #x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    #x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    #x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    #x = tf.keras.layers.Dropout(0.25)(x)
    

    #x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    #x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    #x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    #x = tf.keras.layers.BatchNormalization(axis=-1)(x)

    #x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    #x = tf.keras.layers.BatchNormalization(axis=-1)(x)
    #x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    #x = tf.keras.layers.Dropout(0.25)(x)
    x = Flatten()(baseModel.output)

    #x = Flatten()(baseModel.output)
    x = Dense(256, activation='relu')(x)
    #x = BatchNormalization()(x)
    x = Dropout(0.5)(x)

    x = Dense(2, activation='softmax')(x)
  
    
    covid_model = tf.keras.models.Model(baseModel.input, x)
    adagrad=tf.keras.optimizers.Adagrad(lr=0.001)
    covid_model.compile(optimizer=adagrad, loss='binary_crossentropy',metrics=["accuracy"])
    return covid_model

