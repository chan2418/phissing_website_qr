
from flask import Flask, request, render_template, redirect, url_for, flash, session
import numpy as np
import pandas as pd
from sklearn import metrics
import warnings
import pickle
from feature import FeatureExtraction

warnings.filterwarnings('ignore')

file = open("model.pkl", "rb")
gbc = pickle.load(file)

app = Flask(__name__)
app.secret_key = "supersecret123"  


users = {
    "admin": "admin123",
    "user": "password"
}

@app.route('/')
@app.route('/first')
def first():
    return render_template('landing_page.html')

@app.route('/performance')
def performance():
    return render_template('performance.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form.get("uname")
        pwd = request.form.get("pwd")

        if uname in users and users[uname] == pwd:
            session["username"] = uname
            flash("Login successful ", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password ", "danger")
            return redirect(url_for("login"))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/preview', methods=["POST"])
def preview():
    if request.method == 'POST':
        dataset = request.files['datasetfile']
        df = pd.read_csv(dataset, encoding='unicode_escape')
        df.set_index('Id', inplace=True)
        return render_template("preview.html", df_view=df)

@app.route('/index')
def index():
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))
    return render_template('index.html', username=session["username"])
@app.route("/posts", methods=["GET", "POST"])
def posts():
    if request.method == "POST":
        url = request.form["url"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1, 30)

        y_pred = gbc.predict(x)[0]
        y_pro_phishing = gbc.predict_proba(x)[0, 0]
        y_pro_non_phishing = gbc.predict_proba(x)[0, 1]

        pred = "It is {0:.2f} % safe to go ".format(y_pro_phishing * 100)
        return render_template('result.html', xx=round(y_pro_non_phishing, 2), url=url)

    return render_template("result.html", xx=-1)

if __name__ == "__main__":
    app.run(debug=True)
