#!/usr/bin/python

import urllib2
import json
import sys
import time
import subprocess
import os
import binascii

# Launches specified number of Digital Ocean droplets and binds one Chrome instance to each droplet, 
# resulting in any number of separate windows (up to a reasonable limit) with different IPs.
# Requires a corresponding image on your DO account that starts a SOCKS proxy on boot (the script
# assumes this). Please do not use for anything malicious or illegal, this was made for testing a 
# P2P messaging application.

if len(sys.argv) < 2:
	print "\tPlease specify a number of proxies to launch:"
	print "\t./launch #"
	print "\t Exiting."
	exit(1)
droplets = int(sys.argv[1])
client_id = "YOUR ID"
api_key = "YOUR KEY"
print "DigitalOcean Client ID: " + client_id
print "DigitalOcean API key: " + api_key
image_id = "YOUR IMAGE ID"
size_id = "66"
sshkey_id = "YOUR SSH KEY ID"
region_slug = "nyc2"

# Create a random group ID so that we can launch multiple groups of droplets
group = binascii.b2a_hex(os.urandom(8))

for x in range(1,droplets+1):
	name = "P" + str(x) + "x" + group 
	api_string = ("https://api.digitalocean.com/droplets/new?" +
		      "client_id={0}&api_key={1}&name={2}&size_id={3}&image_id={4}&region_slug={5}&ssh_key_ids={6}"
	              .format(client_id, api_key, name, size_id, image_id, region_slug, sshkey_id))

	launch = urllib2.urlopen(api_string)
	response = json.load(launch)
	print "Sent request for proxy " + str(x) + "... " + response['status']
	if response['status'] == "ERROR":
		print "Uh oh, something went wrong. Printing response from API and exiting."
		print response
		exit(1)
	# Wait between GETs to prevent rate limiting
	time.sleep(3)

print "Now waiting for all proxies to finish booting. This will take 3 minutes."
time.sleep(60)
print "120 seconds left..."
time.sleep(60)
print "60 seconds left..."
time.sleep(60)
print "All proxies should now be initialized."
api_string = "https://api.digitalocean.com/droplets/?client_id={0}&api_key={1}".format(client_id, api_key)
check = urllib2.urlopen(api_string)
response = json.load(check)
print "Group ID for this machine: " + group
for droplet in response['droplets']:
	print droplet['name'] + ":  " + droplet['ip_address'] + "   " + droplet['status']

# For this next step, the private key with correct permissions must be in home dir
# And host checking should be turned off in ssh config
# And the image should auto-start port forwarding on 1080
print "Now opening windows!"
instance = 1
url = "http://whatsmyip.us"
window = "-n"
directory = "--user-data-dir=/your/path/to/chrome/cacher"
executable = "/your/path/to/chrome"
for droplet in response['droplets']:
	if group in droplet['name']:
		server = "--proxy-server=socks://" + droplet['ip_address']
		subprocess.Popen([executable, url, window, directory + str(instance), server])
		time.sleep(5)
		instance += 1
	

	



