from flask import Flask, redirect, url_for, request, render_template
from werkzeug import secure_filename
import mysql.connector
import cv2


app = Flask(__name__)

def plumb_entry(data):
    p = []
    for i in data:
        temp = {}
        g = i[0].split(' ')
        temp['InC'] = g[1]
        temp['OutG'] = i[1]
        temp['roll'] = i[3]
        temp['date'] = g[0]
        temp['name'] = i[2]
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
    if(request.method=='POST'):
        user['Name'] = request.form['name']
        user['roll'] = request.form['roll']
        user['email'] = request.form['email']
        face = request.files['file']
        face.save(secure_filename(face.filename))
        img = cv2.imread(secure_filename(face.filename))
        print(img)
        return redirect(url_for("admin"))
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
