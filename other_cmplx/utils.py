from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import yaml
import bcrypt
import paho.mqtt.client as mqtt

from mqtt_local import mqtt_client
def publish(message, topic):
    mqtt_client.publish(topic, message)
    print(f"Published a {message} to topic: {topic}")
