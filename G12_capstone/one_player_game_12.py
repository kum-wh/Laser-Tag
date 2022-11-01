from operator import length_hint
from threading import Timer
import socket
import threading
import queue
import random
from GameState_12 import GameState
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
import paho.mqtt.client as mqtt 
from colorama import Fore
from colorama import Style
# from pynq import Overlay
# from pynq import allocate
import numpy as np
import time
from struct import *

imu_time = 0
length = 0

'''
Between Viz and U96:
MQTT

grenade query: str ("g")
grenade_hit_or_miss: str ("t" or "f")
game_state: JSON
'''

queue_ai = queue.Queue() # Relay -> AI (sensor readings: str)
queue_game_state = queue.Queue() # AI -> GameMechanics (greande_hit_or_miss: bool, non_grenade_action: str)
queue_visualizer = queue.Queue() # AI -> Viz ("grenade": str), GM -> Viz (game_state: dict)
queue_greande_hit_or_miss = queue.Queue() # Viz -> AI (grenade_hit_or_miss: bool)
queue_eval_client = queue.Queue() # GM -> EvalClient (game_state: dict)

queue_ground_truth = queue.Queue() # 
#queue_visualizer_recalibration = queue.Queue() # 

def padd():
    while True:
        if ((time.time() - imu_time > 1) and length != 0):
            #print("INSIDE ELIF")
            for i in range(100 - length):
                queue_ai.put(b'W\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            time.sleep(1)


class Relay():
    def __init__(self):
        self.server_ip_address = 'localhost'
        self.listening_port = 4002 # Change to 4002
        self.address = ('', self.listening_port)
        self.header = 64
        self.format = 'utf-8'
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)

    def handle_client(self, connection, address):
        print(f"[NEW CONNECTION] {address} is now connected.")

        while True:
            message_length_in_byte = connection.recv(self.header)

            if message_length_in_byte:
                message_length_in_int = int(message_length_in_byte)
                message = connection.recv(message_length_in_int)
                print(message)
                queue_ai.put(message)
                print(f"{Fore.GREEN}[MESSAGE RECEIVED] {address}: {message}{Style.RESET_ALL}")

                connection.send("[MESSAGE RECEIVED] Your message is received!".encode(self.format))
            
        
        connection.close() # Do not need to close

    def run(self):
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.server_ip_address}:{self.listening_port}")

        while True:
            connection, address = self.server.accept()
            thread = threading.Thread(target = self.handle_client, args = (connection, address))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        

class AI():
    def __init__(self):
        # self.sensor_readings = []
        # self.all_actions = ['none', 'shoot', 'grenade', 'shield', 'reload', 'logout']
        # self.actions_to_generate = ['shoot', 'grenade', 'shield', 'reload']
        self.MAXIMUM_COUNTER = 100
        self.x = []
        self.y = []
        self.z = []
        self.gx = []
        self.gy = []
        self.gz = []
        self.counter = 0

    def ai(self):
        '''
        x_mean = np.mean(self.x)
        y_mean = np.mean(self.y)
        z_mean = np.mean(self.z)
        gx_mean = np.mean(self.gx)
        gy_mean = np.mean(self.gy)
        gz_mean = np.mean(self.gz)
        x_sd = np.std(self.x)
        y_sd = np.std(self.y)
        z_sd = np.std(self.z)
        gx_sd = np.std(self.gx)
        gy_sd = np.std(self.gy)
        gz_sd = np.std(self.gz)
        x_max = np.amax(self.x)
        y_max = np.amax(self.y)
        z_max = np.amax(self.z)
        gx_max = np.amax(self.gx)
        gy_max = np.amax(self.gy)
        gz_max = np.amax(self.gz)
        x_min = np.amin(self.x)
        y_min = np.amin(self.y)
        z_min = np.amin(self.z)
        gx_min = np.amin(self.gx)
        gy_min = np.amin(self.gy)
        gz_min = np.amin(self.gz)

        final = []

        for item in self.x:
            final.append(item)
        for item in self.y:
            final.append(item)
        for item in self.z:
            final.append(item)
        for item in self.gx:
            final.append(item)
        for item in self.gy:
            final.append(item)
        for item in self.gz:
            final.append(item)

        final.append(int(x_mean))
        final.append(int(y_mean))
        final.append(int(z_mean))
        final.append(int(gx_mean))
        final.append(int(gy_mean))
        final.append(int(gz_mean))
        final.append(int(x_sd))
        final.append(int(y_sd))
        final.append(int(z_sd))
        final.append(int(gx_sd))
        final.append(int(gy_sd))
        final.append(int(gz_sd))
        final.append(int(x_max))
        final.append(int(y_max))
        final.append(int(z_max))
        final.append(int(gx_max))
        final.append(int(gy_max))
        final.append(int(gz_max))
        final.append(int(x_min))
        final.append(int(y_min))
        final.append(int(z_min))
        final.append(int(gx_min))
        final.append(int(gy_min))
        final.append(int(gz_min))

        
        input_buffer = allocate(shape=(624,), dtype=np.intc)
        output_buffer = allocate(shape=(1,), dtype=np.intc)

        for i in range(624):
            input_buffer[i] = final[i]

        dma.sendchannel.transfer(input_buffer)
        dma.recvchannel.transfer(output_buffer)
        dma.sendchannel.wait()
        dma.recvchannel.wait()

        print(f"REAL AI: {output_buffer[0]}")

        # Testing with Viz
        # action = input("What is your action? ")
        # return action

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
        return 'shoot'


    def run(self):
        while True:
            sensor_reading = queue_ai.get()

            # sensor_reading_in_dict = json.loads(sensor_reading)
            # unpacked_sensor_reading = unpack('<b''6h''b''3h',  sensor_reading)
            unpacked_sensor_reading = unpack('<b''b''6h''b''2h''b',  sensor_reading)
            print(f"AI HAS RECEIVED SENSOR READING {unpacked_sensor_reading}")

            # Updated with Player ID 
            if len(unpacked_sensor_reading) != 12:
                print('Wrong packet received! The length of the packet is ',len(unpacked_sensor_reading))
                continue
            player = unpacked_sensor_reading[1]

            # Added a delay thread for shoot to acocunt for missed shots
            if unpacked_sensor_reading[0] == 71: # GUN 71, VEST 86 or unpacked_sensor_reading[0] == 86
                action = f"{player} shoot"
                #queue_game_state.put(action) # Thread for each player
                delay_shoot = Timer(0.3, queue_game_state.put, args=(action,))
                delay_shoot.daemon = True
                delay_shoot.start() 
                # queue.get()
            elif unpacked_sensor_reading[0] == 86:
                action = f"{player} hit"
                queue_game_state.put(action)

            # TODO Need a new AI for player 2
            elif unpacked_sensor_reading[0] == 87: # IMU 87
                global imu_time
                global length
                imu_time = time.time()

                # Modify the positions as added a new byte to indicate player
                self.x.append(unpacked_sensor_reading[2]) 
                self.y.append(unpacked_sensor_reading[3]) 
                self.z.append(unpacked_sensor_reading[4]) 
                self.gx.append(unpacked_sensor_reading[5]) 
                self.gy.append(unpacked_sensor_reading[6]) 
                self.gz.append(unpacked_sensor_reading[7])

                length = len(self.x) #length += 1
                print(f"{length} number of IMU sensor readings are received!")
                print(length == self.MAXIMUM_COUNTER)

                if (length == self.MAXIMUM_COUNTER): # <-- One more player 2
                    action = self.ai()

                    self.x.clear()
                    self.y.clear()
                    self.z.clear()
                    self.gx.clear()
                    self.gy.clear()
                    self.gz.clear()

                    length = 0

                    #Added
                    pred_action = f"{player} {action}"
                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                    
                    queue_game_state.put(pred_action) # do not care if it is grenade or other actions

class GameMechanics():
    def __init__(self):
        self.p1_action = 'none'
        self.p2_action = 'none'
        self.p1_ready = False
        self.p2_ready = False
        # self.p1_hit = False
        # self.p2_hit = False
        # self.actions_to_generate = ['shoot', 'grenade', 'shield', 'reload']
        self.game_state = GameState()
        self.game_state_in_dict = self.game_state.get_dict()
    
    def run(self):
        while True:
            curr_action = queue_game_state.get()
            
            # Added player ID
            player , action = curr_action.split(" ")
            if player == 1 and not self.p1_ready:
                self.p1_action = action
                self.p1_ready = True
            elif player == 2 and not self.p2_ready:
                self.p2_action = action
                self.p2_ready = True
            else:
                print(f"Player 1 action: {self.p1_action}, Player 1 status: {self.p1_ready}")
                print(f"Player 2 action: {self.p2_action}, Player 2 status: {self.p2_ready}")
                continue

            '''
            if logout need to make sure game ends! Viz job. Ext Comms can make program sleep.
            '''
        
            self.game_state.update_players(curr_action)
            print(f"[GAME MECHANICS] Player states updated with {curr_action} :)")
            self.game_state_in_dict = self.game_state.get_dict()
            if self.p1_ready and self.p2_ready:
                queue_eval_client.put(self.game_state_in_dict)
                self.p1_ready = False
                self.p2_ready = False
                ground_truth = queue_ground_truth.get()

                if ground_truth['p1']['hp'] != (self.game_state.get_dict())['p1']['hp'] or ground_truth['p1']['action'] != (self.game_state.get_dict())['p1']['action'] or ground_truth['p1']['bullets'] != (self.game_state.get_dict())['p1']['bullets'] or ground_truth['p1']['grenades'] != (self.game_state.get_dict())['p1']['grenades'] or ground_truth['p1']['shield_health'] != (self.game_state.get_dict())['p1']['shield_health'] or ground_truth['p1']['num_deaths'] != (self.game_state.get_dict())['p1']['num_deaths'] or ground_truth['p1']['num_shield'] != (self.game_state.get_dict())['p1']['num_shield'] or ground_truth['p2']['hp'] != (self.game_state.get_dict())['p2']['hp'] or ground_truth['p2']['action'] != (self.game_state.get_dict())['p2']['action'] or ground_truth['p2']['bullets'] != (self.game_state.get_dict())['p2']['bullets'] or ground_truth['p2']['grenades'] != (self.game_state.get_dict())['p2']['grenades'] or ground_truth['p2']['shield_health'] != (self.game_state.get_dict())['p2']['shield_health'] or ground_truth['p2']['num_deaths'] != (self.game_state.get_dict())['p2']['num_deaths'] or ground_truth['p2']['num_shield'] != (self.game_state.get_dict())['p2']['num_shield']:

                    print("Predicted game state differs from the ground truth!")

                    self.game_state.player_1.hp = ground_truth['p1']['hp']
                    self.game_state.player_1.action = ground_truth['p1']['action']
                    self.game_state.player_1.bullets = ground_truth['p1']['bullets']
                    self.game_state.player_1.grenades = ground_truth['p1']['grenades']
                    #self.game_state.player_1.shield_time = ground_truth['p1']['shield_time']
                    self.game_state.player_1.shield_health = ground_truth['p1']['shield_health']
                    self.game_state.player_1.num_deaths = ground_truth['p1']['num_deaths']
                    self.game_state.player_1.num_shield = ground_truth['p1']['num_shield']

                    self.game_state.player_2.hp = ground_truth['p2']['hp']
                    self.game_state.player_2.action = ground_truth['p2']['action']
                    self.game_state.player_2.bullets = ground_truth['p2']['bullets']
                    self.game_state.player_2.grenades = ground_truth['p2']['grenades']
                    #self.game_state.player_2.shield_time = ground_truth['p1']['shield_time']
                    self.game_state.player_2.shield_health = ground_truth['p2']['shield_health']
                    self.game_state.player_2.num_deaths = ground_truth['p2']['num_deaths']
                    self.game_state.player_2.num_shield = ground_truth['p2']['num_shield']

                    # queue_visualizer.put(ground_truth)

            queue_visualizer.put(self.game_state_in_dict)

class EvalClient():
    def __init__(self):
        self.server_ip_address = "localhost" # "137.132.92.184"
        self.listening_port = 4010 # 9999
        self.address = (self.server_ip_address, self.listening_port)
        self.header = 64
        self.format = 'utf-8'
        self.key = "PLSPLSPLSPLSWORK"

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET is the Internet address family for IPv4. SOCK_STREAM is the socket type for TCP
        self.client.connect(self.address)

    def recv_game_state(self):
        try:
            # recv length followed by '_' followed by cypher
            data = b''
            while not data.endswith(b'_'):
                _d = self.client.recv(1)
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                print("STOP!!!!")
            data = data.decode("utf-8")
            length = int(data[:-1])
            data = b''
            while len(data) < length:
                _d = self.client.recv(length - len(data))
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                print("STOP!!!!")
            msg = data.decode("utf8")
        except ConnectionResetError:
            print('Connection Reset')
            print("STOP!!!!")
        return msg

    def run(self):
        while True:
            game_state = queue_eval_client.get()
            
            # secret key
            # JSON
            # base64 encoded message of 128-bits initial value + message
            # padding
            # len + ciphertext

            data = json.dumps(game_state)

            plaintext_bytes = pad(data.encode("utf-8"), 16) # expect data to have length multiple of the block size (e.g. 16 bytes for AES)

            # each plaintext block gets XOR-ed with the previous ciphertext block prior to encryption
            secret_key_bytes = self.key.encode("utf-8")
            cipher = AES.new(secret_key_bytes, AES.MODE_CBC)
            iv_bytes = cipher.iv
            ciphertext_bytes = cipher.encrypt(plaintext_bytes)
            message = base64.b64encode(iv_bytes + ciphertext_bytes)

            m = str(len(message))+'_'
            
            try:
                self.client.sendall(m.encode("utf-8"))
                self.client.sendall(message)
                print(f'{Fore.BLUE}[EVAL SERVER HAS RECEIVED GAME STATE]{Style.RESET_ALL}')
            except OSError:
                print("Connection terminated")

            while True:
                ground_truth = self.recv_game_state()
                if ground_truth is not None:
                    ground_truth_in_dict = json.loads(ground_truth)
                    print(f'[RECEIVED GROUND TRUTH FROM EVAL SERVER] {ground_truth_in_dict}')

                    queue_ground_truth.put(ground_truth_in_dict)

                    break

class Visualizer():
    def __init__(self):
        # mqtt.eclipseprojects.io
        #self.mqttBroker ="mqtt.eclipseprojects.io"
        self.mqttBroker = "broker.hivemq.com"

        self.publisher = mqtt.Client("Pub")
        self.publisher.connect(self.mqttBroker, 1883, 60) 

        # self.subscriber = mqtt.Client("Sub")
        # self.subscriber.connect(self.mqttBroker, 1883, 60)

        # self.greande_action = 'g'
        # self.has_received = False


    # def on_message(self, client, userdata, message): #put queue into userdata
    #     grenade_hit = str(message.payload.decode("utf-8"))
    #     if grenade_hit is not None:
    #         self.has_received = True
    #     #print(grenade_hit)
    #     print(f'{Fore.RED}[VISUALIZER HAS RESPONDED GRENADE HIT] {grenade_hit}{Style.RESET_ALL}')
        
    #     queue_greande_hit_or_miss.put(grenade_hit)

    def speak(self):
        while True:
            game_state = queue_visualizer.get()
            self.publisher.publish("B12cNwWz/Ultra96Send", json.dumps(game_state))
            print(f'{Fore.BLUE}[VISUALIZER HAS RECEIVED GAME STATE]{game_state} {Style.RESET_ALL}')
    
    # def listen(self):
    #     self.has_received = False
    #     self.subscriber.loop_start()
        
    #     self.subscriber.subscribe("Capstone/VisualizerReply")
    #     self.subscriber.on_message=self.on_message

    #     if self.has_received == True:
    #         self.subscriber.loop_stop()
            
        
        # recalibrated_result = queue_visualizer_recalibration.get()
        # print(f'[VISUALIZER HAS RECEIVED RECALIBRATED RESULT] {recalibrated_result}')

relay = Relay()
ai = AI()
game_mechanics = GameMechanics()
eval_client = EvalClient()
visualizer = Visualizer()

t1 = threading.Thread(target=relay.run, args=())
t2 = threading.Thread(target=ai.run, args=())
t3 = threading.Thread(target=game_mechanics.run, args=())
t4 = threading.Thread(target=eval_client.run, args=())
t5 = threading.Thread(target=visualizer.speak, args=())
# t6 = threading.Thread(target=visualizer.listen, args=())
t7 = threading.Thread(target=padd, args=())

# ol = Overlay('design_1_wrapper.bit', download = False)
# dma = ol.axi_dma_0

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
# t6.start()
t7.start()


t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
# t6.join()
t7.join()
