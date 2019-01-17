import subprocess
with open("/etc/dhcpcd.conf", "a") as myfile:
    myfile.write("interface wlan0\n static ip_address=192.168.4.1/24\n nohook wpa_supplicant")
subprocess.call(["sleep","2"])
subprocess.call(["sudo","systemctl","daemon-reload"])
subprocess.call(["sleep","2"])
subprocess.call(["sudo","systemctl","restart","dhcpcd"])
subprocess.call(["sleep","2"])
with open("/etc/dnsmasq.conf", "a") as myfile:
    myfile.write("interface=wlan0\n  dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h")
subprocess.call(["sleep","2"])
subprocess.call(["sudo","systemctl","start","hostapd"])
subprocess.call(["sleep","5"])
subprocess.call(["sudo","systemctl","start","dnsmasq"])
subprocess.call(["sleep","5"])


with open("/etc/sysctl.conf", "a") as myfile:
    myfile.write("\nnet.ipv4.ip_forward=1")


subprocess.call(["sleep","2"])
subprocess.call(["sudo","iptables","-t","nat","-A","POSTROUTING","-o","eth0","-j","MASQUERADE"])
subprocess.call(["sleep","2"])
str="iptables-save > /etc/iptables.ipv4.nat"

subprocess.call(["sudo","sh","-c",str])
subprocess.call(["sleep","2"])
print("Just before reboot")
subprocess.call(["sudo","reboot"])
