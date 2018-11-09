import sys
import cv2
import os
import configparser

from os import path
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from FaceDB import FaceDB


class FaceDataSet(QMainWindow):

    faceDetectionEnabled = True
    db = 'db.ini'
    faceDB = FaceDB()

    def __init__(self):
        super(FaceDataSet, self).__init__()
        loadUi('01_face_dataset.ui', self)
        self.faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.addToDatasetButton.clicked.connect(self.detect_webcam_face)
        self.reset_counters()
        self.start_web_cam()

    def reset_counters(self):
        self.count = 0
        self.addToDatasetEnabled = False
        self.isOpenCVDataAdded = False
        self.isOpenFaceDataAdded = False
        self.openFaceImg = None
        self.face_id = ""

    def detect_webcam_face(self):
        self.reset_counters()

        self.face_id = self.studentIDText.text()
        self.folderName = "user" + self.face_id
        self.folderPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dataset/" + self.folderName)
        if not os.path.exists(self.folderPath):
            os.makedirs(self.folderPath)

        self.addToDatasetButton.setText("Progress")
        self.statusLabel.clear()
        self.pictureLabel.clear()
        self.statusLabel.repaint()
        self.pictureLabel.repaint()

        self.addToDatasetEnabled = True

    def start_web_cam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def update_frame(self):
        ret, image = self.capture.read()
        image = cv2.flip(image, 1)

        if self.faceDetectionEnabled:
            detected_image = self.detect_face(image)
            self.display_image(detected_image, 1)
        else:
            self.display_image(image, 1)

    def detect_face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.faceDetector.detectMultiScale(gray, 1.2, 5, minSize=(90, 90))

        for(x,y,w,h) in faces:
            if self.addToDatasetEnabled:
                self.count += 1
                if self.count <= 5:
                    # Save the captured image into the datasets folder
                    cv2.imwrite(self.folderPath + "/User." + self.face_id + "." + str(self.count) + ".jpg",
                                gray[y:y + h, x:x + w])
                    if not self.isOpenFaceDataAdded:
                        y0 = max(y - 120, 0)
                        y1 = min (y + h + 80, 480)
                        x0 = max(x - 80, 0)
                        x1 = min(x + 80 + w, 640)
                        self.openFaceImg = img[y0:y1, x0: x1]
                        cv2.imwrite(self.folderPath + "/User." + self.face_id + ".0.jpg",
                                    self.openFaceImg)
                        self.isOpenFaceDataAdded = True
                elif not self.isOpenCVDataAdded:
                    self.isOpenCVDataAdded = True
                    self.add_data_to_db()
                    self.statusLabel.setText("Dataset Added")
                    image_path = QImage(self.folderPath + "/User." + self.face_id + ".0.jpg")
                    self.pictureLabel.setPixmap(QPixmap.fromImage(image_path))
                    self.pictureLabel.setScaledContents(True)

                    self.addToDatasetEnabled = False
                    self.addToDatasetButton.setText("Add to Dataset")

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        return img

    def get_image(self, img):
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:  # [0]rows, [1]=cols [2]=channels
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        out_image = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        # BGB>>RGB
        out_image = out_image.rgbSwapped()
        return out_image

    def display_image(self, img, window=1):
        out_image = self.get_image(img)

        if window == 1:
            self.webCamLabel.setPixmap(QPixmap.fromImage(out_image))
            self.webCamLabel.setScaledContents(True)

    def stop_web_cam(self):
        self.timer.stop()

    def add_data_to_db(self):
        config = configparser.ConfigParser()
        if path.exists(self.db):
            config.read(self.db)
        else:
            config['USERS'] = {}
        student_name = self.studentNameText.text()
        config['USERS'][self.face_id + '_name'] = student_name.strip()
        student_email = self.studentEmailText.text()
        config['USERS'][self.face_id + '_email'] = student_email.strip()
        with open(self.db, 'w') as configfile:
            config.write(configfile)


        # ADD to MYSQL
        self.faceDB.insert_student(self.face_id, student_name , student_email, (self.folderPath + "/User." + self.face_id + ".0.jpg"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceDataSet()
    window.setWindowTitle("Face Dataset")
    window.setStyleSheet("""
                    QPushButton {
                        border: 2px solid #8f8f91;
                        border-radius: 6px;
                        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #f6f7fa, stop: 1 #dadbde);
                        min-width: 80px;
                    }

                        """)
    window.show()
    sys.exit(app.exec())
