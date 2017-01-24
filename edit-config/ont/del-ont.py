#!/usr/bin/python

#######################################################################
# Program Filename: create-ont.py
# Author: Gregory Brewster
# Date: 7/28/2015
# Description: Deletes an ONT from CMS
#######################################################################

#add configuration module
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import config, login, logout

import urllib, urllib2, httplib, re
import xml.etree.ElementTree as ET
import xml.dom.minidom

def connect():
   #print("Opening session with CMS...")
   sessionID = login.call()
   #print("Session ID for your session is "+str(sessionID)+"...")

   return sessionID

def disconnect(sessionID):
   #print("Clossing session "+str(sessionID)+"...")
   logout.call(sessionID)
   #print("Session terminated!")

def main(gpon_type, gpon_fsan, forced):
   #print ("running main!\n")
   session = connect() # connect to CMS
   pulldata(session, gpon_type, gpon_fsan, forced)
   disconnect(session) # disconnect from CMS

def parseOntId(result):
   #store passed XML data at var data
   data = ET.fromstring(result)
   ont = "0" #make sure the session is le null
   for elem in data.iter(tag='ont'):
      ont = elem.text
   #print ("operation completed! results, ont:",ont)
   return ont

def pulldata(sessionID, gpon_type, gpon_fsan, forced):
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
   if(forced == "true"):
      force_argument = 'force="true"'
   else:
      force_argument = ""
      
   delOnt(sessionID, gpon_type, ont, force_argument)

def delOnt(sessionID, gpon_type, ont, forced):
   target_url = str(config.protocol)+'://'+str(config.host)+':'+str(config.port) +str(config.extension)
   xml_request = """
<soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
  <soapenv:Body>
    <rpc message-id="3" nodename="%s" username="%s" sessionid="%s">
      <edit-config>
        <target><running/></target>
        <config>
          <top>
            <object operation="delete" %s>
              <type>%s</type>
              <id>
                <ont>%s</ont>
              </id>
            </object>
          </top>
        </config>
      </edit-config>
    </rpc>
  </soapenv:Body>
</soapenv:Envelope>
   """ % (config.nodename, config.username, sessionID, forced, gpon_type, ont)
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
   if len(sys.argv) <> 4:
      print "Usage:", sys.argv[0]," <type> <fsan> <forced>"
      print "Type options - Usually 'Ont'"
      print "Fsan or serial, 6 digits base 16"
      print "Forced, (true, false)"
      sys.exit(1)
   gpon_type = sys.argv[1]
   gpon_fsan = sys.argv[2]
   forced = sys.argv[3]
   #arguments are expected to be correct at this point

   main(gpon_type, gpon_fsan, forced)

