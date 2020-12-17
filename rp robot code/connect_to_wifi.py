# purpose of this code is to get from the user ssid and password,
# and write to "wpa_supplicant.conf" all the needed configurations to connect to the user network
import os
from subprocess import call
import sys
 
# this file is responsible for the wifi connection settings
# r+ -> because w is override the file and the OS couldnt run this command:"sudo wpa_cli -i wlan0 reconfigure"
x = open('/etc/wpa_supplicant/wpa_supplicant.conf','r+')

# delete the file content
x.truncate(0)

# write to the file the needed wifi header settings
x.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n"+
        "update_config=1\n" +
        "country=IL\n\n")
x.close()

# command that write ssid and password that was given from the user, to the file: "wpa_supplicant.con"
add_network_configuration =f"sudo sh -c \"wpa_passphrase '{sys.argv[1]}' '{sys.argv[2]}' >> /etc/wpa_supplicant/wpa_supplicant.conf\""

call(add_network_configuration, shell=True)
