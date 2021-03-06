from threading import Thread
from time import sleep
import cv2, math

FPS = 24

try:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
except:
    print("Cannot open Haar cascade files")

class VideoStreamWidget(object):
    wScreen = 0 
    hScreen = 0
    p1 = []
    p2 = [wScreen, hScreen]
    lastKnown = ''
    face_present = False
    eyes_present = False
    def __init__(self, src=0):
        # Create a VideoCapture object
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_FPS,24)
        # calculate the 
        self.wScreen = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH) /2)
        self.hScreen = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT) /2)
        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()

    def calculate_frame(self):
        
        # Display frames in main program
        if self.status:
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5) 
            
            p2 = self.p2
            if len(faces) != 0:
                self.face_present = True
                
                for(x, y, w, h) in faces:
                    xPos = int((w/2)+x)
                    yPos = int((h/2)+y)

                    cv2.line(gray, (xPos,yPos), (self.wScreen, self.hScreen), (255,255,255), 5)
                    cv2.rectangle(gray, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    roi_gray = gray[y:y+h, x:x+w]

                    eyes = eye_cascade.detectMultiScale(roi_gray)
                    if len(eyes) != 0:
                        self.eyes_present = True
                        for (ex,ey,ew,eh) in eyes:
                            cv2.rectangle(roi_gray,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                            self.eyes_present = True 
                    else:
                        self.eyes_present = False

                self.lastKnown = faces 

            else: 
                self.face_present = False

            if self.face_present and self.eyes_present:
                try:
                    for(x, y, w, h) in self.lastKnown:
                        xPos = int((w/2)+x)
                        yPos = int((h/2)+y)
                        lastxPos = xPos
                        lastyPos = yPos
                    
                    # dist calculates a vector in a c format of a graph
                    dist = [lastxPos - self.wScreen, self.hScreen -lastyPos]
                    norm = math.sqrt(dist[0] ** 2 + dist[1] ** 2)
                    direction = [dist[0] / norm, dist[1] / norm]
                    bullet_vector = [direction[0] * math.sqrt(2), direction[1] * math.sqrt(2)]
                    #print(dist, norm, direction,    bullet_vector)
                    #print (bullet_vector)
                    font = cv2.FONT_HERSHEY_PLAIN
                    text = cv2.putText(gray, str(dist),(0,50), font, 1, (255,255,255), 2, cv2.LINE_AA)

                except:
                    print("no work")
            else:
                print("last known: " + str(self.lastKnown))

            cv2.imshow('IP Camera Video Streaming', gray)

        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)

if __name__ == '__main__':
    #stream_link = 'http://10.232.127.140:8080/video'q
    stream_link = 0
    video_stream_widget = VideoStreamWidget(stream_link)
    while True:
        try:
            video_stream_widget.calculate_frame()
            sleep(1/FPS)
        except AttributeError:
            print("error")


# add in that face will only be detected if the eyes are present. without eyes, face detection is cancelled


# Vector calculation
# https://stackoverflow.com/questions/17332759/finding-vectors-with-2-points

# line function
# https://docs.opencv.org/2.4/modules/core/doc/drawing_functions.html


# Multithreading
#https://stackoverflow.com/questions/55828451/video-streaming-from-ip-camera-in-python-using-opencv-cv2-videocapture


# Haar cascade face code
# https://towardsdatascience.com/face-detection-in-2-minutes-using-opencv-python-90f89d7c0f81

# Haar cascade eyes code
# https://pythonprogramming.net/haar-cascade-face-eye-detection-python-opencv-tutorial/