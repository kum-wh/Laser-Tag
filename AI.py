import numpy as np
import tensorflow as tf


EPOCHS = 15


#Main function that compiles the loading of the data and training of the model.
def main():

    acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, x_train, extracted_data, y_train = load_data()

    # Get a compiled neural network
    model = get_ann_model()
    print(model.summary())

    # Fit model on training data
    model.fit((acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, x_train, extracted_data), y_train, epochs=EPOCHS)
    
    t_acc_x, t_acc_y, t_acc_z, t_gyr_x, t_gyr_y, t_gyr_z, x_test, extracted_test_data, y_test = load_test_data()
    
    # Evaluate neural network performance
    model.evaluate((t_acc_x, t_acc_y, t_acc_z, t_gyr_x, t_gyr_y, t_gyr_z, x_test, extracted_test_data),  y_test, verbose=2)

    # Create confusion matrix
    y_pred = model.predict((t_acc_x, t_acc_y, t_acc_z,t_gyr_x, t_gyr_y, t_gyr_z, x_test, extracted_test_data))
    y_pred = tf.argmax(y_pred, axis=1)
    y_test = tf.argmax(y_test, axis=1 )
    print(tf.math.confusion_matrix(y_test, y_pred))
    
    model = get_cnn_model()
    model.fit((acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, x_train), y_train, epochs=EPOCHS)
    model.evaluate((t_acc_x, t_acc_y, t_acc_z, t_gyr_x, t_gyr_y, t_gyr_z, x_test),  y_test, verbose=2)
    y_pred = model.predict((t_acc_x, t_acc_y, t_acc_z,t_gyr_x, t_gyr_y, t_gyr_z, x_test))
    y_pred = tf.argmax(y_pred, axis=1)
    y_test = tf.argmax(y_test, axis=1 )
    print(tf.math.confusion_matrix(y_test, y_pred))

    model = get_rnn_model()
    print(model.summary())
    model.fit(x_train, y_train, epochs=EPOCHS)
    model.evaluate(x_test,  y_test, verbose=2)
    
    # Extracts the model weights and bias.
    # write_param(model)


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

    print("Loading Training Labels . . .")

    label = []

    with open("Dataset\\train\\y_train.txt") as f:

        for row in f:
            number = int(row.strip())

            if number == 1:
                label.append([1,0,0,0,0])
            elif number == 2:
                label.append([0,1,0,0,0])
            elif number == 3:
                label.append([0,0,1,0,0])
            elif number == 4:
                label.append([0,0,0,1,0])
            else:
                label.append([0,0,0,0,1])

    total = np.transpose([body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z],(1,2,0)).astype(np.float64)
    extracted_data = extract_data(np.array(body_acc_x).astype(np.float64), np.array(body_acc_y).astype(np.float64), np.array(body_acc_z).astype(np.float64), np.array(body_gyr_x).astype(np.float64), np.array(body_gyr_y).astype(np.float64), np.array(body_gyr_z).astype(np.float64))
    body_acc_x = np.transpose([body_acc_x],(1,2,0)).astype(np.float64)
    body_acc_y = np.transpose([body_acc_y],(1,2,0)).astype(np.float64)
    body_acc_z = np.transpose([body_acc_z],(1,2,0)).astype(np.float64)
    body_gyr_x = np.transpose([body_gyr_x],(1,2,0)).astype(np.float64)
    body_gyr_y = np.transpose([body_gyr_y],(1,2,0)).astype(np.float64)
    body_gyr_z = np.transpose([body_gyr_z],(1,2,0)).astype(np.float64)

    return body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z, total, extracted_data, np.array(label).astype(np.float64)


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

    print("Loading Testing Labels . . .")

    label = []

    with open("Dataset\\test\\y_test.txt") as f:
           
        for row in f:
            number = int(row.strip())

            
            if number == 1:
                label.append([1,0,0,0,0])
            elif number == 2:
                label.append([0,1,0,0,0])
            elif number == 3:
                label.append([0,0,1,0,0])
            elif number == 4:
                label.append([0,0,0,1,0])
            else:
                label.append([0,0,0,0,1])

    total = np.transpose([body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z],(1,2,0)).astype(np.float64)
    extracted_data = extract_data(np.array(body_acc_x).astype(np.float64), np.array(body_acc_y).astype(np.float64), np.array(body_acc_z).astype(np.float64), np.array(body_gyr_x).astype(np.float64), np.array(body_gyr_y).astype(np.float64), np.array(body_gyr_z).astype(np.float64))
    body_acc_x = np.transpose([body_acc_x],(1,2,0)).astype(np.float64)
    body_acc_y = np.transpose([body_acc_y],(1,2,0)).astype(np.float64)
    body_acc_z = np.transpose([body_acc_z],(1,2,0)).astype(np.float64)
    body_gyr_x = np.transpose([body_gyr_x],(1,2,0)).astype(np.float64)
    body_gyr_y = np.transpose([body_gyr_y],(1,2,0)).astype(np.float64)
    body_gyr_z = np.transpose([body_gyr_z],(1,2,0)).astype(np.float64)

    return body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z, total, extracted_data, np.array(label).astype(np.float64)


# Function extract mean, standard deviation, maximum value and minimum value from array
def extract_data(body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z):

    acc_x_mean = np.mean(body_acc_x, axis=1).reshape(-1,1)
    acc_y_mean = np.mean(body_acc_y, axis=1).reshape(-1,1)
    acc_z_mean = np.mean(body_acc_z, axis=1).reshape(-1,1)
    gyr_x_mean = np.mean(body_gyr_x, axis=1).reshape(-1,1)
    gyr_y_mean = np.mean(body_gyr_y, axis=1).reshape(-1,1)
    gyr_z_mean = np.mean(body_gyr_z, axis=1).reshape(-1,1)

    sd_acc_x = np.std(body_acc_x, axis=1).reshape(-1,1)
    sd_acc_y = np.std(body_acc_y, axis=1).reshape(-1,1)
    sd_acc_z = np.std(body_acc_z, axis=1).reshape(-1,1)
    sd_gyr_x = np.std(body_gyr_x, axis=1).reshape(-1,1)
    sd_gyr_y = np.std(body_gyr_y, axis=1).reshape(-1,1)
    sd_gyr_z = np.std(body_gyr_z, axis=1).reshape(-1,1)

    max_acc_x = np.amax(body_acc_x, axis=1).reshape(-1,1)
    max_acc_y = np.amax(body_acc_y, axis=1).reshape(-1,1)
    max_acc_z = np.amax(body_acc_z, axis=1).reshape(-1,1)
    max_gyr_x = np.amax(body_gyr_x, axis=1).reshape(-1,1)
    max_gyr_y = np.amax(body_gyr_y, axis=1).reshape(-1,1)
    max_gyr_z = np.amax(body_gyr_z, axis=1).reshape(-1,1)

    min_acc_x = np.amin(body_acc_x, axis=1).reshape(-1,1)
    min_acc_y = np.amin(body_acc_y, axis=1).reshape(-1,1)
    min_acc_z = np.amin(body_acc_z, axis=1).reshape(-1,1)
    min_gyr_x = np.amin(body_gyr_x, axis=1).reshape(-1,1)
    min_gyr_y = np.amin(body_gyr_y, axis=1).reshape(-1,1)
    min_gyr_z = np.amin(body_gyr_z, axis=1).reshape(-1,1)

    return np.concatenate((acc_x_mean, acc_y_mean, acc_z_mean, gyr_x_mean, gyr_y_mean, gyr_z_mean, sd_acc_x, sd_acc_y, sd_acc_z, sd_gyr_x, sd_gyr_y, sd_gyr_z, max_acc_x, max_acc_y, max_acc_z, max_gyr_x, max_gyr_y, max_gyr_z, min_acc_x, min_acc_y, min_acc_z, min_gyr_x, min_gyr_y, min_gyr_z), axis=1)


# Function creates the artificial neural network model.
def get_ann_model():

    inputA = tf.keras.layers.Input(shape=(128,1))
    inputB = tf.keras.layers.Input(shape=(128,1))
    inputC = tf.keras.layers.Input(shape=(128,1))
    inputD = tf.keras.layers.Input(shape=(128,1))
    inputE = tf.keras.layers.Input(shape=(128,1))
    inputF = tf.keras.layers.Input(shape=(128,1))
    inputG = tf.keras.layers.Input(shape=(128,6))
    inputH = tf.keras.layers.Input(shape=(24,))

    data = tf.keras.layers.Dense(256, activation="relu")(inputH)
    data = tf.keras.layers.Dense(256, activation="relu")(data)
    data = tf.keras.layers.Dropout(0.5)(data)
    data = tf.keras.Model(inputs=inputH, outputs=data)

    x = tf.keras.layers.Flatten()(inputA)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    x = tf.keras.Model(inputs=inputA, outputs=x)

    y = tf.keras.layers.Flatten()(inputB)
    y = tf.keras.layers.Dense(256, activation="relu")(y)
    y = tf.keras.layers.Dense(256, activation="relu")(y)
    y = tf.keras.layers.Dropout(0.5)(y)
    y = tf.keras.Model(inputs=inputB, outputs=y)

    z = tf.keras.layers.Flatten()(inputC)
    z = tf.keras.layers.Dense(256, activation="relu")(z)
    z = tf.keras.layers.Dense(256, activation="relu")(z)
    z = tf.keras.layers.Dropout(0.5)(z)
    z = tf.keras.Model(inputs=inputC, outputs=z)

    g_x = tf.keras.layers.Flatten()(inputD)
    g_x = tf.keras.layers.Dense(256, activation="relu")(g_x)
    g_x = tf.keras.layers.Dense(256, activation="relu")(g_x)
    g_x = tf.keras.layers.Dropout(0.5)(g_x)
    g_x = tf.keras.Model(inputs=inputD, outputs=g_x)

    g_y = tf.keras.layers.Flatten()(inputE)
    g_y = tf.keras.layers.Dense(256, activation="relu")(g_y)
    g_y = tf.keras.layers.Dense(256, activation="relu")(g_y)
    g_y = tf.keras.layers.Dropout(0.5)(g_y)
    g_y = tf.keras.Model(inputs=inputE, outputs=g_y)

    g_z = tf.keras.layers.Flatten()(inputF)
    g_z = tf.keras.layers.Dense(256, activation="relu")(g_z)
    g_z = tf.keras.layers.Dense(256, activation="relu")(g_z)
    g_z = tf.keras.layers.Dropout(0.5)(g_z)
    g_z = tf.keras.Model(inputs=inputF, outputs=g_z)

    total = tf.keras.layers.Flatten()(inputG)
    total = tf.keras.layers.Dense(512, activation="relu")(total)
    total = tf.keras.layers.Dense(512, activation="relu")(total)
    total = tf.keras.layers.Dropout(0.5)(total)
    total = tf.keras.Model(inputs=inputG, outputs=total)

    combined = tf.keras.layers.concatenate([x.output, y.output, z.output, g_x.output, g_y.output, g_z.output, total.output, data.output])

    final = tf.keras.layers.Dense(512, activation="relu")(combined)
    final = tf.keras.layers.Dropout(0.5)(final)
    final = tf.keras.layers.Dense(512, activation="relu")(final)
    final = tf.keras.layers.Dropout(0.5)(final)
    final = tf.keras.layers.Dense(256, activation="relu")(final)
    final = tf.keras.layers.Dropout(0.5)(final)
    final = tf.keras.layers.Dense(5, activation="softmax")(final)

    model = tf.keras.Model(inputs=[x.input, y.input, z.input, g_x.input, g_y.input, g_z.input, total.input, data.input], outputs=final)

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


# Function creates the convolutional neural network model.
def get_cnn_model():

    inputA = tf.keras.layers.Input(shape=(128,1))
    inputB = tf.keras.layers.Input(shape=(128,1))
    inputC = tf.keras.layers.Input(shape=(128,1))
    inputD = tf.keras.layers.Input(shape=(128,1))
    inputE = tf.keras.layers.Input(shape=(128,1))
    inputF = tf.keras.layers.Input(shape=(128,1))
    inputG = tf.keras.layers.Input(shape=(128,6))

    x = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(inputA)
    x = tf.keras.layers.MaxPooling1D(pool_size=3)(x)
    x = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(x)
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.Model(inputs=inputA, outputs=x)

    y = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(inputB)
    y = tf.keras.layers.MaxPooling1D(pool_size=3)(y)
    y = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(y)
    y = tf.keras.layers.Flatten()(y)
    y = tf.keras.Model(inputs=inputB, outputs=y)

    z = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(inputC)
    z = tf.keras.layers.MaxPooling1D(pool_size=3)(z)
    z = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(z)
    z = tf.keras.layers.Flatten()(z)
    z = tf.keras.Model(inputs=inputC, outputs=z)

    g_x = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(inputD)
    g_x = tf.keras.layers.MaxPooling1D(pool_size=3)(g_x)
    g_x = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(g_x)
    g_x = tf.keras.layers.Flatten()(g_x)
    g_x = tf.keras.Model(inputs=inputD, outputs=g_x)

    g_y = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(inputE)
    g_y = tf.keras.layers.MaxPooling1D(pool_size=3)(g_y)
    g_y = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(g_y)
    g_y = tf.keras.layers.Flatten()(g_y)
    g_y = tf.keras.Model(inputs=inputE, outputs=g_y)

    g_z = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(inputF)
    g_z = tf.keras.layers.MaxPooling1D(pool_size=3)(g_z)
    g_z = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(g_z)
    g_z = tf.keras.layers.Flatten()(g_z)
    g_z = tf.keras.Model(inputs=inputF, outputs=g_z)

    total = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(inputG)
    total = tf.keras.layers.MaxPooling1D(pool_size=3)(total)
    total = tf.keras.layers.Conv1D(filters=24, kernel_size=3, activation="relu")(total)
    total = tf.keras.layers.Flatten()(total)
    total = tf.keras.Model(inputs=inputG, outputs=total)

    combined = tf.keras.layers.concatenate([x.output, y.output, z.output, g_x.output, g_y.output, g_z.output, total.output])

    final = tf.keras.layers.Dense(2048, activation="relu")(combined)
    final = tf.keras.layers.Dropout(0.5)(final)
    final = tf.keras.layers.Dense(512, activation="relu")(final)
    final = tf.keras.layers.Dropout(0.5)(final)
    final = tf.keras.layers.Dense(5, activation="softmax")(final)

    model = tf.keras.Model(inputs=[x.input, y.input, z.input, g_x.input, g_y.input, g_z.input, total.input], outputs=final)
    

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


# Function creates the Recurrent neural networks
def get_rnn_model():

    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(128, input_shape=(128, 6)),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dense(128, activation="relu"),
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