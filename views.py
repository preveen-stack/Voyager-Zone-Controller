from app import app
from models import *
from flask import jsonify, request
import datetime

@app.route('/getCommisioningData', methods = ['GET'])
def commisioningMethod():
    xbee_devices = []
    xbee_objects = XbeeDevices.objects()
    print(XbeeDevices.objects.count())
    for i in range(XbeeDevices.objects.count()):
        xbee = XbeeDevices.objects.get(id=xbee_objects[i].id)
        xbee_devices.append({"rowId": xbee.rowId, "deviceId": xbee.deviceId})
    return jsonify({"xbeeDevices": xbee_devices})

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

@app.route('/sendCommand', methods=['POST'])
def sendCommandMethod():
    command = request.get_json()['command']
    trackerID = request.get_json()['trackerID']
    device = XbeeDevices.objects.get(deviceId=trackerID)
    #TODO send commands to xbee device



@app.route('/trends', methods=['GET', 'POST'])
def trendsMethod():
    trends_obj = Trends.objects.get()
    if request.method == 'GET':
        return jsonify({"zoneData": trends_obj.trendsData})
    if request.method == 'POST':
        content = request.get_json(force=True)
        for zone in range(trends_obj.trendsData.count()):
            if trends_obj.trendsData[zone].zoneId == content['param']['zoneNo']:
                print('zone found')
                for tracker in range(trends_obj.trendsData[zone].trackers.count()):
                    if trends_obj.trendsData[zone].trackers[tracker].trackerId == content['param']['trackerId']:
                        print('trackerId found')
                        for parameter in range(trends_obj.trendsData[zone].trackers[tracker].parameters.count()):
                            if trends_obj.trendsData[zone].trackers[tracker].parameters[parameter].name == content['param']['parameter']:
                                print('parameter found')
                                return jsonify({"coordinates": trends_obj.trendsData[zone].trackers[tracker].parameters[parameter].coordinates})
                            else:
                                print('parameter not found')
                    else:
                        print('trackerId not found')
            else:
                print('zone not found')


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