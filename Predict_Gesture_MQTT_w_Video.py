# Predict_Gesture.py
# Description: Recieved Data from ESP32 Micro via the AGRB-Training-Data-Capture.ino file, make gesture prediction  
# Written by: Nate Damen
# Created on JAN 29th 2021

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

PORT = "/dev/ttyUSB0"
#PORT = "/dev/ttyUSB1"
#PORT = "COM8"

serialport = None
serialport = serial.Serial(PORT, 115200, timeout=0.05)

#load Model
model = tf.keras.models.load_model('../Atltvhead-Gesture-Recognition-Bracer/Model/cnn_model2_half.h5')

# These commands set the screen to full on whatever display is being used. Don't use if you dont mind it being in a window that can move around
cv2.namedWindow("PositiveMessage", cv2.WND_PROP_FULLSCREEN)
#cv2.moveWindow("PositiveMessage", screen.x - 1, screen.y - 1)
cv2.setWindowProperty("PositiveMessage", cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("stream_live")
    client.subscribe("screen_shot")
    client.subscribe("viewer_click")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if (msg.topic == "screen_shot"):
        print(msg.topic)
        cv2.imshow("PositiveMessage", stringToRGB(msg.payload))
        cv2.waitKey(1)    
    else:
        print(msg.topic+" "+str(msg.payload))

# Take in base64 string and return cv image
def stringToRGB(base64_string):
    imgdata = base64.b64decode(str(base64_string))
    im_arr = np.frombuffer(imgdata, dtype=np.uint8)  # im_arr is one-dim Numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    return img


#Get Data from imu. Waits for incomming data and data stop
def get_imu_data():
    global serialport
    if not serialport:
        # open serial port
        serialport = serial.Serial(PORT, 115200, timeout=0.05)
        # check which port was really used
        print("Opened", serialport.name)
        # Flush input
        time.sleep(3)
        serialport.readline()

    # Poll the serial port
    line = str(serialport.readline(),'utf-8')
    if not line:
        return None
 
    vals = line.replace("Uni:", "").strip().split(',')
 
    if len(vals) != 7:
        return None
    try:
        vals = [float(i) for i in vals]
    except ValueError:
        return ValueError
 
    return vals

# Create Reshape function for each row of the dataset
def reshape_function(data):
    reshaped_data = tf.reshape(data, [-1, 3, 1])
    return reshaped_data


#Create a pipeline to process incomming data for the model to read and handle
def data_pipeline(data_a):
    tensor_set = tf.data.Dataset.from_tensor_slices((data_a[:,:,1:4]))
    tensor_set_cnn = tensor_set.map(reshape_function)
    tensor_set_cnn = tensor_set_cnn.batch(192)
    return tensor_set_cnn

def gesture_Handler(rw, data, dataholder, dataCollecting, gesture, old_gesture):
    dataholder = np.array(get_imu_data())
    if dataholder.all() != None:
        #print(dataholder)
        dataCollecting = True
        data[0, rw, :] = dataholder
        rw += 1
        if rw > 380:
            rw = 380
    if dataholder.all() == None and dataCollecting == True:
        if rw == 380:
            prediction = np.argmax(model.predict(data_pipeline(data)), axis=1)
            gesture=gest_id[prediction[0]]
            gc.collect()
        rw = 0
        dataCollecting = False
    return rw, gesture, old_gesture, dataCollecting


if __name__ == "__main__":
    
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("192.168.1.106", 1883, 60) #change This
    mqttc.loop_start()

    #define Gestures, current data, temp data holder, a first cylce boolean,
    gest_id = {0:'wave_mode', 1:'fist_pump_mode', 2:'random_motion_mode', 3:'speed_mode', 4:'pumped_up_mode'}
    data = np.zeros(shape=(1,380,7))
    dataholder = np.zeros(shape=(1,7))
    row = 0
    dataCollecting = False
    gesture = ''
    old_gesture = ''

    #flush the serial port
    time.sleep(3)
    serialport.readline()

    while(1):
        t=time.time()
        row, gesture, old_gesture, dataCollecting = gesture_Handler(row,data,dataholder,dataCollecting,gesture,old_gesture)
        if gesture != old_gesture:
            print(gesture)
            mqttc.publish("glove/gesture", gesture)
            old_gesture=gesture        
        
