from operator import length_hint
from threading import Timer
import socket
import threading
import queue
import random
from GameState import GameState
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
import paho.mqtt.client as mqtt 
from colorama import Fore
from colorama import Style
from pynq import Overlay
from pynq import allocate
import numpy as np
import time
from struct import *

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
# queue_eval_client = queue.Queue() # GM -> EvalClient (game_state: dict)
queue_ground_truth = queue.Queue()

class Relay():
    def __init__(self):
        self.server_ip_address = 'localhost'
        self.listening_port = 4002
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
                queue_ai.put(message)
                # print(f"{Fore.GREEN}[MESSAGE RECEIVED] {address}: {message}{Style.RESET_ALL}")

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
        
        self.x1 = []
        self.y1 = []
        self.z1 = []
        self.gx1 = []
        self.gy1 = []
        self.gz1 = []

        self.x2 = []
        self.y2 = []
        self.z2 = []
        self.gx2 = []
        self.gy2 = []
        self.gz2 = []

    def padder1(self):
        if len(self.x1) != 50:
            print("Packet Not 50 for Player1")
            queue_visualizer.put("bdgun1")
            self.x1.clear()
            self.y1.clear()
            self.z1.clear()
            self.gx1.clear()
            self.gy1.clear()
            self.gz1.clear()
    
    def padder2(self):
        if len(self.x2) != 50:
            print("Packet Not 50 for Player2")
            queue_visualizer.put("bdgun2")
            self.x2.clear()
            self.y2.clear()
            self.z2.clear()
            self.gx2.clear()
            self.gy2.clear()
            self.gz2.clear()

    def ai(self):

        x_mean = np.mean(self.x1)
        y_mean = np.mean(self.y1)
        z_mean = np.mean(self.z1)
        gx_mean = np.mean(self.gx1)
        gy_mean = np.mean(self.gy1)
        gz_mean = np.mean(self.gz1)
        x_max = np.amax(self.x1)
        y_max = np.amax(self.y1)
        z_max = np.amax(self.z1)
        gx_max = np.amax(self.gx1)
        gy_max = np.amax(self.gy1)
        gz_max = np.amax(self.gz1)
        x_min = np.amin(self.x1)
        y_min = np.amin(self.y1)
        z_min = np.amin(self.z1)
        gx_min = np.amin(self.gx1)
        gy_min = np.amin(self.gy1)
        gz_min = np.amin(self.gz1)

        final = []

        for item in self.x1:
            final.append(item)
        for item in self.y1:
            final.append(item)
        for item in self.z1:
            final.append(item)
        for item in self.gx1:
            final.append(item)
        for item in self.gy1:
            final.append(item)
        for item in self.gz1:
            final.append(item)

        final.append(int(x_mean))
        final.append(int(y_mean))
        final.append(int(z_mean))
        final.append(int(gx_mean))
        final.append(int(gy_mean))
        final.append(int(gz_mean))
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
        
        input_buffer = allocate(shape=(318,), dtype=np.intc)
        output_buffer = allocate(shape=(1,), dtype=np.intc)

        for i in range(318):
            input_buffer[i] = final[i]

        dma.sendchannel.transfer(input_buffer)
        dma.recvchannel.transfer(output_buffer)
        dma.sendchannel.wait()
        dma.recvchannel.wait()

        print(f"REAL AI: {output_buffer[0]}")

        if output_buffer[0] == 1:
            return "grenade"
        elif output_buffer[0] == 2:
            return "shield"
        elif output_buffer[0] == 3:
            return "reload"
        elif output_buffer[0] == 4:
            return "logout"
        elif output_buffer[0] == 5:
            return "none"
        else:
            return "none"

    def ai2(self):

        x_mean = np.mean(self.x2)
        y_mean = np.mean(self.y2)
        z_mean = np.mean(self.z2)
        gx_mean = np.mean(self.gx2)
        gy_mean = np.mean(self.gy2)
        gz_mean = np.mean(self.gz2)
        x_max = np.amax(self.x2)
        y_max = np.amax(self.y2)
        z_max = np.amax(self.z2)
        gx_max = np.amax(self.gx2)
        gy_max = np.amax(self.gy2)
        gz_max = np.amax(self.gz2)
        x_min = np.amin(self.x2)
        y_min = np.amin(self.y2)
        z_min = np.amin(self.z2)
        gx_min = np.amin(self.gx2)
        gy_min = np.amin(self.gy2)
        gz_min = np.amin(self.gz2)

        final2 = []

        for item in self.x2:
            final2.append(item)
        for item in self.y2:
            final2.append(item)
        for item in self.z2:
            final2.append(item)
        for item in self.gx2:
            final2.append(item)
        for item in self.gy2:
            final2.append(item)
        for item in self.gz2:
            final2.append(item)

        final2.append(int(x_mean))
        final2.append(int(y_mean))
        final2.append(int(z_mean))
        final2.append(int(gx_mean))
        final2.append(int(gy_mean))
        final2.append(int(gz_mean))
        final2.append(int(x_max))
        final2.append(int(y_max))
        final2.append(int(z_max))
        final2.append(int(gx_max))
        final2.append(int(gy_max))
        final2.append(int(gz_max))
        final2.append(int(x_min))
        final2.append(int(y_min))
        final2.append(int(z_min))
        final2.append(int(gx_min))
        final2.append(int(gy_min))
        final2.append(int(gz_min))
 
        input_buffer = allocate(shape=(318,), dtype=np.intc)
        output_buffer = allocate(shape=(1,), dtype=np.intc)

        for i in range(318):
            input_buffer[i] = final2[i]

        dma.sendchannel.transfer(input_buffer)
        dma.recvchannel.transfer(output_buffer)
        dma.sendchannel.wait()
        dma.recvchannel.wait()

        print(f"REAL AI: {output_buffer[0]}")

        if output_buffer[0] == 1:
            return "grenade"
        elif output_buffer[0] == 2:
            return "shield"
        elif output_buffer[0] == 3:
            return "reload"
        elif output_buffer[0] == 4:
            return "logout"
        elif output_buffer[0] == 5:
            return "none"
        else:
            return "none"

    def run(self):
        while True:
            sensor_reading = queue_ai.get()
            unpacked_sensor_reading = unpack('<b''b''6h''b''2h''b',  sensor_reading)
            print(f"AI HAS RECEIVED SENSOR READING {unpacked_sensor_reading}")

            # Updated with Player ID 
            if len(unpacked_sensor_reading) != 12:
                print('Wrong packet received! The length of the packet is ',len(unpacked_sensor_reading))
                continue
            player = unpacked_sensor_reading[1]

            # Added a delay thread for shoot to acocunt for missed shots
            if unpacked_sensor_reading[0] == 71: # GUN 71, VEST 86 or unpacked_sensor_reading[0] == 86
                action = f"{player} shoot" # Thread for each player
                delay_shoot = Timer(0.3, queue_game_state.put, args=(action,))
                delay_shoot.daemon = True
                delay_shoot.start()

            elif unpacked_sensor_reading[0] == 86:
                action = f"{player} hit"
                queue_game_state.put(action)

            elif unpacked_sensor_reading[0] == 73:
                print("Invalid Data received")

            elif unpacked_sensor_reading[0] == 68: # Disconnected
                if player == 1:
                    queue_visualizer.put("bdgun1")
                    self.x1.clear()
                    self.y1.clear()
                    self.z1.clear()
                    self.gx1.clear()
                    self.gy1.clear()
                    self.gz1.clear()
                elif player == 2:
                    queue_visualizer.put("bdgun2")
                    self.x2.clear()
                    self.y2.clear()
                    self.z2.clear()
                    self.gx2.clear()
                    self.gy2.clear()
                    self.gz2.clear()

            elif unpacked_sensor_reading[0] == 67: # Connected
                if player == 1:
                    queue_visualizer.put("bc1")
                elif player == 2:
                    queue_visualizer.put("bc2")

            elif unpacked_sensor_reading[0] == 87: # IMU 87

                # Modify the positions as added a new byte to indicate player
                if player == 1:
                    if len(self.x1) == 1:
                        delay_IMU1 = Timer(0.5, self.padder1, args=())
                        delay_IMU1.daemon = True
                        delay_IMU1.start()
                    self.x1.append(unpacked_sensor_reading[2]) 
                    self.y1.append(unpacked_sensor_reading[3]) 
                    self.z1.append(unpacked_sensor_reading[4]) 
                    self.gx1.append(unpacked_sensor_reading[5]) 
                    self.gy1.append(unpacked_sensor_reading[6])
                    self.gz1.append(unpacked_sensor_reading[7])
                elif player == 2:
                    if len(self.x2) == 1:
                        delay_IMU2 = Timer(0.5, self.padder2, args=())
                        delay_IMU2.daemon = True
                        delay_IMU2.start()
                    self.x2.append(unpacked_sensor_reading[2]) 
                    self.y2.append(unpacked_sensor_reading[3]) 
                    self.z2.append(unpacked_sensor_reading[4]) 
                    self.gx2.append(unpacked_sensor_reading[5]) 
                    self.gy2.append(unpacked_sensor_reading[6])
                    self.gz2.append(unpacked_sensor_reading[6])

                if (len(self.x1) == 50):
                    delay_IMU1.cancel()
                    action = self.ai()

                    self.x1.clear()
                    self.y1.clear()
                    self.z1.clear()
                    self.gx1.clear()
                    self.gy1.clear()
                    self.gz1.clear()

                    if action != "none":
                        pred_action = f"{player} {action}"
                        print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                        queue_game_state.put(pred_action)
                    else:
                        print("Action is none")

                if (len(self.x2) == 50):
                    delay_IMU2.cancel()
                    action = self.ai2()
                    
                    self.x2.clear()
                    self.y2.clear()
                    self.z2.clear()
                    self.gx2.clear()
                    self.gy2.clear()
                    self.gz2.clear()

                    if action != "none":
                        pred_action = f"{player} {action}"
                        print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                        queue_game_state.put(pred_action)
                    else: 
                        print("Action is none")


class GameMechanics():
    def __init__(self):
        self.p1_action = 'none'
        self.p2_action = 'none'
        self.p1_ready = False
        self.p2_ready = False
        self.game_state = GameState()
        self.game_state_in_dict = self.game_state.get_dict()
    
    def run(self):
        while True:
            curr_action = queue_game_state.get()
            
            # Added player ID
            player , action = curr_action.split(" ")

            if action == "hit" or action == "hit_G":
                print(curr_action)
            elif player == "1" and self.p1_ready is False:
                self.p1_action = action
                self.p1_ready = True
            elif player == "2" and self.p2_ready is False:
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

                if self.p1_action == "grenade":
                    # is_hit = queue_greande_hit_or_miss.get()
                    is_hit = "f"
                    if is_hit == "t":
                        hit_action = f"2 hit_G"
                        print(f"[GAME MECHANICS] Player states updated with {hit_action} :)")
                        self.game_state_in_dict = self.game_state.get_dict()
                        
                if self.p2_action == "grenade":
                    # is_hit = queue_greande_hit_or_miss.get()
                    is_hit = "f"
                    if is_hit == "t":
                        hit_action = f"1 hit_G"
                        self.game_state.update_players(hit_action)
                        print(f"[GAME MECHANICS] Player states updated with {hit_action} :)")
                        self.game_state_in_dict = self.game_state.get_dict()

                if self.game_state_in_dict["p1"]["action"] == "hit_G" or self.game_state_in_dict["p1"]["action"] == "hit":
                    self.game_state_in_dict["p1"]["action"] = self.p1_action
                if self.game_state_in_dict["p2"]["action"] == "hit_G" or self.game_state_in_dict["p2"]["action"] == "hit":
                    self.game_state_in_dict["p2"]["action"] = self.p2_action

                # queue_eval_client.put(self.game_state_in_dict)

                self.p1_ready = False
                self.p2_ready = False
                while queue_ai.empty() == False:
                    queue_ai.get()
                while queue_game_state.empty() == False:
                    queue_game_state.get()
                while queue_visualizer.empty() == False:
                    queue_visualizer.get()
                while queue_greande_hit_or_miss.empty() == False:
                    queue_greande_hit_or_miss.get()
                # while queue_eval_client.empty() == False:
                    # queue_eval_client.clear()

                # ground_truth = queue_ground_truth.get()
                '''
                if ground_truth['p1']['hp'] != (self.game_state.get_dict())['p1']['hp'] or ground_truth['p1']['action'] != (self.game_state.get_dict())['p1']['action'] or ground_truth['p1']['bullets'] != (self.game_state.get_dict())['p1']['bullets'] or ground_truth['p1']['grenades'] != (self.game_state.get_dict())['p1']['grenades'] or ground_truth['p1']['shield_health'] != (self.game_state.get_dict())['p1']['shield_health'] or ground_truth['p1']['num_deaths'] != (self.game_state.get_dict())['p1']['num_deaths'] or ground_truth['p1']['num_shield'] != (self.game_state.get_dict())['p1']['num_shield'] or ground_truth['p2']['hp'] != (self.game_state.get_dict())['p2']['hp'] or ground_truth['p2']['action'] != (self.game_state.get_dict())['p2']['action'] or ground_truth['p2']['bullets'] != (self.game_state.get_dict())['p2']['bullets'] or ground_truth['p2']['grenades'] != (self.game_state.get_dict())['p2']['grenades'] or ground_truth['p2']['shield_health'] != (self.game_state.get_dict())['p2']['shield_health'] or ground_truth['p2']['num_deaths'] != (self.game_state.get_dict())['p2']['num_deaths'] or ground_truth['p2']['num_shield'] != (self.game_state.get_dict())['p2']['num_shield']:
                    
                    print("Predicted game state differs from the ground truth!")

                    self.game_state.player_1.hp = ground_truth['p1']['hp']
                    self.game_state.player_1.action = ground_truth['p1']['action']
                    self.game_state.player_1.bullets = ground_truth['p1']['bullets']
                    self.game_state.player_1.grenades = ground_truth['p1']['grenades']
                    self.game_state.player_1.shield_health = ground_truth['p1']['shield_health']
                    self.game_state.player_1.num_deaths = ground_truth['p1']['num_deaths']
                    self.game_state.player_1.num_shield = ground_truth['p1']['num_shield']

                    self.game_state.player_2.hp = ground_truth['p2']['hp']
                    self.game_state.player_2.action = ground_truth['p2']['action']
                    self.game_state.player_2.bullets = ground_truth['p2']['bullets']
                    self.game_state.player_2.grenades = ground_truth['p2']['grenades']
                    self.game_state.player_2.shield_health = ground_truth['p2']['shield_health']
                    self.game_state.player_2.num_deaths = ground_truth['p2']['num_deaths']
                    self.game_state.player_2.num_shield = ground_truth['p2']['num_shield']
                '''
            # Clear the other player's action
            if player == '1':
                self.game_state_in_dict['p2']['action'] = 'none'
            elif player == '2':
                self.game_state_in_dict['p1']['action'] = 'none'
            
            queue_visualizer.put(self.game_state_in_dict)

'''
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
'''

class Visualizer():
    def __init__(self):
        self.mqttBroker = "broker.hivemq.com"
        # self.mqttBroker = "18.143.111.203"

        self.publisher = mqtt.Client("Pub")
        self.publisher.connect(self.mqttBroker, 1883, 60)
        
        # self.publisher.on_message = self.on_message
        # self.publisher.loop_start()
        # self.publisher.subscribe("B12cNwWz/VisualizerReply")
        self.subscriber = mqtt.Client("Sub")
        self.subscriber.connect(self.mqttBroker, 1883, 60)
        
        self.greande_action = 'g'
        self.has_received = False

    def on_message(self, client, userdata, message): #put queue into userdata
        grenade_hit = str(message.payload.decode("utf-8"))
        if grenade_hit is not None:
            self.has_received = True
        print(f'{Fore.RED}[VISUALIZER HAS RESPONDED GRENADE HIT] {grenade_hit}{Style.RESET_ALL}')
        
        queue_greande_hit_or_miss.put(grenade_hit)

    def speak(self):
        while True:
            game_state = queue_visualizer.get()
            self.publisher.publish("B12cNwWz/Ultra96Send", json.dumps(game_state))
            print(f'{Fore.BLUE}[VISUALIZER HAS RECEIVED GAME STATE]{game_state} {Style.RESET_ALL}')

    def listen(self):
        self.has_received = False
        self.subscriber.loop_start()
        self.subscriber.subscribe("B12cNwWz/VisualizerReply")
        self.subscriber.on_message = self.on_message
        if self.has_received == True:
            self.subscriber.loop_stop()


relay = Relay()
ai = AI()
game_mechanics = GameMechanics()
# eval_client = EvalClient()
visualizer = Visualizer()

t1 = threading.Thread(target=relay.run, args=())
t2 = threading.Thread(target=ai.run, args=())
t3 = threading.Thread(target=game_mechanics.run, args=())
# t4 = threading.Thread(target=eval_client.run, args=())
t5 = threading.Thread(target=visualizer.speak, args=())
t6 = threading.Thread(target=visualizer.listen, args=())

ol = Overlay('design_1_wrapper.bit')
dma = ol.axi_dma_0

t1.start()
t2.start()
t3.start()
# t4.start()
t5.start()
t6.start()

t1.join()
t2.join()
t3.join()
# t4.join()
t5.join()
t6.join()