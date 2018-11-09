import threading
from FaceDB import FaceDB


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
        print(self.student_id, "done with thread")