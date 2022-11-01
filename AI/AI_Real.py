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

    write_weight(model)
    convert_to_C()


def import_data2():
    with open("..\\Relay_Node\\RealData\\grenade.txt","r") as f:
        x_array = []
        y_array = []
        z_array = []
        gx_array = []
        gy_array = []
        gz_array = []

        for row in f:
            values = row.replace("x","").split("\")
            x_array.append(int(values[2], base=16))
            y_array.append(int(values[3], base=16))
            z_array.append(int(values[4], base=16))
            gx_array.append(int(values[5], base=16))
            gy_array.append(int(values[6], base=16))
            gz_array.append(int(values[7], base=16))
            if len(x_array) == 50:
                with open("RealData\\label.txt","a") as f2:
                    f.write("1")
                with open("RealData\\x.txt","a") as fx:
                    f.write(str(x_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\y.txt","a") as fx:
                    f.write(str(y_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\z.txt","a") as fx:
                    f.write(str(z_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gx.txt","a") as fx:
                    f.write(str(gx_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gy.txt","a") as fx:
                    f.write(str(gy_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gz.txt","a") as fx:
                    f.write(str(gz_array).replace("[","").replace("]","").replace(" ","") + "\n")
                x_array = []
                y_array = []
                z_array = []
                gx_array = []
                gy_array = []
                gz_array = []
                

    with open("..\\Relay_Node\\RealData\\shield.txt") as f:
        x_array = []
        y_array = []
        z_array = []
        gx_array = []
        gy_array = []
        gz_array = []

        for row in f:
            values = row.replace("x","").split("\")
            x_array.append(int(values[2], base=16))
            y_array.append(int(values[3], base=16))
            z_array.append(int(values[4], base=16))
            gx_array.append(int(values[5], base=16))
            gy_array.append(int(values[6], base=16))
            gz_array.append(int(values[7], base=16))
            if len(x_array) == 50:
                with open("RealData\\label.txt","a") as f2:
                    f.write("2")
                with open("RealData\\x.txt","a") as fx:
                    f.write(str(x_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\y.txt","a") as fx:
                    f.write(str(y_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\z.txt","a") as fx:
                    f.write(str(z_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gx.txt","a") as fx:
                    f.write(str(gx_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gy.txt","a") as fx:
                    f.write(str(gy_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gz.txt","a") as fx:
                    f.write(str(gz_array).replace("[","").replace("]","").replace(" ","") + "\n")
                x_array = []
                y_array = []
                z_array = []
                gx_array = []
                gy_array = []
                gz_array = []

    with open("..\\Relay_Node\\RealData\\reload.txt") as f:
        x_array = []
        y_array = []
        z_array = []
        gx_array = []
        gy_array = []
        gz_array = []

        for row in f:
            values = row.replace("x","").split("\")
            x_array.append(int(values[2], base=16))
            y_array.append(int(values[3], base=16))
            z_array.append(int(values[4], base=16))
            gx_array.append(int(values[5], base=16))
            gy_array.append(int(values[6], base=16))
            gz_array.append(int(values[7], base=16))
            if len(x_array) == 50:
                with open("RealData\\label.txt","a") as f2:
                    f.write("3")
                with open("RealData\\x.txt","a") as fx:
                    f.write(str(x_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\y.txt","a") as fx:
                    f.write(str(y_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\z.txt","a") as fx:
                    f.write(str(z_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gx.txt","a") as fx:
                    f.write(str(gx_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gy.txt","a") as fx:
                    f.write(str(gy_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gz.txt","a") as fx:
                    f.write(str(gz_array).replace("[","").replace("]","").replace(" ","") + "\n")
                x_array = []
                y_array = []
                z_array = []
                gx_array = []
                gy_array = []
                gz_array = []

    with open("..\\Relay_Node\\RealData\\none.txt") as f:
        x_array = []
        y_array = []
        z_array = []
        gx_array = []
        gy_array = []
        gz_array = []

        for row in f:
            values = row.replace("x","").split("\")
            x_array.append(int(values[2], base=16))
            y_array.append(int(values[3], base=16))
            z_array.append(int(values[4], base=16))
            gx_array.append(int(values[5], base=16))
            gy_array.append(int(values[6], base=16))
            gz_array.append(int(values[7], base=16))
            if len(x_array) == 50:
                with open("RealData\\label.txt","a") as f2:
                    f.write("4")
                with open("RealData\\x.txt","a") as fx:
                    f.write(str(x_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\y.txt","a") as fx:
                    f.write(str(y_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\z.txt","a") as fx:
                    f.write(str(z_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gx.txt","a") as fx:
                    f.write(str(gx_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gy.txt","a") as fx:
                    f.write(str(gy_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gz.txt","a") as fx:
                    f.write(str(gz_array).replace("[","").replace("]","").replace(" ","") + "\n")
                x_array = []
                y_array = []
                z_array = []
                gx_array = []
                gy_array = []
                gz_array = []

    with open("..\\Relay_Node\\RealData\\logout.txt") as f:
        x_array = []
        y_array = []
        z_array = []
        gx_array = []
        gy_array = []
        gz_array = []

        for row in f:
            values = row.replace("[","").replace("]","").replace(" ","").strip().split(",")
            x_array.append(int(values[2]))
            y_array.append(int(values[3]))
            z_array.append(int(values[4]))
            gx_array.append(int(values[5]))
            gy_array.append(int(values[6]))
            gz_array.append(int(values[7]))
            if len(x_array) == 50:
                with open("RealData\\label.txt","a") as f2:
                    f.write("5")
                with open("RealData\\x.txt","a") as fx:
                    f.write(str(x_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\y.txt","a") as fx:
                    f.write(str(y_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\z.txt","a") as fx:
                    f.write(str(z_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gx.txt","a") as fx:
                    f.write(str(gx_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gy.txt","a") as fx:
                    f.write(str(gy_array).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData\\gz.txt","a") as fx:
                    f.write(str(gz_array).replace("[","").replace("]","").replace(" ","") + "\n")
                x_array = []
                y_array = []
                z_array = []
                gx_array = []
                gy_array = []
                gz_array = []


def load_data():
    
    load_data2()
    print("Loading Training Data . . .")

    body_acc_x = []
    body_acc_y = []
    body_acc_z = []
    body_gyr_x = []
    body_gyr_y = []
    body_gyr_z = []

    with open("RealData\\x.txt","r") as f:
        for row in f:
            body_acc_x.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData\\y.txt","r") as f:
        for row in f:
            body_acc_y.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData\\z.txt","r") as f:
        for row in f:
            body_acc_z.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData\\gx.txt","r") as f:
        for row in f:
            body_gyr_x.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData\\gy.txt","r") as f:
        for row in f:
            body_gyr_y.append(row.replace("[","").replace("]","").strip().split(","))

    with open("RealData\\gz.txt","r") as f:
        for row in f:
            body_gyr_z.append(row.replace("[","").replace("]","").strip().split(","))
    
    print("Loading Training Labels . . .")
    
    label = []
    with open("RealData\\label.txt","r") as f:
        
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

    return np.concatenate((acc_x_mean, acc_y_mean, acc_z_mean, gyr_x_mean, gyr_y_mean, gyr_z_mean, max_acc_x, max_acc_y, max_acc_z, max_gyr_x, max_gyr_y, max_gyr_z, min_acc_x, min_acc_y, min_acc_z, min_gyr_x, min_gyr_y, min_gyr_z), axis=1)


def write_weight(model):

    print("Writing weights and bias")

    weight = np.array(model.layers[13].get_weights()[0])
    np.savetxt("Real-Weights\\layerx1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[20].get_weights()[0])
    np.savetxt("Real-Weights\\layerx2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[14].get_weights()[0])
    np.savetxt("Real-Weights\\layery1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[21].get_weights()[0])
    np.savetxt("Real-Weights\\layery2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[15].get_weights()[0])
    np.savetxt("Real-Weights\\layerz1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[22].get_weights()[0])
    np.savetxt("Real-Weights\\layerz2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[16].get_weights()[0])
    np.savetxt("Real-Weights\\layergx1.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[23].get_weights()[0])
    np.savetxt("Real-Weights\\layergx2.txt", weight, fmt="%f", delimiter=",")           

    weight = np.array(model.layers[17].get_weights()[0])
    np.savetxt("Real-Weights\\layergy1.txt", weight, fmt="%f", delimiter=",")
   
    weight = np.array(model.layers[24].get_weights()[0])
    np.savetxt("Real-Weights\\layergy2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[18].get_weights()[0])
    np.savetxt("Real-Weights\\layergz1.txt", weight, fmt="%f", delimiter=",")       

    weight = np.array(model.layers[25].get_weights()[0])
    np.savetxt("Real-Weights\\layergz2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[19].get_weights()[0])
    np.savetxt("Real-Weights\\layerdata1.txt", weight, fmt="%f", delimiter=",")
    
    weight = np.array(model.layers[26].get_weights()[0])
    np.savetxt("Real-Weights\\layerdata2.txt", weight, fmt="%f", delimiter=",")

    weight = np.array(model.layers[35].get_weights()[0])
    np.savetxt("Real-Weights\\layerfinal1.txt", weight, fmt="%f", delimiter=",") 

    weight = np.array(model.layers[37].get_weights()[0])
    np.savetxt("Real-Weights\\layerfinal2.txt", weight, fmt="%f", delimiter=",")


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

    files = ["Real-Weights\\layerx1.txt",
            "Real-Weights\\layerx2.txt",
            "Real-Weights\\layery1.txt",
            "Real-Weights\\layery2.txt",
            "Real-Weights\\layerz1.txt",
            "Real-Weights\\layerz2.txt",
            "Real-Weights\\layergx1.txt",
            "Real-Weights\\layergx2.txt",
            "Real-Weights\\layergy1.txt",
            "Real-Weights\\layergy2.txt",
            "Real-Weights\\layergz1.txt",
            "Real-Weights\\layergz2.txt",
            "Real-Weights\\layerdata1.txt",
            "Real-Weights\\layerdata2.txt",
            "Real-Weights\\layerfinal1.txt",
            "Real-Weights\\layerfinal2.txt"
            ]
    
    for f in files:
        convert(f)


def get_model():

    inputA = tf.keras.layers.Input(shape=(50,1))
    inputB = tf.keras.layers.Input(shape=(50,1))
    inputC = tf.keras.layers.Input(shape=(50,1))
    inputD = tf.keras.layers.Input(shape=(50,1))
    inputE = tf.keras.layers.Input(shape=(50,1))
    inputF = tf.keras.layers.Input(shape=(50,1))
    inputG = tf.keras.layers.Input(shape=(18,))

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