import socket
import sshtunnel
import queue
import threading
from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
from concurrent.futures import ThreadPoolExecutor
import struct
import time
import math
from crccheck.crc import Crc8

queue_sensor_data = queue.Queue()

SERVER = 'localhost'
PORT = 4002
ADDRESS = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'

# For Internal Comms
CURRENT_PLAYER = 1
SEND_ACK_INTERVAL = 100
SEND_HANDSHAKE_INTERVAL = 100
DATA_UPDATE_TIMEOUT = 300
CONNECTION_INTERVAL = 50
DEFAULT_AMMO = 6
DEFAULT_HEALTH = 100
DATA_COLLECTION_FRAME = 5000
INTERNAL_COLLECTION_FREQUENCY = 20
DATA_SENDING_INTERVAL = 48

NOT_DONE = 0
DONE = 1
isBeetleHandshakeDone = []
isNewDataSent = []

rawdata = bytearray()

packetList = ['A', 'U', 'G', 'W', 'V']

beetleAddresses = [
    "50:F1:4A:CC:0D:60",  # Glove USB Down
    "50:F1:4A:CC:0D:21",  # Glove USB Side
    # "D0:39:72:BF:C8:D1"  # Orange Gun
    # "50:F1:4A:CC:06:54",  # Green Gun
    # "50:F1:4A:CC:0D:21",  # Glove USB Side
    # "78:DB:2F:BF:2C:F5"  # Vest Blue
    # "78:DB:2F:BF:43:63"   # Orange vest
]


def current_milli_time():
    return round(time.time() * 1000)


def ssh_tunnel():
    SUNFIRE_USERNAME = "kum-wh"
    SUNFIRE_PASSWORD = "uigeksj2"
    XILINX_USERNAME = "xilinx"
    XILINX_PASSWORD = "xilinx"

    SUNFIRE = "stu.comp.nus.edu.sg"
    XILINX = "192.168.95.235" # zk: 5
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


class BeetleClient(DefaultDelegate):
    def __init__(self, serialCharacteristic, index):
        DefaultDelegate.__init__(self)
        self.serialCharacteristic = serialCharacteristic
        self.index = index
        self.prevTime = current_milli_time()
        self.lastSecond = current_milli_time()
        self.notificationCount = 0
        self.recvBuffer = bytearray()
        self.existingBufferLength = 0
        self.beetleIdentity = 'none'
        self.counter = 0

    def handleAcknowledge(self):
        current_time = current_milli_time()
        if current_time - self.prevTime > SEND_ACK_INTERVAL:
            if isBeetleHandshakeDone[self.index] == NOT_DONE:
                print(f'Sending Acknowledgement Packet to beetle {self.index}')
            self.serialCharacteristic.write(bytes("A", "utf-8"))
            isBeetleHandshakeDone[self.index] = DONE
            self.prevTime = current_time

    def handleUpdateAcknowledge(self):
        print(f'update acknowledged by beetle {self.index}')
        isNewDataSent[self.index] = DONE

    def sendData(self, data):
        queue_sensor_data.put(data)
        print(f"data is put into the queue {data}")

    def getUnpackedData(self, data):
        packetFormat = '<b''6h''b''3h'
        packet = struct.unpack(packetFormat, data)
        return packet

    def handleBuffer(self, data):
        if self.existingBufferLength > 0:
            lengthToAdd = 20 - self.existingBufferLength
            self.recvBuffer += data[0:lengthToAdd]
            if len(self.recvBuffer) == 20:
                # if self.validatePacket(self.recvBuffer):
                self.handleData(self.recvBuffer)
            self.recvBuffer = data[-self.existingBufferLength:]
            self.existingBufferLength = len(self.recvBuffer)
        else:
            if len(data) < 20:
                self.recvBuffer = data
                self.existingBufferLength = len(data)

    def validatePacket(self, data):
        packetID = data[0]
        packet = self.getUnpackedData(data)
        if packetID == ord('A') or packetID == ord('U'):
            return True
        if math.floor(packet[7] / 16) == CURRENT_PLAYER:
            if packetID == ord('G'):
                if packet[7] % 16 == 4 and (0 <= packet[1] <= 99):
                    self.beetleIdentity = 'gun'
                    return True
                return False
            elif packetID == ord('W'):
                if packet[7] % 16 == 3:
                    for x in range(1, 6):
                        if (-32, 768 <= packet[x] <= 32, 767):
                            continue
                        else:
                            return False
                else:
                    return False
                self.beetleIdentity = 'Wrist'
                return True
            elif packetID == ord('V'):
                if packet[7] % 16 == 5 and (0 <= packet[1] <= 99):
                    self.beetleIdentity = 'Vest'
                    return True
                return False
        return False

    def handleData(self, data):
        packetID = data[0]
        packet = self.getUnpackedData(data)
        # self.sendData(data)
        if packetID == ord('A'):
            self.handleAcknowledge()
        elif packetID == ord('G') or ord('V') or ord('W'):
            # self.sendData(packet)
            self.counter += 1
            print(self.counter)
            self.sendData(data)
        else:
            pass

    def handleNotification(self, cHandle, data):

        # self.notificationCount += 1
        #
        # if current_milli_time() - self.lastSecond >= 1000:
        #     self.lastSecond = current_milli_time()
        #     self.notificationCount = 0

        print(data)
        unpacked = struct.unpack('<b''6h''b''3h', data)
        print(unpacked)

        if len(data) < 20:
            self.handleBuffer(data)
        elif len(data) == 20:

            packetID = [0]

            if data[0] == ord('A') or data[0] == ord('G') or data[0] == ord('W') or data[0] == ord('V'):
                print("character recognized, checking validation")
                if self.validatePacket(data):
                    self.handleData(data)
                    if self.existingBufferLength > 0:
                        self.recvBuffer = bytearray()
                        self.existingBufferLength = 0
                #     else:
                #         self.handleBuffer(data)
                # else:
                #     self.handleBuffer(data)

        else:
            pass


class DataRelay():
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
            print(f"data is taken out from the queue {data}")
            self.send(data)
            print(f"[MESSAGE SENT] {data}")


def BeetleClientThread(beetle_MAC, currIndex):
    beetle = Peripheral()
    isBeetleConnected = False
    isFirstConnection = True
    isFirstLoop = True
    serialCharacteristic = None
    delegate = None
    prevConnectionTime = current_milli_time()
    lastSendUpdateTime = current_milli_time()

    while True:

        try:

            if (isFirstConnection):
                print(f'Connecting to beetle {currIndex}')
                beetle.connect(beetle_MAC)
                isFirstConnection = False
                isBeetleConnected = True

            elif isBeetleConnected == False:
                    # and (current_milli_time() - prevConnectionTime >= CONNECTION_INTERVAL):
                prevConnectionTime = current_milli_time()
                print(f'RE-connecting to beetle {currIndex}')
                beetle.connect(beetle_MAC)
                isBeetleConnected = True

            if isBeetleConnected:
                if isFirstLoop:
                    print(f'Establishing connection parameters with beetle {currIndex}')
                    serialService = beetle.getServiceByUUID("0000dfb0-0000-1000-8000-00805f9b34fb")
                    serialCharacteristic = serialService.getCharacteristics()[0]
                    delegate = BeetleClient(serialCharacteristic, currIndex)
                beetle.delegate = delegate

                isFirstLoop = False
                if not isBeetleHandshakeDone[currIndex]:
                    print(f'Initiating Handshake with beetle {currIndex}')
                    if startHandshake(beetle, serialCharacteristic, currIndex):
                        print(f'Handshake Success with beetle {currIndex}, current time is {current_milli_time()}')
                    else:
                        print(f'Handshake Failed with beetle {currIndex}')
                        isBeetleConnected = False

                if (isBeetleHandshakeDone[currIndex]) & isBeetleConnected:
                    while isBeetleConnected:
                        try:
                            if beetle.waitForNotifications(100):
                                pass
                            else:
                                # isBeetleConnected = False
                                pass
                        except BTLEDisconnectError:
                            isBeetleConnected = False
                            startHandshake(beetle, serialCharacteristic, currIndex)
                            # beetle.disconnect()
                            # break

                print(
                    f'No notification heard, disconnecting from beetle {currIndex}, current time is {current_milli_time()}')
                isBeetleHandshakeDone[currIndex] = NOT_DONE
                beetle.disconnect()
                time.sleep(0.05)

        except BTLEDisconnectError:
            beetle.disconnect()
            time.sleep(0.05)


def startHandshake(beetle, serialCharacteristic, index):
    isBeetleHandshakeDone[index] = NOT_DONE
    lastHandshakeTime = current_milli_time()
    isFirstHS = True
    while not isBeetleHandshakeDone[index]:
        if ((current_milli_time() - lastHandshakeTime > SEND_HANDSHAKE_INTERVAL) or isFirstHS):
            try:
                isFirstHS = False
                print(f'Sending Handshake Packet to beetle {index}')
                serialCharacteristic.write(bytes("H", "utf-8"))
                lastHandshakeTime = current_milli_time()

                if beetle.waitForNotifications(1.0):
                    pass
                else:
                    return False
            except Exception as e:
                return False
    return True


def main():
    # ssh_tunnel()
    concurrentBeetles = 0

    # data_relay = DataRelay()
    # if data_relay is not None:
    #     print(f"data relay object is created!")
    # t1 = threading.Thread(target=data_relay.run)
    # t1.start()
    # if t1.is_alive():
    #     print("t1 is alive")

    with ThreadPoolExecutor(max_workers=len(beetleAddresses) + 10) as executor:
        for address in beetleAddresses:
            isBeetleHandshakeDone.append(NOT_DONE)
            # isNewDataSent.append(DONE)
            executor.submit(BeetleClientThread, address, concurrentBeetles)
            concurrentBeetles += 1

        # data_relay = DataRelay()
        # executor.submit(data_relay.run)
        # # if data_relay is not None:
        #     print(f"data relay object is created!")
        # t1 = threading.Thread(target=data_relay.run)
        # t1.start()
        # if t1.is_alive():
        #     print("t1 is alive")
        # t1.join()

    #
    # for address in beetleAddresses:
    #     try:
    #         beetle = BeetleClientThread(address)
    #     except:
    #         time.sleep(2)
    #         beetle =BeetleClientThread(address, )
    #
    # #data_relay = DataRelay()
    #
    # t1 = threading.Thread(target=BeetleClientThread, args=(beetleAddresses[0], 0))
    # #t2 = threading.Thread(target=data_relay.run, args=())
    #
    # t1.start()
    # #t2.start()
    #
    # t1.join()
    # #t2.join()


if __name__ == '__main__':
    main()
