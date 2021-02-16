import picamera
import picamera.array
import time
import cv2
from cv2 import aruco
import threading
import numpy as np

class RoboCam:
    continue_recording = False
    #Set up aruco dictionary & parameters
    aruco_dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)
    aruco_parameters = aruco.DetectorParameters_create()
    #Holds tags that are currently being seen
    current_seen = {}

    def __init__(self, framerate = 10, resolution = (640, 480)):
        #To initialise the camera
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = picamera.array.PiRGBArray(self.camera, size = self.camera.resolution)

        #To allow settings to apply
        time.sleep(0.1)
    
    def start_video_thread(self):
        thread = threading.Thread(target = self.capture_video, daemon = True)
        thread.start()

    def capture_video(self):
        self.continue_recording = True
        for frame in self.camera.capture_continuous(self.rawCapture, format = "bgr", use_video_port = True):
            image = frame.array

            #Image processing code
            self.current_seen = self.find_aruco_tags(image)

            #Erases current frame
            self.rawCapture.truncate(0)

            #Break the loop & clear current scene
            if self.capture_video is False:
                self.current_seen = {}
                break
            
    def find_aruco_tags(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners,ids,rejectedImgPoints = aruco.detectMarkers(gray, self.aruco_dictionary, parameters = self.aruco_parameters)
        #To take the the middle of each corner
        middles = [(np.mean([c[0][0], c[1][0], c[2][0], c[3][0]]), np.mean([c[0][1], c[1][1], c[2][1], c[3][1]])) for i in corners for c in i]
        if ids is None:
            return {}
        found_aruco_tags = {int(ids[i]):middles[i] for i in range(len(ids))}
        return found_aruco_tags