from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

import yaml
import bcrypt
import paho.mqtt.client as mqtt

mqtt_broker = 'localhost'
mqtt_port = 1883
mqtt_client=mqtt.Client()

def f_login(client, userdata, message):

    print("Logged in", message)

def f_regis(client, userdata, message):
    print("Registered",message)
    # cursor = mysql.connection.cursor()
    # cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (email, password))
    # mysql.connection.commit()
    # cursor.close()

def f_congo(client, userdata, message):
    print("Congo", message)

sub_d={
    'login' : f_login,
    'register' : f_regis,
    'congo' : f_congo
}

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("MQTT broker connected")
        for topic, func in sub_d.items():
            mqtt_client.subscribe(topic)
            mqtt_client.message_callback_add(topic,func)
    else:
        print("Failed to connect to MQTT broker, return code %d\n", rc)

def on_disconnect(client, userdata, rc):
    print("Disconnected, return code %d\n", rc)
    mqtt_client.reconnect()


def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} {msg.payload.decode()}")

def init_mqtt():
    """MQTT client connections."""
    try:
        mqtt_client.connect(mqtt_broker,mqtt_port,60)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_disconnect = on_disconnect
        # mqtt_client.on_message = on_message
        print(f"init function {mqtt_client}")
        mqtt_client.loop_start()
    except Exception as err:
        print("Local mqtt Error in init_mqtt" + str(err))