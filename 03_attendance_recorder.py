import sys
import cv2
import face_recognition
import pickle
import datetime

from Student import Student
from collections import defaultdict
from FaceDB import FaceDB
from CheckedInThread import CheckedInThread

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.uic import loadUi


class FaceRecognition(QMainWindow):
    faceDB = FaceDB()
    classroom_id = 'R301'
    classroom_name = None
    course_id = None
    course_name = None

    students_course_dictionary = {}
    all_course_classroom_dictionary = {}
    all_students_course_dictionary = {}
    all_students_dictionary = {}
    checked_in_students = {}
    rejected_students = {}

    capture = None
    open_face_enabled = False
    face_locations = None
    face_names = None
    openface_known_face_encodings = None
    openface_known_face_ids = None

    process_this_frame = True
    all_frame_count = 0
    recognized_frame_count = defaultdict(int)
    recognized_frame_start = defaultdict(int)
    recognition_check_frame = 10  # Check each 10 frames
    confidence_frame_count = recognition_check_frame * 0.4  # at least 40% recognized
    font = None
    msec_timer = 10

    def __init__(self):
        super(FaceRecognition, self).__init__()
        loadUi('03_attendance_recorder.ui', self)

        self.checked_in_list_model = QStandardItemModel(self.checkedInListView)
        self.checkedInListView.setModel(self.checked_in_list_model)

        self.rejected_list_model = QStandardItemModel(self.rejectedCheckedInListView)
        self.rejectedCheckedInListView.setModel(self.rejected_list_model)

        self.load_remote_db()
        self.setUIClassroomText()

        self.load_open_face()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.startWebCam()
        self.openface_button_clicked(True)

    def load_remote_db(self):
        # ALL_STUDENTS
        print("# LOADING DATA FROM DATABASE...")
        data = self.faceDB.query_all_student_no_images()
        for row in data:
            # print(row[0], row[1], row[2])
            if self.all_students_dictionary.get(str(row[0])) is None:
                student = Student()
                student.id = str(row[0])
                student.full_name = row[1]
                student.email = row[2]
                self.all_students_dictionary[str(row[0])] = student

        # CLASSROOM
        self.classroom_name = self.faceDB.query_classroom(self.classroom_id)[1]

        # COURSE
        self.course_id = self.faceDB.query_course_with_classroom(self.classroom_id)[0]
        self.course_name = self.faceDB.query_course_with_classroom(self.classroom_id)[1]

        # STUDENTS_COURSE and ALL_STUDENTS_COURSE
        data = self.faceDB.query_all_course_students()
        for row in data:
            # print(row[0], row[1])
            if row[0] == self.course_id:
                self.students_course_dictionary[row[1]]= row[0]
            else:
                self.all_students_course_dictionary[row[1]]= row[0]

        # ALL_COURSE_CLASSROOMS
        data = self.faceDB.query_all_course_classroom()
        for row in data:
            # print(row[0], row[1])
            self.all_course_classroom_dictionary[row[0]]= row[1]

        print("# LOADING COMPLETED!")

    def setUIClassroomText(self):
        self.roomText.setText(self.classroom_name)
        self.courseText.setText(self.course_id + " - " + self.course_name)
        self.registeredStudentNumber.setText(str(len(self.students_course_dictionary)))

    def load_open_face(self):
        with open('trainer/openface_trainer_encodings', 'rb') as fp:
            self.openface_known_face_encodings = pickle.load(fp)

        with open('trainer/openface_trainer_ids', 'rb') as fp:
            self.openface_known_face_ids = pickle.load(fp)

    def openface_button_clicked(self, status):
        if status:
            self.open_face_enabled = True
        else:
            # self.openFaceRecognitionButton.setText("OpenFace Recognition")
            self.open_face_enabled = False

    def startWebCam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        timer = QTimer(self)
        timer.timeout.connect(self.update_frame)
        timer.start(self.msec_timer)

    def update_frame(self):
        ret, image = self.capture.read()
        image = cv2.flip(image, 1)

        if self.open_face_enabled:
            detected_image = self.open_face_recognize_face(image)
            self.displayImage(detected_image)
        else:
            self.displayImage(image)

    def open_face_recognize_face(self, img):
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if self.process_this_frame:

            self.process_this_frame = False

            self.all_frame_count += 1

            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame, 2, "hog")
            face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                # matches = face_recognition.compare_faces(self.openface_known_face_encodings, face_encoding)
                tolerance = 0.35
                matches = list(face_recognition.face_distance(self.openface_known_face_encodings,
                                                              face_encoding) <= tolerance)
                name = ""

                # If a match was found in known_face_encodings, just use the first one.
                if True in matches:
                    first_match_index = matches.index(True)
                    student_id = self.openface_known_face_ids[first_match_index]
                    # Check if already checked in class

                    if student_id not in self.checked_in_students and student_id not in self.rejected_students:
                        # Set the initial recognized frame
                        if self.recognized_frame_start[student_id] == 0:
                            self.recognized_frame_start[student_id] = self.all_frame_count

                        self.recognized_frame_count[student_id] += 1

                        if (self.all_frame_count - self.recognized_frame_start[student_id]) >= self.recognition_check_frame:

                            if self.recognized_frame_count[student_id] >= self.confidence_frame_count:

                                if student_id in self.students_course_dictionary:
                                    self.checkedInStudent(student_id)
                                elif student_id in self.all_students_course_dictionary:
                                    self.rejectStudent(student_id)
                                else:
                                    print("==UNKNOWN CASE")

                            else: # reset counters
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

    def checkedInStudent(self, student_id):
        self.checked_in_students[student_id] = True
        student = self.getStudentFromDB(student_id)
        now = datetime.datetime.now()
        item_string = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2) + ' - ' + str(
            student_id) + ' : ' + student.full_name + '  '
        item = QStandardItem(item_string)
        self.checked_in_list_model.insertRow(0, item)
        self.checkedInStudentNumber.setText(str(len(self.checked_in_students)))
        new_thread = CheckedInThread(student_id, student.full_name, student.email,
                                      self.course_id, self.course_name, self.classroom_name, now)
        new_thread.start()

    def rejectStudent(self, student_id):
        self.rejected_students[student_id] = True
        full_name = self.getFullNameFromDB(student_id)
        now = datetime.datetime.now()
        item_string = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2) + ' - ' + \
            str(student_id) + ' : ' + full_name + '  '
        correct_course = self.all_students_course_dictionary[str(student_id)]
        correct_classroom = self.all_course_classroom_dictionary[correct_course]
        item = QStandardItem(item_string + '=> ' + correct_course + ' : ' + correct_classroom)
        self.rejected_list_model.insertRow(0, item)

    def displayImage(self, img):
        qformat=QImage.Format_Indexed8
        if len(img.shape) == 3: # [0]rows, [1]=cols [2]=channels
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        # BGB>>RGB
        outImage = outImage.rgbSwapped()

        self.webCamLabel.setPixmap(QPixmap.fromImage(outImage))
        self.webCamLabel.setScaledContents(True)

    def stopWebCam(self):
        self.timer.stop()

    def getNameFromDB(self, user_id):
        try:
            student = self.all_students_dictionary.get(user_id)
            return student.full_name.split()[0]
        except:
            return "unknown"

    def getFullNameFromDB(self, user_id):
        try:
            student = self.all_students_dictionary.get(user_id)
            return student.full_name
        except:
            return "unknown"

    def getStudentFromDB(self, user_id):
        try:
            student = self.all_students_dictionary.get(user_id)
            return student
        except:
            return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceRecognition()
    window.setWindowTitle("Class Attendance Recorder")
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
