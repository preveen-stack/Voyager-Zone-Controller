from app import app
from models import *
from flask import jsonify, request
import datetime

@app.route('/getCommissioningData', methods = ['GET'])
def commisioningMethod():
    static_objects = []
    print(StaticData.objects.count())
    for i in range(StaticData.objects.count()):
        tracker = StaticData.objects.get(id=static_objects[i].id)
        static_objects.append(tracker)
    return jsonify(StaticData.objects())

@app.route('/getCurrentTrackerInfo', methods=['GET'])
def currentTrackerMethod():
    id = request.args.get('id')

    power_table = PowerTable.objects(trackerID=id).order_by('timeStamp')
    power_table_data = power_table[(power_table.count())-1]


    status_table = StatusTable.objects(trackerID=id).order_by('timeStamp')
    status_table_data = status_table[(status_table.count()) - 1]

    data_required = {"pvCurrent": power_table_data['pvCurrent'], "pvVoltage": power_table_data['pvVoltage'],
                     "batteryCurrent": power_table_data['batteryCurrent'], "batteryVoltage": power_table_data['batteryVoltage'],
                     "motor": status_table_data['motor'], "errorCode": status_table_data['errorCode'],
                     "currentMode": status_table_data['currentMode'], "currentAngle": status_table_data['currentAngle'],
                     "calculatedAngle": status_table_data['calculatedAngle'], "timeStamp": power_table_data['timeStamp'],
                     "trackerID": power_table_data['trackerID']}
    return jsonify(data_required)


@app.route('/trends', methods=['POST'])
def trendsMethod():
    trackerID = request.get_json()['param']['trackerId']
    parameter = request.get_json()['param']['parameter']
    coordinate = []
    [outer_para, inner_para] = parameter.split(" ")
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
            coordinates.append({trackerID[i]: coordinate})
        return jsonify({"coordinates": coordinates})

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
