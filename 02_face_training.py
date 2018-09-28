
import cv2
import numpy as np
from PIL import Image
import os

faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
faceDetector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

path = 'dataset'
def getImagesAndLabels(path):

    faceSamples=[]
    ids = []
    allFolderList = [os.path.join(path, allFolders) for allFolders in os.listdir(path)]

    for singleFolderPath in allFolderList:

        if singleFolderPath.startswith("dataset/user"):

            singleImageList = [os.path.join(singleFolderPath, singleFolder) for singleFolder in os.listdir(singleFolderPath)]

            for singleImagePath in singleImageList:

                if singleImagePath.endswith(('.jpg', '.gif', '.png')):

                    PIL_img = Image.open(singleImagePath).convert('L') # convert it to grayscale
                    img_numpy = np.array(PIL_img,'uint8')

                    id = int(os.path.split(singleImagePath)[-1].split(".")[1])
                    #print("---singleImagePath", singleImagePath, " id:", id)
                    faces = faceDetector.detectMultiScale(img_numpy)

                    for (x,y,w,h) in faces:
                        faceSamples.append(img_numpy[y:y+h,x:x+w])
                        ids.append(id)

    return faceSamples,ids

print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces,ids = getImagesAndLabels(path)
faceRecognizer.train(faces, np.array(ids))

faceRecognizer.write('trainer/trainer.yml')

print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
