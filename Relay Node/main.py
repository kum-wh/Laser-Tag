from bluepy.btle import DefaultDelegate, Peripheral, BTLEDisconnectError
from bluepy.btle import BTLEException
from crccheck.crc import Crc8
import threading
import time
import struct

BEETLE1 = 'd0:39:72:bf:cf:89'
BEETLE2 = 'd0:39:72:bf:bf:d1'
BEETLE3 = 'd0:39:72:bf:bd:d5'
ALL_BEETLE_MAC = [BEETLE1]

BEETLE_ID = {BEETLE1: 'beetle 1', BEETLE2: 'beetle 2', BEETLE3: 'beetle 3'}

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

    def checkSum(self, len):
        return Crc8.calc(self.buffer[0: len]) == self.buffer[len]

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

                    if not self.checkSum(3):
                        print("Wrong Bullet")
                        self.buffer = b''
                        BEETLE_CLEAR[self.beetle] = True
                        DROP[self.beetle] += 1
                        return

                    RECEIVE[self.beetle] += 1
                    self.buffer = self.buffer[20:]

                elif (self.buffer[0] == 68 and len(self.buffer) >= 20):
                    SPEEDCOUNT[self.beetle] += 1
                    raw_packet_data = self.buffer[0: 20]
                    data_packet_data = raw_packet_data[0: 14]
                    PARSED_DATA[self.beetle] = struct.unpack(
                        '!chhhhhhc', data_packet_data)
                    #print(PARSED_DATA[self.beetle])

                    if not self.checkSum(13):
                        BEETLE_CLEAR[self.beetle] = True
                        self.buffer = b''
                        DROP[self.beetle] += 1
                        return

                    RECEIVE[self.beetle] += 1
                    self.buffer = self.buffer[20:]

                elif (self.buffer[0] == 86 and len(self.buffer) >= 20):
                    SPEEDCOUNT[self.beetle] += 1
                    raw_packet_data = self.buffer[0: 20]
                    data_packet_data = raw_packet_data[0: 8]
                    PARSED_DATA[self.beetle] = struct.unpack(
                        '!chhhc', data_packet_data)
                    #print(PARSED_DATA[self.beetle])

                    if not self.checkSum(7):
                        BEETLE_CLEAR[self.beetle] = True
                        self.buffer = b''
                        DROP[self.beetle] += 1
                        return

                    RECEIVE[self.beetle] += 1
                    self.buffer = self.buffer[20:]

                else:
                    self.buffer = self.buffer[20:]

            elif (self.buffer[0] == 65 and len(self.buffer) >= 20):
                if not self.checkSum(2):
                    BEETLE_CLEAR[self.beetle] = True
                    self.buffer = b''
                    return

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
    for mac in ALL_BEETLE_MAC:
        try:
            beetle = Peripheral(mac)
        except:
            time.sleep(2)
            beetle = Peripheral(mac)

        beetle.withDelegate(Delegate(mac))
        BeetleThread(beetle).start()

