import sys
import cv2
import configparser

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi

class FaceRecognition(QMainWindow):
    count = 0
    face_id = 0
    db = 'db.ini'

    def __init__(self):
        super(FaceRecognition, self).__init__()
        loadUi('03_face_recognition.ui', self)
        self.image=None
        self.detectFaceButton.setCheckable(True)
        self.detectFaceButton.toggled.connect(self.detect_webcam_face)
        self.faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
        self.faceRecognizer.read('trainer/trainer.yml')
        self.face_Enabled = False
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.config = configparser.ConfigParser()
        self.config.read(self.db)
        self.startWebCam();

    def detect_webcam_face(self, status):
        if status:
            self.detectFaceButton.setText("Stop Detection")
            self.face_Enabled = True
        else:
            self.detectFaceButton.setText("Detect Face")
            self.face_Enabled = False

    def startWebCam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def update_frame(self):
        ret,self.image = self.capture.read()
        self.image = cv2.flip(self.image, 1)

        if (self.face_Enabled):
            detected_image = self.detect_face(self.image)
            self.displayImage(detected_image, 1)
        else:
            self.displayImage(self.image, 1)

    def detect_face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.faceDetector.detectMultiScale(gray, 1.2, 5, minSize=(90, 90))

        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w, y+h),(0,0,255),2)
            id, confidence = self.faceRecognizer.predict(gray[y:y + h, x:x + w])
            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence < 100):
                name = self.getNameFromDB(id)
                confidence = "  {0}%".format(round(100 - confidence))
            else:
                name = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))

            cv2.putText(img, str(name), (x + 5, y - 5), self.font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x + 5, y + h - 5), self.font, 1, (255, 255, 0), 1)
        return img

    def displayImage(self, img, window =1):
        qformat=QImage.Format_Indexed8
        if len(img.shape) == 3: #[0]rows, [1]=cols [2]=channels
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        #BGB>>RGB
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.webCamLabel.setPixmap(QPixmap.fromImage(outImage))
            self.webCamLabel.setScaledContents(True)

    def stopWebCam(self):
        self.timer.stop()

    def getNameFromDB(self, user_id):
        try:
            name = self.config['USERS'][str(user_id) + '_name']
            return name.split()[0]
        except:
            return "unknown"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceRecognition()
    window.setWindowTitle("Webcam Client Test")
    window.show()
    sys.exit(app.exec())
