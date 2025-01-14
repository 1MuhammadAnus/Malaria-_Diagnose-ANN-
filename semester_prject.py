# -*- coding: utf-8 -*-
"""Semester_prject.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HumnlwO4Tdg7zHexzl0-mkLs0QFf-yPo
"""

import tensorflow as tf
import tensorflow_datasets as tfds
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.layers import Conv2D, MaxPooling2D, InputLayer, Dense, Flatten ,BatchNormalization
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.optimizers import Adam

# Load the dataset
data, data_info = tfds.load('malaria', with_info=True, as_supervised=True, shuffle_files=True, split=['train'])

# Function to split the dataset
def split(dataset, train_rat, val_rat, test_rat):
    length = len(list(dataset))

    tr_data = dataset.take(int(train_rat * length))
    val_test_data = dataset.skip(int(train_rat * length))

    val_data = val_test_data.take(int(val_rat * length))
    tst_data = val_test_data.skip(int(val_rat * length))

    return tr_data, val_data, tst_data

# Split ratios
train_rat = 0.6
val_rat = 0.2
test_rat = 0.2

# Split the dataset
trda, vd, tsd = split(data[0], train_rat, val_rat, test_rat)

# Print the shapes of the splits
print(list(trda.take(1).as_numpy_iterator()))
print(list(vd.take(1).as_numpy_iterator()))
print(list(tsd.take(1).as_numpy_iterator()))

# Plot some images
for i, (image, label) in enumerate(trda.take(16)):
    ax = plt.subplot(4, 4, i + 1)
    plt.imshow(image)
    plt.title(data_info.features['label'].int2str(label))
    plt.axis('off')

# Resizing the image
IM_SIZE = 224

def rescale_resizing(img, label):
    img = tf.image.resize(img, (IM_SIZE, IM_SIZE)) / 255.0
    label = tf.expand_dims(label, axis=-1)  # Ensure label shape is (None, 1)
    return img, label

train_data = trda.map(rescale_resizing)
train_data = train_data.shuffle(buffer_size=8, reshuffle_each_iteration=True).batch(32).prefetch(tf.data.AUTOTUNE)

# Define the model
lenet_model = tf.keras.Sequential([
    InputLayer(input_shape=(IM_SIZE, IM_SIZE, 3)),
    Conv2D(filters=6, kernel_size=2, strides=1, padding='valid', activation='relu'),
    BatchNormalization(),

    MaxPooling2D(pool_size=2, strides=2),
    Conv2D(filters=16, kernel_size=2, strides=1, padding='valid', activation='relu'),
    BatchNormalization(),

    MaxPooling2D(pool_size=2, strides=2),
    Flatten(),

    Dense(1000, activation='relu'),
    BatchNormalization(),
    Dense(100, activation='relu'),
    BatchNormalization(),
    Dense(1, activation='sigmoid')
])

lenet_model.summary()

val_data = vd.map(rescale_resizing)
val_data = val_data.shuffle(buffer_size=8, reshuffle_each_iteration=True).batch(32).prefetch(tf.data.AUTOTUNE)

# Compile and train the model
lenet_model.compile(optimizer=Adam(learning_rate=0.01), loss=BinaryCrossentropy() , metrics='accuracy')
history = lenet_model.fit(train_data, validation_data=val_data, epochs=10, verbose=1)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title("Loss")
plt.ylabel('loss')
plt.xlabel('epochs')
plt.legend(['loss' , 'val_loss'])
plt.show()

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title("Accuracy")
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend(['Accuracy' , 'Val_Accuracy'])
plt.show()

"""**Evaluating And Testing the Models**"""

test_data= tsd.map(rescale_resizing)
test_data = test_data.batch(1)

# test_data
lenet_model.evaluate(test_data)

lenet_model.predict(test_data.take(1))[0][0]

def pre(x):
  if(x<0.5):
    print("P")
  else:
    print("u")

pre(lenet_model.predict(test_data.take(1))[0][0])

for i, (image, label) in enumerate(test_data.take(9)):
    ax = plt.subplot(3,3, i + 1)
    plt.imshow(image[0])
    plt.title(str(pre(label.numpy()[0])) + ":" + str( pre(lenet_model.predict(image)[0][0])))
    plt.axis('off')

