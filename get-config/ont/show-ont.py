#!/usr/bin/python

#######################################################################
# Program Filename: login.py
# Author: Gregory Brewster
# Date: 4/9/2015
# Description: Displays status of a unit
#######################################################################

#add configuration module
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import config, login, logout

import urllib, urllib2, httplib, re
import xml.dom.minidom 

def connect():
   #print("This program will display the status of an ONT in XML")
   #print("Opening session with CMS...")
   sessionID = login.call()
   #print("Session ID for your session is "+str(sessionID)+"...")

   return sessionID

def disconnect(sessionID):
   #print("Clossing session "+str(sessionID)+"...")
   logout.call(sessionID)
   #print("Session terminated!")

def main(gpon_type, gpon_fsan):
   #print ("running main!\n")
   session = connect() # connect to CMS
   pulldata(session, gpon_type, gpon_fsan)
   disconnect(session) # disconnect from CMS

def pulldata(sessionID, gpon_type, gpon_fsan):
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
   #result = urllib2.urlopen(request).read()
   result = urllib2.urlopen(request)
   #print result
   output =  xml.dom.minidom.parse(result)
   print output.toprettyxml()
   result.close()
   #parseSession(result)



if __name__== "__main__":
   if len(sys.argv) <> 3:
      print "Usage:", sys.argv[0]," <type> <fsan>"
      print "Type options - Usually 'Ont'"
      print "Fsan or serial, 6 digits base 16"
      sys.exit(1)
   gpon_type = sys.argv[1]
   gpon_fsan = sys.argv[2]
   #arguments are expected to be correct at this point

   main(gpon_type, gpon_fsan)

