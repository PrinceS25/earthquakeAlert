# STARTUP 

# Install:
# $ sudo apt-get update
# $ sudo apt-get install build-essential git
# $ sudo apt-get install python-dev python-smbus python-pip 
# $ sudo apt-get install i2c-tools
#
# Usage via cron: 
# $ crontab -e
# @reboot sudo python /home/pi/Desktop/earthquakeAlert/startup.py >/dev/null 2>&1
#


import time
import socket

time.sleep(10)	# Need time for WiFi to connect

# Find local IP address
myip = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
print ("earthquakeAlert started at IP:", myip)
