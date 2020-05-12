from threading import Thread
import cv2
import math
from time import sleep
import nxt
import bluetooth
import nxt.bluesock
import nxt.usbsock

global motorX, motorY
FPS = 5
#setting up the nxt and the cascade classifiers
try:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    print("Attempting to connect to NXT...")
    b = nxt.bluesock.BlueSock('00:16:53:11:58:AB').connect()
    #b = nxt.usbsock.find_bricks(name="Dan's NXT")
    print("Connected!")
    print("Initializing motors...")
    motorX = nxt.Motor(b, nxt.PORT_A)
    motorY = nxt.Motor(b, nxt.PORT_B)
    print("Testing motors...")
    #motorX.run(50) #nunber from -100 to 100
    #motorY.run(50) 
    motorX.brake()
    motorY.brake()

except:
    print("Something went wrong")    
    quit()

class VideoStreamWidget(object):
    wScreen = 0 
    hScreen = 0
    p1 = []
    p2 = [wScreen, hScreen]
    lastKnown = ''
    face_present = False
    eyes_present = False

    turnX = 0
    turnY = 0
    multiplier = 50

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
        #self.motor_thread = Thread(target =self.send_control, args=())
        #self.motor_thread.daemon = True
        #self.motor_thread.start()

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
                    dist = [lastxPos-self.wScreen, self.hScreen-lastyPos ]
                    norm = math.sqrt(dist[0] ** 2 + dist[1] ** 2)
                    direction = [dist[0] / norm, dist[1] / norm]
                    bullet_vector = [direction[0] * math.sqrt(2), direction[1] * math.sqrt(2)]
                    #print(dist, norm, direction,    bullet_vector)
                    #print (bullet_vector)
                    font = cv2.FONT_HERSHEY_PLAIN
                    text = cv2.putText(gray, str(dist),(0,50), font, 1, (255,255,255), 2, cv2.LINE_AA)

                    #self.turnX = int((dist[0])/10) #* self.multiplier
                    #self.turnY = int((dist[1])/10) #* self.multiplier
                    self.turnX = dist[0]
                    self.turnY = dist[1]
                    print(self.turnX, self.turnY)
                    #self.send_control()
                    #if self.turnX != 0 and self.turnY != 0:
                    #    motorX.turn(100,30, False, 1, True) if self.turnX > 0 else motorX.turn(-100,45, False, 1, True)
                    #    motorY.turn(100,30, False, 1, True) if self.turnX > 0 else motorY.turn(-100,45, False, 1, True)


                except:
                    print("no work")
            else:
                print("last known: " + str(self.lastKnown))

            cv2.imshow('IP Camera Video Streaming', gray)


    def send_control(self):
        if self.turnX == 0 or self.turnY == 0:
            pass
        else:
            motorX.turn(70,50, False, 0, True) if self.turnX > 0 else motorX.turn(-70,50, False, 0, True)
            motorY.turn(70,50, False, 0, True) if self.turnY > 0 else motorY.turn(-70,50, False, 0, True)
        #print(self.turnX, self.turnY)


        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            motorX.idle()
            motorY.idle()
            self.capture.release()
            cv2.destroyAllWindows()
            quit()


if __name__ == '__main__':
    stream_link = 'http://10.232.127.140:8080/video'
    #stream_link = 0
    tracking = VideoStreamWidget(stream_link)
    print("Attempting to connect to stream.")
    while True:
        try:
            tracking.calculate_frame()
            #tracking.send_control()
            motorX.turn(70,50, False, 0, True) if VideoStreamWidget.turnX > 0 else motorX.turn(-70,50, False, 0, True)
            motorY.turn(70,50, False, 0, True) if VideoStreamWidget.turnY > 0 else motorY.turn(-70,50, False, 0, True)
            #sleep(1/FPS)

        except AttributeError:
            print("Error connecting.")


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