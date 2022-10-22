import numpy as np

# Handles the testing of the C version of code
def main():

    # Load the testing data
    print('Loading data')
    acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, extracted_data, y_train = load_data()
    result = []
    test(acc_x[0], acc_y[0], acc_z[0], gyr_x[0], gyr_y[0], gyr_z[0])
    
    for i in range(30):
        result.append(model(acc_x[i], acc_y[i], acc_z[i], gyr_x[i], gyr_y[i], gyr_z[i], extracted_data[i]))

    counter = 0
    for i in range(len(result)):
        print(result[i])
        print(y_train[i])
    
    print(counter / len(acc_x))


def test(x, y, z, gx, gy, gz):
    final = []
    for i in range(100):
        final.append([x[i], y[i], z[i], gx[i], gy[i], gz[i]])
    print(final)


#Handles calculation for a node in a layer of 32 nodes with 128 inputs
def node350_40(inputs, weights):
    temp = 0
    for i in range(100):
        temp += inputs[i] * weights[i]
    if (temp < 0):
        return 0
    return temp


# Handle the processing of layer of 32 nodes with 128 inputs
def layer350_40(inputs, weights):
    output = [ 0 for i in range(40)]
    for i in range(40):
        output[i] = node350_40(inputs, weights[i])
    return output


#Handles calculation for nodes in a layer of 32 nodes with 24 inputs
def node24_40(inputs, weights):
    temp = 0
    for i in range(24):
        temp += inputs[i] * weights[i]
    if (temp < 0):
        return 0
    return temp


# Handle the processing of layer of 32 nodes with 24 inputs
def layer24_40(inputs, weights):
    output = [ 0 for i in range(40)]
    for i in range(40):
        output[i] = node24_40(inputs, weights[i])
    return output


#Handles calculation for nodes in a layer of 32 nodes with 32 inputs
def node40_35(inputs, weights):
    temp = 0
    for i in range(40):
        temp += inputs[i] * weights[i]
    if (temp < 0):
        return 0
    return temp


# Handle the processing of layer of 32 nodes with 32 inputs
def layer40_35(inputs, weights):
    output = [ 0 for i in range(35)]
    for i in range(35):
        output[i] = node40_35(inputs, weights[i])
    return output


#Handles calculation for nodes in a layer of 32 nodes with 128 inputs
def node35_5(inputs, weights):
    temp = 0
    for i in range(35):
        temp += inputs[i] * weights[i]
    if (temp < 0):
        return 0
    return temp


# Handle the processing of layer of 5 nodes with 32 inputs
def layer35_5(inputs, weights):
    output = [ 0 for i in range(5)]
    for i in range(5):
        output[i] = node35_5(inputs, weights[i])
    return output


#Handles calculation for nodes in a layer of 32 nodes with 224 inputs
def node245_35(x_layer, y_layer, z_layer, gx_layer, gy_layer, gz_layer, data_layer, weights):
    temp = 0
    for i in range(35):
        temp += x_layer[i] * weights[i]
    for i in range(35):
        temp += y_layer[i] * weights[35 + i]
    for i in range(35):
        temp += z_layer[i] * weights[70 + i]
    for i in range(35):
        temp += gx_layer[i] * weights[105 + i]
    for i in range(35):
        temp += gy_layer[i] * weights[140 + i]
    for i in range(35):
        temp += gz_layer[i] * weights[175 + i]
    for i in range(35):
        temp += data_layer[i] * weights[210 + i]
    if (temp < 0):
        return 0
    return temp


# Handle the processing of layer of 32 nodes with 224 inputs
def layer245_35(x_layer, y_layer, z_layer, gx_layer, gy_layer, gz_layer, data_layer, weights):
    output= [ 0 for i in range(35)]
    for i in range(35):
        output[i] = node245_35(x_layer, y_layer, z_layer, gx_layer, gy_layer, gz_layer, data_layer, weights[i])
    return output


#Handles the creation of the sequential model by combining the layers
def model(acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, data):

    weight_x_1 = []
    weight_x_2 = []
    weight_y_1 = []
    weight_y_2 = []
    weight_z_1 = []
    weight_z_2 = []
    weight_gx_1 = []
    weight_gx_2 = []
    weight_gy_1 = []
    weight_gy_2 = []
    weight_gz_1 = []
    weight_gz_2 = []
    weight_data_1 = []
    weight_data_2 = []
    weight_final_1 = []
    weight_final_2 = []

    with open("test.txt","r") as f:
        counter = 0
        for row in f:
            counter += 1
            b = []
            a = row.replace(","," ").strip().replace("{","").replace("}","").replace(";","").split(" ")
            
            for weight in a:
                b.append(float(weight))
            
            if counter <= 40:
                weight_x_1.append(b)
            elif counter <= 40 + 35:
                weight_x_2.append(b)
            elif counter <= 40 + 35 + 40:
                weight_y_1.append(b)
            elif counter <= 40 + 35 + 40 + 35:
                weight_y_2.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40:
                weight_z_1.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35:
                weight_z_2.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40:
                weight_gx_1.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35:
                weight_gx_2.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40:
                weight_gy_1.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35:
                weight_gy_2.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40:
                weight_gz_1.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35:
                weight_gz_2.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40:
                weight_data_1.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35:
                weight_data_2.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 35:
                weight_final_1.append(b)
            elif counter <= 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 40 + 35 + 35 + 5:
                weight_final_2.append(b)

    x_layer = layer350_40(acc_x, weight_x_1)
    x_layer = layer40_35(x_layer, weight_x_2)

    y_layer = layer350_40(acc_y, weight_y_1)
    y_layer = layer40_35(y_layer, weight_y_2)

    z_layer = layer350_40(acc_z, weight_z_1)
    z_layer = layer40_35(z_layer, weight_z_2)

    gx_layer = layer350_40(gyr_x, weight_gx_1)
    gx_layer = layer40_35(gx_layer, weight_gx_2)

    gy_layer = layer350_40(gyr_y, weight_gy_1)
    gy_layer = layer40_35(gy_layer, weight_gy_2)

    gz_layer = layer350_40(gyr_z, weight_gz_1)
    gz_layer = layer40_35(gz_layer, weight_gz_2)

    data_layer = layer24_40(data, weight_data_1)
    data_layer = layer40_35(data_layer, weight_data_2)

    final_layer = layer245_35(x_layer, y_layer, z_layer, gx_layer, gy_layer, gz_layer, data_layer, weight_final_1)
    output = layer35_5(final_layer, weight_final_2)

    max_value = 0
    max_index = 0
    print(output)
    for i in range(5):
        if (output[i] > max_value):
            max_value = output[i]
            max_index = i + 1
    return max_index


def load_data():

    print("Loading Training Data . . .")

    body_acc_x = []
    body_acc_y = []
    body_acc_z = []
    body_gyr_x = []
    body_gyr_y = []
    body_gyr_z = []

    with open("RealData2\\x.txt","r") as f:
        for row in f:
            body_acc_x.append(row.strip().split(","))

    with open("RealData2\\y.txt","r") as f:
        for row in f:
            body_acc_y.append(row.strip().split(","))

    with open("RealData2\\z.txt","r") as f:
        for row in f:
            body_acc_z.append(row.strip().split(","))

    with open("RealData2\\gx.txt","r") as f:
        for row in f:
            body_gyr_x.append(row.strip().split(","))

    with open("RealData2\\gy.txt","r") as f:
        for row in f:
            body_gyr_y.append(row.strip().split(","))

    with open("RealData2\\gz.txt","r") as f:
        for row in f:
            body_gyr_z.append(row.strip().split(","))
    
    print("Loading Training Labels . . .")
    
    label = []
    with open("RealData2\\label.txt","r") as f:
        
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
    extracted_data = extract_data(body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z).astype(np.int16)

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

if __name__ == "__main__":
    main()
