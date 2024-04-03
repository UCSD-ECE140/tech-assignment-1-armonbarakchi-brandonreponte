import paho.mqtt.client as paho
from paho import mqtt
import time

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


while True:
    time.sleep(3)
    client1.publish("challenge1/cool", payload="hot", qos=1)
    client2.publish("challenge1/beans", payload="hot", qos=1)

