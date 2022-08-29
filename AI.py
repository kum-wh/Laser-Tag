import numpy as np
import tensorflow as tf


EPOCHS = 5


#Main function that compiles the loading of the data and training of the model.
def main():

    x_train = load_data()
    y_train = load_label()

    # Get a compiled neural network
    model = get_model()
    print(model.summary())

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    x_test = load_test_data()
    y_test = load_test_label()
    
    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Extracts the model weights and bias.
    write_param(model)
  

# Function loads the model layer parameters into a text file.
def write_param(model):

    print("Writing weights and bias")

    #Dense Layer 1
    weight_1 = np.array(model.layers[1].get_weights()[0])
    bias_1 = np.array(model.layers[1].get_weights()[1])
    
    with open("layer1.txt", "w") as f:
        for row in weight_1:
            f.write(str(row) + "\n")
            
    with open("bias1.txt", "w") as f:
        f.write(str(bias_1))

    #Dense Layer 2
    weight_2 = np.array(model.layers[2].get_weights()[0])
    bias_2 = np.array(model.layers[2].get_weights()[1])

    with open("layer2.txt", "w") as f:
        for row in weight_2:
            f.write(str(row) + "\n")
        
    with open("bias2.txt", "w") as f:
        f.write(str(bias_2))

    #Output Layer
    weight_3 = np.array(model.layers[3].get_weights()[0])
    bias_3 = np.array(model.layers[3].get_weights()[1])

    with open("layer3.txt", "w") as f:
        for row in weight_3:
            f.write(str(row) + "\n")
        
    with open("bias3.txt", "w") as f:
        f.write(str(bias_3))


# Function loads the sensor data.
def load_data():

    print("Loading Training Data . . .")

    body_acc_x = []
    body_acc_y = []
    body_acc_z = []
    body_gyr_x = []
    body_gyr_y = []
    body_gyr_z = []
    
    with open("Dataset\\train\\Inertial Signals\\body_acc_x_train.txt", 'r') as f:
        for row in f:
            body_acc_x.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\train\\Inertial Signals\\body_acc_y_train.txt", 'r') as f:
        for row in f:
            body_acc_y.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\train\\Inertial Signals\\body_acc_z_train.txt", 'r') as f:
        for row in f:
             body_acc_z.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\train\\Inertial Signals\\body_gyro_x_train.txt", 'r') as f:
        for row in f:
            body_gyr_x.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\train\\Inertial Signals\\body_gyro_y_train.txt", 'r') as f:
        for row in f:
            body_gyr_y.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\train\\Inertial Signals\\body_gyro_z_train.txt", 'r') as f:
        for row in f:
            body_gyr_z.append(row.replace("  ", " ").strip().split(" "))

    return np.transpose([body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z],(1,2,0)).astype(np.float64)


# Function loads the sensor data for testing.
def load_test_data():

    print("Loading Testing Data . . .")

    body_acc_x = []
    body_acc_y = []
    body_acc_z = []
    body_gyr_x = []
    body_gyr_y = []
    body_gyr_z = []
    
    with open("Dataset\\test\\Inertial Signals\\body_acc_x_test.txt", 'r') as f:
        for row in f:
            body_acc_x.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\test\\Inertial Signals\\body_acc_y_test.txt", 'r') as f:
        for row in f:
            body_acc_y.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\test\\Inertial Signals\\body_acc_z_test.txt", 'r') as f:
        for row in f:
             body_acc_z.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\test\\Inertial Signals\\body_gyro_x_test.txt", 'r') as f:
        for row in f:
            body_gyr_x.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\test\\Inertial Signals\\body_gyro_y_test.txt", 'r') as f:
        for row in f:
            body_gyr_y.append(row.replace("  ", " ").strip().split(" "))

    with open("Dataset\\test\\Inertial Signals\\body_gyro_z_test.txt", 'r') as f:
        for row in f:
            body_gyr_z.append(row.replace("  ", " ").strip().split(" "))

    return np.transpose([body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z],(1,2,0)).astype(np.float64)


# Function loads the label actions respective to the sensor data.
def load_label():

    print("Loading Training Labels . . .")

    label = []

    with open("Dataset\\train\\y_train.txt") as f:
        for row in f:
            number = int(row.strip())
            if number == 1:
                label.append([1,0,0,0,0,0])
            elif number == 2:
                label.append([0,1,0,0,0,0])
            elif number == 3:
                label.append([0,0,1,0,0,0])
            elif number == 4:
                label.append([0,0,0,1,0,0])
            elif number == 5:
                label.append([0,0,0,0,1,0])
            elif number == 6:
                label.append([0,0,0,0,0,1])
    
    return np.array(label).astype(np.float64)


# Function loads the label actions respective to the sensor data for the testing set.
def load_test_label():

    print("Loading Testing Labels . . .")

    label = []

    with open("Dataset\\test\\y_test.txt") as f:
        for row in f:
            number = int(row.strip())
            if number == 1:
                label.append([1,0,0,0,0,0])
            elif number == 2:
                label.append([0,1,0,0,0,0])
            elif number == 3:
                label.append([0,0,1,0,0,0])
            elif number == 4:
                label.append([0,0,0,1,0,0])
            elif number == 5:
                label.append([0,0,0,0,1,0])
            elif number == 6:
                label.append([0,0,0,0,0,1])
    
    return np.array(label).astype(np.float64)


# Function creates the artificial neural network model.
def get_model():
    
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(128, 6)),
        tf.keras.layers.Dense(256, activation="relu"),
        tf.keras.layers.Dense(256, activation="relu"),
        tf.keras.layers.Dense(6, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()