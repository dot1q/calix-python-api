#!/usr/bin/python

#######################################################################
# Program Filename: login.py
# Author: Gregory Brewster
# Date: 4/9/2015
# Description: Adds SIP interface to ONT
#######################################################################

#add configuration module
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import config, login, logout

import urllib, urllib2, httplib, re
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString #for debugging


def connect():
   #print("Opening session with CMS...")
   sessionID = login.call()
   #print("Session ID for your session is "+str(sessionID)+"...")

   return sessionID

def disconnect(sessionID):
   #print("Clossing session "+str(sessionID)+"...")
   logout.call(sessionID)
   #print("Session terminated!")

def main(gpon_fsan, ontPots, sipUser, sipPass, uri, sipProfile, callWaiting, callerId, threeWayCalling, t38FaxRelay, dialPlan):
   #print ("running main!\n")
   session = connect() # connect to CMS
   ontId = pullOntId(session, gpon_fsan)
   #print ontId
   #Now that we have the ont, lets add the service
   addService(session, ontId, ontPots, sipUser, sipPass, uri, sipProfile, callWaiting, callerId, threeWayCalling, t38FaxRelay, dialPlan)

   disconnect(session) # disconnect from CMS

def pullOntId(sessionID, gpon_fsan):
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
   return parseOntId(resultRead)

def parseOntId(result):
   #store passed XML data at var data
   data = ET.fromstring(result)
   ont = "NULL ONT ID, MAY NOT EXIST!" #make sure the session is le null
   for elem in data.iter(tag='ont'):
      ont = elem.text
   #print ("operation completed! results, ont:",ont)
   return ont


def addService(sessionID, ont, ontPots, sipUser, sipPass, uri, sipProfile, callWaiting, callerId, threeWayCalling, t38FaxRelay, dialPlan):
   target_url = str(config.protocol)+'://'+str(config.host)+':'+str(config.port) +str(config.extension)
   xml_request = """
<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
 <soapenv:Body>
	 <rpc message-id="96" nodename="%s" username="%s" sessionid="%s" timeout="35000">
		 <edit-config>
		 <target>
			<running/>
		 </target>
		 <config>
			 <top>
				 <object operation="create" get-config="true">
					<type>SipSvc</type>
					<id>
						<ont>%s</ont>
						<ontslot>6</ontslot>
						<ontpots>%s</ontpots>
						<sipsvc>1</sipsvc>
					</id>
					<user>%s</user>
					<passwd>%s</passwd>
					<uri>%s</uri>
					<admin>enabled</admin>
					<sip-prof>
						<type>SipGwProf</type>
						<id>
							<sipgwprof>%s</sipgwprof>
						</id>
					</sip-prof>
					<call-waiting>%s</call-waiting>
					<caller-id-enabled>%s</caller-id-enabled>
					<three-way-calling>%s</three-way-calling>
					<t38-fax-relay>%s</t38-fax-relay>
					<sip-rmt-cfg-override>false</sip-rmt-cfg-override>
					<dial-plan>
						<type>DialPlan</type>
						<id>
							<dialplan>%s</dialplan>
						</id>
					</dial-plan>
					<enable-msg-waiting-ind>true</enable-msg-waiting-ind>
					<direct-connect></direct-connect>
					<direct-conn-timer-sec>0</direct-conn-timer-sec>
				 </object>
			 </top>
		 </config>
		 </edit-config>
	 </rpc>
 </soapenv:Body>
</soapenv:Envelope>
   """ % (config.nodename, config.username, sessionID, ont, ontPots, sipUser, sipPass, uri, sipProfile, callWaiting, callerId, threeWayCalling, t38FaxRelay, dialPlan)
#   print xml_request;
   request = urllib2.Request(target_url, xml_request)
   request.add_header('Content-Type','text/plain;charset=UTF-8')
   #resultRead = urllib2.urlopen(request).read()
   #uncommet these to print debug info
   result = urllib2.urlopen(request)
   print parse( result ).toprettyxml()
   result.close()

if __name__== "__main__":
   if len(sys.argv) <> 12:
      print "Usage:", sys.argv[0]," <fsan> <ontPots> <sipUser> <sipPass> <uri> <sipProfile> <callWaiting> <callerId> <threeWayCalling> <t38FaxRelay> <dialPlan>"
      print "Fsan or serial, 6 digits base 16"
      print "Ont Pot ID"
      print "Sip Username"
      print "Sip Password"
      print "URI"
      print "Sip Profile ID"
      print "Call Waiting"
      print "Caller ID"
      print "3 Way Calling"
      print "t38-fax-relay"
      print "Dialplan ID"
      sys.exit(1)
   gpon_fsan = sys.argv[1]
   ontPots = sys.argv[2]
   sipUser = sys.argv[3]
   sipPass = sys.argv[4]
   uri = sys.argv[5]
   sipProfile = sys.argv[6]
   callWaiting = sys.argv[7]
   callerId = sys.argv[8]
   threeWayCalling = sys.argv[9]
   t38FaxRelay = sys.argv[10]
   dialPlan = sys.argv[11]

   #arguments are expected to be correct at this point
   main(gpon_fsan, ontPots, sipUser, sipPass, uri, sipProfile, callWaiting, callerId, threeWayCalling, t38FaxRelay, dialPlan)

