from flask import Flask, redirect, url_for, request, render_template
import mysql.connector
from datetime import datetime
from werkzeug import secure_filename
import cv2

from add import *

app = Flask(__name__)
def get_duration(t,g):
        ans = ""
        g = g[1]
        t = t[1]
        t = t.split(':')
        g = g.split(':')
        ans = "{}:{}:{}".format(float(t[0])-float(g[0]), float(t[1]) - float(g[1]),float(t[2])-float(g[2]))
        return ans
def plumb_entry(data):
    p = []
    for i in data:
        temp = {}
        g = i[0].split(' ')
        t = i[1].split(' ')
        temp['InC'] = g[1]
        temp['OutG'] = t[1]
        temp['roll'] = i[3]
        temp['date'] = g[0]
        temp['name'] = i[2]
        temp['duration'] = get_duration(t,g)
        p.append(temp)
    return p
def plumb_person(data):
    p = []
    for j in data:
        temp = {}
        temp['id'] = j[0]
        temp['name'] = j[1]
        temp['roll'] = j[2]
        temp['email'] = j[3]
        p.append(temp)
    return p


@app.route("/add_user",methods=['POST','GET'])
def add_user():
    error =None
    user = {}
    temp = {}
    print(error)
    if(request.method=='POST'):
        user['Name'] = request.form['name']
        user['roll'] = request.form['roll']
        user['email'] = request.form['email']
        face = request.files['file']
        face.save(secure_filename(face.filename))
        img = cv2.imread(secure_filename(face.filename))
        faces = getFace(img)
        for face in faces:
            user["myId"] = int(time.time())
            temp[user["myId"]] = face['embedding'][0]
            store_to_database(user["myId"],user["Name"],user["roll"],user['email'])
        write_to_file(temp)

        return redirect(url_for("user_data"))
    return render_template("user_add.html")

@app.route("/user_data")
def user_data():
        mydb = mysql.connector.connect(
                host = 'localhost',
                user = "byte-rider",
                passwd = '23155878',
                database = 'reFace'
                )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM perData")
        data = mycursor.fetchall()
        data = plumb_person(data)
        return render_template("index2.html",rows=data)

@app.route("/admin")
def admin():
    mydb = mysql.connector.connect(
            host = 'localhost',
            user = "byte-rider",
            passwd = '23155878',
            database = 'reFace'
            )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT entryExit.InC, entryExit.OutG , perData.Name, perData.Roll FROM entryExit INNER JOIN perData ON entryExit.ID = perData.myID")
    data = mycursor.fetchall()
    data = plumb_entry(data)
    return render_template("index.html",rows=data)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/",methods=['POST','GET'])
def index():
    error=None
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        if(user=='admin' and password =='1234'):
            return redirect(url_for("admin"))
        else:
            error = "No user exists"
    return render_template("login.html",error=error)




if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5005,debug=True)
