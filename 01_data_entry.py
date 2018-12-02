import sys
import cv2
import os

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.uic import loadUi
from FaceDB import FaceDB


class FaceDataSet(QMainWindow):
    faceDB = FaceDB()
    count = 0
    addToDatasetEnabled = False
    isOpenFaceDataAdded = False
    faceDetector = None
    openFaceImg = None
    capture = None
    face_id = None
    faceDetectionEnabled = True
    folderName = None
    folderPath = None

    def __init__(self):
        super(FaceDataSet, self).__init__()
        loadUi('01_data_entry.ui', self)
        self.faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.addToDatasetButton.clicked.connect(self.detect_webcam_face)

        self.student_list_model = QStandardItemModel(self.studentListView)
        self.studentListView.setModel(self.student_list_model)
        self.studentListView.selectionModel().selectionChanged.connect(self.listview_change)
        self.tabWidget.currentChanged.connect(self.tab_change)

        self.load_course_students()
        self.reset_counters()

        self.courseComboBox.currentIndexChanged.connect(self.combo_change)
        self.combo_change(0)
        self.updateDatabaseButton.clicked.connect(self.button_clicked)

        self.timer = QTimer(self)
        self.start_web_cam()

    def load_course_students(self):
        # ALL COURSES
        data = self.faceDB.query_all_courses()
        for row in data:
            item_string = row[0] + "-" + row[1]
            self.courseComboBox.addItem(item_string)

        # ALL_STUDENTS
        data = self.faceDB.query_all_student_no_images()
        for row in data:
            item_string = row[0] + "-" + row[1]
            item = QStandardItem(item_string)
            item.setCheckable(True)
            item.setSelectable(False)
            self.student_list_model.appendRow(item)

    def reset_counters(self):
        self.count = 0
        self.addToDatasetEnabled = False
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
        self.addDatasetStatus.clear()
        self.pictureLabel.clear()
        QApplication.processEvents()

        self.addToDatasetEnabled = True

    def start_web_cam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def update_frame(self):
        ret, image = self.capture.read()
        image = cv2.flip(image, 1)

        if self.faceDetectionEnabled:
            detected_image = self.detect_face(image)
            self.display_image(detected_image)
        else:
            self.display_image(image, 1)

    def detect_face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.faceDetector.detectMultiScale(gray, 1.2, 5, minSize=(90, 90))

        for(x,y,w,h) in faces:
            if self.addToDatasetEnabled:
                self.count += 1
                if not self.isOpenFaceDataAdded:
                    y0 = max(y - 120, 0)
                    y1 = min (y + h + 80, 480)
                    x0 = max(x - 80, 0)
                    x1 = min(x + 80 + w, 640)
                    self.openFaceImg = img[y0:y1, x0: x1]
                    cv2.imwrite(self.folderPath + "/User." + self.face_id + ".0.jpg",
                                self.openFaceImg)
                    self.isOpenFaceDataAdded = True
                    self.add_data_to_db()
                    self.addDatasetStatus.setText("Dataset Added")
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

    def display_image(self, img):
        out_image = self.get_image(img)

        self.webCamLabel.setPixmap(QPixmap.fromImage(out_image))
        self.webCamLabel.setScaledContents(True)

    def stop_web_cam(self):
        self.timer.stop()
        self.capture = None

    def add_data_to_db(self):
        student_name = self.studentNameText.text()
        student_email = self.studentEmailText.text()

        # ADD to MYSQL
        self.faceDB.insert_student(self.face_id, student_name , student_email,
                                   (self.folderPath + "/User." + self.face_id + ".0.jpg"))
        item = QStandardItem(self.face_id + '-' + student_name)
        item.setCheckable(True)
        item.setSelectable(False)
        self.student_list_model.insertRow(0, item)

    def tab_change(self, i):
        if i == 0:
            self.start_web_cam()
        else:
            self.stop_web_cam()

        self.updateDatabaseStatus.clear()

    def combo_change(self, i):
        # COURSES-STUDENTS
        course_id = str(self.courseComboBox.currentText()).split('-', 1)[0]

        for index in range(self.student_list_model.rowCount()):
            item = self.student_list_model.item(index)
            item.setCheckState(Qt.Unchecked)

        data = self.faceDB.query_course_students(course_id)
        for row in data:
            for item in self.student_list_model.findItems(row[1], Qt.MatchStartsWith):
                item.setCheckState(Qt.Checked)

        self.updateDatabaseStatus.clear()

    def button_clicked(self):
        self.updateDatabaseStatus.setText('')
        self.updateDatabaseButton.setText('Progress..')
        QApplication.processEvents()
        # REMOVE COURSES-STUDENTS
        course_id = str(self.courseComboBox.currentText()).split('-', 1)[0]
        self.faceDB.delete_course_students(course_id)

        # ADD NEW COURSES-STUDENTS
        data_tuple_list = []
        for index in range(self.student_list_model.rowCount()):
            item = self.student_list_model.item(index)
            if item.checkState() == Qt.Checked:
                student_id = str(item.text()).split('-', 1)[0]
                data_tuple_list.append((course_id,student_id))
        self.faceDB.insert_course_students(data_tuple_list)

        self.updateDatabaseStatus.setText('Database Updated')
        self.updateDatabaseButton.setText('Update Database')

    def listview_change(self):
        self.updateDatabaseStatus.clear()
        self.updateDatabaseStatus.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceDataSet()
    window.setWindowTitle("Class Attendance Data Entry")
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
