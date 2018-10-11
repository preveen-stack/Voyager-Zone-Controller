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



toSend=''
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

from models import XbeeDevices, SimpleUpdate
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

            if discoverFlagSet:
                xbee_network = device.get_network()

                xbee_network.set_discovery_timeout(15)  # 15 seconds.

                xbee_network.clear()

                # Callback for discovered devices. TODO save device ID to db in seperate collection
                def callback_device_discovered(remote):
                    xbee_device = XbeeDevices(deviceID=device_id)              #TODO how to get device_id?
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
                 print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),xbee_message.data.decode()))
                 payload=xbee_message.data.decode()
                 if(payload == "REQUEST_INIT_DATA"):
                    device.send_data_broadcast(INIT_DATA)
                    print("init data broadcasted")
                 elif 'angle' in payload:
                    arr=re.findall(r"[-+]?\d*\.\d+|\d+",payload)
                    updateData = SimpleUpdate(angle=float(arr[0]),pvVoltage=float(arr[1]),batteryVoltage=float(arr[2]))
                    updateData.save()
                    mqtt.publish('voyager/site001',payload)
                    print("message published")
                 else :
                    print(payload)
    finally:
        if device is not None and device.is_open():
            device.close()



if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=5000)


