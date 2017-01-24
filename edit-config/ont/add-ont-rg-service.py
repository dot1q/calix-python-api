#!/usr/bin/python

#######################################################################
# Program Filename: login.py
# Author: Gregory Brewster
# Date: 4/9/2015
# Description: creates an RG service to an ONT
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

def main(gpon_type, gpon_fsan, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_ethsvc, gpon_svcTagAction, gpon_bwProf, gpon_in_tag, gpon_out_tag):
   #print ("running main!\n")
   session = connect() # connect to CMS
   pullOntId(session, gpon_type, gpon_fsan, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_ethsvc, gpon_svcTagAction, gpon_bwProf, gpon_in_tag, gpon_out_tag)
   disconnect(session) # disconnect from CMS

def pullOntId(sessionID, gpon_type, gpon_fsan, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_ethsvc, gpon_svcTagAction, gpon_bwProf, gpon_in_tag, gpon_out_tag):
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

   addService(sessionID, gpon_type, gpon_fsan, ont, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_ethsvc, gpon_svcTagAction, gpon_bwProf, gpon_in_tag, gpon_out_tag) 

def parseOntId(result):
   #store passed XML data at var data
   data = ET.fromstring(result)
   ont = "NULL ONT ID, MAY NOT EXIST!" #make sure the session is le null
   for elem in data.iter(tag='ont'):
      ont = elem.text
   #print ("operation completed! results, ont:",ont)
   return ont

def addService(sessionID, gpon_type, gpon_fsan, ont, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_ethsvc, gpon_svcTagAction, gpon_bwProf, gpon_in_tag, gpon_out_tag):
   target_url = str(config.protocol)+'://'+str(config.host)+':'+str(config.port) +str(config.extension)
   xml_request = """
<soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
        <soapenv:Body>
                <rpc message-id="62" nodename="%s" username="%s" sessionid="%s">
                    <edit-config>
						<target>
							<running/>
						</target>
						<config>
							<top>
								<object operation="create" get-config="true">
									<type>%s</type>
									<id>
										<ont>%s</ont>
										<ontslot>%s</ontslot>
										<ontethany>%s</ontethany>
										<ethsvc>%s</ethsvc>
									</id>
									<admin>enabled</admin>
									<descr>Service added by Intranet</descr>
									<tag-action>
										<type>SvcTagAction</type>
										<id>
											<svctagaction>%s</svctagaction>
										</id>
									</tag-action>
									<bw-prof>
										<type>BwProf</type>
										<id>
											<bwprof>%s</bwprof>
										</id>
									</bw-prof>
									<out-tag>%s</out-tag>
									<in-tag>%s</in-tag>
									<mcast-prof></mcast-prof>
									<pon-cos>derived</pon-cos>
								</object>
							</top>
						</config>
                    </edit-config>
                </rpc>
        </soapenv:Body>
</soapenv:Envelope>
   """ % (config.nodename, config.username, sessionID, object_type, ont, gpon_ontSlot, gpon_ontEthAny, gpon_ethsvc, gpon_svcTagAction, gpon_bwProf, gpon_in_tag, gpon_out_tag)
   request = urllib2.Request(target_url, xml_request)
   request.add_header('Content-Type','text/xml; charset=utf-8')
   #resultRead = urllib2.urlopen(request).read()
   #uncommet these to print debug info
   result = urllib2.urlopen(request)
   print parse( result ).toprettyxml()
   result.close()

if __name__== "__main__":
   if len(sys.argv) <> 11:
      print "Usage:", sys.argv[0]," <type> <fsan> <type> <ontslot> <ontethany> <ethsvc> <svctagaction> <bwprof> <in-tag> <out-tag>"
      print "Type options - Usually 'Ont'"
      print "Fsan or serial, 6 digits base 16"
      print "Type, EX: Ethsvc"
      print "Ontslot, 8=RG, 9-FG, etc"
      print "OntEthAny, 1-8"
      print "EthSvc, 1-12"
      print "SvcTagAction, place the profile id here"
      print "BwProf, bandwidth profile id here"
      print "In-Tag, in vlan"
      print "Out-tag, out vlan"
      sys.exit(1)
   gpon_type = sys.argv[1]
   gpon_fsan = sys.argv[2]
   object_type = sys.argv[3]
   gpon_ontSlot = sys.argv[4]
   gpon_ontEthAny = sys.argv[5]
   gpon_ethsvc = sys.argv[6]
   gpon_svcTagAction = sys.argv[7]
   gpon_bwProf = sys.argv[8]
   gpon_in_tag = sys.argv[9]
   gpon_out_tag = sys.argv[10]
   #arguments are expected to be correct at this point
   #print("Processing type: "+str(gpon_type)+" serial "+str(gpon_fsan)+" state "+str(gpon_state)+"\n"); #Debuging for inputs
   main(gpon_type, gpon_fsan, object_type, gpon_ontSlot, gpon_ontEthAny, gpon_ethsvc, gpon_svcTagAction, gpon_bwProf, gpon_in_tag, gpon_out_tag)

