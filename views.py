from app import app, main
from models import *
from flask import jsonify

@app.route('/commissioning', methods = ['GET'])
def commissioningMethod():
    static_data = []
    xbee_devices = []
    objects = StaticData.objects()
    for i in range(StaticData.objects.count()):
        static_data.append(StaticData.objects.get(id=objects[i].id))
    xbee_objects = XbeeDevices.objects()
    for i in range(XbeeDevices.objects.count()):
        xbee_devices.append(XbeeDevices.objects.get(id=xbee_objects[i].id))
    return jsonify({"staticData": static_data, "XbeeDevice": xbee_devices})


