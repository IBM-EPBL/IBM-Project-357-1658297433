from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify

import numpy as np
import pickle
import pandas
import sqlite3


import requests

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "MCpcEwC0ndHw-26QtyWKsoygqkdNWKvaCPB-l4M-6RSa"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

# Declare a Flask app
app = Flask(__name__)
app.secret_key="#@universityflaskapp@#"
@app.route('/predict',methods=["POST","GET"])
def predict():
    res = " "
     # If a form is submitted
    if request.method == "POST":
        input_feature=[x for x in request.form.values() ]
        features_values=[np.array(input_feature)]
        names = [['Location','MinTemp','MaxTemp','Rainfall','WindGustSpeed',
        'WindSpeed9am','WindSpeed3pm','Humidity9am','Humadity3pm',
        'Pressure9pm','Pressure3am','Temp9pm','Temp3pm','RainyTodaty',
        'WindGustDir','WindDir9pm','WindDir3pm']]
        data = pandas.DataFrame(features_values,columns=names)
        data = scale.fit_transform(data)
        data = pandas.DataFrame(data,columns=names)

        #Get prediction
        prediction = model.predict(data)

        # NOTE: manually define and pass the array(s) of values to be scored in the next line
        payload_scoring = {"input_data": [{"fields":['Location','MinTemp','MaxTemp','Rainfall','WindGustSpeed',
        'WindSpeed9am','WindSpeed3pm','Humidity9am','Humadity3pm',
        'Pressure9pm','Pressure3am','Temp9pm','Temp3pm','RainyTodaty',
        'WindGustDir','WindDir9pm','WindDir3pm'], "values": payload_scoring}]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/c7fa8c3c-12bd-4c77-800b-56faf606278c/predictions?version=2022-11-23', json=payload_scoring,
        headers={'Authorization': 'Bearer ' + mltoken})
        print("Scoring response")
        print(response_scoring.json())
        #return render_template("prediction.html", output = res)
    # database creation
    con=sqlite3.connect("database.db")
    print("Opened database successfully")
    con.execute("create table if not exists customer(pid integer primary key, username text, email text, password text,status BOOLEAN)")
    print("Table created successfully")
    con.close()

    # model = pickle.load(open("rainfall.pkl",'rb'))
    # scale = pickle.load(open("scale.pkl",'rb'))

    @app.route("/",methods=['POST','GET'])
    def index():
        return render_template("login.html")

    @app.route('/home/')
    def home():
        return render_template("home.html")

    @app.route('/chance/',methods=['GET', 'POST'])
    def chance():
        return render_template("chance.html")

    @app.route('/nochance/',methods=['GET', 'POST'])
    def nochance():
        return render_template("noChance.html")


    # @app.route('/help/')
    # def help():
    #     return render_template("help.html")

    @app.route('/contact/')
    def contact():
        return render_template("contact.html")

    @app.route('/logout')
    def logout():
        session.clear()
        return render_template('login.html')

    # @app.route('/about/')
    # def about():
    #     return render_template("about.html")

    @app.route('/login',methods=['POST','GET'])
    def login():
        if request.method =='POST':
            email = request.form['email']
            password = request.form['password']
            con=sqlite3.connect("database.db")
            con.row_factory=sqlite3.Row
            cur=con.cursor()
            cur.execute("SELECT * FROM customer where email=? and password=?",(email,password))
            data=cur.fetchone()

            if data:
                session["email"]=data["email"]
                print("sent to home")
                return render_template("home.html")
                        
            else:
                flash("Username or Password is incorrect","danger")
                print("not sent to home")
                return render_template("login.html")
            
    @app.route('/register',methods=['GET','POST'])
    def register():
        if request.method == 'POST':
            try:
                username=request.form['username']
                email=request.form['email']
                password=request.form['password']
                con=sqlite3.connect("database.db")
                cur=con.cursor()
                cur.execute("INSERT INTO customer(username,email,password) VALUES (?,?,?)",(username,email,password))
                con.commit()
                flash("Registered successfully","success")
                print("registered")
            except:
                con.rollback()  
                flash("Problem in Registration, Please try again","danger")
            finally:
                return render_template("login.html")
                con.close()
        else:
            return render_template('register.html')


#Running the app

if __name__== "___main___":
    app.run(Debug = True)