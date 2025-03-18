# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 15:45:16 2014

@author: Maurice Spiegels
"""
from naoqi import ALProxy
import random
import time

NAO_IP = "192.168.0.114"

leds = ALProxy("ALLeds", NAO_IP, 9559)
off = 0x000000
on = 0xffffff #led=wit
leds.fadeRGB( "FaceLeds", on, 0)  
leds.fadeRGB( "RightEarLeds", off, 0)  
leds.fadeRGB( "LeftEarLeds", off, 0)

while True:
    rDur = 0
    zleep = 0.02 #eye blink speed 
    time.sleep(random.uniform(2.0,10.0))
    #----------------------------------------------['close' eye-lid]
    leds.post.fadeRGB( "FaceLed0", off, rDur )  
    time.sleep(zleep)
    leds.post.fadeRGB( "FaceLed1", off, rDur ) 
    leds.post.fadeRGB( "FaceLed7", off, rDur ) 
    time.sleep(zleep)
    leds.post.fadeRGB( "FaceLed2", off, rDur ) 
    leds.post.fadeRGB( "FaceLed6", off, rDur ) 
    time.sleep(zleep)
    leds.post.fadeRGB( "FaceLed3", off, rDur ) 
    leds.post.fadeRGB( "FaceLed5", off, rDur ) 
    time.sleep(zleep)
    leds.post.fadeRGB( "FaceLed4", off, rDur )
    time.sleep(zleep)
    #----------------------------------------------['open' eye-lid]       
    leds.post.fadeRGB( "FaceLed4", on, rDur ) 
    time.sleep(zleep)
    leds.post.fadeRGB( "FaceLed5", on, rDur ) 
    leds.post.fadeRGB( "FaceLed3", on, rDur ) 
    time.sleep(zleep)
    leds.post.fadeRGB( "FaceLed6", on, rDur ) 
    leds.post.fadeRGB( "FaceLed2", on, rDur ) 
    time.sleep(zleep)
    leds.post.fadeRGB( "FaceLed7", on, rDur ) 
    leds.post.fadeRGB( "FaceLed1", on, rDur )
    time.sleep(zleep) 
    leds.post.fadeRGB( "FaceLed0", on, rDur ) 
    time.sleep(zleep) 