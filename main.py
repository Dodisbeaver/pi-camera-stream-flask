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

pi_camera = VideoCamera(flip=False) # flip pi camera if upside down.
# def signal_handler(sig, frame):
#     print('Caught Ctrl+C, shutting down...')
#     # Add your cleanup code here:
#     if pi_camera:  # Assuming you have a camera_object 
#         pi_camera.release()  # Release the camera
#     # Close any other resources (files, connections, etc.)
#     sys.exit(0)  # Exit gracefully

# signal.signal(signal.SIGINT, signal_handler)
# App Globals (do not edit)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') #you can customze index.html here

def gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()

        if frame is not None:  
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            print('Sleeping')
            time.sleep(2.0)  # Short delay if no frame is available
        # frame = camera.get_frame()
        # yield (b'--frame\r\n'
        #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

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
