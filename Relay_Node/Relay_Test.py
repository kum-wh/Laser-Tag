import socket
# import sshtunnel
import queue
import threading

SERVER = '192.168.95.235'
PORT = 4700
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'
HEADER = 64

queue_sensor_data = queue.Queue()
'''
def ssh_tunnel():
    SUNFIRE_USERNAME = "kum-wh"
    SUNFIRE_PASSWORD = "uigeksj2"
    XILINX_USERNAME = "xilinx"
    XILINX_PASSWORD = "xilinx"

    SUNFIRE = "sunfire.comp.nus.edu.sg"
    XILINX = "192.168.95.235"
    LOCAL_HOST = 'localhost'

    SSH_PORT = 22
    PORT = 4223

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
''''

class DataRelay:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(ADDRESS)
        except Exception as e:
            print(e)

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


if __name__ == '__main__':
    # ssh_tunnel()

    data_relay = DataRelay()
    if data_relay is not None:
        print(f"data relay object is created!")
    t1 = threading.Thread(target=data_relay.run)
    t1.start()
    if t1.is_alive():
        print("t1 is alive")
    
    while True:
        action1 = input("PLayer 1 action:")
        action2 = input("PLayer 2 action:")
        
        if action1 == "F": # shoot
            queue_sensor_data.put(b'G\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action1 == "V": # Hit
            queue_sensor_data.put(b'V\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action1 == "R": #reload
            for i in range(46):
                queue_sensor_data.put(b'W\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action1 == "G": # Grenade
            for i in range(50):
                queue_sensor_data.put(b'W\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action1 == "S": #shield
            for i in range(50):
                queue_sensor_data.put(b'W\x01\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action1 == "L": # LogOut
            for i in range(50):
                queue_sensor_data.put(b'W\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action1 == "N": # None
            for i in range(20):
                queue_sensor_data.put(b'I\x01\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

        if action2 == "F": # shoot
            queue_sensor_data.put(b'G\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action2 == "V": # Hit
            queue_sensor_data.put(b'V\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action2 == "R": #reload
            for i in range(46):
                queue_sensor_data.put(b'W\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action2 == "G": # Grenade
            for i in range(50):
                queue_sensor_data.put(b'W\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action2 == "S": #shield
            for i in range(50):
                queue_sensor_data.put(b'W\x02\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action2 == "L": # LogOut
            for i in range(50):
                queue_sensor_data.put(b'W\x02\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        elif action2 == "N": # None
            for i in range(20):
                queue_sensor_data.put(b'I\x02\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')