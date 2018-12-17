import time
from digi.xbee.models.address import XBee64BitAddress, XBee16BitAddress, XBeeIMEIAddress 
from digi.xbee.devices import RemoteXBeeDevice, DigiMeshDevice, XBeeDevice 
from klein import Klein
from flask import jsonify
import json

PORT = "/dev/serial0"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 57600

app = Klein()

def my_data_received_callback(xbee_message):
    address = xbee_message.remote_device.get_64bit_addr()
    data = xbee_message.data.decode("utf8")
    #device.send_data_broadcast("TTT",64)
    print(data)
    remote_device = RemoteXBeeDevice(device, address)

    device.send_data_async(remote_device,"received")

@app.route('/sendCommand',methods=['POST'])
def sendCommand(request):
    request.setHeader('Access-Control-Allow-Origin', '*')
    request.setHeader('Access-Control-Allow-Methods', 'GET')
    request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
    request.setHeader('Access-Control-Max-Age', 2520)
    
    content = json.loads(request.content.read().decode("utf8"))
    print(content)
    command = content['command']
    DID = content['deviceID']

    if DID != "00000000":
        toSend={"CMD":"HMOD","MODE":command, "TS": str(int(time.time()))}
        remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(DID))

        # Send data using the remote object.
        device.send_data_async(remote_device, json.dumps(toSend))
    else:
        toSend={"CMD":"HMOD","MODE":command, "TS": str(int(time.time()))}
        print("broadcasting command " + json.dumps(toSend))
        device.send_data_broadcast(json.dumps(toSend))




    return json.dumps({"result":"success"})


device = DigiMeshDevice(PORT, BAUD_RATE)
device.open()
device.add_data_received_callback(my_data_received_callback)

app.run("0.0.0.0", 5001)
