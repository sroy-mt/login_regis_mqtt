#install the following
'''
pip install paho-mqtt
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients
mosquitoo
'''
import paho.mqtt.client as mqtt # type: ignore
import time
# MQTT settings
MQTT_BROKER = '127.0.0.1'
MQTT_PORT = 1883
MQTT_TOPIC = 'flask/mqtt'
# Initialize the MQTT client
mqtt_client = mqtt.Client()
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc)) #3
    client.subscribe(MQTT_TOPIC) #subscription part
    print(f'subscribed to {MQTT_TOPIC}') #4
mqtt_client.on_connect = on_connect
def run_mqtt_client():
    print('inside run_mqtt_client function') #2
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    # mqtt_client.loop_forever()  #subscription part
def publish_message(topic, message):
    mqtt_client.publish(topic, message)
def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()} on topic {msg.topic}")
#subscription part
mqtt_client.on_message = on_message
print('starting the app') #1
# Start the MQTT client
run_mqtt_client()
for i in range(10):
    message = f'localhost : {i}'
    print(f'sending message... :{i} : {message}') #5
    publish_message(MQTT_TOPIC, message)
    time.sleep(1)  # Add a small delay between messages