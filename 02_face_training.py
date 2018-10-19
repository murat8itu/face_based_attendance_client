import cv2
import numpy as np
from PIL import Image
import os
import face_recognition
import pickle

faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
faceDetector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

path = 'dataset'


def get_images_and_labels(path):

    openface_encodings =[]
    openface_ids = []

    opencv_faces=[]
    opencv_ids = []

    all_folder_list = [os.path.join(path, allFolders) for allFolders in os.listdir(path)]

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
                        #print("---singleImagePath", singleImagePath, " id:", id, " count:", counter)
                        faces = faceDetector.detectMultiScale(img_numpy)

                        for (x,y,w,h) in faces:
                            opencv_faces.append(img_numpy[y:y+h,x:x+w])
                            opencv_ids.append(int(student_id))

    return opencv_faces, opencv_ids, openface_encodings, openface_ids


print ("\n Training faces. It will take a few seconds. Please wait ...")

opencv_faces, opencv_ids, openface_encodings, openface_ids = get_images_and_labels(path)

faceRecognizer.train(opencv_faces, np.array(opencv_ids))
faceRecognizer.write('trainer/opencv_trainer.yml')

with open('trainer/openface_trainer_encodings', 'wb') as fp:
    pickle.dump(openface_encodings, fp)
with open('trainer/openface_trainer_ids', 'wb') as fp:
    pickle.dump(openface_ids, fp)

print("\n {0} faces trained.".format(len(np.unique(openface_ids))))
