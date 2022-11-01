import queue
import time
from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError, BTLEException
from crccheck.crc import Crc8

isBeetleHandshakeDone = []
queue_sensor_data = queue.Queue()

beetleAddresses = [
    "50:F1:4A:CC:0D:60",  # Glove USB Down
    # "50:F1:4A:CC:0D:21",  # Glove USB Side
]

class BeetleClient(DefaultDelegate):
    def __init__(self, serialCharacteristic, index):
        DefaultDelegate.__init__(self)
        self.serialCharacteristic = serialCharacteristic
        self.index = index
        self.recvBuffer = bytearray()
        self.existingBufferLength = 0
        self.counter = 0

    def handleAcknowledge(self):
        if isBeetleHandshakeDone[self.index] == NOT_DONE:
            print(f'Sending Acknowledgement Packet to beetle {self.index}')
        self.serialCharacteristic.write(bytes("A", "utf-8"))
        isBeetleHandshakeDone[self.index] = DONE

    def sendData(self, data):
        queue_sensor_data.put(data)
        # print(f"Data is inside queue {data}")

    def handleBuffer(self, data):
        if self.existingBufferLength > 0:
            lengthToAdd = 20 - self.existingBufferLength
            self.recvBuffer += data[0:lengthToAdd]
            if len(self.recvBuffer) == 20:
                self.sendData(self.recvBuffer)
            self.recvBuffer = data[-self.existingBufferLength:]
            self.existingBufferLength = len(self.recvBuffer)
        else:
            if len(data) < 20:
                self.recvBuffer = data
                self.existingBufferLength = len(data)

    def handleNotification(self, cHandle, data):

        if len(data) < 20:
            print(len(data))
            self.handleBuffer(data)
        elif len(data) == 20:
            packetID = data[0]
            if packetID == ord('A'):
                self.handleAcknowledge()
            elif packetID == ord('G') or packetID == ord('W') or packetID == ord('V'):
                # print(data)
                self.counter += 1
                print("Packet No: " + str(self.counter))
                self.sendData(data)
        else:
            print("Invalid Data Packet!")
            pass


def BeetleClientThread(beetle_MAC, currIndex):
    beetle = Peripheral(beetle_MAC)
    isBeetleConnected = False

    print(f'Establishing connection parameters with beetle {currIndex}')
    serialService = beetle.getServiceByUUID("0000dfb0-0000-1000-8000-00805f9b34fb")
    serialCharacteristic = serialService.getCharacteristics()[0]
    beetle.delegate = BeetleClient(serialCharacteristic, currIndex)

    while True:

        try:
            if not isBeetleConnected:
                print(f'Connecting to beetle {currIndex}')
                beetle.connect(beetle_MAC)
                isBeetleConnected = True
            else:
                if not isBeetleHandshakeDone[currIndex]:
                    print(f'Initiating Handshake with beetle {currIndex}')
                    if startHandshake(beetle, serialCharacteristic, currIndex):
                        isBeetleHandshakeDone[currIndex] = DONE
                        print(f'Handshake Success with beetle {currIndex}')
                    else:
                        print(f'Handshake Failed with beetle {currIndex}')
                        isBeetleConnected = False

                else:
                    beetle.waitForNotifications(2.0)

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
    isBeetleHandshakeDone.append(NOT_DONE)
    BeetleClientThread("50:F1:4A:CC:0D:60", 0)

if __name__ == '__main__':
    main()