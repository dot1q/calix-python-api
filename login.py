#!/usr/bin/python

####################################################################### 
# Program Filename: login.py
# Author: Gregory Brewster
# Date: 4/9/2015
# Description: Logs into the CMS XML API
#######################################################################

#If 0 is returned for return code, then login was successful! Have yourself a beer!

#add configuration module
import config

import urllib
import urllib2
import httplib
import re
import xml.etree.ElementTree as ET


def call():
   target_url = str(config.protocol)+'://'+str(config.host)+':'+str(config.port) +str(config.extension)

   #Request string goes here
   xml_request = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <auth message-id="1">
      <login>
        <UserName>%s</UserName>
        <Password>%s</Password>
      </login>
    </auth>
  </soapenv:Body>
</soapenv:Envelope>
""" % (config.username, config.password)
   return send_xml(target_url,xml_request)


def send_xml(target_url,xml_request):
  #Send target_url and xml_request to cms server, result is what was returned
  #NOTE! you must specify the header properly, or you will get an error returned!
  req = urllib2.Request(target_url, xml_request)
  req.add_header('Content-Type','text/plain;charset=UTF-8')
  result = urllib2.urlopen(req).read()  
  return parseSession(result) 

def parseSession(result):
   #store passed XML data at var data
   data = ET.fromstring(result)
   #print data
   session = "null dude"
   for elem in data.iter(tag='SessionId'):
      session = elem.text
   #print(session)

   return session

