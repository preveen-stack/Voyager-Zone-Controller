import pymongo
import datetime

import Adafruit_ADS1x15
import time
from urllib import request, parse
import re
from subprocess import check_output
import json



myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["voyagerDB"]
mycol = mydb["sensor"]

READING_COUNT = 25
THRESHOLD_WIND_SPEED = 12
sum=0

value = [0]
GAIN = 1
mycol.delete_many({"type":"WINDSPEED"})
while True:

    sum = 0
    for counter in range(0,READING_COUNT):
        adc = Adafruit_ADS1x15.ADS1115(address=0x49, busnum=1)
        value[0] = adc.read_adc(2, gain=GAIN)
        volts = value[0]*0.00762939453
        dt = datetime.datetime.now()
        print(dt)

        adc.stop_adc()
        print(' Wind Speed: {0} km/hr'.format(volts))
        time.sleep(0.5)
        global sum
        sum = sum + volts


    if sum>0 :
        print("saving ")
        print(sum/READING_COUNT)
        mydict = { "reading":sum/READING_COUNT, "type":"WINDSPEED", "zone":"zoneA", "timeStamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S")}
        x = mycol.insert_one(mydict)

    else :
        print("saving 0")
        mydict = { "reading":0, "type":"WINDSPEED", "zone":"zoneA", "timeStamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S")}
        x = mycol.insert_one(mydict)

    if sum/READING_COUNT > THRESHOLD_WIND_SPEED:
        print("SENDING STOW on XBEE")
        ipsStr = str(check_output(['hostname', '-I']))
        ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", ipsStr)[0]

        data = {"command":"STOW","deviceID":"00000000"}
        data = json.dumps(data).encode('utf8')
        req =  request.Request("http://"+ip+":5001/sendCommand", data=data,headers={'content-type': 'application/json'}) # this will make the method "POST"
        resp = request.urlopen(req)


