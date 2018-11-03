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
            print('Connecting to MySQL database...')
            conn = MySQLConnection(**db_config)

            if conn.is_connected():
                print('connection established.')
            else:
                print('connection failed.')

        except Error as error:
            print(error)

        finally:
            conn.close()
            print('Connection closed.')

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

            print ("Student ID:", student_id, " is inserted")
            #if cursor.lastrowid:
            #    print('last insert id', cursor.lastrowid)
            #else:
                # print('last insert id not found')

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

            print ("Student ID:", student_id, " is updated")
            #if cursor.lastrowid:
            #    print('last insert id', cursor.lastrowid)
            #else:
            #    print('last insert id not found')

            conn.commit()
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app = FaceDB()
    app.insert_student(93895, 'Murat Unal','unalmurat1613@stundets.itu.edu', 'dataset/user93895/User.93895.0.jpg')
    app.insert_student(94130, 'Prasanna Andaju','andojuprasa1773@students.itu.edu', 'dataset/user94130/User.94130.0.jpg')
    app.insert_student(92927, 'Priyanka Shengole','shengolepriya1603@students.itu.edu', 'dataset/user92927/User.92927.0.jpg')
    app.insert_student(94135, 'Soumya Devarakonda','soumya.rajesh1417@gmail.com', 'dataset/user94135/User.94135.0.jpg')
    app.insert_student(91111, 'Emre Unl','emre@test.com', 'dataset/user91111/User.91111.0.jpg')
    app.insert_student(91112, 'Ediz Unl','ediz@test.com', 'dataset/user91112/User.91112.0.jpg')
    app.insert_student(91113, 'Gul Unl','gul@test.com', 'dataset/user91113/User.91113.0.jpg')
    app.insert_student(99999, 'Alex Wu','alex@itu.edu', 'dataset/user99999/User.99999.0.jpg')
