# -*- coding: utf-8 -*-
"""
Created on Fri Nov 28 01:37:48 2014

@author: Maurice Spiegels
"""
import linecache
import re
import sys
import time
NuanceDNSlog = 'C:\ProgramData\Nuance\NaturallySpeaking12\Users\Maurice (v12)\RecogLog.txt'
firstrun = True

def Init():
    global NuanceDNSlog
    
    # read a text file as a list of lines
    # find the last line, change to a file you have
    fileHandle = open (NuanceDNSlog,"r")
    lineList = fileHandle.readlines()
    fileHandle.close()
    nextline = len(lineList)+1
#    print lineList
    lineList = []
    print "The last line is (", nextline-1,")"
    
    return nextline

def GetWords(stop=False, PollingRate=0.01):
    global firstrun
    global nextline
    
    time.sleep(PollingRate)
    words = ['<???>']
    if stop == False:
        if firstrun == True:
            nextline = Init()
            firstrun = False
        else:
            linecache.checkcache(NuanceDNSlog)
            sentence = linecache.getline(NuanceDNSlog,nextline)
            
            if sentence != '': # Is returned when reading line >= EOF
                nextline += 1
                print '\n'+sentence
                words = re.split('[|]', sentence)
                print words[-1]
                words = words[-1].split()
                #print words
            else:
                words = ['<???>']
                pass
                #sys.stdout.write('.')
                #print "previous line number was:", nextline
                #nextline = raw_input("give next line number:")
             
    elif stop == True:
        linecache.clearcache()
    
    return words