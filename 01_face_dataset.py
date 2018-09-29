import sys
import cv2
import os
import configparser

from os import path
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi

class FaceDataset(QMainWindow):
    count = 0
    faceDetectionEnabled = False
    addToDatasetEnabled = False
    isDataAdded = False
    face_id =""
    db = 'db.ini'

    def __init__(self):
        super(FaceDataset, self).__init__()
        loadUi('01_face_dataset.ui', self)
        self.image=None
        self.addToDatasetButton.setCheckable(True)
        self.addToDatasetButton.toggled.connect(self.detect_webcam_face)
        self.faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.faceDetectionEnabled = True
        self.startWebCam()

    def detect_webcam_face(self, status):
        self.face_id = self.studentIDText.text()
        self.folderName = "user" + self.face_id
        self.folderPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dataset/" + self.folderName)
        if not os.path.exists(self.folderPath):
            os.makedirs(self.folderPath)

        if status:
            self.addToDatasetButton.setText("Stop Progress")
            self.statusLabel.setText("")
            self.addToDatasetEnabled = True
            self.isDataAdded = False
        else:
            self.addToDatasetButton.setText("Add to Dataset")
            self.addToDatasetEnabled = False
            self.statusLabel.setText("")

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

        if self.faceDetectionEnabled:
            detected_image = self.detect_face(self.image)
            self.displayImage(detected_image, 1)
        else:
            self.displayImage(self.image, 1)

    def detect_face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.faceDetector.detectMultiScale(gray, 1.2, 5, minSize=(90, 90))

        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w, y+h),(0,0,255),2)
            if self.addToDatasetEnabled:
                self.count += 1
                if self.count <= 30:
                    # Save the captured image into the datasets folder
                    cv2.imwrite(self.folderPath + "/User." + self.face_id + "." + str(self.count) + ".jpg",
                                gray[y:y + h, x:x + w])
                elif not self.isDataAdded:
                    self.isDataAdded = True
                    self.addDatatoDB()
                    self.statusLabel.setText("<font color='Blue'>Dataset Added</font>")
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

    def addDatatoDB(self):
        config = configparser.ConfigParser()
        if path.exists(self.db):
            config.read(self.db)
        else:
            config['USERS'] = {}
        studentName = self.studentNameText.text()
        config['USERS'][self.face_id + '_name'] = studentName.strip()
        studentEmail = self.studentEmailText.text()
        config['USERS'][self.face_id + '_email'] = studentEmail.strip()
        with open('db.ini', 'w') as configfile:
            config.write(configfile)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceDataset()
    window.setWindowTitle("Face Dataset")
    window.show()
    sys.exit(app.exec())
