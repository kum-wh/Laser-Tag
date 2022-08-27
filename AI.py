import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
TEST_SIZE = 0.4


def main():

    # Get image arrays and labels for all image files
    actions, labels = load_data()
    print(x_train)
    print(y_train)
    # Split data into training and testing sets
    #labels = tf.keras.utils.to_categorical(labels)
    #x_train, x_test, y_train, y_test = train_test_split(
    #    np.array(actions), np.array(labels), test_size=TEST_SIZE
    #)

    # Get a compiled neural network
    #model = get_model()

    # Fit model on training data
    #model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    #model.evaluate(x_test,  y_test, verbose=2)


def load_data():
    
    actions = []
    labels = []
    with open("Dataset\\test\\X_test.txt","r") as f:
        line = f.readline()
        while line != "":
            actions.append(line)
    with open("Dataset\\test\\y_test.txt","r") as y:
        line = f.readline()
        print()
    return (actions,labels)

    def load_X(X_signals_paths):
    X_signals = []
    
    for signal_type_path in X_signals_paths:
        file = open(signal_type_path, 'r')
        # Read dataset from disk, dealing with text files' syntax
        X_signals.append(
            [np.array(serie, dtype=np.float32) for serie in [
                row.replace('  ', ' ').strip().split(' ') for row in file
            ]]
        )
        file.close()
    
    return np.transpose(np.array(X_signals), (1, 2, 0))

X_train_signals_paths = [
    DATASET_PATH + TRAIN + "Inertial Signals/" + signal + "train.txt" for signal in INPUT_SIGNAL_TYPES
]
X_test_signals_paths = [
    DATASET_PATH + TEST + "Inertial Signals/" + signal + "test.txt" for signal in INPUT_SIGNAL_TYPES
]

X_train = load_X(X_train_signals_paths)
X_test = load_X(X_test_signals_paths)


def get_model():
    
    model = tf.keras.models.Sequential([

        tf.keras.layers.Dense(10, activation="relu"),

        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()