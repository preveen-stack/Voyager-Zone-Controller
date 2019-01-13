from flask import Flask

import json
from flask import request, jsonify
import time
from flask_cors import CORS


from flask_cors import CORS
from optAngle import *
from pymongo import MongoClient


app = Flask(__name__)
import re
from flask_mongoengine import MongoEngine
from multiprocessing import Process, Value



app.config.from_pyfile('config.py')


db = MongoEngine(app)
client = MongoClient('localhost', 27017)
mongo = client.voyagerDB

#flask-cors initialization
CORS(app, supports_credentials=True)


class Stow(db.EmbeddedDocument):
    snowStow = db.FloatField()
    windStow = db.FloatField()
    nightStow = db.FloatField()
    cleanStow = db.FloatField()

class Limits(db.EmbeddedDocument):
    east = db.FloatField()
    west = db.FloatField()

class Position(db.EmbeddedDocument):
    lat = db.FloatField()
    lng = db.FloatField()
    alt = db.FloatField()
    azimuthDeviation = db.FloatField()
    pitch_east = db.FloatField()
    pitch_west = db.FloatField()
    rowWidth = db.FloatField()


class ControllerInfo(db.EmbeddedDocument):
    siteName = db.StringField()
    siteID = db.StringField()
    zoneID = db.StringField()
    rowID = db.StringField()
    firmwareVersion = db.StringField()
    boardSerialNo = db.IntField()
    threshold_wind_speed = db.FloatField()
    table_length = db.FloatField()
    table_width = db.FloatField()
    stow = db.EmbeddedDocumentField(Stow)
    limits = db.EmbeddedDocumentField(Limits)
    position = db.EmbeddedDocumentField(Position)

class Coordinates(db.EmbeddedDocument):
    x = db.IntField()
    y = db.IntField()

class Sensor(db.Document):
    reading = db.FloatField()
    type = db.StringField()
    zone = db.StringField()
    timeStamp = db.StringField()
    rainSpeed = db.FloatField()

class PowerTable(db.Document):
    trackerID = db.StringField()
    timeStamp = db.StringField()
    pvCurrent = db.StringField()
    pvVoltage = db.StringField()
    batteryCurrent = db.StringField()
    batteryVoltage = db.StringField()
    meta = {'collection': 'powerTable'}

class StatusTable(db.Document):
    trackerID = db.StringField()
    timeStamp = db.StringField()
    currentMode = db.StringField()
    currentAngle = db.FloatField()
    motor = db.StringField()
    errorCode = db.StringField()
    calculatedAngle = db.FloatField()
    meta = {'collection': 'statusTable'}

class StaticData(db.Document):
    trackerID = db.StringField(unique=True)
    deviceID = db.StringField(unique=True)
    controllerInfo = db.EmbeddedDocumentField(ControllerInfo)
    discovered = db.BooleanField(default=False)
    meta = {'collection': 'static_data'}

class XbeeDevices(db.Document):
    deviceID = db.StringField()
    trackerID = db.StringField()
    meta = {'collection': 'xbeeDevices'}

class Logs(db.Document):
    log = db.StringField()
    timeStamp = db.StringField()
    meta = {'collection': 'logs'}

class Wifi(db.Document):
    ssid = db.StringField()
    password = db.StringField()
    meta = {'max_documents': 1, 'max_size': 200}


def getJSON(filePath):
    with open(filePath, 'r') as fp:
        return json.load(fp)


@app.route('/getCommissioningData', methods = ['GET'])
def commisioningMethod():
    static_objects = []
    ids = []
    for data in StaticData.objects():
        ids.append({"trackerID": data['trackerID'], "deviceID": data['deviceID']})

    for id in ids:
        try:
            xbee = XbeeDevices.objects.get(deviceID=id['deviceID'])
            if xbee.trackerID == id['trackerID']:
                static = StaticData.objects.get(deviceID=id['deviceID'])
                static.discovered = True
                static.save()
        except:
            static = StaticData.objects.get(deviceID=id['deviceID'])
            static.discovered = False
            static.save()

    for data in StaticData.objects():
        static_objects.append(data)

    return jsonify({"staticData": static_objects})


@app.route('/getCurrentTrackerInfo', methods=['GET'])
def currentTrackerMethod():
    id = request.args.get('id')

    power_table = PowerTable.objects(trackerID=id).order_by('timeStamp')
    power_table_data = power_table[(power_table.count())-1]                #latest timeStamp

    status_table = StatusTable.objects(trackerID=id).order_by('timeStamp')
    status_table_data = status_table[(status_table.count()) - 1]         #latest timeStamp

    static_data = StaticData.objects.get(trackerID=id)
    zoneID = static_data.controllerInfo['zoneID']
    types=[]
    for sensor in Sensor.objects(zone=zoneID):
        if sensor.type not in types:
            types.append(sensor.type)
    print(types)
    sensor_data = []
    for type in types:
        sensor = Sensor.objects(zone=zoneID, type=type).order_by('timeStamp')
        sensor_data.append(sensor[(sensor.count()) -1])
    print(sensor_data)

    data_required = {"pvCurrent": power_table_data['pvCurrent'], "pvVoltage": power_table_data['pvVoltage'],
                     "batteryCurrent": power_table_data['batteryCurrent'], "batteryVoltage": power_table_data['batteryVoltage'],
                     "motor": status_table_data['motor'], "errorCode": status_table_data['errorCode'],
                     "currentMode": status_table_data['currentMode'], "currentAngle": status_table_data['currentAngle'],
                     "calculatedAngle": status_table_data['calculatedAngle'], "timeStamp": power_table_data['timeStamp'],
                     "trackerID": power_table_data['trackerID']}
    for sensor in sensor_data:
        type = (sensor.type).lower()
        data_required[type] = sensor.reading
    return jsonify(data_required)


@app.route('/trends', methods=['POST'])
def trendsMethod():
    trackerID = request.get_json(force=True)['param']['trackerId']
    parameter = request.get_json(force=True)['param']['parameter']
    coordinate = []
    try:
        [outer_para, inner_para] = parameter.split(" ")
    except:
        outer_para = parameter
        inner_para = ""

    if type(trackerID) == str:
        parameter = outer_para+inner_para.capitalize()
        print(parameter)
        for power_table in PowerTable.objects(trackerID=trackerID).order_by('timeStamp'):
            try:
                parameter_value = power_table[parameter]
                time_stamp = power_table['timeStamp']
                coordinate.append({"x": time_stamp, "y": parameter_value})
            except:
                break
        for status_table in StatusTable.objects(trackerID=trackerID).order_by('timeStamp'):
            try:
                parameter_value = status_table[parameter]
                time_stamp = status_table['timeStamp']
                coordinate.append({"x": time_stamp, "y": parameter_value})
            except:
                break

        static_data = StaticData.objects.get(trackerID=trackerID)
        zoneID = static_data.controllerInfo['zoneID']
        parameter = parameter.upper()
        for sensor in Sensor.objects(zone=zoneID, type=parameter).order_by('timeStamp'):
            try:
                parameter_value = sensor['reading']
                time_stamp = sensor['timeStamp']
                coordinate.append({"x": time_stamp, "y": parameter_value})
            except:
                break
        return jsonify({"coordinates": coordinate})

    coordinates = []

    if type(trackerID) == list:
        parameter = outer_para + inner_para.capitalize()
        for i in range(len(trackerID)):
            coordinate = []
            for power_table in PowerTable.objects(trackerID=trackerID[i]).order_by('timeStamp'):
                try:
                    parameter_value = power_table[parameter]
                    time_stamp = power_table['timeStamp']
                    coordinate.append({"x": time_stamp, "y": parameter_value})
                except:
                    break
            for status_table in StatusTable.objects(trackerID=trackerID[i]).order_by('timeStamp'):
                try:
                    parameter_value = status_table[parameter]
                    time_stamp = status_table['timeStamp']
                    coordinate.append({"x": time_stamp, "y": parameter_value})
                except:
                    break
            static_data = StaticData.objects.get(trackerID=trackerID[i])
            zoneID = static_data.controllerInfo['zoneID']
            parameter = parameter.upper()
            for sensor in Sensor.objects(zone=zoneID, type=parameter).order_by('timeStamp'):
                try:
                    parameter_value = sensor['reading']
                    time_stamp = sensor['timeStamp']
                    coordinate.append({"x": time_stamp, "y": parameter_value})
                except:
                    break
            coordinates.append({trackerID[i]: coordinate})
        return jsonify({"coordinates": coordinates})

@app.route('/loadStaticData', methods=['POST'])
def loadStaticDataMethod():
    f = request.files['file']
    f.save('staticData.json')
    loadedList = getJSON('C:\\Users\\amd\\PycharmProjects\\zc-noc\\staticData.json')
    for json in loadedList:
        try:
            static_data = StaticData(trackerID=json['trackerID'], deviceID=json['deviceID'],
                                 controllerInfo=json['controllerInfo'])
            static_data.save()
        except:
            None


    return jsonify({"message": "staticData saved"})

@app.route('/discovery', methods=['GET'])
def discoveryMethod():
    ids = []
    for data in StaticData.objects():
        ids.append({"trackerID": data['trackerID'], "deviceID": data['deviceID']})

    for id in ids:
        try:
            xbee = XbeeDevices.objects.get(deviceID=id['deviceID'])
            if xbee.trackerID == id['trackerID']:
                static = StaticData.objects.get(deviceID=id['deviceID'])
                static.discovered = True
                static.save()
        except:
            static = StaticData.objects.get(deviceID=id['deviceID'])
            static.discovered = False
            static.save()
    return jsonify({"list": ids})

@app.route('/getLog/<timeStamp>', methods=['GET'])
def getLogMethod(timeStamp):
    logs=[]
    for log in Logs.objects():
        if log.timeStamp >= timeStamp:
           logs.append({"log":log.log, "timeStamp": log.timeStamp})
    return jsonify(logs)

@app.route('/setWifiInfo', methods=["POST"])
def wifiMethod():
    content = request.get_json(force=True)
    try:
        wifi = Wifi.objects()
        wifi = Wifi.objects.get()
        wifi.ssid = content['ssid']
        wifi.password = content['password']
        wifi.save()
    except:
        wifi = Wifi(ssid=content['ssid'], password=content['password'])
        wifi.save()
    return jsonify({"message": "Success"})

app.run(host='0.0.0.0',port=5000, use_reloader=True)
