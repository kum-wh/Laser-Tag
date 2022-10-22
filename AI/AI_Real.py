import numpy as np
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 100

def main():
    
    acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, extracted_data, y_label = load_data()
    acc_x_train, acc_x_test, acc_y_train, acc_y_test, acc_z_train, acc_z_test, gyr_x_train, gyr_x_test, gyr_y_train, gyr_y_test, gyr_z_train, gyr_z_test, extracted_data_train, extracted_data_test, y_train, y_test = train_test_split(acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, extracted_data, y_label, test_size=0.25)
    
    model = get_model()
    print(model.summary())

    model.fit((acc_x_train, acc_y_train, acc_z_train, gyr_x_train, gyr_y_train, gyr_z_train, extracted_data_train), y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate((acc_x_test, acc_y_test, acc_z_test, gyr_x_test, gyr_y_test, gyr_z_test, extracted_data_test),  y_test, verbose=2)
    
    # Print Confusion matrix
    y_pred = model.predict((acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, extracted_data))
    y_pred = tf.argmax(y_pred, axis=1)
    y_test = tf.argmax(y_label, axis=1)
    print(tf.math.confusion_matrix(y_test, y_pred))

    confuse = []
    for i in range(len(y_pred)):
        if y_pred[i] != y_test[i]:
            confuse.append(i)
            print(i)

    with open("confusion.txt", "a") as f:
        f.write(str(confuse).replace("[","").replace("]","") +"\n")

    write_weight(model)
    convert_to_C()
    


def load_data():

    print("Loading Training Data . . .")

    body_acc_x = []
    body_acc_y = []
    body_acc_z = []
    body_gyr_x = []
    body_gyr_y = []
    body_gyr_z = []

    with open("RealData3\\x.txt","r") as f:
        for row in f:
            body_acc_x.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData3\\y.txt","r") as f:
        for row in f:
            body_acc_y.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData3\\z.txt","r") as f:
        for row in f:
            body_acc_z.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData3\\gx.txt","r") as f:
        for row in f:
            body_gyr_x.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData3\\gy.txt","r") as f:
        for row in f:
            body_gyr_y.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData3\\gz.txt","r") as f:
        for row in f:
            body_gyr_z.append(row.replace("[","").replace("]","").strip().split(","))
    
    print("Loading Training Labels . . .")
    
    label = []
    with open("RealData3\\label.txt","r") as f:
        
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

    body_acc_x = np.array(body_acc_x).astype(np.int16)
    body_acc_y = np.array(body_acc_y).astype(np.int16)
    body_acc_z = np.array(body_acc_z).astype(np.int16)
    body_gyr_x = np.array(body_gyr_x).astype(np.int16)
    body_gyr_y = np.array(body_gyr_y).astype(np.int16)
    body_gyr_z = np.array(body_gyr_z).astype(np.int16)
    extracted_data = extract_data(body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z)

    return body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z, extracted_data, np.array(label).astype(np.int16)
            
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


def write_weight(model):

    print("Writing weights and bias")

    weight = np.array(model.layers[13].get_weights()[0])
    np.savetxt("Real-Weights3\\layerx1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[20].get_weights()[0])
    np.savetxt("Real-Weights3\\layerx2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[14].get_weights()[0])
    np.savetxt("Real-Weights3\\layery1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[21].get_weights()[0])
    np.savetxt("Real-Weights3\\layery2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[15].get_weights()[0])
    np.savetxt("Real-Weights3\\layerz1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[22].get_weights()[0])
    np.savetxt("Real-Weights3\\layerz2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[16].get_weights()[0])
    np.savetxt("Real-Weights3\\layergx1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[23].get_weights()[0])
    np.savetxt("Real-Weights3\\layergx2.txt", weight, fmt="%f", delimiter=",")           

    weight = np.array(model.layers[17].get_weights()[0])
    np.savetxt("Real-Weights3\\layergy1.txt", weight, fmt="%f", delimiter=",")
   
    weight = np.array(model.layers[24].get_weights()[0])
    np.savetxt("Real-Weights3\\layergy2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[18].get_weights()[0])
    np.savetxt("Real-Weights3\\layergz1.txt", weight, fmt="%f", delimiter=",")       

    weight = np.array(model.layers[25].get_weights()[0])
    np.savetxt("Real-Weights3\\layergz2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[19].get_weights()[0])
    np.savetxt("Real-Weights3\\layerdata1.txt", weight, fmt="%f", delimiter=",")
    
    weight = np.array(model.layers[26].get_weights()[0])
    np.savetxt("Real-Weights3\\layerdata2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[35].get_weights()[0])
    np.savetxt("Real-Weights3\\layerfinal1.txt", weight, fmt="%f", delimiter=",") 

    weight = np.array(model.layers[37].get_weights()[0])
    np.savetxt("Real-Weights3\\layerfinal2.txt", weight, fmt="%f", delimiter=",")


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
            text.append("{" + line.strip() + "},\n")
    with open(filename,"w") as f:
        f.writelines(text)


def convert_to_C():

    files = ["Real-Weights3\\layerx1.txt",
            "Real-Weights3\\layerx2.txt",
            "Real-Weights3\\layery1.txt",
            "Real-Weights3\\layery2.txt",
            "Real-Weights3\\layerz1.txt",
            "Real-Weights3\\layerz2.txt",
            "Real-Weights3\\layergx1.txt",
            "Real-Weights3\\layergx2.txt",
            "Real-Weights3\\layergy1.txt",
            "Real-Weights3\\layergy2.txt",
            "Real-Weights3\\layergz1.txt",
            "Real-Weights3\\layergz2.txt",
            "Real-Weights3\\layerdata1.txt",
            "Real-Weights3\\layerdata2.txt",
            "Real-Weights3\\layerfinal1.txt",
            "Real-Weights3\\layerfinal2.txt"
            ]
    
    for f in files:
        convert(f)


def get_model():

    inputA = tf.keras.layers.Input(shape=(100,1))
    inputB = tf.keras.layers.Input(shape=(100,1))
    inputC = tf.keras.layers.Input(shape=(100,1))
    inputD = tf.keras.layers.Input(shape=(100,1))
    inputE = tf.keras.layers.Input(shape=(100,1))
    inputF = tf.keras.layers.Input(shape=(100,1))
    inputG = tf.keras.layers.Input(shape=(24,))

    data = tf.keras.layers.Dense(40, activation="relu", use_bias=False)(inputG)
    data = tf.keras.layers.Dense(35, activation="relu", use_bias=False)(data)
    data = tf.keras.layers.Dropout(0.5)(data)
    data = tf.keras.Model(inputs=inputG, outputs=data)

    x = tf.keras.layers.Flatten()(inputA)
    x = tf.keras.layers.Dense(40, activation="relu", use_bias=False)(x)
    x = tf.keras.layers.Dense(35, activation="relu", use_bias=False)(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    x = tf.keras.Model(inputs=inputA, outputs=x)

    y = tf.keras.layers.Flatten()(inputB)
    y = tf.keras.layers.Dense(40, activation="relu", use_bias=False)(y)
    y = tf.keras.layers.Dense(35, activation="relu", use_bias=False)(y)
    y = tf.keras.layers.Dropout(0.5)(y)
    y = tf.keras.Model(inputs=inputB, outputs=y)

    z = tf.keras.layers.Flatten()(inputC)
    z = tf.keras.layers.Dense(40, activation="relu", use_bias=False)(z)
    z = tf.keras.layers.Dense(35, activation="relu", use_bias=False)(z)
    z = tf.keras.layers.Dropout(0.5)(z)
    z = tf.keras.Model(inputs=inputC, outputs=z)

    g_x = tf.keras.layers.Flatten()(inputD)
    g_x = tf.keras.layers.Dense(40, activation="relu", use_bias=False)(g_x)
    g_x = tf.keras.layers.Dense(35, activation="relu", use_bias=False)(g_x)
    g_x = tf.keras.layers.Dropout(0.5)(g_x)
    g_x = tf.keras.Model(inputs=inputD, outputs=g_x)

    g_y = tf.keras.layers.Flatten()(inputE)
    g_y = tf.keras.layers.Dense(40, activation="relu", use_bias=False)(g_y)
    g_y = tf.keras.layers.Dense(35, activation="relu", use_bias=False)(g_y)
    g_y = tf.keras.layers.Dropout(0.5)(g_y)
    g_y = tf.keras.Model(inputs=inputE, outputs=g_y)

    g_z = tf.keras.layers.Flatten()(inputF)
    g_z = tf.keras.layers.Dense(40, activation="relu", use_bias=False)(g_z)
    g_z = tf.keras.layers.Dense(35, activation="relu", use_bias=False)(g_z)
    g_z = tf.keras.layers.Dropout(0.5)(g_z)
    g_z = tf.keras.Model(inputs=inputF, outputs=g_z)

    combined = tf.keras.layers.concatenate([x.output, y.output, z.output, g_x.output, g_y.output, g_z.output, data.output])

    final = tf.keras.layers.Dense(35, activation="relu", use_bias=False)(combined)
    final = tf.keras.layers.Dropout(0.5)(final)
    final = tf.keras.layers.Dense(5, activation="softmax", use_bias=False)(final)

    model = tf.keras.Model(inputs=[x.input, y.input, z.input, g_x.input, g_y.input, g_z.input, data.input], outputs=final)

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model

if __name__ == "__main__":
    main()