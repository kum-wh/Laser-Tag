import socket
import sshtunnel
import queue
import time
import threading
from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError, BTLEException
from concurrent.futures import ThreadPoolExecutor

SERVER = '192.168.95.235'
PORT = 4536
ADDRESS = (SERVER, PORT)
HEADER = 64
NOT_DONE = 0
DONE = 1

INVALID = b'I\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

P1_CONNECT = b'C\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
P2_CONNECT = b'C\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

P1_DISCONNECT_GUN = b'D\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
P1_DISCONNECT_GLOVE = b'D\x01\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
P1_DISCONNECT_VEST = b'D\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
P2_DISCONNECT_GUN = b'D\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
P2_DISCONNECT_GLOVE = b'D\x02\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
P2_DISCONNECT_VEST = b'D\x02\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# MAC Addresses for BTLE devices
P1_GLOVE = "50:F1:4A:CC:0D:60"  # Glove USB Down P1
P1_GUN = "D0:39:72:BF:C8:D1"    # Gun Orange P1
P1_VEST = "78:DB:2F:BF:43:63"   # Vest Orange P1
P2_GLOVE = "50:F1:4A:CC:0D:21"  # Glove USB Side P2
P2_GUN = "50:F1:4A:CC:06:54"    # Gun Green P2
P2_VEST = "78:DB:2F:BF:2C:F5"   # Vest Blue P2

isBeetleHandshakeDone = []
queue_sensor_data = queue.Queue()
queue_visualizer = queue.Queue()

beetleAddresses = [
    P1_GLOVE,
    #P1_GUN,
    #P1_VEST,
    P2_GLOVE,
    #P2_GUN,
    #P2_VEST
]


def ssh_tunnel():
    SUNFIRE_USERNAME = "kum-wh"
    SUNFIRE_PASSWORD = "uigeksj2"
    XILINX_USERNAME = "xilinx"
    XILINX_PASSWORD = "xilinx"
    SUNFIRE = "sunfire.comp.nus.edu.sg"
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
        send_length = str(message_length).encode('utf-8')

        send_length += b' ' * (HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)

    def run(self):
        while True:
            data = queue_sensor_data.get()
            print(f"Data taken out from queue {data}")
            self.send(data)
            print(f"[MESSAGE SENT] {data}")


class BeetleClient(DefaultDelegate):
    def __init__(self, serialCharacteristic, index):
        DefaultDelegate.__init__(self)
        self.serialCharacteristic = serialCharacteristic
        self.index = index
        self.recvBuffer = b""
        self.counter = 0

    def handleAcknowledge(self):
        if isBeetleHandshakeDone[self.index] == NOT_DONE:
            print(f'Sending Acknowledgement Packet to BTLE {self.index}')
        self.serialCharacteristic.write(bytes("A", "utf-8"))
        isBeetleHandshakeDone[self.index] = DONE

    def handleNotification(self, cHandle, data):

        self.recvBuffer += data
        if len(self.recvBuffer) >= 20:
            packetID = self.recvBuffer[0]
            if packetID == ord('A'):
                self.handleAcknowledge()
                self.recvBuffer = self.recvBuffer[20:]
            elif packetID == ord('G') or packetID == ord('W') or packetID == ord('V'):
                queue_sensor_data.put(self.recvBuffer[0:20])
                self.counter += 1
                print("Packet No: " + str(self.counter))
                self.recvBuffer = self.recvBuffer[20:]
            else:
                print("Invalid Data Packet!")
                queue_sensor_data.put(INVALID)
                print(self.recvBuffer)
                self.counter += 1
                self.recvBuffer = b""


def BeetleClientThread(beetle_MAC, currIndex):
    beetle = Peripheral()
    isBeetleConnected = False
    isFirstLoop = True
    serialCharacteristic = None

    while True:

        try:

            if not isBeetleConnected:
                print(f'Connecting to BTLE {currIndex}')
                beetle.connect(beetle_MAC)

                if isFirstLoop:
                    print(f'Establishing connection parameters with BTLE {currIndex}')
                    serialService = beetle.getServiceByUUID("0000dfb0-0000-1000-8000-00805f9b34fb")
                    serialCharacteristic = serialService.getCharacteristics()[0]
                    beetle.delegate = BeetleClient(serialCharacteristic, currIndex)
                    isFirstLoop = False

                isBeetleConnected = True

            if isBeetleConnected:
                if not isBeetleHandshakeDone[currIndex]:
                    print(f'Initiating Handshake with BTLE {currIndex}')
                    if startHandshake(beetle, serialCharacteristic, currIndex):
                        isBeetleHandshakeDone[currIndex] = DONE
                        print(f'Handshake Success with BTLE {currIndex}')
                        ConnectMsg(beetle_MAC)
                    else:
                        print(f'Handshake Failed with BTLE {currIndex}')
                        isBeetleConnected = False

                else:
                    beetle.waitForNotifications(1.0)

        except BTLEDisconnectError:
            print(f'Something went wrong with BTLE {currIndex}')
            beetle.disconnect()
            DisconnectMsg(beetle_MAC)
            isBeetleConnected = False
            isBeetleHandshakeDone[currIndex] = NOT_DONE
            time.sleep(0.05)


def startHandshake(beetle, serialCharacteristic, index):
    while not isBeetleHandshakeDone[index]:
        try:
            print(f'Sending Handshake Packet to BTLE {index}')
            serialCharacteristic.write(bytes("H", "utf-8"))

            if beetle.waitForNotifications(1.0):
                pass
            else:
                return False
        except BTLEException:
            return False
    return True


def ConnectMsg(address):
    if address == P1_GLOVE:
        queue_sensor_data.put(P1_CONNECT)
    elif address == P2_GLOVE:
        queue_sensor_data.put(P2_CONNECT)
    elif address == P1_GUN:
        queue_sensor_data.put(P1_CONNECT)
    elif address == P2_GUN:
        queue_sensor_data.put(P2_CONNECT)
    elif address == P1_VEST:
        queue_sensor_data.put(P1_CONNECT)
    elif address == P2_VEST:
        queue_sensor_data.put(P2_CONNECT)
    else:
        pass


def DisconnectMsg(address):
    if address == P1_GLOVE:
        queue_sensor_data.put(P1_DISCONNECT_GLOVE)
    elif address == P2_GLOVE:
        queue_sensor_data.put(P2_DISCONNECT_GLOVE)
    elif address == P1_GUN:
        queue_sensor_data.put(P1_DISCONNECT_GUN)
    elif address == P2_GUN:
        queue_sensor_data.put(P2_DISCONNECT_GUN)
    elif address == P1_VEST:
        queue_sensor_data.put(P1_DISCONNECT_VEST)
    elif address == P2_VEST:
        queue_sensor_data.put(P2_DISCONNECT_VEST)
    else:
        pass


def main():
    # ssh_tunnel()
    data_relay = DataRelay()
    if data_relay is not None:
        print(f"Data relay object is created!")
    t1 = threading.Thread(target=data_relay.run)
    t1.start()
    if t1.is_alive():
        print("t1 is alive")

    concurrentBeetles = 0
    with ThreadPoolExecutor(max_workers=len(beetleAddresses)) as executor:
        for address in beetleAddresses:
            isBeetleHandshakeDone.append(NOT_DONE)
            executor.submit(BeetleClientThread, address, concurrentBeetles)
            concurrentBeetles += 1


if __name__ == '__main__':
    main()
