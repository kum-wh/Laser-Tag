import paho.mqtt.client as mqtt 
from random import uniform
import time
from GameState import GameState
import threading
import json
from colorama import Fore
from colorama import Style

#mqttBroker = "mqtt.eclipseprojects.io"
mqttBroker = "broker.hivemq.com"


publisher = mqtt.Client("Pub")
publisher.connect(mqttBroker, 1883, 60) 
subscriber = mqtt.Client("Sub")
subscriber.connect(mqttBroker, 1883, 60)

greande = 'g'
game_state = GameState()
game_state_in_dict = game_state.get_dict()
game_state_in_json = json.dumps(game_state_in_dict)


class Pub:
    def __init__(self):
        pass

    def run(self):
        for i in range(100):
            if i % 2 == 0:
                publisher.publish("Capstone/Ultra96Send", game_state_in_json)
                print(f"{Fore.GREEN}Laptop just published game_state!{Style.RESET_ALL}")
            else:
                publisher.publish("Capstone/Ultra96Send", greande)
                print(f"{Fore.BLUE}Laptop just published greande query!{Style.RESET_ALL}")
            time.sleep(5)

class Sub:
    def __init__(self):
            pass

    def on_message(self, client, userdata, message):
        grenade = str(message.payload.decode("utf-8"))
        print(f"{Fore.MAGENTA}Received message from Visualizer: {greande}{Style.RESET_ALL}")

        if grenade == 't':
            print(f"{Fore.RED}Visualizer has responded with a grenade hit!{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}Visualizer has responded with a grenade miss!{Style.RESET_ALL}")

    def run(self):
        subscriber.loop_start()
        
        subscriber.subscribe("Capstone/VisualizerReply")
        subscriber.on_message=self.on_message 
        time.sleep(1000000)

        subscriber.loop_stop()

pub = Pub()
sub = Sub()

t1 = threading.Thread(target=pub.run, args=())
t2 = threading.Thread(target=sub.run, args=())

t1.start()
t2.start()

t1.join()
t2.join()
