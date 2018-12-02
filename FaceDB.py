import sys

from configparser import ConfigParser
from mysql.connector import MySQLConnection, Error


class FaceDB(object):

    def __init__(self):
        self.connect()

    def read_db_config(self, filename='config.ini', section='mysql'):
        """ Read database configuration file and return a dictionary object
        :param filename: name of the configuration file
        :param section: section of database configuration
        :return: a dictionary of database parameters
        """
        # create parser and read ini configuration file
        parser = ConfigParser()
        parser.read(filename)

        # get section, default to mysql
        db = {}
        if parser.has_section(section):
            items = parser.items(section)
            for item in items:
                db[item[0]] = item[1]
        else:
            raise Exception('{0} not found in the {1} file'.format(section, filename))

        return db

    def connect(self):
        """ Connect to MySQL database """

        db_config = self.read_db_config()

        try:
            conn = MySQLConnection(**db_config)

            if conn.is_connected():
                print('connection established.')
            else:
                print('connection failed.')

        except Error as error:
            print(error)

        finally:
            conn.close()

    def read_file(self, filename):
        with open(filename, 'rb') as f:
            photo = f.read()
        return photo

    def insert_student(self, student_id, student_name, student_email, picture_file):
        query = "INSERT INTO STUDENT(id, name, email, picture) " \
                "VALUES(%s, %s, %s, %s)" \
                "ON DUPLICATE KEY " \
                "UPDATE name = %s, email = %s, picture = %s"

        picture = self.read_file(picture_file)
        args = (student_id, student_name, student_email, picture, student_name, student_email, picture)

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def insert_student_attendance(self, student_id, course_id, date):
        query = "INSERT INTO STUDENT_ATTENDANCE(student_id, course_id, attend_date) " \
                "VALUES(%s, %s, %s)"

        args = (student_id, course_id, date)

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def update_student(self, student_id, student_name, student_email, picture_file):
        query = "UPDATE STUDENT " \
                "SET name = %s, email = %s , picture = %s " \
                "WHERE STUDENT.id = %s"

        picture = self.read_file(picture_file)
        args = (student_name, student_email, picture, student_id)

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_all_student_with_images(self):
        query = "SELECT id, name, email, picture FROM STUDENT"

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_all_student_no_images(self):
        query = "SELECT id, name, email FROM STUDENT"

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_all_courses(self):
        query = "SELECT id, name FROM course"

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_all_course_classroom(self):
        query = "SELECT course_id, classroom_id FROM classroom_course"

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_all_course_students(self):
        query = "SELECT course_id, student_id FROM course_student"

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query)

            data = cursor.fetchall()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_course_students(self, course_id):
        query = "SELECT course_id, student_id FROM course_student " \
                "WHERE course_student.course_id = %s"

        args = (course_id,)
        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)

            data = cursor.fetchall()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def delete_course_students(self, course_id):
        query = "DELETE FROM course_student " \
                "WHERE course_student.course_id = %s"

        args = (course_id,)
        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def insert_course_student(self, course_id, student_id):
        query = "INSERT INTO course_student(course_id, student_id) " \
                "VALUES(%s, %s)"

        args = (course_id, student_id)

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def insert_course_students(self, data_tuple_list):
        query = "INSERT INTO course_student(course_id, student_id) " \
                "VALUES(%s, %s)"

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.executemany(query, data_tuple_list)
            conn.commit()

        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_student(self, student_id ):
        query = "SELECT id, name, email, picture FROM STUDENT " \
                "WHERE STUDENT.id = %s"

        args = (student_id, )

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)

            data = cursor.fetchone()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_course_with_classroom(self, classroom_id):
        query = "SELECT course.id, course.name " \
                "FROM course, classroom_course "  \
                "WHERE classroom_course.course_id = course.id AND "  \
                "classroom_course.classroom_id = %s"

        args = (classroom_id,)

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)

            data = cursor.fetchone()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_classroom(self, classroom_id ):
        query = "SELECT id, name " \
                "FROM classroom "  \
                "WHERE classroom.id = %s"

        args = (classroom_id,)

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)

            data = cursor.fetchone()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def update_classroom_pic(self, classroom_id, classroom_name, picture_file):
        query = "INSERT INTO CLASSROOM(id, name, picture) " \
                 "VALUES(%s, %s, %s) " \
                 "ON DUPLICATE KEY " \
                 "UPDATE name = %s, picture = %s "

        picture = self.read_file(picture_file)
        args = (classroom_id, classroom_name, picture, classroom_name, picture)

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def query_all_classroom_with_images(self):
        query = "SELECT id, name, picture FROM CLASSROOM"

        try:
            db_config = self.read_db_config()
            conn = MySQLConnection(**db_config)

            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()

            return data
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()
