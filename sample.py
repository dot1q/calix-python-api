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
import login
import logout


print("This is a sample file, made to login, and then logout of the Calix CMS system for e7!")
print("Opening session with CMS...")
sessionID = login.call()
print("Session ID for your session is "+str(sessionID)+"...")
print("Clossing session "+str(sessionID)+"...")
logout.call(sessionID)
print("Session terminated!")
