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
from flask import request

from flask_cors import CORS
from optAngle import *
from pymongo import MongoClient


app = Flask(__name__)
from digi.xbee.devices import XBeeDevice
import re
from flask_mongoengine import MongoEngine
from multiprocessing import Process, Value



discoverFlagSet=False
toSend=''
INIT_DATA="row1lat28lng29stow20 row2lat35lng80stow20"

# TODO: Replace with the serial port where your local module is connected to.
PORT = "/dev/ttyUSB0"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 9600

app.config.from_pyfile('config.py')

toSend = ''
mqtt = Mqtt(app)
# mqtt.subscribe('voyager')

db = MongoEngine(app)
client = MongoClient('localhost', 27017)
mongo = client.voyagerDB

@app.route('/sendCommand', methods=['POST'])
def sendCommandMethod():
    content = request.get_json(force=True)
    print(content)
    command = content['command']
    trackerID = content['trackerID']

    global toSend
    toSend = content['payload']

    print("sending command " + command)
    mqtt.publish('xbee', 'STOP')
    return "success"

from views import *
from models import *


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print('subscribing to topics now')
    mqtt.subscribe('voyager/site001/zoneA')


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    global toSend
    toSend = data['payload']
    print(data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    logged = True
    # print(level, buf)

def main():
    device = XBeeDevice(PORT, BAUD_RATE)
    print(" +-------------------------------------------------+")
    print(" | 			ZC 			      |")
    print(" +-------------------------------------------------+\n")

    try:
        device.open()

        device.flush_queues()

        print("Waiting for data...\n")

        while True:
            global toSend
            if toSend != '':
                 print("sending broadcast")
                 device.send_data_broadcast(toSend)
                 toSend = ''

            if discoverFlagSet:
                xbee_network = device.get_network()

                xbee_network.set_discovery_timeout(15)  # 15 seconds.

                xbee_network.clear()

                # Callback for discovered devices.  #save device ID to db in seperate collection
                def callback_device_discovered(remote):
                    xbee_device = XbeeDevices(deviceID=remote, rowID=row_id)              #TODO how to get row_id?
                    xbee_device.save()
                    print("Device discovered: %s" % remote)

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


            xbee_message = device.read_data()
            if xbee_message is not None:
                 print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(), xbee_message.data.decode()))
                 payload=xbee_message.data.decode()
                 if(payload['CMD'] == "DPWR"):
                    #TODO save date to power table along with timestamp, pv current, pv voltage,
                    #TODO batt current, battery voltage under payload['VALUES'] as a comma seperated
                    #TODO string in same order
                    values = payload['VALUES']
                    values = values.split(",")
                        
                    power_table = PowerTable(timeStamp=payload['TS'], pvCurrent=values[0], pvVoltage=values[1],
                                             battCurrent=values[2], battVoltage=values[3])
                    power_table.save()
                    device.send_data_broadcast(INIT_DATA)

                    print("init data broadcasted")
                 elif (payload['CMD'] == "DSTA"):
                     # TODO save date to status table, 5 paramters along with time stamp that are
                     # TODO payload['MODE'], payload['ANGLE'], payload['MOTOR'], payload['ERROR'], each one
                     # TODO is received as  string , only angle has to be stored as number

                     static_data = StaticData.objects.get(deviceID=payload['DID'])
                     latitude = static_data['controllerInfo']['position']['lat']
                     longitude = static_data['controllerInfo']['position']['lng']
                     azimuth_angle = static_data['controllerInfo']['position']['azimuthDeviation']

                     computedAngle = opt_Tilt(latitude, longitude, azimuth_angle)
                     computedAngle=(degrees(computedAngle))
                     status_table = StatusTable(timeStamp=payload['TS'], mode=payload['MODE'],
                                                angle=float(payload['ANGLE']), motor=payload['MOTOR'],
                                                error=payload['ERROR'], computedAngle=computedAngle)
                     status_table.save()
                     device.send_data_broadcast(INIT_DATA)

                     print("init data broadcasted")

                 elif 'angle' in payload:
                    arr=re.findall(r"[-+]?\d*\.\d+|\d+", payload)
                    updateData = SimpleUpdate(angle=float(arr[0]), pvVoltage=float(arr[1]), batteryVoltage=float(arr[2]))
                    updateData.save()

                    content = request.get_json(force=True)
                    print(content)
                    # TODO publish mqtt message to update siteDB
                    print("message published")
                 else:
                    print(payload)
    finally:
        if device is not None and device.is_open():
            device.close()

if __name__ == '__main__':
    p = Process(target=main)
    p.start()
    app.run(host='0.0.0.0', port=6050, debug=True, use_reloader=True)
    p.join()
