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
    c_time = datetime.datetime.now()
    c_error = 999999999999
    c_time = c_time.strftime("%Y%m%d%H%M")

    objects = UpdateData.objects()

    for obj in range(UpdateData.objects.count()):
        update_data = UpdateData.objects.get(id=objects[obj].id)
        if (update_data.trackerID == id):
            error = int(c_time) - int(update_data.timeStamp)
            if error <= c_error:
                c_error = error
            update_data_required = update_data
    update_data_required = {"motor": update_data_required.motor, "battery": update_data_required.battery, "pv": update_data_required.pv, "tracking":update_data_required.tracking, "misc": update_data_required.misc}
    return jsonify({"UpdateData": update_data_required})


@app.route('/trends', methods=['POST'])
def trendsMethod():
    #zoneID = request.get_json()['param']['zoneNo']
    trackerID = request.get_json()['param']['trackerId']
    parameter = request.get_json()['param']['parameter']
    coordinate = []
    [outer_para, inner_para] = parameter.split(" ")
    update_data = UpdateData.objects(trackerID=trackerID).order_by('timeStamp')
    for obj in range(UpdateData.objects(trackerID=trackerID).order_by('timeStamp').count()):
        data = UpdateData.objects.get(id=update_data[obj].id)
        y = data[outer_para][inner_para]
        x = data.timeStamp
        coordinate.append({"x": x, "y": y})

    return jsonify({"coordinates": coordinate})


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
