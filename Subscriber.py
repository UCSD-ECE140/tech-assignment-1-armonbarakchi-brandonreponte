import paho.mqtt.client as paho
from paho import mqtt

receiver = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="receiver", userdata=None, protocol=paho.MQTTv5)

receiver.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
receiver.username_pw_set("beans", "Beans4Life")

receiver.connect("5e411a7e06134539ac30e0ebb5aff733.s1.eu.hivemq.cloud", 8883)

# subscribe to all topics of encyclopedia by using the wildcard "#"
receiver.subscribe("challenge1/#", qos=1)
