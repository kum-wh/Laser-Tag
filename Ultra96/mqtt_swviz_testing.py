import paho.mqtt.client as mqtt 
from random import uniform
import time
from GameState import GameState
import threading
import json
from colorama import Fore
from colorama import Style

'''
pip install paho-mqtt
eval_server
'''

mqttBroker = "broker.hivemq.com"

publisher = mqtt.Client("Pub")
publisher.connect(mqttBroker, 1883, 60) 


greande = 'g'
game_state = GameState()

#ACTIONS = ['grenade', 'shoot', 'shoot', 'shoot', 'shoot', 'shoot', 'grenade', 'reload', 'reload', 'logout']
p1_action = ''
p2_action = "none"

class Pub:
    def __init__(self):
        self.counter = 0

    def run(self):
        for i in range(100):
            # p1_action = ACTIONS[i % 10]
            # game_state.update_players(p1_action, p2_action)

            # game_state_in_dict = game_state.get_dict()
            # game_state_in_json = json.dumps(game_state_in_dict)

            ACTIONS = ['logout', 'shoot', 'shoot', 'shoot', 'shoot', 'shoot', 'grenade', 
            'reload', 'reload', 'shield', 'shoot', 'shoot', 'shoot', 'shoot', 'grenade', 
            'reload', 'shield', 'shield', 'logout', 'shoot']
            p1_action = ACTIONS[self.counter]
            self.counter += 1
            if self.counter == 19:
                self.counter = 0
            
            game_state.update_players(p1_action, p2_action)
            game_state_in_dict = game_state.get_dict()
            game_state_in_json = json.dumps(game_state_in_dict)

            publisher.publish("B12cNwWz/Ultra96Send", game_state_in_json)
            print(f"{Fore.GREEN}Laptop just published game_state!{Style.RESET_ALL}")
            print(f"Fore.RED{game_state.get_dict()}")
            _ = input("Please press enter to get the next action :) ")

class Sub:
    def __init__(self):
            self.has_received = False
            self.subscriber = mqtt.Client("Sub")
            self.subscriber.connect(mqttBroker, 1883, 60)
            self.grenade_hit = "None"
    def on_message(self, client, userdata, message):
        self.grenade_hit = str(message.payload.decode("utf-8"))
        print(f"{Fore.MAGENTA}Received message from Visualizer: {self.grenade_hit}{Style.RESET_ALL}")

        if self.grenade_hit == 't':
            print(f"{Fore.RED}Visualizer has responded with a grenade hit!{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}Visualizer has responded with a grenade miss!{Style.RESET_ALL}")

    def run(self):
        self.has_received = False
        self.subscriber.loop_start()
        
        self.subscriber.subscribe("Capstone/VisualizerReply")
        self.subscriber.on_message=self.on_message

        if self.has_received == True:
            self.subscriber.loop_stop()

pub = Pub()
sub = Sub()

t1 = threading.Thread(target=pub.run, args=())
t2 = threading.Thread(target=sub.run, args=())

t1.start()
t2.start()

t1.join()
t2.join()
