import threading
from FaceDB import FaceDB
import smtplib
import datetime


class CheckedInThread(threading.Thread):

    def __init__(self, student_id, student_name, student_email, course_id, course_name, classroom_name, date):
        threading.Thread.__init__(self)
        self.student_id = student_id
        self.student_name = student_name
        self.student_email = student_email
        self.course_id = course_id
        self.course_name = course_name
        self.classroom_name = classroom_name
        self.date = date

    def run(self):
        self.faceDB = FaceDB()
        self.faceDB.insert_student_attendance(self.student_id, self.course_id, self.date)
        # e-mail to student
        if self.student_id in ['93895']:
            self.sendemail('noreplyituproject@gmail.com', self.student_email, '',
                            self.course_id + ' check-in', # subject
                            'Dear ' + self.student_name.split()[0] + ',' + '\r\n' + # message
                            '\r\n' +
                            'Here is your attendance information:' + '\r\n' +
                            'Code: ' + self.course_id + '\r\n' +
                            'Name: ' + self.course_name + '\r\n' +
                            'Classroom: ' + self.classroom_name + '\r\n' +
                            'Date & Time: ' + str(self.date) + '\r\n' +
                            '\r\n' +
                            'Thank you,' + '\r\n'+
                            'Face Based Class Attendance System' + '\r\n' +
                            'ITU Capstone Project',
                            'noreplyituproject@gmail.com', # username
                            'noreply2018' # password
                           )

    def sendemail(self, from_addr, to_addr_list, cc_addr_list,
                  subject, message,
                  login, password,
                  smtpserver='smtp.gmail.com:587'):
        header = 'From: %s ' % from_addr
        header += '\r\n'
        header += 'To: %s' % to_addr_list
        header += '\r\n'
        header += 'Cc: %s' % cc_addr_list
        header += '\r\n'
        header += 'Subject: %s' % subject
        header += '\r\n'
        message = header + message

        #print (message)
        server = smtplib.SMTP(smtpserver)
        server.starttls()
        server.login(login, password)
        problems = server.sendmail(from_addr, to_addr_list, message)
        server.quit()


if __name__ == '__main__':
    now = datetime.datetime.now()
    app = CheckedInThread('93895', 'SW680', now)
    app.sendemail('noreplyituproject@gmail.com', 'unalmurat1613@students.itu.edu', '', 'Course CheckIn',
             'Your attendance is recorded for Course 360',
             'noreplyituproject@gmail.com', 'noreply2018')
