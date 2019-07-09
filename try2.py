import tensorflow as tf
import numpy as np
import facenet
from align import detect_face
import cv2
import argparse
import csv
from math import *
from tqdm import tqdm
import datetime
import mysql.connector
import smtplib

# some constants kept as default from facenet
N_records = 0
minsize = 20
threshold = [0.6, 0.7, 0.7]
factor = 0.709
margin = 44
input_image_size = 160

sess = tf.Session()

# read pnet, rnet, onet models from align directory and files are det1.npy, det2.npy, det3.npy
pnet, rnet, onet = detect_face.create_mtcnn(sess, 'align')

# read 20170512-110547 model file downloaded from https://drive.google.com/file/d/0B5MzpY9kBtDVZ2RpVDYwWmxoSUk
facenet.load_model("20170512-110547/20170512-110547.pb")

# Get input and output tensors
images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
embedding_size = embeddings.get_shape()[1]

def getFace(img):
    faces = []
    img_size = np.asarray(img.shape)[0:2]
    bounding_boxes, _ = detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
    if not len(bounding_boxes) == 0:
        for face in bounding_boxes:
            if face[4] > 0.50:
                det = np.squeeze(face[0:4])
                bb = np.zeros(4, dtype=np.int32)
                bb[0] = np.maximum(det[0] - margin / 2, 0)
                bb[1] = np.maximum(det[1] - margin / 2, 0)
                bb[2] = np.minimum(det[2] + margin / 2, img_size[1])
                bb[3] = np.minimum(det[3] + margin / 2, img_size[0])
                cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
                resized = cv2.resize(cropped, (input_image_size,input_image_size),interpolation=cv2.INTER_CUBIC)
                prewhitened = facenet.prewhiten(resized)
                faces.append({'face':resized,'rect':[bb[0],bb[1],bb[2],bb[3]],'embedding':getEmbedding(prewhitened)})
        #cv2.imshow("",img)
        #cv2.waitKey(10)
    return faces
def getEmbedding(resized):
    reshaped = resized.reshape(-1,input_image_size,input_image_size,3)
    feed_dict = {images_placeholder: reshaped, phase_train_placeholder: False}
    embedding = sess.run(embeddings, feed_dict=feed_dict)
    return embedding

def compare2face(img2):
    threshold = 1.1
    face2 = getFace(img2)
    with open('data.csv','r') as f:
        fr = csv.reader(f)
        d = list(fr)
    prev = 1000000
    ans = -100
    
    for face in d:
        face1 = np.asarray(face[1:])
        face1 = face1.astype(np.float)
        if face2:
            dist = np.sqrt(np.sum(np.square(np.subtract(face1, face2[0]['embedding']))))
            print dist,face[0]
            if(dist <= threshold and dist < prev):
                prev = dist
                ans = face[0]
    return ans

    
def send_mail(name,flag):
    message = ""
    if(flag == 'x' or flag == 'X'):
        message += "Dear "+name[0]+"\nThis is a conformation mail for your Entry @ "+str(datetime.datetime.now())+"\n\nregards,"
    else:
        message += "Dear "+name[0]+"\nThis is a conformation mail for your Exit @ "+str(datetime.datetime.now())+"\n\nRegards" 
    s = smtplib.SMTP('smtp.gmail.com',587)
    s.starttls()
    s.login('eabcd8235@gmail.com','04023155878')
    s.sendmail('eabcd8235@gmail.com',name[1],message)
    s.close()


def get_mapping():

    temp = {}
    mydb = mysql.connector.connect(
            host = 'localhost',
            user = "byte-rider",
            passwd = '23155878',
            database = 'reFace'
            )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT myId,name,email FROM perData")
    p = mycursor.fetchall()
    mydb.close()
    
    
    print 'Fetching Data'    
    for j in tqdm(p):
        temp[j[0]] = j[1:]
    return temp


def updateDb(ans,flag):
    mydb = mysql.connector.connect(
            host = 'localhost',
            user = "byte-rider",
            passwd = '23155878',
            database = 'reFace'
            )
    now = datetime.datetime.now()
    now = str(now)
    mycursor = mydb.cursor()
    if(flag=='N' or flag=='n'):

        val = (mycursor.rowcount+1,ans,now)
        mycursor.execute("INSERT INTO entryExit (Serial,ID,InC) VALUES (%s,%s,%s)",val)
        mydb.commit()

    else:
        val = (now)
        mycursor.execute("UPDATE entryExit SET OutG = '"+str(now)+"' WHERE ID = "+str(ans),val)
    mydb.close()
    

#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&



names = get_mapping()
print names.keys()
answer = ""
cap = cv2.VideoCapture(0)
i = 0
n = 0
while(n<10):
    _,img2 = cap.read()
    
    ans = compare2face(img2)
    if(ans != -100):
        i += 1
    n += 1
    cv2.imshow("",img2)
    cv2.waitKey(5)
if((i+0.0)/n < 0.5):
    print "Sorry"
else:
    ansi = int(ans)
    print "Welcome "+ names[ansi][0] + " !!"
    flag = raw_input("Entry or Exit (N/X) : ")
    updateDb(ansi,flag)
    send_mail(names[ansi],flag)


