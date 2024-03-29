import os
import RPi.GPIO as GPIO
import datetime
import threading
import sys
import time
import logging

# SYSTEM REQUIREMENTS: mail.mailutils and configured for gmail relay e.g. https://wiki.debian.org/GmailAndExim4
# configured in /etc/ssmtp/ssmtp.conf

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/var/log/sump.alarm.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

textemail = "3014486005@vtext.com,larrucifer@gmail.com,lsymms@gmail.com"
 
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN)


def alarmThread():
	logger.info("starting alarm thread" + '\n')
	pressed = False

	while True:
        	if ( GPIO.input(23) == False and pressed == False):
			pressed = True
			logger.info("sending alarm text" + '\n')
                	os.system('echo "SUMP PUMP ALARM!!!" | mail -s "SUMP PUMP ALARM!!!" '+ textemail +'  &')
	        	time.sleep(30)
        	elif ( GPIO.input(23) == True and pressed == True):
			pressed = False 
			logger.info("alarm has turned off" + '\n')
                	os.system('echo "Sump Pump Normal" | mail -s "Sump Pump Normal" '+ textemail +'   &')
	        	time.sleep(30)
		else:
			logger.debug("alarm thread: situation normal" + '\n')
        	time.sleep(0.1)


alarm = threading.Thread(target=alarmThread)

alarm.start()

sendOkMsg = False

#2:30pm/3:30pm
monitorTime = datetime.time(hour=19, minute=30, second=0);

timeBetweenMonitorUpdates = datetime.timedelta(minutes=15);

lastMonitorFileTouch = datetime.datetime.now() - timeBetweenMonitorUpdates;

logger.info("Starting monitoring of Sump Pump")
os.system('echo "Starting monitoring of Sump Pump" | mail -s "Starting monitoring of Sump Pump" '+ textemail +'   &')

while True:
	now = datetime.datetime.now()

	if ( (now - lastMonitorFileTouch) > timeBetweenMonitorUpdates ): 

                exists = os.path.isfile('/mnt/zfs500raidz/sumpMonitorMonitor.sh')
                if exists:
                        logger.debug("touching sumpMonitor.touch file" + '\n')
                        os.system('touch /mnt/zfs500raidz/sumpMonitor.touch')
                else:
                        logger.debug("zfs not mounted or unable to connect to nfs" + '\n')

	if ( now.time() > monitorTime and sendOkMsg == False):
		sendOkMsg = True
		logger.info("sending ok message" + '\n')
             	os.system('echo "Sump Pump Monitor OK" | mail -s "Sump Pump Monitor OK" larrucifer@gmail.com  &')
	elif ( now.time() < monitorTime and sendOkMsg == True):
		sendOkMsg = False
		logger.info("reset monitor message trigger flag" + '\n')
	else:
		logger.debug("time thread: nothing to do " + str(now) + '\n')		
	time.sleep(15)
