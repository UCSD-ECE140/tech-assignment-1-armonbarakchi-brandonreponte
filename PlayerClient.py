import os
import json
import numpy as np
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    if msg.topic == f"games/{lobby_name}/{player}/game_state":
        client.gamestate = json.loads(str(msg.payload)[2:-1])
        pathfind()
    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

# retrieve a map of the player's vision
def playerVision():
    # get relative positions of game objects from player
    offset = np.array(client.gamestate["currentPosition"]) - 2
    walls = np.array(client.gamestate["walls"])
    teammates = np.array(client.gamestate["teammatePositions"])
    enemies = np.array(client.gamestate["enemyPositions"])
    coins1 = np.array(client.gamestate["coin1"])
    coins2 = np.array(client.gamestate["coin2"])
    coins3 = np.array(client.gamestate["coin3"])
    
    vision = np.zeros(shape=(5,5))      # create 5x5 vision around the player
    vision[2][2] = 1                    # player position

    for wall in walls:
        vision[wall[0] - offset[0]][wall[1] - offset[1]] = -1

    for teammate in teammates:
        vision[teammate[0] - offset[0]][teammate[1] - offset[1]] = -1

    for enemy in enemies:
        vision[enemy[0] - offset[0]][enemy[1] - offset[1]] = -1

    for coin in coins1:
        vision[coin[0] - offset[0]][coin[1] - offset[1]] = 1

    for coin in coins2:
        vision[coin[0] - offset[0]][coin[1] - offset[1]] = 2

    for coin in coins3:
        vision[coin[0] - offset[0]][coin[1] - offset[1]] = 3

    return vision

# BFS to find nearest coin
def pathfind():
    # get map of player's vision
    vision = playerVision()
    # player at center
    player = (2,2)
    
    # next to explore
    frontier = [player]
    # already explored
    explored = [player]
    # previous pointers for path reconstruction
    prev = {}
    # path found to nearest coin
    pathCurr = []

    # BFS loop
    while len(frontier) != 0:
        # get next coordinate to explore
        v = frontier.pop(0)
        # iterate through all directions
        for direction in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
            # coordinate at given direction
            u = (v[0]+direction[0], v[1]+direction[1])
            # check if in bound of map
            if u[0] < 0 or u[0] > 4 or u[1] < 0 or u[1] > 4:
                continue
            # if not a wall and not explored
            if u not in explored and vision[u[0]][u[1]] >= 0:
                # add to frontier and explored
                frontier.append(u)
                explored.append(u)
                # track previous of this coordinate
                prev[u] = v
                # if found a coin, break out of loop
                if vision[u[0]][u[1]] >= 1:
                    pathCurr = u
                    break

    # path reconstruction
    path = [pathCurr]
    # while there is a previous pointer for the specified coordinate
    while np.any(pathCurr == prev):
        pathCurr = prev[pathCurr]
        path.append(pathCurr)

    # IT IS NOT WORKING
    print(vision)
    print(path)

if __name__ == "__main__":
    load_dotenv(dotenv_path="./credentials.env")
    
    broker_address = os.environ.get("BROKER_ADDRESS")
    broker_port = int(os.environ.get("BROKER_PORT"))
    username = os.environ.get("USER_NAME")
    password = os.environ.get("PASSWORD")

    player = input("Enter your name: ")
    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id=player, userdata=None, protocol=paho.MQTTv5)
    
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    # name of lobby
    lobby_name = "TestLobby"
    # store 5x5 vision around player
    client.gamestate = None

    # subscribe to lobby topics
    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f"games/{lobby_name}/{player}/game_state")
    client.subscribe(f"games/{lobby_name}/scores")

    # join the lobby
    client.publish("new_game", json.dumps({"lobby_name":lobby_name,
                                            "team_name":"ATeam",
                                            "player_name" : player}))

    # flag to check if this client is hosting the game (publishing START)
    isStarting = True
    if input("Are you Hosting (Y) or Joining (any other input) the Game? ") != "Y":
        isStarting = False

    # block until clients wants to join
    while input("Join Game (Y)? ") != "Y":
        pass

    # start game
    if isStarting:
        print("STARTING!")
        time.sleep(1) # Wait a second to resolve game start
        client.publish(f"games/{lobby_name}/start", "START")
    
    # new thread to receive subscribed messages
    client.loop_start()

    # user movement input
    while True:
        time.sleep(1) # Wait a second to resolve game state
        step = input("Enter your move (UP/DOWN/LEFT/RIGHT)? ")
        if step in ["UP", "DOWN", "LEFT", "RIGHT"]:
            client.publish(f"games/{lobby_name}/{player}/move", step)




