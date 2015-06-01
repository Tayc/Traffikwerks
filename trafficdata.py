#!/usr/bin/env python

import requests
import time

i = 598

while True:
	r = requests.get('http://207.251.86.229/nyc-links-cams/LinkSpeedQuery.txt')
	address = '/home/god/Desktop/Data/trafficNYC{:04d}.txt'.format(i)
	i += 1
	printer = open(address, "w")
	printer.write(r.text)
	printer.close()
	time.sleep(60)
	
				
