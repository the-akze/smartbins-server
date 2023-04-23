from flask import Flask, request, render_template, jsonify
import firebase_admin
from firebase_admin import credentials, db
from json import loads
import os
from time import time

app = Flask(__name__)

print("initializing firebase...")
c = loads(os.environ['firebase_admin_certificate'])
cred = credentials.Certificate(c)
firebase_admin.initialize_app(cred, {
    'databaseURL':
    'https://lahacks23-futuretrashcan-default-rtdb.firebaseio.com'
})
print("firebase initialized")

class Vars:
    project_name = "SmartBins"

@app.route("/")
def r_index():
    return render_template("index.html", product_name=Vars.project_name)

@app.route("/dashboard")
def r_dashboard():
    return render_template("dashboard.html", product_name=Vars.project_name, weightData=get_weight_data(), sortData=get_sort_data())

@app.route("/send_data", methods=["POST"])
def r_send_data():
    try:
        data = request.get_json()
        garbage_weight = data["garbageWeight"]
        recycle_weight = data["recycleWeight"]

        t = round(time() * 1000)

        ref = db.reference("/data/weightData/" + str(t))
        newData = {}
        newData["garbageWeight"] = garbage_weight
        newData["recycleWeight"] = recycle_weight
        ref.update(newData)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/get_data")
def r_get_data():
    ref = db.reference("/data/weightData/")

@app.route("/set_prediction", methods=["POST"])
def r_set_sort_data():
    try:
        data = request.get_json()
        recyclable = True if data[0] == "Recycle" else False
        update_sort_data(recyclable)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/get_realtime_weight_data")
def get_realtime_weight_data():
    dataList = get_weight_data()
    maxIndex = 0
    for i in range(len(dataList)):
        if (dataList[i]["time"] > dataList[maxIndex]["time"]):
            maxIndex = i
    latest = dataList[maxIndex]
    return jsonify(latest)

def get_sort_data():
    ref = db.reference("/data/sortData/")
    data = ref.get()
    filteredData = {}
    countR = 0
    countG = 0
    for t in data:
        if int(t) < time() * 1000 - (24 * 60 * 60 * 1000):
            filteredData[t] = data[t]
            if (data[t][0] == "Recycle"):
                countR += 1
            else:
                countG += 1

    return {"data": filteredData, "countR": countR, "countG": countG}

def update_sort_data(recyclable:bool):
    if recyclable == None:
        return False
    t = round(time() * 1000)
    ref = db.reference("/data/sortData/" + str(t))
    newData = {}
    newData = {"recyclable": recyclable}
    ref.update(newData)

def get_weight_data():
    # get data by days if dayOrHr true, else get by hours
    ref = db.reference("/data/weightData")
    data = ref.get()
    # hoursData = [[],[],[],[],[]]
    dataList = [] if data == None else [{**value, **{"time": key}} for key, value in data.items()]
    return dataList

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')