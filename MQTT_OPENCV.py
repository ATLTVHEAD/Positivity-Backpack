# MQTT_OPENCV.py
# Description: Recieved Data from MQTT and Display the base64 image 
# Written by: Nate Damen
# Created on Feb 13th 2021

import cv2
import numpy as np
import paho.mqtt.client as mqtt
import base64
import time

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("stream_live")
    client.subscribe("screen_shot")
    #client.subscribe("viewer_click")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if (msg.topic == "screen_shot"):
        print(msg.topic)
        img = readb64(msg.payload)
        cv2.namedWindow ('screen', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty ('screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('screen',img)
        cv2.waitKey(1)
    else:
        print(msg.topic+" "+str(msg.payload))

def readb64(uri):
   nparr = np.frombuffer(base64.b64decode(uri), np.uint8)
   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   return img


if __name__ == "__main__":
    
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("192.168.1.106", 1883, 60) #change This
    mqttc.loop_start()
    toggle = True
    while(1):
        if(toggle):
            mqttc.publish("glove/gesture", "This is a test")
            toggle=False
        else:
            mqttc.publish("glove/gesture", "Wut Wut")
            toggle = True
        time.sleep(2)