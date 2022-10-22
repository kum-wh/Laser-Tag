import serial

'''
if output_buffer[0] == 1:
    return "grenade"
elif output_buffer[0] == 2:
    return "shield"
elif output_buffer[0] == 3:
    return "reload"
elif output_buffer[0] == 4:
    return "none"
elif output_buffer[0] == 5:
    return "logout"   
'''

action_num = 4

def main():
    print("Clear file?")
    inputs = input()
    if inputs == "1":
        with open("RealData2\\x.txt","w") as f:
            f.write("")
        with open("RealData2\\y.txt","w") as f:
            f.write("")
        with open("RealData2\\z.txt","w") as f:
            f.write("")
        with open("RealData2\\gx.txt","w") as f:
            f.write("")
        with open("RealData2\\gy.txt","w") as f:
            f.write("")
        with open("RealData2\\gz.txt","w") as f:
            f.write("")
        with open("RealData2\\label.txt","w") as f:
            f.write("")
        print("clear")
    
    x = []
    y = []
    z = []
    gx = []
    gy = []
    gz = []

    counter = 0

    arduino = serial.Serial(port='COM6', baudrate=115200, timeout=.1)
    arduino.close()
    arduino.open()

    while True:
        
        data = arduino.readline()
        
        if (len(data) >= 30):

            print(data)
            values = str(data).replace("\\r\\n","").replace("b\'","").replace("\'","").replace(","," ").strip().replace("count","").replace("accXF","").replace("accYF","").replace("accZF","").replace("gyroXF","").replace("gyroYF","").replace("gyroZF","").replace(":","").split(" ")

            if(len(values) != 7):
                print(data)
                continue

            x.append(int(values[1]))
            y.append(int(values[2]))
            z.append(int(values[3]))
            gx.append(int(values[4]))
            gy.append(int(values[5]))
            gz.append(int(values[6]))
                        
            if (len(x) == 100):

                counter += 1  
                
                with open("RealData2\\x.txt","a") as f:
                    f.write(str(x).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData2\\y.txt","a") as f:
                    f.write(str(y).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData2\\z.txt","a") as f:
                    f.write(str(z).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData2\\gx.txt","a") as f:
                    f.write(str(gx).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData2\\gy.txt","a") as f:
                    f.write(str(gy).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData2\\gz.txt","a") as f:
                    f.write(str(gz).replace("[","").replace("]","").replace(" ","") + "\n")
                with open("RealData2\\label.txt","a") as f:
                    f.write(str(action_num) + "\n")
                
                print(counter)

                x.clear()
                y.clear()
                z.clear()
                gx.clear()
                gy.clear()
                gz.clear()
        

if __name__ == "__main__":
    main()