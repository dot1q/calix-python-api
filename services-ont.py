#!/usr/bin/python

#######################################################################
# Program Filename: login.py
# Author: Gregory Brewster
# Date: 4/9/2015
# Description: Disables or restores service to an ONT
#######################################################################

#add configuration module
import config
import login
import logout

import sys
import urllib, urllib2, httplib, re
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString #for debugging

def connect():
   print("This program will suspend or restore service to an ONT")
   print("Opening session with CMS...")
   sessionID = login.call()
   print("Session ID for your session is "+str(sessionID)+"...")

   return sessionID

def disconnect(sessionID):
   print("Clossing session "+str(sessionID)+"...")
   logout.call(sessionID)
   print("Session terminated!")

def main(gpon_type, gpon_fsan, gpon_state):
   #print ("running main!\n")
   session = connect() # connect to CMS
   pulldata(session, gpon_type, gpon_fsan, gpon_state)
   disconnect(session) # disconnect from CMS

def pulldata(sessionID, gpon_type, gpon_fsan, gpon_state):
   target_url = str(config.protocol)+'://'+str(config.host)+':'+str(config.port) +str(config.extension)
   xml_request = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soapenv:Body>
      <rpc message-id="1" nodename="%s" username="%s" sessionid="%s">
         <action>
            <action-type>show-ont</action-type>
            <action-args><serno>%s</serno></action-args>
         </action>
      </rpc>
   </soapenv:Body>
</soapenv:Envelope>
   """ % (config.nodename, config.username, sessionID, gpon_fsan)

   request = urllib2.Request(target_url, xml_request)
   request.add_header('Content-Type','text/plain;charset=UTF-8')
   resultRead = urllib2.urlopen(request).read()
   #uncommet these to print debug info
   #result = urllib2.urlopen(request)
   #print parse( result ).toprettyxml()
   #result.close()
   ont = parseOntId(resultRead)

   disableRG(sessionID, gpon_type, gpon_fsan, gpon_state, ont) #disable Residential Gateway (modify for ge, pots, etc)

def parseOntId(result):
   #store passed XML data at var data
   data = ET.fromstring(result)
   ont = "null dude" #make sure the session is le null
   for elem in data.iter(tag='ont'):
      ont = elem.text
   print ("operation completed! results, ont:",ont)
   return ont

def disableRG(sessionID, gpon_type, gpon_fsan, gpon_state, ont):
   target_url = str(config.protocol)+'://'+str(config.host)+':'+str(config.port) +str(config.extension)
   if (gpon_state == 1):
      gpon_state = "enabled"
   elif (gpon_state == 0):
      gpon_state = "disabled"
   else:
      gpon_state = "enabled"
   xml_request = """
<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
   <soapenv:Body>
      <rpc message-id="180" nodename="%s" username="%s" sessionid="%s">
         <edit-config>
            <target>
               <running/>
            </target>
            <config>
	       <top>
	          <object operation="merge">
		    <type>Ont</type>
		       <id>
		          <ont>%s</ont>
		       </id>
		    <admin>%s<admin>
		  </object>
	       </top>
            </config>
         </edit-config>
      </rpc>
   </soapenv:Body>
</soapenv:Envelope>
   """ % (config.nodename, config.username, sessionID, ont, gpon_state)
   request = urllib2.Request(target_url, xml_request)
   request.add_header('Content-Type','text/plain;charset=UTF-8')
   resultRead = urllib2.urlopen(request).read()
   #uncommet these to print debug info
   result = urllib2.urlopen(request)
   print parse( result ).toprettyxml()
   result.close()

if __name__== "__main__":
   if len(sys.argv) <> 4:
      print "Usage:", sys.argv[0]," <type> <fsan> <status>"
      print "Type options - Usually 'Ont'"
      print "Fsan or serial, 6 digits base 16"
      print "Status - 0=suspended, 1=active"
      sys.exit(1)
   gpon_type = sys.argv[1]
   gpon_fsan = sys.argv[2]
   gpon_state = sys.argv[3]
   #arguments are expected to be correct at this point

   main(gpon_type, gpon_fsan, gpon_state)

