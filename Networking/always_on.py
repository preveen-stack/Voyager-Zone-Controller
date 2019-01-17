import netifaces
import os
import subprocess
import time
print("running always on")
time.sleep(15)
while True:
    addr = netifaces.ifaddresses('wlan0')
    if (netifaces.AF_INET in addr):
        print(netifaces.AF_INET in addr)
        time.sleep(30)
    else:
        print(netifaces.AF_INET in addr)
        if not os.stat("/home/pi/Voyager-Zone-Controller/Networking/isScript.txt").st_size == 0:
            subprocess.call(["sudo", "cp", "-f", "/home/pi/Voyager-Zone-Controller/Networking/sysctl.conf", "/etc/sysctl.conf"])
            subprocess.call(["sleep", "1"])
            subprocess.call(["sudo", "cp", "-f", "/home/pi/Voyager-Zone-Controller/Networking/dhcpcd.conf", "/etc/dhcpcd.conf"])
            subprocess.call(["sleep", "1"])
            subprocess.call(["sudo", "cp", "-f", "/home/pi/Voyager-Zone-Controller/Networking/dnsmasq.conf", "/etc/dnsmasq.conf"])
            subprocess.call(["sudo", "cp", "-f", "/home/pi/Voyager-Zone-Controller/Networking/wpa_supplicant.conf","/etc/wpa_supplicant/wpa_supplicant.conf"])
            print("default files made")
            open('/home/pi/Voyager-Zone-Controller/Networking/isScript.txt', 'w').close()
            subprocess.call(["sleep", "2"])
            print ("enter into apscript")
            subprocess.call(["sudo", "python", "/home/pi/Voyager-Zone-Controller/Networking/APscript.py"])
