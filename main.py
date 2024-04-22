#Modified by smartbuilds.io
#Date: 27.09.20
#Desc: This web application serves a motion JPEG stream
# main.py
# import the necessary packages
from flask import Flask, render_template, Response, request, send_from_directory
from camera import VideoCamera
import os
import time
import signal
import sys
import pygame
import threading

pi_camera = VideoCamera(flip=False) # flip pi camera if upside down.

pygame.mixer.init()

sounds = {
    1: ["AUDIO/1.1.wav", "AUDIO/1.2.wav", "AUDIO/1.3.wav"],
    2: ["AUDIO/2.1.wav", "AUDIO/2.2.wav", "AUDIO/2.3.wav"],
    3: ["AUDIO/3.1.wav", "AUDIO/3.2.wav", "AUDIO/3.3.wav"],
    4: ["AUDIO/4.1.wav", "AUDIO/4.2.wav", "AUDIO/4.3.wav"],
    5: ["AUDIO/5.1.wav", "AUDIO/5.2.wav", "AUDIO/5.3.wav"],
    6: ["AUDIO/6.1.wav", "AUDIO/6.2.wav", "AUDIO/6.3.wav"],
    7: ["AUDIO/7.1.wav", "AUDIO/7.2.wav", "AUDIO/7.3.wav"]
}

# Load the sounds
for section, filenames in sounds.items():
    for filename in filenames:
        sounds[section][filenames.index(filename)] = pygame.mixer.Sound(filename)


def signal_handler(sig, frame):
    print('Caught Ctrl+C, shutting down...')
    # Add your cleanup code here:
    if pi_camera:  # Assuming you have a camera_object 
        pi_camera.release()  # Release the camera
    # Close any other resources (files, connections, etc.)
    sys.exit(0)  # Exit gracefully

signal.signal(signal.SIGINT, signal_handler)
# App Globals (do not edit)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') #you can customze index.html here

def gen(camera):
    #get camera frame
    can_play = True
    frames = 0
    while True:
        frame, person_detected = camera.get_frame()
        frames += 1
        print(frames)
        if frames == 100:
            can_play = True
        if frame is not None:  
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            time.sleep(0.1)  # Short delay if no frame is available
        # frame = camera.get_frame()
        # yield (b'--frame\r\n'
        #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if person_detected and can_play:
            can_play = False
            frames = 0
            threading.Thread(target=say_something, args=(1, 2)).start()
def say_something(phrase=1, version=1):
    
    sound_channel = pygame.mixer.Channel(0)  # Use a channel for playback
    sound_channel.play(sounds[phrase][version])



@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Take a photo when pressing camera button
@app.route('/picture')
def take_picture():
    pi_camera.take_picture()
    return "None"


if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=False)
