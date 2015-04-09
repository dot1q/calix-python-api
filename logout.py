#!/usr/bin/python

####################################################################### 
# Program Filename: logout.py
# Author: Gregory Brewster
# Date: 4/9/2015
# Description: Logs out of CMS XML API
#######################################################################

#import config module!
import config

import sys
import urllib
import urllib2
import httplib
import re
import xml.etree.ElementTree as ET

sessionID = sys.argv[1]
target_url = str(config.protocol)+'://'+str(config.host)+':'+str(config.port)+str(config.extension)
#Request string goes here
xml_request = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <auth message-id="2">
      <logout>
        <UserName>%s</UserName>
        <SessionId>%s</SessionId>
      </logout>
    </auth>
  </soapenv:Body>
</soapenv:Envelope>
""" % (config.username, sessionID)


def send_xml():
  #Send target_url and xml_request to cms server, result is what was returned
  #NOTE! you must specify the header properly, or you will get an error returned!
  req = urllib2.Request(target_url, xml_request)
  req.add_header('Content-Type','text/plain;charset=UTF-8')
  result = urllib2.urlopen(req).read()
  #if you get no errors, assume you are logged out. Might want to check CMS to make sure it worked!


def main():   
  send_xml()

if __name__ == "__main__":
  main()
