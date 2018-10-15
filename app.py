
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

from pymongo import MongoClient
import time
from digi.xbee.devices import XBeeDevice
import re
from flask_mongoengine import MongoEngine

INIT_DATA = "row1lat28lng29stow20 row2lat35lng80stow20"



# TODO: Replace with the serial port where your local module is connected to.
PORT = "/dev/ttyUSB0"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 9600



app = Flask(__name__)

CORS(app)

app.config.from_pyfile('config.py')

toSend=''
mqtt = Mqtt(app)
#mqtt.subscribe('voyager')

db = MongoEngine(app)
client = MongoClient('localhost', 27017)
mongo = client.voyagerDB


@app.route('/sendCommand', methods=['POST'])
def sendCommandMethod():
    content = request.get_json(force=True)
    print(content)
    command = content['command']
    trackerID = content['trackerID']
    #TODO send commands to xbee device
    print("sending command "+command)
    mqtt.publish('xbee','STOP')
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
    logged=True
    #print(level, buf)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
