import threading
from FaceDB import FaceDB
import time


class CheckedInThread(threading.Thread):

    def __init__(self, student_id, course_id, date ):
        threading.Thread.__init__(self)
        self.student_id = student_id
        self.course_id = course_id
        self.date = date
        self.faceDB = FaceDB()

    def run(self):
        self.faceDB.insert_student_attendance(self.student_id, self.course_id, self.date)
        # e-mail to student
        count = 0
        for i in range(1, 1000000):
            count + 1
            time.sleep(5)
        print(self.student_id, "done with thread")