#Modified by smartbuilds.io
#Date: 27.09.20
#Desc: This scrtipt script..



import cv2 as cv
import imutils
from imutils.video.pivideostream import PiVideoStream
import time
from datetime import datetime
import numpy as np

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference


class VideoCamera(object):
    def __init__(self, flip = False, file_type  = ".jpg", photo_string= "stream_photo", camera_index=0):
        self.vs = PiVideoStream(resolution=(640, 480), framerate=30).start()
        # self.vs = cv.VideoCapture(camera_index, cv.CAP_V4L2)
        # self.vs.set(cv.CAP_PROP_FOURCC,cv.VideoWriter_fourcc('M','J','P','G'))
        self.flip = flip # Flip frame vertically
        self.file_type = file_type # image type i.e. .jpg
        self.photo_string = photo_string # Name to save the photo
        # self.model = cv.dnn.readNetFromTensorflow('models/frozen_inference_graph.pb',
        #                              'models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')
        self.interpreter = make_interpreter('models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite')
        self.interpreter.allocate_tensors()
        self.labels = read_label_file('models/coco_labels.txt')
        self.inference_size = input_size(self.interpreter)

        self.classNames = {0: 'background',
              1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane', 6: 'bus',
              7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant',
              13: 'stop sign', 14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
              18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
              24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
              32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
              37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
              41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
              46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
              51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
              56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
              61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
              67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
              75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
              80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
              86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush'}


        time.sleep(2.0)
        
        # if not self.vs.isOpened():
        #     raise ValueError("Unable to open USB camera")
        
    def id_class_name(self, class_id):  # Only takes class_id
        for key, value in self.classNames.items():
            if class_id == key:
                return value



    def __del__(self):
        self.vs.stop()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):

        frame = self.vs.read()
        print('we have tried to read the frame')
        # print(self.vs)
        # if not ret:  # Check if frame was read successfully
        #     print("Error reading frame, check camera connection")
        #     print(ret)
        #     return None # Or raise an exception if needed
        # image_height, image_width, _ = frame.shape
        # self.model.setInput(cv.dnn.blobFromImage(frame, size=(300,300), swapRB=True))
        # output = self.model.forward()

        # for detection in output[0, 0, :, :]:
        #     confidence = detection[2]
        #     if confidence > .5:
        #         class_id = detection[1]
        #         class_name= self.id_class_name(class_id)
        #         print(str(str(class_id) + " " + str(detection[2])  + " " + class_name))
        #         box_x = detection[3] * image_width
        #         box_y = detection[4] * image_height
        #         box_width = detection[5] * image_width
        #         box_height = detection[6] * image_height
        #         cv.rectangle(frame, (int(box_x), int(box_y)), (int(box_width), int(box_height)), (23, 230, 210), thickness=1)
        #         cv.putText(frame,class_name ,(int(box_x), int(box_y+.05*image_height)),cv.FONT_HERSHEY_SIMPLEX,(.005*image_width),(0, 0, 255))
        cv2_im = frame

        cv2_im_rgb = cv.cvtColor(cv2_im, cv.COLOR_BGR2RGB)
        cv2_im_rgb = cv.resize(cv2_im_rgb, self.inference_size)
        print('trying to run inference')
        run_inference(self.interpreter, cv2_im_rgb.tobytes())
        print('we are running inference')
        objs = get_objects(self.interpreter, 0.5)[:3]
        cv2_im = append_objs_to_img(cv2_im, self.inference_size, objs, self.labels)

        
        ret, jpeg = cv.imencode('.jpg', cv2_im)
        if not ret:
            print("Error encoding frame as JPEG")
            return None 

        self.previous_frame = jpeg
        return jpeg.tobytes()

    def append_objs_to_img(cv2_im, inference_size, objs, labels):
        height, width, channels = cv2_im.shape
        scale_x, scale_y = width / inference_size[0], height / inference_size[1]
        for obj in objs:
            bbox = obj.bbox.scale(scale_x, scale_y)
            x0, y0 = int(bbox.xmin), int(bbox.ymin)
            x1, y1 = int(bbox.xmax), int(bbox.ymax)

            percent = int(100 * obj.score)
            label = '{}% {}'.format(percent, labels.get(obj.id, obj.id))

            cv2_im = cv.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
            cv2_im = cv.putText(cv2_im, label, (x0, y0+30),
                                cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
        return cv2_im

    # Take a photo, called by camera button
    def take_picture(self):
        ret, frame = self.flip_if_needed(self.vs.read())
        ret, image = cv.imencode(self.file_type, frame)
        today_date = datetime.now().strftime("%m%d%Y-%H%M%S") # get current time
        cv.imwrite(str(self.photo_string + "_" + today_date + self.file_type), frame)
    
    

    

