import numpy as np
import tensorflow as tf
import time

EPOCHS = 50


#Main function that compiles the loading of the data and training of the model.
def main():

    acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, extracted_data, y_train = load_data()

    # Get a compiled neural network
    model = get_ann_model()
    print(model.summary())
    
    # Fit model on training data
    model.fit((acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, extracted_data), y_train, epochs=EPOCHS)

    t_acc_x, t_acc_y, t_acc_z, t_gyr_x, t_gyr_y, t_gyr_z, extracted_test_data, y_test = load_test_data()

    # Evaluate neural network performance
    model.evaluate((t_acc_x, t_acc_y, t_acc_z, t_gyr_x, t_gyr_y, t_gyr_z, extracted_test_data),  y_test, verbose=2)
    
    # Create confusion matrix
    start = time.perf_counter()
    y_pred = model.predict((t_acc_x, t_acc_y, t_acc_z,t_gyr_x, t_gyr_y, t_gyr_z, extracted_test_data))
    print(time.perf_counter() - start)
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
    write_param(model)
    convert_to_C()
    

# Function loads the model layer parameters into a text file.
def write_param(model):

    print("Writing weights and bias")

    weight = np.array(model.layers[13].get_weights()[0])
    np.savetxt("DataSet-Weights\\layerx1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[20].get_weights()[0])
    np.savetxt("DataSet-Weights\\layerx2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[14].get_weights()[0])
    np.savetxt("DataSet-Weights\\layery1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[21].get_weights()[0])
    np.savetxt("DataSet-Weights\\layery2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[15].get_weights()[0])
    np.savetxt("DataSet-Weights\\layerz1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[22].get_weights()[0])
    np.savetxt("DataSet-Weights\\layerz2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[16].get_weights()[0])
    np.savetxt("DataSet-Weights\\layergx1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[23].get_weights()[0])
    np.savetxt("DataSet-Weights\\layergx2.txt", weight, fmt="%f", delimiter=",")           

    weight = np.array(model.layers[17].get_weights()[0])
    np.savetxt("DataSet-Weights\\layergy1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[24].get_weights()[0])
    np.savetxt("DataSet-Weights\\layergy2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[18].get_weights()[0])
    np.savetxt("DataSet-Weights\\layergz1.txt", weight, fmt="%f", delimiter=",")       

    weight = np.array(model.layers[25].get_weights()[0])
    np.savetxt("DataSet-Weights\\layergz2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[19].get_weights()[0])
    np.savetxt("DataSet-Weights\\layerdata1.txt", weight, fmt="%f", delimiter=",")
    
    weight = np.array(model.layers[26].get_weights()[0])
    np.savetxt("DataSet-Weights\\layerdata2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[35].get_weights()[0])
    np.savetxt("DataSet-Weights\\layerfinal1.txt", weight, fmt="%f", delimiter=",") 

    weight = np.array(model.layers[37].get_weights()[0])
    np.savetxt("DataSet-Weights\\layerfinal2.txt", weight, fmt="%f", delimiter=",")


def convert(filename):
    node = []
    text = []
    with open(filename,"r") as f:
        for line in f:
            row  = np.array(line.split(",")).astype(np.float32)
            node.append(row)
        node = np.transpose(node)
    np.savetxt(filename, node, fmt="%f", delimiter=",")
    with open(filename,"r") as f:
        for line in f:
            text.append("[" + line.strip() + "],\n")
    with open(filename,"w") as f:
        f.writelines(text)

# Function convert the txt to C++ arrays
def convert_to_C():

    files = ["DataSet-Weights\\layerx1.txt",
            "DataSet-Weights\\layerx2.txt",
            "DataSet-Weights\\layery1.txt",
            "DataSet-Weights\\layery2.txt",
            "DataSet-Weights\\layerz1.txt",
            "DataSet-Weights\\layerz2.txt",
            "DataSet-Weights\\layergx1.txt",
            "DataSet-Weights\\layergx2.txt",
            "DataSet-Weights\\layergy1.txt",
            "DataSet-Weights\\layergy2.txt",
            "DataSet-Weights\\layergz1.txt",
            "DataSet-Weights\\layergz2.txt",
            "DataSet-Weights\\layerdata1.txt",
            "DataSet-Weights\\layerdata2.txt",
            "DataSet-Weights\\layerfinal1.txt",
            "DataSet-Weights\\layerfinal2.txt"
            ]
    
    for f in files:
        convert(f)


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

    extracted_data = extract_data(np.array(body_acc_x).astype(np.float32), np.array(body_acc_y).astype(np.float32), np.array(body_acc_z).astype(np.float32), np.array(body_gyr_x).astype(np.float32), np.array(body_gyr_y).astype(np.float32), np.array(body_gyr_z).astype(np.float32))
    body_acc_x = np.transpose([body_acc_x],(1,2,0)).astype(np.float32)
    body_acc_y = np.transpose([body_acc_y],(1,2,0)).astype(np.float32)
    body_acc_z = np.transpose([body_acc_z],(1,2,0)).astype(np.float32)
    body_gyr_x = np.transpose([body_gyr_x],(1,2,0)).astype(np.float32)
    body_gyr_y = np.transpose([body_gyr_y],(1,2,0)).astype(np.float32)
    body_gyr_z = np.transpose([body_gyr_z],(1,2,0)).astype(np.float32)

    return body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z, extracted_data, np.array(label).astype(np.float32)


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

    extracted_data = extract_data(np.array(body_acc_x).astype(np.float32), np.array(body_acc_y).astype(np.float32), np.array(body_acc_z).astype(np.float32), np.array(body_gyr_x).astype(np.float32), np.array(body_gyr_y).astype(np.float32), np.array(body_gyr_z).astype(np.float32))
    body_acc_x = np.transpose([body_acc_x],(1,2,0)).astype(np.float32)
    body_acc_y = np.transpose([body_acc_y],(1,2,0)).astype(np.float32)
    body_acc_z = np.transpose([body_acc_z],(1,2,0)).astype(np.float32)
    body_gyr_x = np.transpose([body_gyr_x],(1,2,0)).astype(np.float32)
    body_gyr_y = np.transpose([body_gyr_y],(1,2,0)).astype(np.float32)
    body_gyr_z = np.transpose([body_gyr_z],(1,2,0)).astype(np.float32)

    return body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z, extracted_data, np.array(label).astype(np.float32)


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
    inputG = tf.keras.layers.Input(shape=(24,))

    data = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(inputG)
    data = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(data)
    data = tf.keras.layers.Dropout(0.5)(data)
    data = tf.keras.Model(inputs=inputG, outputs=data)

    x = tf.keras.layers.Flatten()(inputA)
    x = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(x)
    x = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    x = tf.keras.Model(inputs=inputA, outputs=x)

    y = tf.keras.layers.Flatten()(inputB)
    y = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(y)
    y = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(y)
    y = tf.keras.layers.Dropout(0.5)(y)
    y = tf.keras.Model(inputs=inputB, outputs=y)

    z = tf.keras.layers.Flatten()(inputC)
    z = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(z)
    z = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(z)
    z = tf.keras.layers.Dropout(0.5)(z)
    z = tf.keras.Model(inputs=inputC, outputs=z)

    g_x = tf.keras.layers.Flatten()(inputD)
    g_x = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(g_x)
    g_x = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(g_x)
    g_x = tf.keras.layers.Dropout(0.5)(g_x)
    g_x = tf.keras.Model(inputs=inputD, outputs=g_x)

    g_y = tf.keras.layers.Flatten()(inputE)
    g_y = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(g_y)
    g_y = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(g_y)
    g_y = tf.keras.layers.Dropout(0.5)(g_y)
    g_y = tf.keras.Model(inputs=inputE, outputs=g_y)

    g_z = tf.keras.layers.Flatten()(inputF)
    g_z = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(g_z)
    g_z = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(g_z)
    g_z = tf.keras.layers.Dropout(0.5)(g_z)
    g_z = tf.keras.Model(inputs=inputF, outputs=g_z)

    combined = tf.keras.layers.concatenate([x.output, y.output, z.output, g_x.output, g_y.output, g_z.output, data.output])

    final = tf.keras.layers.Dense(32, activation="relu", use_bias=False)(combined)
    final = tf.keras.layers.Dropout(0.5)(final)
    final = tf.keras.layers.Dense(5, activation="softmax", use_bias=False)(final)

    model = tf.keras.Model(inputs=[x.input, y.input, z.input, g_x.input, g_y.input, g_z.input, data.input], outputs=final)

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

    x = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(inputA)
    x = tf.keras.layers.MaxPooling1D(pool_size=3)(x)
    x = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(x)
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.Model(inputs=inputA, outputs=x)

    y = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(inputB)
    y = tf.keras.layers.MaxPooling1D(pool_size=3)(y)
    y = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(y)
    y = tf.keras.layers.Flatten()(y)
    y = tf.keras.Model(inputs=inputB, outputs=y)

    z = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(inputC)
    z = tf.keras.layers.MaxPooling1D(pool_size=3)(z)
    z = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(z)
    z = tf.keras.layers.Flatten()(z)
    z = tf.keras.Model(inputs=inputC, outputs=z)

    g_x = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(inputD)
    g_x = tf.keras.layers.MaxPooling1D(pool_size=3)(g_x)
    g_x = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(g_x)
    g_x = tf.keras.layers.Flatten()(g_x)
    g_x = tf.keras.Model(inputs=inputD, outputs=g_x)

    g_y = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(inputE)
    g_y = tf.keras.layers.MaxPooling1D(pool_size=3)(g_y)
    g_y = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(g_y)
    g_y = tf.keras.layers.Flatten()(g_y)
    g_y = tf.keras.Model(inputs=inputE, outputs=g_y)

    g_z = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(inputF)
    g_z = tf.keras.layers.MaxPooling1D(pool_size=3)(g_z)
    g_z = tf.keras.layers.Conv1D(filters=12, kernel_size=3, activation="relu")(g_z)
    g_z = tf.keras.layers.Flatten()(g_z)
    g_z = tf.keras.Model(inputs=inputF, outputs=g_z)

    combined = tf.keras.layers.concatenate([x.output, y.output, z.output, g_x.output, g_y.output, g_z.output])

    final = tf.keras.layers.Dense(256, activation="relu")(combined)
    final = tf.keras.layers.Dropout(0.5)(final)
    final = tf.keras.layers.Dense(64, activation="relu")(final)
    final = tf.keras.layers.Dropout(0.5)(final)
    final = tf.keras.layers.Dense(5, activation="softmax")(final)

    model = tf.keras.Model(inputs=[x.input, y.input, z.input, g_x.input, g_y.input, g_z.input], outputs=final)
    

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