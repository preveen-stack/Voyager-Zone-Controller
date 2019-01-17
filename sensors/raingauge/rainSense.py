import datetime
import time
import pigpio
import rainGauge
import pymongo

from urllib import request, parse
import re
from subprocess import check_output
import json

THRESHOLD_RAIN_FALL = 20

PWM_GPIO = 17
RUN_TIME = 600.0
SAMPLE_TIME = 20.0

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["voyagerDB"]
mycol = mydb["sensor"]

mycol.delete_many({"type":"RAINSPEED"})

pi = pigpio.pi()

p = rainGauge.reader(pi, PWM_GPIO)

start = time.time()

while (time.time() - start) < RUN_TIME:

    time.sleep(SAMPLE_TIME)

    f = p.frequency()
    pw = p.pulse_width()
    dc = p.duty_cycle()
    count = p.rainMM()
    mydict = { "reading":count, "type":"RAINSPEED", "zone":"zoneA", "timeStamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S")}
    x = mycol.insert_one(mydict)

    print("f={:.1f} pw={} dc={:.2f} rainMM={}".format(f, int(pw+0.5), dc,count))

    if count > THRESHOLD_RAIN_FALL:
        print("SENDING xbee STOW")
        ipsStr = str(check_output(['hostname', '-I']))
        ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", ipsStr)[0]

        data = {"command":"STOW","deviceID":"00000000"}
        data = json.dumps(data).encode('utf8')
        req =  request.Request("http://"+ip+":5001/sendCommand", data=data,headers={'content-type': 'application/json'}) # this will make the method "POST"
        resp = request.urlopen(req)

p.cancel()
pi.stop()
