import netifaces
import os
import subprocess
import pymongo
import time
import sys
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["voyagerDB"]
mycol = mydb["wifi"]
x=mycol.find_one()
#subprocess.call(["sudo","systemctl","stop","hostapd","dnsmasq"])
if os.stat("/home/pi/Voyager-Zone-Controller/Networking/isScript.txt").st_size == 0:
    str="iptables-restore < /etc/iptables.ipv4.nat"
    subprocess.call(["sudo","sh","-c",str])
    subprocess.call(["sleep","2"])
    with open("/home/pi/Voyager-Zone-Controller/Networking/isScript.txt", "a") as myfile:
        myfile.write("Alive")
    sys.exit()

if mycol.count==0:
    if not os.stat("/home/pi/Voyager-Zone-Controller/Networking/isScript.txt").st_size == 0 :
        subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/sysctl.conf","/etc/sysctl.conf"])
        subprocess.call(["sleep","1"])
        subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/dhcpcd.conf","/etc/dhcpcd.conf"])
        subprocess.call(["sleep","1"])
        subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/dnsmasq.conf","/etc/dnsmasq.conf"])
        print("default files made")
        open('/home/pi/Voyager-Zone-Controller/Networking/isScript.txt','w').close()
        subprocess.call(["sleep","2"])
        print ("enter into apscript")
        subprocess.call(["sudo","python","/home/pi/Voyager-Zone-Controller/Networking/APscript.py"])
else:
    print("start")
    if not os.stat("/home/pi/Voyager-Zone-Controller/Networking/isScript.txt").st_size == 0:
        subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/wpa_supplicant.conf","/etc/wpa_supplicant/wpa_supplicant.conf"])
        subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/sysctl.conf","/etc/sysctl.conf"])
        subprocess.call(["sleep","1"])
        subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/dhcpcd.conf","/etc/dhcpcd.conf"])
        subprocess.call(["sleep","1"])
        subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/dnsmasq.conf","/etc/dnsmasq.conf"])
        ssid=x['ssid']
        password=x['password']
        target = '\nnetwork={\n\tssid=\"' +  ssid + '\"\n\tpsk=\"' + password + '\"\n\tkey_mgmt=WPA-PSK\n}\n'
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as myfile:
            myfile.write(target)
        print (target)
        subprocess.call(["sudo", "systemctl", "stop", "hostapd","dnsmasq"])
        subprocess.call(["sudo", "systemctl", "daemon-reload"])
        subprocess.call(["sudo", "systemctl", "restart", "dhcpcd"])
        time.sleep(15)
        addr = netifaces.ifaddresses('wlan0')
        bool=netifaces.AF_INET in addr
        print(bool)
    if (bool):
        subprocess.call(["sudo","python3","/home/pi/Voyager-Zone-Controller/Networking/always_on.py"])
    else:
        if not os.stat("/home/pi/Voyager-Zone-Controller/Networking/isScript.txt").st_size == 0 :
            subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/sysctl.conf","/etc/sysctl.conf"])
            subprocess.call(["sleep","1"])
            subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/dhcpcd.conf","/etc/dhcpcd.conf"])
            subprocess.call(["sleep","1"])
            subprocess.call(["sudo", "cp", "-f","/home/pi/Voyager-Zone-Controller/Networking/dnsmasq.conf","/etc/dnsmasq.conf"])
            subprocess.call(["sudo", "cp", "-f", "/home/pi/Voyager-Zone-Controller/Networking/wpa_supplicant.conf","/etc/wpa_supplicant/wpa_supplicant.conf"])
            print("default files made")
            open('/home/pi/Voyager-Zone-Controller/Networking/isScript.txt','w').close()
            subprocess.call(["sleep","2"])
            print ("enter into apscript")
            subprocess.call(["sudo","python","/home/pi/Voyager-Zone-Controller/Networking/APscript.py"])

