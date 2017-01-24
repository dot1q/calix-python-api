#!/usr/bin/python

#######################################################################
# Program Filename: login.py
# Author: Gregory Brewster
# Date: 4/9/2015
# Description: Adds RG interface to ONT
#######################################################################

#add configuration module
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import config, login, logout

import urllib, urllib2, httplib, re
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString #for debugging

def connect():
   #print("This program will suspend or restore service to an ONT")
   #print("Opening session with CMS...")
   sessionID = login.call()
   #print("Session ID for your session is "+str(sessionID)+"...")

   return sessionID

def disconnect(sessionID):
   #print("Clossing session "+str(sessionID)+"...")
   logout.call(sessionID)
   #print("Session terminated!")

def main(gpon_type, gpon_fsan, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_subscr, gpon_description):
   #print ("running main!\n")
   session = connect() # connect to CMS
   pullOntId(session, gpon_type, gpon_fsan, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_subscr, gpon_description)
   disconnect(session) # disconnect from CMS

def pullOntId(sessionID, gpon_type, gpon_fsan, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_subscr, gpon_description):
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

   addService(sessionID, gpon_type, gpon_fsan, ont, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_subscr, gpon_description) 

def parseOntId(result):
   #store passed XML data at var data
   data = ET.fromstring(result)
   ont = "NULL ONT ID, MAY NOT EXIST!" #make sure the session is le null
   for elem in data.iter(tag='ont'):
      ont = elem.text
   #print ("operation completed! results, ont:",ont)
   return ont

def addService(sessionID, gpon_type, gpon_fsan, ont, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_subscr, gpon_description):
   target_url = str(config.protocol)+'://'+str(config.host)+':'+str(config.port) +str(config.extension)
   xml_request = """
<soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
	<soapenv:Body>
		<rpc message-id="37" nodename="%s" username="%s" sessionid="%s">
			<edit-config>
				<target>
					<running/>
				</target>
				<config>
					<top>
						<object operation="merge" >
							<type>%s</type>
							<id>
								<ont>%s</ont>
								<ontslot>%s</ontslot>
								<ontrg>%s</ontrg>
							</id>
							<admin>enabled</admin>
							<subscr-id>%s</subscr-id>
							<descr>%s</descr>
							<mgmt-prof>
								<type>OntRgMgmtProf</type>
								<id>
									<ontrgmgmtprof>3</ontrgmgmtprof>
								</id>
							</mgmt-prof>
						</object>
					</top>
				</config>
			</edit-config>
		</rpc>
	</soapenv:Body>
</soapenv:Envelope>
   """ % (config.nodename, config.username, sessionID, object_type, ont, gpon_ontSlot, gpon_ontEthAny, gpon_subscr.replace("&", "&amp;"), gpon_description.replace("&", "&amp;"))
   request = urllib2.Request(target_url, xml_request)
   request.add_header('Content-Type','text/plain;charset=UTF-8')
   resultRead = urllib2.urlopen(request).read()
   #uncommet these to print debug info
   result = urllib2.urlopen(request)
   print parse( result ).toprettyxml()
   result.close()

if __name__== "__main__":
   if len(sys.argv) <> 8:
      print "Usage:", sys.argv[0]," <type> <fsan> <type> <ontslot> <ontethany> <subscr-id> <description>"
      print "Type options - Usually 'Ont'"
      print "Fsan or serial, 6 digits base 16"
      print "Type, EX: Ethsvc"
      print "Ontslot, 8=RG, 9-FG, etc"
      print "OntEthAny, 1-8"
      sys.exit(1)
   gpon_type = sys.argv[1]
   gpon_fsan = sys.argv[2]
   object_type = sys.argv[3]
   gpon_ontSlot = sys.argv[4]
   gpon_ontEthAny = sys.argv[5]
   gpon_subscr = sys.argv[6]
   gpon_description = sys.argv[7]
   #arguments are expected to be correct at this point
   #print("Processing type: "+str(gpon_type)+" serial "+str(gpon_fsan)+" state "+str(gpon_state)+"\n"); #Debuging for inputs
   main(gpon_type, gpon_fsan, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_subscr, gpon_description)

