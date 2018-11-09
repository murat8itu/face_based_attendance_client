import cv2
import numpy as np
from PIL import Image
import os
import face_recognition
import pickle

from FaceDB import FaceDB


class FaceTraining(object):
    faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
    faceDetector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");
    faceDB = FaceDB()
    local_path = 'dataset'

    def run(self):
        # print("==LOCAL==")
        # self.train_local_files()
        # print("==REMOTE==")
        self.train_remote_files()

    def get_images_and_labels_from_local(self, path):

        openface_encodings =[]
        openface_ids = []

        opencv_faces=[]
        opencv_ids = []

        all_folder_list = [os.path.join(path, allFolders) for allFolders in os.listdir(path)]
        all_folder_list.sort()
        for single_folder_path in all_folder_list:

            if single_folder_path.startswith("dataset/user"):

                single_image_list = [os.path.join(single_folder_path, singleFolder) for singleFolder in os.listdir(single_folder_path)]

                for singleImagePath in single_image_list:

                    if singleImagePath.endswith(('.jpg', '.gif', '.png')):

                        pil_img = Image.open(singleImagePath).convert('L') # convert it to grayscale
                        img_numpy = np.array(pil_img,'uint8')

                        student_id = os.path.split(singleImagePath)[-1].split(".")[1]
                        counter = int(os.path.split(singleImagePath)[-1].split(".")[2])
                        if counter == 0:
                            openface_image = face_recognition.load_image_file(singleImagePath)
                            openface_encoding = face_recognition.face_encodings(openface_image)[0]
                            openface_encodings.append(openface_encoding)
                            openface_ids.append(student_id)
                        else:
                            # print("---singleImagePath", singleImagePath, " id:", id, " count:", counter)
                            faces = self.faceDetector.detectMultiScale(img_numpy)

                            for (x,y,w,h) in faces:
                                opencv_faces.append(img_numpy[y:y+h,x:x+w])
                                opencv_ids.append(int(student_id))

        return opencv_faces, opencv_ids, openface_encodings, openface_ids

    def train_local_files(self):
        print ("\n Training local faces. It will take a few seconds. Please wait ...")

        opencv_faces, opencv_ids, openface_encodings, openface_ids = self.get_images_and_labels_from_local(self.local_path)

        self.faceRecognizer.train(opencv_faces, np.array(opencv_ids))
        self.faceRecognizer.write('trainer/opencv_trainer.yml')

        with open('trainer/openface_trainer_encodings', 'wb') as fp:
            pickle.dump(openface_encodings, fp)

        with open('trainer/openface_trainer_ids', 'wb') as fp:
            pickle.dump(openface_ids, fp)

        print("\n {0} faces trained.".format(len(np.unique(openface_ids))))

    def train_remote_files(self):
        print ("\n Training faces from remote DB. It will take seconds. Please wait ...")

        data = self.faceDB.query_all_student_with_images()
        openface_encodings =[]
        openface_ids = []

        for row in data:
            # print(row[0], row[1], row[2])
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
