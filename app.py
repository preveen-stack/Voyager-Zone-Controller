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

from digi.xbee.devices import XBeeDevice
import re
from flask_mongoengine import MongoEngine

INIT_DATA = "row1lat28lng29stow20 row2lat35lng80stow20"

# TODO: Replace with the serial port where your local module is connected to.
PORT = "/dev/ttyUSB0"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 9600


from flask import Flask
from flask_mqtt import Mqtt

from pymongo import MongoClient
import time

app = Flask(__name__)

app.config.from_pyfile('config.py')

toSend = ''
mqtt = Mqtt(app)
#mqtt.subscribe('voyager')

db = MongoEngine(app)
client = MongoClient('localhost', 27017)
mongo = client.voyagerDB


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
    print(level, buf)


device = XBeeDevice(PORT, BAUD_RATE)

class SimpleUpdate(db.Document):
    angle = db.FloatField()
    pvVoltage = db.FloatField()
    batteryVoltage = db.FloatField()

def main():
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
                 device.send_data_broadcast(toSend)
                 toSend = ''

            xbee_message = device.read_data()
            if xbee_message is not None:
                 print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(), xbee_message.data.decode()))
                 payload=xbee_message.data.decode()
                 if(payload == "REQUEST_INIT_DATA"):
                    device.send_data_broadcast(INIT_DATA)
                    print("init data broadcasted")
                 elif 'angle' in payload:
                    arr = re.findall(r"[-+]?\d*\.\d+|\d+",payload)
                    updateData = SimpleUpdate(angle=float(arr[0]),pvVoltage=float(arr[1]),batteryVoltage=float(arr[2]))
                    updateData.save()
                    mqtt.publish('voyager/site001',payload)
                    print("message published")
                 else:
                    print(payload)
    finally:
        if device is not None and device.is_open():
            device.close()


from views import *


if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=5000)
