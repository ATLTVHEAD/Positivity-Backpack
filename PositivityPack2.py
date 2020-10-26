# PositivityPack.py
# Description: Recieved Data from ESP32 Micro via the AGRB-Training-Data-Capture.ino file, make gesture prediction and tell it to twitch
#   Display an image that changes according to what is said in twitch chat or after 30 seconds    
# Written by: Nate Damen
# Created on July 13th 2020
# Updated on OCT 24th 2020


import socket
import cfg
import re
import time
import random
import numpy as np 
import pandas as pd 
import datetime
import os, os.path
import tensorflow as tf
import serial
import cv2
import traceback

#PORT = "/dev/ttyUSB0"
#PORT = "/dev/ttyUSB1"
PORT = "COM5"

serialport = None
serialport = serial.Serial(PORT, 115200, timeout=0.05)

#load Model
model = tf.keras.models.load_model('../Atltvhead-Gesture-Recognition-Bracer/Model/cnn_model2_half.h5')

# These commands set the screen to full on whatever display is being used. Don't use if you dont mind it being in a window that can move around
cv2.namedWindow("PositiveMessage", cv2.WND_PROP_FULLSCREEN)
#cv2.moveWindow("PositiveMessage", screen.x - 1, screen.y - 1)
cv2.setWindowProperty("PositiveMessage", cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

#loading some of the images in and resizing them to the dimensions of the screen, which isn't really needed but hey whatevas
message1= cv2.imread('photos/img_2.1.1.png')
message1= cv2.resize(message1,(1024,600),interpolation = cv2.INTER_AREA)
message2= cv2.imread('photos/img_2.1.2.png')
message2= cv2.resize(message2,(1024,600),interpolation = cv2.INTER_AREA)
message3= cv2.imread('photos/img_2.1.3.png')
message3= cv2.resize(message3,(1024,600),interpolation = cv2.INTER_AREA)
message4= cv2.imread('photos/img_2.1.4.png')
message4= cv2.resize(message4,(1024,600),interpolation = cv2.INTER_AREA)
message5= cv2.imread('photos/img_2.1.5.png')
message5= cv2.resize(message5,(1024,600),interpolation = cv2.INTER_AREA)
message6= cv2.imread('photos/img_2.1.6.png')
message6= cv2.resize(message6,(1024,600),interpolation = cv2.INTER_AREA)
message7= cv2.imread('photos/img_2.1.7.png')
message7= cv2.resize(message7,(1024,600),interpolation = cv2.INTER_AREA)
message8= cv2.imread('photos/img_2.1.8.png')
message8= cv2.resize(message8,(1024,600),interpolation = cv2.INTER_AREA)
message9= cv2.imread('photos/img_2.1.9.png')
message9= cv2.resize(message9,(1024,600),interpolation = cv2.INTER_AREA)
message10= cv2.imread('photos/img_2.1.10.png')
message10= cv2.resize(message10,(1024,600),interpolation = cv2.INTER_AREA)
message11= cv2.imread('photos/img_2.1.11.png')
message11= cv2.resize(message11,(1024,600),interpolation = cv2.INTER_AREA)
message12= cv2.imread('photos/img_2.1.12.png')
message12= cv2.resize(message12,(1024,600),interpolation = cv2.INTER_AREA)
message13= cv2.imread('photos/img_2.1.13.png')
message13= cv2.resize(message13,(1024,600),interpolation = cv2.INTER_AREA)
message14= cv2.imread('photos/img_2.1.14.png')
message14= cv2.resize(message14,(1024,600),interpolation = cv2.INTER_AREA)
message15= cv2.imread('photos/img_2.1.15.png')
message15= cv2.resize(message15,(1024,600),interpolation = cv2.INTER_AREA)
message16= cv2.imread('photos/img_2.1.16.png')
message16= cv2.resize(message16,(1024,600),interpolation = cv2.INTER_AREA)
message17= cv2.imread('photos/img_2.1.17.png')
message17= cv2.resize(message17,(1024,600),interpolation = cv2.INTER_AREA)
message18= cv2.imread('photos/img_2.1.18.png')
message18= cv2.resize(message18,(1024,600),interpolation = cv2.INTER_AREA)
message19= cv2.imread('photos/img_2.1.19.png')
message19= cv2.resize(message19,(1024,600),interpolation = cv2.INTER_AREA)
message20= cv2.imread('photos/img_2.1.20.png')
message20= cv2.resize(message20,(1024,600),interpolation = cv2.INTER_AREA)
message21= cv2.imread('photos/img_2.1.21.png')
message21= cv2.resize(message21,(1024,600),interpolation = cv2.INTER_AREA)
message22= cv2.imread('photos/img_2.1.22.png')
message22= cv2.resize(message22,(1024,600),interpolation = cv2.INTER_AREA)
message23= cv2.imread('photos/img_2.1.23.png')
message23= cv2.resize(message23,(1024,600),interpolation = cv2.INTER_AREA)


messages = (
    message1,
    message2,
    message3,
    message4,
    message5,
    message6,
    message7,
    message8,
    message9,
    message10,
    message11,
    message12,
    message13,
    message14,
    message15,
    message16,
    message17,
    message18,
    message19,
    message20,
    message21,
    message22,
    message23)

messages_text = (
    "Fuel the Future with Love",
    "Stay True to your Values",
    "Don't Give Up Friend!",
    "You don't have to be perfect.",
    "The future is inside of us",
    "We are friends :)",
    "We are a community",
    "We are all neighbors",
    "We are there for one another",
    "We are in this together",
    "You are a gift",
    "Nice Moves!",
    "you look great today :)",
    "You've Got This!",
    "You are a beautiful human",
    "Don't forget to breathe",
    "We are united!",
    "Open Mind, Open Heart",
    "Keep It Weird!",
    "Everything will end up alright, even if it's painful in this moment",
    "You are loving awareness",
    "Be Yourself!",
    "There is power in play!")

#Creating a variable that we can swap messages to
displayimage = message1

#Creating our socket and passing on info for twitch
sock = socket.socket()
sock.connect((cfg.HOST,cfg.PORT))
sock.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
sock.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
sock.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))
sock.setblocking(0)

#handling of some of the string characters in the twitch message
chat_message = re.compile(r"^:\w+!\w+@\w+.tmi.twitch.tv PRIVMSG #\w+ :")

#Lets create a new function that allows us to chat a little easier. Create two variables for the socket and messages to be passed in and then the socket send function with proper configuration for twitch messages. 
def chat(s,msg):
    s.send("PRIVMSG {} :{}\r\n".format(cfg.CHAN,msg).encode("utf-8"))

#The next two functions allow for twitch messages from socket receive to be passed in and searched to parse out the message and the user who typed it. 
def getMSG(r):
    mgs = chat_message.sub("", r)
    return mgs


def getUSER(r):
    try:
        user=re.search(r"\w+",r).group(0)
    except AttributeError:
        user ="tvheadbot"
        print(AttributeError)
    return user


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

# header for the incomming data
header = ["deltaTime","Acc_X","Acc_Y","Acc_Z","Gyro_X","Gyro_Y","Gyro_Z"]

#Create a way to see the length of the data incomming, needs to be 380 points. Used for testing incomming data
#def dataFrameLenTest(data):
#    df=pd.DataFrame(data,columns=header)
#    x=len(df[['Acc_X','Acc_Y','Acc_Z']].to_numpy())
#    print(x)
#    return x

#Create a pipeline to process incomming data for the model to read and handle
def data_pipeline(data_a):
    tensor_set = tf.data.Dataset.from_tensor_slices((data_a[:,:,1:4]))
    tensor_set_cnn = tensor_set.map(reshape_function)
    tensor_set_cnn = tensor_set_cnn.batch(192)
    return tensor_set_cnn

def gesture_Handler(sock, rw, data, dataholder, dataCollecting, gesture, old_gesture):
    dataholder = np.array(get_imu_data())
    if dataholder.all() != None:
        #print(dataholder)
        dataCollecting = True
        data[0, rw, :] = dataholder
        rw += 1
    if dataholder.all() == None and dataCollecting == True:
        #print(data.itemsize * data.size)
        if row == 380:
            prediction = np.argmax(model.predict(data_pipeline(data)), axis=1)
            gesture=gest_id[prediction[0]]
        rw = 0
        dataCollecting = False
    return rw, gesture, old_gesture, dataCollecting


def message_changer(displayimage, messa):
    global messages_text
    global messages
    #otherwise get the user and message
    mess= getMSG(messa)
    # If the message matches one of the cammands do something
    if "love" in mess.strip() or "love" == mess.strip():
        #Sets the image to be displayed to our image 1, do the same for every message 
        displayimage = messages[0]
    elif "values" in mess.strip():
        displayimage = messages[1]
    elif "dont" in mess.strip():
        displayimage = messages[2]
    elif "perect" in mess.strip():
        displayimage = messages[3]
    elif "future" in mess.strip():
        displayimage = messages[4]
    elif "friends" in mess.strip():
        displayimage = messages[5]
    elif  "community" in mess.strip():
        displayimage = messages[6]
    elif "neighbor" in mess.strip():
        displayimage = messages[7]
    elif "another" in mess.strip():
        displayimage = messages[8]
    elif "together" in mess.strip():
        displayimage = messages[9]
    elif "gift" in mess.strip():
        displayimage = messages[10]
    elif "nice" in mess.strip():
        displayimage = messages[11]
    elif "look"in mess.strip():
        displayimage = messages[12]
    elif "got" in mess.strip():
        displayimage = messages[13]
    elif "beautiful" in mess.strip():
        displayimage = messages[14]
    elif "breathe" in mess.strip():
        displayimage = messages[15]
    elif "united" in mess.strip():
        displayimage = messages[16]
    elif "heart" in mess.strip():
        displayimage = messages[17]
    elif "weird" in mess.strip():
        displayimage = messages[18]
    elif "okay" in mess.strip():
        displayimage = messages[19]
    elif "aware" in mess.strip():
        displayimage = messages[20]
    elif "be" in mess.strip():
        displayimage = messages[21]
    elif "play" in mess.strip():
        displayimage = messages[22]
    elif "TVHEAD MAGIC" in mess.strip():
        displayimage = random.choice(messages)
    elif "COMPUTER VISION" in mess.strip():
        displayimage = random.choice(messages)
    elif "Terminal_VIEW" in mess.strip():
        displayimage = random.choice(messages)
    elif "Sending Positive Message" in mess.strip():
        displayimage = random.choice(messages)
        chat(sock, messages_text[messages.index(displayimage)])
    return displayimage



if __name__ == "__main__":
    #define Gestures, current data, temp data holder
    gest_id = {0:'wave_mode', 1:'fist_pump_mode', 2:'random_motion_mode', 3:'speed_mode', 4:'pumped_up_mode'}
    data = np.zeros(shape=(1,380,7))
    dataholder = np.zeros(shape=(1,7))
    row = 0
    dataCollecting = False
    gesture = ''
    old_gesture = ''
    t = 0
    ot = 0

    #flush the serial port
    serialport.flush()
    while True:
        t=time.time()
        try:
            #listen to twitch messages incoming
            response = sock.recv(1024).decode("utf-8")
        except:
            row, gesture, old_gesture, dataCollecting = gesture_Handler(sock,row,data,dataholder,dataCollecting,gesture,old_gesture)
            if gesture != old_gesture:
                chat(sock,'!' + gesture)
                #print(gesture)    
                old_gesture=gesture        
            if t-ot > 30:
                displayimage = random.choice(messages)
                ot=t
                cv2.imshow("PositiveMessage",displayimage)
                cv2.waitKey(1)
            continue
        else:
            if len(response)==0:
                print('orderly shutdown on the server end')
                sock = socket.socket()
                sock.connect((cfg.HOST,cfg.PORT))
                sock.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
                sock.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
                sock.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))
                sock.setblocking(0)
            else:
                #print(response)
                if response == "PING :tmi.twitch.tv\r\n":
                    sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                else:
                    displayimage = message_changer(displayimage,response)
                    cv2.imshow("PositiveMessage",displayimage)
                    cv2.waitKey(1)
    
    #Closes all the windows
    cv2.destroyAllWindows()