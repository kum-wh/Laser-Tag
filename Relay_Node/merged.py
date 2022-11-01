# import socket
# import sshtunnel
import queue

from bluepy.btle import DefaultDelegate, Peripheral, BTLEDisconnectError
from bluepy.btle import BTLEException
# from crccheck.crc import Crc8
import threading
import time
import struct

SERVER = '192.168.95.235'
PORT = 4002
ADDRESS = (SERVER, PORT)

queue_sensor_data = queue.Queue()

BEETLE1 = '50:F1:4A:CC:0D:21'
BEETLE2 = 'd0:39:72:bf:bf:d1'
BEETLE3 = 'd0:39:72:bf:bd:d5'
ALL_BEETLE_MAC = [BEETLE1]

# BEETLE_ID = {BEETLE1: 'beetle 1', BEETLE2: 'beetle 2', BEETLE3: 'beetle 3'}
BEETLE_ID = {BEETLE1: 'beetle 1'}

HANDSHAKE_STATUS = {
    BEETLE1: False,
    BEETLE2: False,
    BEETLE3: False,
}

BEETLE_CLEAR = {
    BEETLE1: False,
    BEETLE2: False,
    BEETLE3: False,
}

DROP = {BEETLE1: 0, BEETLE2: 0, BEETLE3: 0}
RECEIVE = {BEETLE1: 0, BEETLE2: 0, BEETLE3: 0}
SPEED = {BEETLE1: 0, BEETLE2: 0, BEETLE3: 0}
SPEEDCOUNT = {BEETLE1: 0, BEETLE2: 0, BEETLE3: 0}

PARSED_DATA = {BEETLE1: "", BEETLE2: "", BEETLE3: ""}

def ssh_tunnel():
    SUNFIRE_USERNAME = "kum-wh"
    SUNFIRE_PASSWORD = "uigeksj2"
    XILINX_USERNAME = "xilinx"
    XILINX_PASSWORD = "xilinx"

    SUNFIRE = "stu.comp.nus.edu.sg"
    XILINX = "192.168.95.235"  # zk: 5
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

class BeetleThread(threading.Thread):
    def __init__(self, beetleObject):
        threading.Thread.__init__(self)
        self.beetleObject = beetleObject
        self.serial_service = self.beetleObject.getServiceByUUID(
            "0000dfb0-0000-1000-8000-00805f9b34fb")
        self.serial_characteristic = self.serial_service.getCharacteristics()[
            0]
        self.start_handshake()

    def start_handshake(self):
        try:
            self.reset()
            while not HANDSHAKE_STATUS[self.beetleObject.addr]:
                print('Handshaking with ', beetle.addr, '...')
                self.serial_characteristic.write(
                    bytes('H', 'utf-8'), withResponse=False)

                if (self.beetleObject.waitForNotifications(2) and HANDSHAKE_STATUS[self.beetleObject.addr]):
                    self.serial_characteristic.write(bytes('A', 'utf-8'), withResponse=False)

            return True

        except BTLEDisconnectError:
            self.reconnect()
            self.start_handshake()

        except BTLEException:
            self.reconnect()
            self.start_handshake()

    def reconnect(self):
        try:
            self.beetleObject.disconnect()
            time.sleep(2)
            self.beetleObject.connect(self.beetleObject.addr)
            self.beetleObject.withDelegate(
                Delegate(self.beetleObject.addr))
        except BTLEException:
            self.reconnect()


    def reset(self):
        self.serial_characteristic.write(bytes('R', 'utf-8'), withResponse=False)
        HANDSHAKE_STATUS[self.beetleObject.addr] = False
        BEETLE_CLEAR[self.beetleObject.addr] = False
        self.reconnect()

    def run(self):
        try:
            while True:
                if BEETLE_CLEAR[self.beetleObject.addr]:
                    break

                if self.beetleObject.waitForNotifications(2) and not BEETLE_CLEAR[self.beetleObject.addr]:
                    continue

            self.reset()
            self.start_handshake()
            self.run()

        except BTLEException:
            print('Device disconneted!', BEETLE_ID[self.beetleObject.addr])
            self.reconnect()
            self.reset()
            self.start_handshake()
            self.run()

class Delegate(DefaultDelegate):

    def __init__(self, beetle):
        DefaultDelegate.__init__(self)
        self.beetle = beetle
        self.buffer = b''

    def handleNotification(self, cHandle, data):
        time1 = time.time()
        count = 0
        self.buffer += data
        count += len(self.buffer)
        if (len(self.buffer) >= 20):
            if (HANDSHAKE_STATUS[self.beetle]):

                if (self.buffer[0] == 71 and len(self.buffer) >= 20):
                    SPEEDCOUNT[self.beetle] += 1
                    raw_packet_data = self.buffer[0: 20]
                    bulletData = raw_packet_data[0: 4]
                    PARSED_DATA[self.beetle] = struct.unpack(
                        '!chc', bulletData)
                    #print(PARSED_DATA[self.beetle])

                    RECEIVE[self.beetle] += 1
                    self.buffer = self.buffer[20:]

                elif (self.buffer[0] == 68 and len(self.buffer) >= 20):
                    SPEEDCOUNT[self.beetle] += 1
                    raw_packet_data = self.buffer[0: 20]
                    data_packet_data = raw_packet_data[0: 14]
                    PARSED_DATA[self.beetle] = struct.unpack(
                        '!chhhhhhc', data_packet_data)
                    #print(PARSED_DATA[self.beetle])

                    RECEIVE[self.beetle] += 1
                    self.buffer = self.buffer[20:]

                elif (self.buffer[0] == 86 and len(self.buffer) >= 20):
                    SPEEDCOUNT[self.beetle] += 1
                    raw_packet_data = self.buffer[0: 20]
                    data_packet_data = raw_packet_data[0: 8]
                    PARSED_DATA[self.beetle] = struct.unpack(
                        '!chhhc', data_packet_data)
                    #print(PARSED_DATA[self.beetle])

                    RECEIVE[self.beetle] += 1
                    self.buffer = self.buffer[20:]

                else:
                    self.buffer = self.buffer[20:]

            elif (self.buffer[0] == 65 and len(self.buffer) >= 20):
                HANDSHAKE_STATUS[self.beetle] = True
                print(BEETLE_ID[self.beetle], " handshake successfully!")
                self.buffer = self.buffer[20:]

            else:
                BEETLE_CLEAR[self.beetle] = True

        if (SPEEDCOUNT[self.beetle] == 50):
            print(BEETLE_ID[self.beetle], "rate: ", 50 / (time.time() - SPEED[self.beetle]), "drop: ", DROP[self.beetle], "received: ",
                  RECEIVE[self.beetle])
            SPEED[self.beetle] = time.time()
            SPEEDCOUNT[self.beetle] = 0


if __name__ == '__main__':
    
    # ssh_tunnel()

    for mac in ALL_BEETLE_MAC:
        try:
            beetle = Peripheral(mac)
        except:
            time.sleep(2)
            beetle = Peripheral(mac)

        beetle.withDelegate(Delegate(mac))
        BeetleThread(beetle).start() #One Thread for each beetle
    '''
    data_relay = DataRelay()
    if data_relay is not None:
        print(f"data relay object is created!")
    t1 = threading.Thread(target=data_relay.run)
    t1.start()
    if t1.is_alive():
        print("t1 is alive")
    '''
