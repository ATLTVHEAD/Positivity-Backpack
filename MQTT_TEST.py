import cfg
import numpy as np 
import paho.mqtt.client as mqtt
import datetime
import re
import os, os.path
import time
import random
import tensorflow as tf
import serial
import traceback
import gc
import cv2
import base64
import numpy as np



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("stream_live")
    #client.subscribe("screen_shot")
    #client.subscribe("viewer_click")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #if (msg.topic == "screen_shot"):
    #    print(msg.topic)
    #    cv2.imshow("PositiveMessage", stringToRGB(msg.payload))
    #   cv2.waitKey(1)    
    #else:
    #    print(msg.topic+" "+str(msg.payload))
    print(msg.topic+" "+str(msg.payload))



if __name__ == "__main__":
    
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("192.168.1.106", 1883, 60) #change This
    mqttc.loop_start()
    
    while(1):
        mqttc.publish("glove/gesture", "This is a test")
        time.sleep(2)
