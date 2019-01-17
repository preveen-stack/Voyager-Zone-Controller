# Copyright 2017, Digi International Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
from flask import Flask
from flask_mqtt import Mqtt
import json
from flask import request
import time
from flask_cors import CORS



from flask_cors import CORS
from optAngle import *
from pymongo import MongoClient


app = Flask(__name__)
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from digi.xbee.models.status import NetworkDiscoveryStatus
import re
from flask_mongoengine import MongoEngine
from multiprocessing import Process, Value



discoverFlagSet=False
toSend=''
INIT_DATA="row1lat28lng29stow20 row2lat35lng80stow20"

# TODO: Replace with the serial port where your local module is connected to.
PORT = "COM9"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 9600

app.config.from_pyfile('config.py')


db = MongoEngine(app)
client = MongoClient('localhost', 27017)
mongo = client.voyagerDB

#flask-cors initialization
CORS(app, supports_credentials=True)

@app.route('/sendCommand', methods=['POST'])
def sendCommandMethod():
    content = request.get_json(force=True)
    print(content)
    command = content['command']
    trackerID = content['trackerID']

    if trackerID != "00000000":
        static_data = StaticData.objects.get(trackerID=trackerID)
        DID=static_data.deviceID
        toSend={"CMD":"HMOD","MODE":command,"DID":DID, "TS": str(int(time.time()))}
        remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(DID))

        # Send data using the remote object.
        device.send_data_async(remote_device, json.dumps(toSend))
    else:
        DID=trackerID
        toSend={"CMD":"HMOD","MODE":command,"DID":DID, "TS": str(int(time.time()))}
        device.send_data_broadcast(json.dumps(toSend))
        print("broadcasting command " + json.dumps(toSend))



    return jsonify({"result":"success"})

from views import *
from models import *



def my_data_received_callback(xbee_message):
    address = xbee_message.remote_device.get_64bit_addr()
    data = xbee_message.data.decode("utf8")
    payload = xbee_message.data.decode()
    payload=json.loads(payload)
    if (payload['CMD'] == "DPWR"):

        values = payload['VALUES']
        values = values.split(",")

        static = StaticData.objects.get(deviceID=payload['DID'])

        power_table = PowerTable(trackerID=static.trackerID ,timeStamp=payload['TS'], pvCurrent=values[0], pvVoltage=values[1],
                                 battCurrent=values[2], battVoltage=values[3])
        power_table.save()
    elif (payload['CMD'] == "DSTA"):

        static_data = StaticData.objects.get(deviceID=payload['DID'])


        latitude = static_data['controllerInfo']['position']['lat']
        longitude = static_data['controllerInfo']['position']['lng']
        azimuth_angle = static_data['controllerInfo']['position']['azimuthDeviation']

        computedAngle = opt_Tilt(latitude, longitude, azimuth_angle)
        computedAngle = (degrees(computedAngle))
        status_table = StatusTable(trackerID=static_data.trackerID, timeStamp=payload['TS'], currentMode=payload['MODE'],
                                   currentAngle=float(payload['ANGLE']), motor=payload['MOTOR'],
                                   errorCode=payload['ERROR'], calculatedAngle=computedAngle)
        status_table.save()


    else:
        print(payload)
    print("Received data from %s: %s" % (address, data))

@app.route('/discoverDevices', methods=['GET'])
def discoverDevices():

    xbee_network = device.get_network()

    xbee_network.set_discovery_timeout(15)  # 15 seconds.

    xbee_network.clear()

    # Callback for discovered devices.  #save device ID to db in seperate collection
    def callback_device_discovered(remote):
        did=str(remote)[:-4]
        print(did)

        static = StaticData.objects.get(deviceID=did)
        XbeeDevices.objects.delete()
        xbee_device = XbeeDevices(deviceID=did, trackerID=static.trackerID)

        xbee_device.save()


    # Callback for discovery finished.
    def callback_discovery_finished(status):
        if status == NetworkDiscoveryStatus.SUCCESS:
            print("Discovery process finished successfully.")
        else:
            print("There was an error discovering devices: %s" % status.description)

    xbee_network.add_device_discovered_callback(callback_device_discovered)

    xbee_network.add_discovery_process_finished_callback(callback_discovery_finished)

    xbee_network.start_discovery_process()

    print("Discovering remote XBee devices...")

    while xbee_network.is_discovery_running():
        time.sleep(0.1)

    return jsonify({"result":"success","data": XbeeDevices.objects()})

device = XBeeDevice(PORT, BAUD_RATE)
device.open()
device.add_data_received_callback(my_data_received_callback)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6050, debug=True, use_reloader=True)
