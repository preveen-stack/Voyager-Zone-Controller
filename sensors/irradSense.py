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
mycol.delete_many({"type":"IRRADIATION"})

READING_COUNT = 25
THRESHOLD_IRR = 20

sum=0

value = [0]
GAIN = 1
while True:

    sum = 0
    for counter in range(0,READING_COUNT):
        adc = Adafruit_ADS1x15.ADS1115(address=0x49, busnum=1)
        value[0] = adc.read_adc(1, gain=GAIN)
        milliVolts = value[0]*0.187
        measurement = milliVolts/0.00874

        adc.stop_adc()
        print(' Irradiation : {0} watt/m2'.format(measurement))
        time.sleep(0.5)
        global sum
        sum = sum + measurement


    if sum>0 :
        print("saving ")
        print(sum/READING_COUNT)
        mydict = { "reading":sum/READING_COUNT, "type":"IRRADIATION", "zone":"zoneA", "timeStamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S")}
        x = mycol.insert_one(mydict)

    if sum/READING_COUNT > THRESHOLD_IRR:
        ipsStr = str(check_output(['hostname', '-I']))
        ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", ipsStr)[0]

        data = {"command":"STOW","deviceID":"00000000"}
        data = json.dumps(data).encode('utf8')
        req =  request.Request("http://"+ip+":5001/sendCommand", data=data,headers={'content-type': 'application/json'}) # this will make the method "POST"
        resp = request.urlopen(req)
