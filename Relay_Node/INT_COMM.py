import socket
import sshtunnel
import queue
import struct
import time
import threading
import paho.mqtt.client as mqtt 
from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError, BTLEException
from concurrent.futures import ThreadPoolExecutor

SERVER = '192.168.95.235'
PORT = 4002
ADDRESS = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'

NOT_DONE = 0
DONE = 1
isBeetleHandshakeDone = []

queue_sensor_data = queue.Queue()
queue_visualizer = queue.Queue()

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
    XILINX = "192.168.95.235"
    LOCAL_HOST = 'localhost'

    SSH_PORT = 22
    PORT = 4002

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
        self.counter = 0

    def handleAcknowledge(self):
        if isBeetleHandshakeDone[self.index] == NOT_DONE:
            print(f'Sending Acknowledgement Packet to beetle {self.index}')
        self.serialCharacteristic.write(bytes("A", "utf-8"))
        isBeetleHandshakeDone[self.index] = DONE

    
    def handleNotification(self, cHandle, data):
        
        self.recvBuffer += data
        if(len(self.recvBuffer) >= 20):
            packetID = self.recvBuffer[0]
            if packetID == ord('A'):
                self.handleAcknowledge()
                self.recvBuffer = self.recvBuffer[20:]
            elif packetID == ord('G') or packetID == ord('W') or packetID == ord('V'):
                # data_to_send = self.recvBuffer[0:20]
                # self.sendData(data_to_send)
                queue_sensor_data.put(self.recvBuffer[0:20])
                self.counter += 1
                print("Packet No: " + str(self.counter))
                self.recvBuffer = self.recvBuffer[20:]
            else:
                print(self.recvBuffer)
                print("Invalid Data Packet: ")
                self.counter += 1
                self.recvBuffer = self.recvBuffer[20:]
        

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
            queue_visualizer.put("disconnect")
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

class Visualizer:
    def __init__(self):
        self.mqttBroker = "broker.hivemq.com"
        self.publisher = mqtt.Client("Pub")
        self.publisher.connect(self.mqttBroker, 1883, 60)

    def speak(self):
        while True:
            game_state = queue_visualizer.get()
            self.publisher.publish("B12cNwWz/Ultra96Send", game_state)
            print(f'{Fore.BLUE}[VISUALIZER HAS RECEIVED GAME STATE]{game_state} {Style.RESET_ALL}')

def main():

    ssh_tunnel()

    data_relay = DataRelay()
    # viz = Visualizer()
    if data_relay is not None:
        print(f"data relay object is created!")
    t1 = threading.Thread(target=data_relay.run)
    # t2 = threading.Thread(target=viz.speak)
    t1.start()
    # t2.start()
    if t1.is_alive():
       print("t1 is alive")
    # if t2.is_alive():
    #    print("t2 is alive")   

    concurrentBeetles = 0
    with ThreadPoolExecutor(max_workers=len(beetleAddresses) + 10) as executor:
        for address in beetleAddresses:
            isBeetleHandshakeDone.append(NOT_DONE)
            executor.submit(BeetleClientThread, address, concurrentBeetles)
            concurrentBeetles += 1



if __name__ == '__main__':
    main()
