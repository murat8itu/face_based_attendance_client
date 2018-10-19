import sys
import cv2
import configparser
import face_recognition
import pickle
import datetime

from Student import Student
from collections import defaultdict

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.uic import loadUi


class FaceRecognition(QMainWindow):
    student_dictionary = {}
    process_this_frame = True
    in_class = defaultdict(bool)
    all_frame_count = 0
    recognized_frame_count = defaultdict(int)
    recognized_frame_start = defaultdict(int)
    recognition_check_frame = 10  # Check each 10 frames
    confidence_frame_count = recognition_check_frame * 0.4  # at least 40% recognized
    msec_timer = 10
    db = 'db.ini'

    def __init__(self):
        super(FaceRecognition, self).__init__()

        loadUi('03_face_recognition.ui', self)

        self.open_cv_enabled = False
        self.openCVRecognitionButton.setCheckable(True)
        self.openCVRecognitionButton.toggled.connect(self.opencv_button_clicked)

        self.open_face_enabled = False
        self.openFaceRecognitionButton.setCheckable(True)
        self.openFaceRecognitionButton.toggled.connect(self.openface_button_clicked)
        self.list_model = QStandardItemModel(self.checkedInListView)
        self.checkedInListView.setModel(self.list_model)

        self.load_db()

        self.load_open_cv()
        self.load_open_face()

        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self.startWebCam()

    def load_db(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.db)
        user_list = self.config['USERS']

        for item in user_list:
            student_id = item.split('_')[0]

            if self.student_dictionary.get(student_id) is None:
                student = Student()
                student.id = student_id
                student.full_name = self.config['USERS'][str(student_id) + '_name']
                student.email = self.config['USERS'][str(student_id) + '_email']
                self.student_dictionary[student_id] = student

    def load_open_cv(self):
        self.opencv_face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.opencv_face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.opencv_face_recognizer.read('trainer/opencv_trainer.yml')

    def load_open_face(self):
        with open('trainer/openface_trainer_encodings', 'rb') as fp:
            self.openface_known_face_encodings = pickle.load(fp)
        with open('trainer/openface_trainer_ids', 'rb') as fp:
            self.openface_known_face_ids = pickle.load(fp)

    def opencv_button_clicked(self, status):
        if status:
            self.openCVRecognitionButton.setText("Stop Recognition")
            self.openFaceRecognitionButton.setEnabled(False)
            self.open_cv_enabled = True
        else:
            self.openCVRecognitionButton.setText("OpenCV Recognition")
            self.open_cv_enabled = False
            self.openFaceRecognitionButton.setEnabled(True)

    def openface_button_clicked(self, status):
        if status:
            self.openFaceRecognitionButton.setText("Stop Recognition")
            self.openCVRecognitionButton.setEnabled(False)
            self.open_face_enabled = True
        else:
            self.openFaceRecognitionButton.setText("OpenFace Recognition")
            self.open_face_enabled = False
            self.openCVRecognitionButton.setEnabled(True)

    def startWebCam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(self.msec_timer)

    def update_frame(self):
        ret, image = self.capture.read()
        image = cv2.flip(image, 1)

        if self.open_cv_enabled:
            detected_image = self.open_cv_recognize_face(image)
            self.displayImage(detected_image, 1)
        elif self.open_face_enabled:
            detected_image = self.open_face_recognize_face(image)
            self.displayImage(detected_image, 1)
        else:
            self.displayImage(image, 1)

    def open_face_recognize_face(self, img):
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if self.process_this_frame:

            self.process_this_frame = False

            self.all_frame_count +=1

            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame, 2, "hog")
            face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                #matches = face_recognition.compare_faces(self.openface_known_face_encodings, face_encoding)
                tolerance = 0.5
                matches = list(face_recognition.face_distance(self.openface_known_face_encodings, face_encoding) <= tolerance)
                name = ""

                # If a match was found in known_face_encodings, just use the first one.
                if True in matches:
                    first_match_index = matches.index(True)
                    student_id = self.openface_known_face_ids[first_match_index]
                    # Check if already checked in class

                    if not self.in_class[student_id]:
                        # Set the initial recognized frame
                        if self.recognized_frame_start[student_id] == 0:
                            self.recognized_frame_start[student_id] = self.all_frame_count

                        self.recognized_frame_count[student_id] += 1

                        if (self.all_frame_count - self.recognized_frame_start[student_id]) >= self.recognition_check_frame:

                            if self.recognized_frame_count[student_id] >= self.confidence_frame_count:

                                self.in_class[student_id] = True
                                full_name = self.getFullNameFromDB(student_id)
                                now = datetime.datetime.now()
                                item_string = str(now.hour) + ':' + str(now.minute) + ' - ' + str(student_id) + ' : ' + full_name + '  '
                                item = QStandardItem(item_string)
                                self.list_model.insertRow(0, item)

                            else: #reset counters
                                print(self.recognized_frame_count[student_id], " - reset counters")
                                self.recognized_frame_start[student_id] = 0
                                self.recognized_frame_count[student_id] = 0

                    name = self.getNameFromDB(student_id)

                self.face_names.append(name)

        else:
            self.process_this_frame = True

        # Display the results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(img, name, (left + 6, bottom - 6), self.font, 1, (255, 255, 255), 2)
        return img

    def open_cv_recognize_face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.opencv_face_detector.detectMultiScale(gray, 1.2, 5, minSize=(90, 90))

        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w, y+h),(0,0,255),2)
            student_id, confidence = self.opencv_face_recognizer.predict(gray[y:y + h, x:x + w])
            # Check if confidence is less them 100 ==> "0" is perfect match
            if confidence < 60:
                name = self.getNameFromDB(student_id)
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
            student = self.student_dictionary.get(user_id)
            return student.full_name.split()[0]
        except:
            return "unknown"

    def getFullNameFromDB(self, user_id):
        try:
            student = self.student_dictionary.get(user_id)
            return student.full_name
        except:
            return "unknown"


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = FaceRecognition()
    window.setWindowTitle("Webcam Client Test")
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
