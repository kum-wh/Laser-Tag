# import socket
# import sshtunnel
import queue
import struct
import time
import threading
from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError, BTLEException
from concurrent.futures import ThreadPoolExecutor

SERVER = 'localhost'
PORT = 4003
ADDRESS = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'
NOT_DONE = 0
DONE = 1
isBeetleHandshakeDone = []
queue_sensor_data = queue.Queue()

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

Action = 1

beetleAddresses = [
    # "50:F1:4A:CC:0D:60",  # Glove USB Down
    "50:F1:4A:CC:0D:21",  # Glove USB Side
    # "D0:39:72:BF:C8:D1",  # Gun Orange
    # "50:F1:4A:CC:06:54",  # Gun Green
    # "78:DB:2F:BF:2C:F5",  # Vest Blue
    # "78:DB:2F:BF:43:63"   # Vest Orange
]


def ssh_tunnel():
    SUNFIRE_USERNAME = "kum-wh"
    SUNFIRE_PASSWORD = "uigeksj2"
    XILINX_USERNAME = "xilinx"
    XILINX_PASSWORD = "xilinx"

    SUNFIRE = "stu.comp.nus.edu.sg"
    XILINX = "192.168.95.235"  # zk: 5
    LOCAL_HOST = 'localhost'

    SSH_PORT = 22
    PORT = 4003

    tunnel1 = sshtunnel.open_tunnel(
        ssh_address_or_host=(SUNFIRE, SSH_PORT),
        remote_bind_address=(XILINX, SSH_PORT),
        ssh_username=SUNFIRE_USERNAME,
        ssh_password=SUNFIRE_PASSWORD,
        block_on_close=False
    )
    tunnel1.start()
    print(f'Connection to tunnel1 {SUNFIRE}:{SSH_PORT} established!')
    print("LOCAL PORT:", tunnel1.local_bind_port)

    tunnel2 = sshtunnel.open_tunnel(
        ssh_address_or_host=(LOCAL_HOST, tunnel1.local_bind_port),
        remote_bind_address=(LOCAL_HOST, PORT),
        ssh_username=XILINX_USERNAME,
        ssh_password=XILINX_PASSWORD,
        local_bind_address=(LOCAL_HOST, PORT),
        block_on_close=False
    )
    tunnel2.start()
    print(f"Connection to tunnel2 {XILINX}:{PORT} established!")
    print("LOCAL PORT:", tunnel2.local_bind_port)


class DataRelay:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDRESS)

    def send(self, message):
        message_length = len(message)
        send_length = str(message_length).encode(FORMAT)

        # Add padding
        send_length += b' ' * (HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)

    def run(self):
        while True:
            print("HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            data = queue_sensor_data.get()
            print(f"Data taken out from queue {data}")
            self.send(data)
            print(f"[MESSAGE SENT] {data}")


class BeetleClient(DefaultDelegate):
    def __init__(self, serialCharacteristic, index):
        DefaultDelegate.__init__(self)
        self.serialCharacteristic = serialCharacteristic
        self.index = index
        self.recvBuffer = b"" # Changed
        # self.existingBufferLength = 0 # Removed
        self.collect = False
        self.counter = 0

    def handleAcknowledge(self):
        if isBeetleHandshakeDone[self.index] == NOT_DONE:
            print(f'Sending Acknowledgement Packet to beetle {self.index}')
        self.serialCharacteristic.write(bytes("A", "utf-8"))
        isBeetleHandshakeDone[self.index] = DONE
    '''
    def sendData(self, data):
        queue_sensor_data.put(data)
        # print(f"Data is inside queue {data}")
        
    '''
    '''
    def handleBuffer(self, data):
        if self.existingBufferLength > 0:
            lengthToAdd = 20 - self.existingBufferLength
            self.recvBuffer += data[0:lengthToAdd]
            if len(self.recvBuffer) == 20:
                self.sendData(self.recvBuffer)
            self.recvBuffer = data[-self.existingBufferLength:] #??????
            self.existingBufferLength = len(self.recvBuffer) #??????
        else:
            if len(data) < 20:
                self.recvBuffer = data
                self.existingBufferLength = len(data)
    '''
    def collect_Data(self, data):
        if Action == 1:
            with open("RealData\\grenade.txt","a") as f:
                    f.write(str(data) "\n")
        elif Action == 2:
            with open("RealData\\shield.txt","a") as f:
                    f.write(str(data) + "\n")
        elif Action == 3:
            with open("RealData\\reload.txt","a") as f:
                    f.write(str(data) + "\n")
        elif Action == 4:
            with open("RealData\\none.txt","a") as f:
                    f.write(str(data) + "\n")
        elif Action == 5:
            with open("RealData\\logout.txt","a") as f:
                    f.write(str(data) + "\n")
    
    def handleNotification(self, cHandle, data):
        # unpacked = struct.unpack('<b''6h''b''3h', data)
        # print(unpacked)
        
        self.recvBuffer += data
        if(len(self.recvBuffer) >= 20):
            packetID = self.recvBuffer[0]
            if packetID == ord('A'):
                self.handleAcknowledge()
                self.recvBuffer = self.recvBuffer[20:]
            elif packetID == ord('G') or packetID == ord('W') or packetID == ord('V'):
                # data_to_send = self.recvBuffer[0:20]
                # self.sendData(data_to_send)
                unpacked_sensor_reading = unpack('<b''b''6h''b''2h''b',  self.recvBuffer[0:20])
                if self.collect == False and (unpacked_sensor_reading[2] > 75 or unpacked_sensor_reading[3] > 75 or unpacked_sensor_reading[4] > 75 or unpacked_sensor_reading[5] > 80 or unpacked_sensor_reading[6] > 80 or unpacked_sensor_reading[7] > 80):
                    self.collect = True
                if self.collect == True:
                    self.collect_Data([unpacked_sensor_reading[2], unpacked_sensor_reading[3], unpacked_sensor_reading[4], unpacked_sensor_reading[5], unpacked_sensor_reading[6], unpacked_sensor_reading[7]])
                    self.counter += 1
                if self.counter == 50:
                    self.collect = False
                # queue_sensor_data.put(self.recvBuffer[0:20])
                print("Packet No: " + str(self.counter))
                self.recvBuffer = self.recvBuffer[20:]
            else:
                print(self.recvBuffer)
                print("Invalid Data Packet: ")
                # self.counter += 1
                self.recvBuffer = self.recvBuffer[20:]
            
        '''    
        if len(data) < 20:
            print(len(data))
            # self.handleBuffer(data)
            self.recvBuffer += data
        elif len(data) == 20:
            packetID = data[0]
            if packetID == ord('A'):
                self.handleAcknowledge()
            elif packetID == ord('G') or packetID == ord('W') or packetID == ord('V'):
                # print(data)
                self.counter += 1
                # print("Packet No: " + str(self.counter))
                self.sendData(data)
        else:
            print("Invalid Data Packet!")
            pass
        '''
        

def BeetleClientThread(beetle_MAC, currIndex):
    beetle = Peripheral()
    isBeetleConnected = False
    isFirstLoop = True
    serialCharacteristic = None

    while True:

        try:

            if not isBeetleConnected:
                print(f'Connecting to beetle {currIndex}')
                beetle.connect(beetle_MAC)

                if isFirstLoop:
                    print(f'Establishing connection parameters with beetle {currIndex}')
                    serialService = beetle.getServiceByUUID("0000dfb0-0000-1000-8000-00805f9b34fb")
                    serialCharacteristic = serialService.getCharacteristics()[0]
                    beetle.delegate = BeetleClient(serialCharacteristic, currIndex)
                    isFirstLoop = False

                isBeetleConnected = True

            if isBeetleConnected:
                if not isBeetleHandshakeDone[currIndex]:
                    print(f'Initiating Handshake with beetle {currIndex}')
                    if startHandshake(beetle, serialCharacteristic, currIndex):
                        isBeetleHandshakeDone[currIndex] = DONE
                        print(f'Handshake Success with beetle {currIndex}')
                    else:
                        print(f'Handshake Failed with beetle {currIndex}')
                        isBeetleConnected = False

                else:
                    beetle.waitForNotifications(1.0)

        except BTLEDisconnectError:
            print(f'Something went wrong with {currIndex}')
            beetle.disconnect()
            isBeetleConnected = False
            isBeetleHandshakeDone[currIndex] = NOT_DONE
            time.sleep(0.05)


def startHandshake(beetle, serialCharacteristic, index):
    while not isBeetleHandshakeDone[index]:
        try:
            print(f'Sending Handshake Packet to beetle {index}')
            serialCharacteristic.write(bytes("H", "utf-8"))

            if beetle.waitForNotifications(2.0):
                pass
            else:
                return False
        except BTLEException:
            return False
    return True


def main():

    # ssh_tunnel()
    # data_relay = DataRelay()
    # if data_relay is not None:
    #     print(f"data relay object is created!")
    # t1 = threading.Thread(target=data_relay.run)
    # t1.start()
    # if t1.is_alive():
    #     print("t1 is alive")

    concurrentBeetles = 0
    with ThreadPoolExecutor(max_workers=len(beetleAddresses) + 10) as executor:
        for address in beetleAddresses:
            isBeetleHandshakeDone.append(NOT_DONE)
            executor.submit(BeetleClientThread, address, concurrentBeetles)
            concurrentBeetles += 1


if __name__ == '__main__':
    main()

