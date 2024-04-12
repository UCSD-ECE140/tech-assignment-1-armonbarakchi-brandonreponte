import paho.mqtt.client as paho
from paho import mqtt
import time
import random

client1 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="publisher1", userdata=None, protocol=paho.MQTTv5)
client2 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="publisher2", userdata=None, protocol=paho.MQTTv5)

# enable TLS for secure connection
client1.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client2.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

# set username and password
client1.username_pw_set("beans", "Beans4Life")
client2.username_pw_set("beans", "Beans4Life")

# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client1.connect("5e411a7e06134539ac30e0ebb5aff733.s1.eu.hivemq.cloud", 8883)
client2.connect("5e411a7e06134539ac30e0ebb5aff733.s1.eu.hivemq.cloud", 8883)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid), client.random_number)

if __name__ == "__main__":
    client1.on_publish = on_publish
    client2.on_publish = on_publish

    client1.loop_start()
    client2.loop_start()

    client1.random_number = 0
    client2.random_number = 0

    while True:
        client1.random_number = random.randint(1, 100)
        client2.random_number = random.randint(1, 100)
        client1.publish("challenge1/cool", payload=client1.random_number, qos=1)
        client2.publish("challenge1/beans", payload=client2.random_number, qos=1)
        time.sleep(3)

