import cv2
import numpy as np
import os
import face_recognition
import pickle

from FaceDB import FaceDB


class FaceTraining(object):
    faceDB = FaceDB()
    faceRecognizer = None
    faceDetector = None

    def __init__(self):
        self.faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
        self.faceDetector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def run(self):
        self.train_remote_files()

    def train_remote_files(self):
        print ("\n Training faces from remote DB. It will take seconds. Please wait ...")

        data = self.faceDB.query_all_student_with_images()
        openface_encodings =[]
        openface_ids = []

        for row in data:
            open('temp.jpg', 'wb').write(row[3])
            openface_image = face_recognition.load_image_file('temp.jpg')
            openface_encoding = face_recognition.face_encodings(openface_image)[0]
            openface_encodings.append(openface_encoding)
            openface_ids.append(str(row[0]))

        os.remove('temp.jpg')

        with open('trainer/openface_trainer_encodings', 'wb') as fp:
            pickle.dump(openface_encodings, fp)

        with open('trainer/openface_trainer_ids', 'wb') as fp:
            pickle.dump(openface_ids, fp)

        print("\n {0} faces trained.".format(len(np.unique(openface_ids))))


if __name__ == '__main__':
    FaceTraining().run()
