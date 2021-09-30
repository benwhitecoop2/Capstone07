import numpy as np
from cv2 import cv2, data
import threading

class facial_detection(threading.Thread):
    # url is the url of the target image to scan 
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url
        self.return_ = None
    def run(self):
        #print("Starting Thread...")
        self.return_ = detect_face(self.url)
        #print("Exiting Thread...")
    def join(self):
        threading.Thread.join(self)
        return self.return_

def detect_face(url):

    urlSuffix = ['.jpg', '.jpeg', '.png']
    scale = 1.03
    neighbors = 15

    face_cascade = cv2.CascadeClassifier(data.haarcascades + 'haarcascade_frontalface_alt2.xml')

    img = cv2.imread(url)

    try:

        faces = face_cascade.detectMultiScale(img, scaleFactor=scale, minNeighbors=neighbors)

        if (len(faces) > 0):
            for (x, y, width, height) in faces:
                cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 0), 2)
            
            for suffix in urlSuffix:
                if (url.endswith(suffix)):
                    url = url[:-len(suffix)]
                    url = url + f'_alt{suffix}'
            
            cv2.imwrite(url, img)

    except Exception as e:
        return(f'{__name__} Has exception: {e}', 0)

    return (url, len(faces))

if __name__ == "__main__":
    faceDetect_thread = facial_detection('./faceExamples/group2.jpg')
    faceDetect_thread.start()
    result = faceDetect_thread.join()
    print(f'Saved at: {result[0]}\nNumber of faces found: {result[1]}')
    #os.kill(os.getpid(), signal.SIGTERM)