from threading import Thread
import cv2
import math

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

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
        # calculate the 
        VideoStreamWidget.wScreen = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH) /2)
        VideoStreamWidget.hScreen = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT) /2)
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
            
            p2 = VideoStreamWidget.p2
            if len(faces) != 0:
                VideoStreamWidget.face_present = True
                
                for(x, y, w, h) in faces:
                    xPos = int((w/2)+x)
                    yPos = int((h/2)+y)

                    cv2.line(gray, (xPos,yPos), (VideoStreamWidget.wScreen, VideoStreamWidget.hScreen), (255,255,255), 5)
                    cv2.rectangle(gray, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    roi_gray = gray[y:y+h, x:x+w]

                    eyes = eye_cascade.detectMultiScale(roi_gray)
                    if len(eyes) != 0:
                        VideoStreamWidget.eyes_present = True
                        for (ex,ey,ew,eh) in eyes:
                            cv2.rectangle(roi_gray,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                            VideoStreamWidget.eyes_present = True 
                    else:
                        VideoStreamWidget.eyes_present = False

                VideoStreamWidget.lastKnown = faces 

            else: 
                VideoStreamWidget.face_present = False

            if VideoStreamWidget.face_present and VideoStreamWidget.eyes_present:
                try:
                    for(x, y, w, h) in VideoStreamWidget.lastKnown:
                        xPos = int((w/2)+x)
                        yPos = int((h/2)+y)
                        lastxPos = xPos
                        lastyPos = yPos
                    
                    # dist calculates a vector in a c format of a graph
                    dist = [lastxPos-VideoStreamWidget.wScreen, VideoStreamWidget.hScreen-lastyPos ]
                    norm = math.sqrt(dist[0] ** 2 + dist[1] ** 2)
                    direction = [dist[0] / norm, dist[1] / norm]
                    bullet_vector = [direction[0] * math.sqrt(2), direction[1] * math.sqrt(2)]
                    #print(dist, norm, direction, bullet_vector)
                    print (bullet_vector)

                except:
                    print("no work")
            else:
                print("no face detected")
        
            cv2.imshow('IP Camera Video Streaming', gray)

        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)

if __name__ == '__main__':
    #sstream_link = 'http://10.232.127.140:8080/video'
    stream_link = 0
    video_stream_widget = VideoStreamWidget(stream_link)
    while True:
        try:
            video_stream_widget.calculate_frame()
        except AttributeError:
            pass


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