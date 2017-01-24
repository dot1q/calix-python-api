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

def main(gpon_fsan):
   #print ("running main!\n")
   session = connect() # connect to CMS
   ontId = pullOntId(session, gpon_fsan)
   #print ontId
   #Now that we have the ont, lets add the service
   createIpHost(session, ontId)

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

def createIpHost(sessionID, ont):
   target_url = str(config.protocol)+'://'+str(config.host)+':'+str(config.port) +str(config.extension)
   xml_request = """
<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
	<soapenv:Body>
		<rpc message-id="333" nodename="%s" username="%s" sessionid="%s">
			<edit-config>
				<target>
					<running/>
				</target>
				<config>
					<top>
						<object operation="merge" get-config="true">
							<type>OntIpHost</type>
							<id>
								<ont>%s</ont>
								<ontiphost>1</ontiphost>
							</id>
							<tag-action>
							<type>SvcTagAction</type>
							<id>
								<svctagaction>10</svctagaction>
							</id>
							</tag-action>
							<out-tag>none</out-tag>
							<in-tag>none</in-tag>
							<host-proto>dhcp</host-proto>
						</object>
					</top>
				</config>
			</edit-config>
		</rpc>
	</soapenv:Body>
</soapenv:Envelope>
   """ % (config.nodename, config.username, sessionID, ont)
#   print xml_request;
   request = urllib2.Request(target_url, xml_request)
   request.add_header('Content-Type','text/plain;charset=UTF-8')
 #line below is the one that that causes errors. REmove it
   #resultRead = urllib2.urlopen(request).read()
   #uncommet these to print debug info
   result = urllib2.urlopen(request)
   print parse( result ).toprettyxml()
   result.close()

if __name__== "__main__":
   if len(sys.argv) <> 2:
      print "Usage:", sys.argv[0]," <fsan> "
      print "Fsan or serial, 6 digits base 16"
      sys.exit(1)
   gpon_fsan = sys.argv[1]

   #arguments are expected to be correct at this point
   main(gpon_fsan)

