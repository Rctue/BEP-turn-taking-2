from math import exp
from scipy.io import loadmat
from naoqi import ALProxy
import vision_definitions as vd
import cv
import cv2
import numpy
import time
import os
import sys
import nao
import datetime
import numpy as np

currentpath = os.path.dirname(sys.argv[0])+'/'
firstrun = True
count = 0
facelocation = list((0,0))   #centre coordinates in approx. radians.
runAVG = []
NAO_PORT = 9559
MYWINDOW="Camera_Window"
ExitNAO_IP = None
ExituseNAOcam = None
ExitVideoFile = None
ExitfacedetectTYPE = None
KeyPress = 0
writer = None
InitVideofile = True
resolution = (640,480)          # Default value

TRAINED_NEURAL_NETWORK = currentpath+"pythonNN.mat"
mat = loadmat(TRAINED_NEURAL_NETWORK)
offset_pitch = 0 #-10
offset_yaw = 0 #-10
pitch_yaw = list([0,0])

outpitch = list()
outpitch_mirrored = list()
outyaw = list()
outyaw_mirrored = list()

class Region:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

def tansig(number):
    x = list()
    for i in range (0,len(number)):
        x.append((exp(number[i]) - exp(-number[i])) /(exp(number[i]) + exp(-number[i])))
    return numpy.asarray(x)

def mapminmax(array):
    difference = array.max() - array.min()
    array = array - (difference/2)
    array = array / (difference/2)
    return array

def remap(array):
    out = list()
    for i in range(0,len(array)):
        out.append(array[i][0])
    return numpy.asarray(out)

def detect_faces(image):
    #HAAR_CASCADE_PATH = "C:\SimpleCV1.3\files\opencv\opencv\sources\data\haarcascades\haarcascade_frontalface_default.xml"
    HAAR_CASCADE_PATH = currentpath+"haarcascade_frontalface_default.xml"
    storage = cv.CreateMemStorage()
    cascade = cv.Load(HAAR_CASCADE_PATH)
    faces = []
    detected = cv.HaarDetectObjects(image, cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (100,100))
    if detected:
        for (x,y,w,h),n in detected:
            faces.append((x,y,w,h,n))
        faces.reverse()
    return faces, len(faces)

def PitchYaw(image):
    global mat
    global image_list
    global outpitch
    global outpitch_mirrored
    global outyaw
    global outyaw_mirrored

    image_list= list()
    for i in range(0,90): # Convert image to list
        for j in range(0,40):
            image_list.append(image[i,j])

    image_list_mirrored= list()
    for i in range(0,90): # Convert image to list
        for j in range(39,-1,-1):
            image_list_mirrored.append(image[i,j])

    outpitch = list()
    for i in range(1,11): # Calculate pitch for all available Networks
        if i > 9:
            name = str(i)
        else:
            name = '0'+str(i)
        #start_time = time.clock()
        #print "10, ", clock()-start_time
        w1 = mat["pitch_0"+name+"_w1"]
        w2 = mat["pitch_0"+name+"_w2"][0]
        rangenet = mat["pitch_0"+name+"_range"]
        b1 = mat["pitch_0"+name+"_b1"]
        b1 = remap(b1)
        b2 = mat["pitch_0"+name+"_b2"]
        b2 = remap(b2)
        #print "11, ", clock()-start_time

        image_ar = numpy.asarray(image_list)
        image_ar = mapminmax(image_ar)
        
        layer1out = tansig(numpy.dot(w1,image_ar)+b1)

        layer2out = numpy.dot(layer1out, w2)+b2;
        range_multi = (rangenet[0][1]-rangenet[0][0])/2;
        outpitch.append(range_multi*layer2out)

    outpitch_mirrored = list()
    for i in range(1,11): # Calculate pitch for all available Networks
        if i > 9:
            name = str(i)
        else:
            name = '0'+str(i)
            
        w1 = mat["pitch_0"+name+"_w1"]
        w2 = mat["pitch_0"+name+"_w2"][0]
        rangenet = mat["pitch_0"+name+"_range"]
        b1 = mat["pitch_0"+name+"_b1"]
        b1 = remap(b1)
        b2 = mat["pitch_0"+name+"_b2"]
        b2 = remap(b2)

        image_ar = numpy.asarray(image_list_mirrored)
        image_ar = mapminmax(image_ar)

        layer1out = tansig(numpy.dot(w1,image_ar)+b1)

        layer2out = numpy.dot(layer1out, w2)+b2;
        range_multi = (rangenet[0][1]-rangenet[0][0])/2;
        outpitch_mirrored.append(range_multi*layer2out)

    outyaw = list()
    for i in range(1,11):
        if i > 9:
            name = str(i)
        else:
            name = '0'+str(i)

        w1 = mat["yaw_0"+name+"_w1"]
        w2 = mat["yaw_0"+name+"_w2"][0]
        rangenet = mat["yaw_0"+name+"_range"]
        b1 = mat["yaw_0"+name+"_b1"]
        b1 = remap(b1)
        b2 = mat["yaw_0"+name+"_b2"]
        b2 = remap(b2)
        
        
        image_ar = numpy.asarray(image_list)
        image_ar = mapminmax(image_ar)

        layer1out = tansig(numpy.dot(w1,image_ar)+b1)

        layer2out = numpy.dot(layer1out, w2)+b2;
        range_multi = (rangenet[0][1]-rangenet[0][0])/2;
        outyaw.append(range_multi*layer2out)



    outyaw_mirrored = list()
    for i in range(1,11):
        if i > 9:
            name = str(i)
        else:
            name = '0'+str(i)
            
        w1 = mat["yaw_0"+name+"_w1"]
        w2 = mat["yaw_0"+name+"_w2"][0]
        rangenet = mat["yaw_0"+name+"_range"]
        b1 = mat["yaw_0"+name+"_b1"]
        b1 = remap(b1)
        b2 = mat["yaw_0"+name+"_b2"]
        b2 = remap(b2)
        
        image_ar = numpy.asarray(image_list_mirrored)
        image_ar = mapminmax(image_ar)

        layer1out = tansig(numpy.dot(w1,image_ar)+b1)

        layer2out = numpy.dot(layer1out, w2)+b2;
        range_multi = (rangenet[0][1]-rangenet[0][0])/2;
        outyaw_mirrored.append(range_multi*layer2out)

    outyaw = numpy.asarray(outyaw[0:len(outyaw)])
    outyaw_mirrored = numpy.asarray(outyaw_mirrored[0:len(outyaw)])
    outpitch = numpy.asarray(outpitch[0:len(outyaw)])
    outpitch_mirrored = numpy.asarray(outpitch_mirrored[0:len(outyaw)])
    #print numpy.mean(outpitch),numpy.mean(outpitch_mirrored),numpy.mean(outyaw),numpy.mean(outyaw_mirrored)
    
    return (numpy.mean(outpitch)+numpy.mean(outpitch_mirrored))/2,(numpy.mean(outyaw)-numpy.mean(outyaw_mirrored))/2

def HeadPose(image,SQregion):
    region = Region()
    global pitch_yaw
    global offset_pitch
    global offset_yaw
    global KeyPress
    #save_time = time.clock()
    gray = cv.CreateImage(cv.GetSize(image),image.depth,1)

    if image.channels != 1:
        cv.CvtColor(image,gray,cv.CV_RGB2GRAY)
    else:
        cv.Copy(image,gray)    
    
    ## convert image to correct ratio
    ## the viola jones method returns a square region while we need a rectangular region
    region.x = int(SQregion.x+(SQregion.width*(1-0.6)/2))
    region.y = int(SQregion.y + (SQregion.height*(1-((90/40)*0.6))/2))
    region.width = int(SQregion.width*0.6);
    region.height = int(SQregion.height*(90/40)*0.6);

    ## filter image
    cv.SetImageROI(gray,(region.x,region.y,region.width,region.height))
    small = cv.CreateImage((40,90),8,1)
    cv.Resize(gray,small)
    cv.Smooth(small,small,cv.CV_GAUSSIAN, 3)
    cv.EqualizeHist(small,small)
    lap_small_16 = cv.CreateImage(cv.GetSize(small),cv.IPL_DEPTH_16S,1)
    cv.Laplace(small,lap_small_16,3)
    laplace = cv.CreateImage(cv.GetSize(lap_small_16), 8,1) ## image number one
    cv.ConvertScaleAbs(lap_small_16,laplace)

    ## image number two mirrored image
    laplace3 = cv.CreateImage(cv.GetSize(laplace),laplace.depth,laplace.channels)
    cv.SetImageROI(laplace,(2,2,laplace.width,laplace.height))
    cv.Resize(laplace,laplace3) ## image number three slighty smaller image
    cv.ResetImageROI(laplace)

    ## Try to determine the yaw and pitch using NN's    
    try:
        pitch_yaw=list(PitchYaw(laplace))
    except:
        print "PitchYaw function not working"

    k = cv.WaitKey(1)
    if k == 2490368:        #Up-arrow key
        offset_pitch -= 0.2
    elif k == 2621440:      #Down-arrow key
        offset_pitch += 0.2
    elif k == 2555904:      #Right-arrow key
        offset_yaw -= 0.2
    elif k == 2424832:      #Left-arrow key
        offset_yaw += 0.2
    KeyPress = chr(k & 255)
    
    pitch_yaw[0] = -(-pitch_yaw[0]+offset_pitch)
    pitch_yaw[1] = -(pitch_yaw[1]+offset_yaw)

    return (pitch_yaw[0], pitch_yaw[1], region)
        
def InsertYawGaze(frame, yawgaze):
    ## Function Framerate(frame) adds the framerate to the provided opencv image "frame"

    font = cv.InitFont(cv.CV_FONT_HERSHEY_TRIPLEX, 0.5, 0.5, 0.0, 1)
    cv.PutText(frame,
               "HeadYaw = "+str(yawgaze)+" deg.",
               (440,15),
               font,
               cv.RGB(0,0,255))
    return frame

def SaveCapture(cap, EXIT=0):
    """
    Unfortunately this function does not work for the image shown in the output window "MYWINDOW". 
    It does however work for the unaltered QueryFrame captures (i.e. you save wat the webcam sees),
    which has to be resolved since both the Query-Frame as the Window-image are of type 'cv2.cv.iplimage'...?
    """
    global InitVideofile
    global writer
    global resolution
    
    #img = cv.LoadImage(cap)
    if EXIT == 0 and InitVideofile:
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d_%H-%M")
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        writer = cv.CreateVideoWriter(str(filename)+'.avi', fourcc, 10.0, resolution)
        InitVideofile = False
        
    if EXIT == 0:
        # write the frame
        if cap != None:
            cv.WriteFrame(writer, cap)  
            
    else:
        del(writer)
        
def GetFaceData(facedetectTYPE=1, 
                faceYawPitchON=1, 
                NAO_IP="192.168.0.114", 
                indexEXTERNALcam=0, 
                CreateVideoFile=0,
                useNAOcam=0, 
                dimension=vd.kVGA, 
                maxFPS=30):

    global ExitNAO_IP
    global ExituseNAOcam
    global ExitfacedetectTYPE
    global ExitVideoFile
    global firstrun    
    global facelocation
    global runAVG
    global MYWINDOW
    global NAO_PORT
    global capture
    global image
    global resolution
    global facebuffer
    global faceregion 
    global facecenter
    global facelocation
    global facedetected
    global yaw_avg
    global pitch_avg
    global ROI
    global ROIn
    global margin
    global timings
    global start_time
    global videofile

    if firstrun == True:
        ##                                             ||Define extra settings in box below||
        ## ============================================================================================================================
        colorspace = vd.kYuvColorSpace # importANT: adjust pixel depth AND number of color channels appropriately to the colorspace chosen
        pixeldepth = cv.IPL_DEPTH_8U
        colchannels = 1
        NAO_PORT = 9559
        naoCam_facePosUpdate = 1
        ## ============================================================================================================================
            
        faceregion=Region() 
        facecenter = [0,0]
        facelocation = [0,0]   #centre coordinates in approx. radians.
        yaw = 0
        yaw_avg = [0,0,0,0,0]
        pitch = 0
        pitch_avg = [0,0,0,0,0]
        cv.NamedWindow(MYWINDOW)
        ROI = Region()  # Rectangular Region Of Interest (ROI) is of class 'Region()'
        ROIn = Region() # Square Region Of Interest (ROIn) is of class 'Region()'
        margin = 30
        facebuffer = 0
        timings = []
        runAVG = []
        ExitNAO_IP = NAO_IP
        ExituseNAOcam = useNAOcam
        ExitfacedetectTYPE = facedetectTYPE
        ExitVideoFile = CreateVideoFile
        
        if dimension == vd.kQQVGA:         #because openCV can't interpret the vision_definition library
            resolution = (160,120)
        elif dimension == vd.kQVGA:
            resolution = (320,240)
        elif dimension == vd.kVGA:
            resolution = (640,480)
        elif dimension == vd.k4VGA or vd.k960p:
            resolution = (1280,720) #max NAO resolution is 1280,960
                
        if useNAOcam == 0 and facedetectTYPE != 2:
            # This will start the main program. It uses the cam(s) attached to the computer
            # to gather the images.
            image = cv.CreateImage(resolution, pixeldepth, colchannels)   #Empty image template used in grayscale conversion
            capture = cv.CaptureFromCAM(indexEXTERNALcam)
            cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FPS,maxFPS)
            cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, resolution[0])
            cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT,resolution[1])
#            img = cv.QueryFrame(capture)
#            cv.SaveImage('pic.jpg', img)
        else:
            try:
                videoProxy = ALProxy("ALVideoDevice", NAO_IP, NAO_PORT)
                videoProxy.unsubscribe("_client")
            except RuntimeError:
                pass # 'Unsubscribing Video module was already done, program continues...'
            nao.InitProxy(NAO_IP)   #Many modules including cameraProxy = ALProxy("ALVideoDevice", IP, NAO_PORT) are registered #see nao.py line 121
            nao.InitVideo(dimension, colorspace, maxFPS, pixeldepth, colchannels)        #see nao.py line 640 and 697
        start_time=time.time()
        firstrun = False
    
    if firstrun == False:
        facedetected = False
        match = 0
        if useNAOcam == 0  and facedetectTYPE != 2:
            t0 = time.clock()
            frame = cv.QueryFrame(capture)    
            cv.CvtColor(frame, image, cv.CV_BGR2GRAY)     #Convert image to gray (= like using only the Y channel of YUV)
            t1 = time.clock()-t0
        else:
            t0 = time.clock()
            image = nao.GetImage()
            frame = image
            t1 = time.clock()-t0
        
        if facedetectTYPE == 1:
            image, facelocation, facedetected, faceregion = nao.Detect(image)   #see nao.py line 717
            facelocation[0] = round(float(facelocation[0]),3)
            facelocation[1] = round(float(facelocation[1]),3)
            if facedetected == True:
                ROI.x = faceregion.x
                ROI.y = faceregion.y
                ROI.width = faceregion.width
                ROI.height = faceregion.height
                facecenter[0] = faceregion.x+(faceregion.width/2)
                facecenter[1] = faceregion.y+(faceregion.height/2)
            # When facedetected = true, the facelocation wil give the centre coordinates in approx. radians. 2 coordinates, respectively 
            # horizontal position (left+, center0, right-) and
            # the vertical position (up-, center0, down+)
        elif facedetectTYPE == 2:
            facelocation, facedetected = nao.ALFacePosition(True, naoCam_facePosUpdate)   #see nao.py line 480
            convrad = 0.55/(resolution[0]/2.0)
            facecenter[0] = (facelocation[0]/convrad) + (resolution[0]/2.0)   #Same conversion to approx. radians
            facecenter[1] = (facelocation[1]/convrad) + (resolution[0]/2.0)     
            facelocation[0] = round(float(facelocation[0]),3)
            facelocation[1] = round(float(facelocation[1]),3)
            ROI.x = 0
            ROI.y = 0
            ROI.width = 0
            ROI.height = 0
        elif facedetectTYPE == 3:   
            region, facecounter = detect_faces(image)
            if facecounter > 0:
                facedetected = True
             ## transform region values to region class since this is expected by the HeadPose function
             ## important NOTE: Only the region of one single face will be processed from now on to apply head pose estimation  
                for i in range(facecounter):
                    if (ROI.x-margin <= region[i][0] <= ROI.x+margin) and (ROI.y-margin <= region[i][1] <= ROI.y+margin):
                        match = i
                    else:
                        pass #this means the old ROI values will be kept even if no face was found
                ROI.x = region[match][0]
                ROI.y = region[match][1]
                ROI.width = region[match][2]
                ROI.height = region[match][3]
                
                cv.Rectangle(image, (ROI.x, ROI.y), (ROI.x+ROI.width, ROI.y+ROI.height), (255,0,0))
                facecenter[0] = ROI.x+(ROI.width/2)
                facecenter[1] = ROI.y+(ROI.height/2)
                convrad = 0.55/(resolution[0]/2.0)
                facelocation[0] = round((facecenter[0] - (resolution[0]/2.0))*convrad,3)   #Same conversion to approx. radians
                facelocation[1] = round((facecenter[1] - (resolution[1]/2.0))*convrad,3)
        
#        if facedetected == True:
#            print "\nFaceDetected =", facedetected, "\nFacecenter =", facecenter[0], facecenter[1], "\nFaceLocation =",round(facelocation[0], 3), round(facelocation[1], 3)
#        else:
#            print "\nFaceDetected =", facedetected

        if (faceYawPitchON == 1 and facedetectTYPE != 2):
            if facedetected == False:
                if (ROI.x !=0) and (facebuffer<15):
                    facebuffer += 1
#                    print "Yaw/Pitch estimation buffer =", facebuffer
            else: # facedetected == True:
                facebuffer = 0
            if (facedetected == True ) or ((facedetected == False) and ((ROI.x !=0) and (facebuffer<15))):
                pitch, yaw, ROIn = HeadPose(image, ROI)
                cv.Rectangle(image, (ROIn.x, ROIn.y), (ROIn.x+ROIn.width, ROIn.y+ROIn.height), (34,173,75))
             ## Below is a 'shift register' principle, append new value to list, remove (pop) the oldest value from list
                yaw_avg = yaw_avg[1:-1]+[yaw_avg[-1]]+[yaw]
                pitch_avg = pitch_avg[1:-1]+[pitch_avg[-1]]+[pitch]
            else:
                yaw_avg = [0,0,0,0,0]   # Head is lost for several frames, therefor reset yaw/pitch values
                pitch_avg = [0,0,0,0,0]
        else:
            yaw_avg = [0,0,0,0,0]   # Head pose estimation is not activated and returns zero's
            pitch_avg = [0,0,0,0,0]
            
        
        if (time.time()-start_time)<1:
            timings.append(t1)
        else:
            timings.append(t1)
           # print 1/(float(sum(timings))/len(timings)), " Hz"     #floating point precision
           # runAVG.append(1/(float(sum(timings))/len(timings)))   #floating point precision
           # print "\t\t\t\t\t", len(timings), " fps (Hz)"  #integer precision
            runAVG.append(len(timings))                     #integer precision
            timings=[]
            start_time=time.time()

        ## Taking the mean of 5 values of the 'shift registers' for yaw and pitch and round the result
        yaw = round(float(sum(yaw_avg))/len(yaw_avg),1)
        pitch = round(float(sum(pitch_avg))/len(pitch_avg),1)
        
        ## Median filter of N=5:
#        yaw_med = sorted(yaw_avg, key=float)
#        pitch_med = sorted(pitch_avg, key=float)
#        yaw = round(yaw_med[2],1)
#        pitch = round(pitch_med[2],1)
        
        ## Taking the single newest calculated values for yaw and pitch (i.e. not taking the average of multiple values)
#        yaw = round(yaw_avg[-1],1)
#        pitch = round(pitch_avg[-1],1)
        
        ## Re-scale head-pose estimation since positive values tend to be on a smaller scale
        if yaw>0:
            yaw=round(yaw*1.4375,1)
        
        image = nao.Framerate(image)
        image = InsertYawGaze(image, yaw)
        cv.ShowImage(MYWINDOW, image)
        
        if CreateVideoFile == 1:
            SaveCapture(frame)
        
        yawpitch = [yaw, pitch]

        facedata = [facedetected, facecenter, ROI.width, facelocation, yawpitch, KeyPress]

    return facedata ###, image

def ExitCamera():
    global capture
    global facelocation
    global ExitNAO_IP
    global ExituseNAOcam
    global ExitfacedetectTYPE   
    global ExitVideoFile
    
    print "Initiating proper closure of camera script"
    sys.stdout.flush()
    
    if ExituseNAOcam != 0:
        try:
            print 'Unsubscribing Video module...' 
            sys.stdout.flush()
            videoProxy = ALProxy("ALVideoDevice", ExitNAO_IP, NAO_PORT)
            videoProxy.unsubscribe("_client")
        except RuntimeError:
            print 'Done'
            sys.stdout.flush()
            
    if ExitfacedetectTYPE == 2:
        facelocation = nao.ALFacePosition(False)
    
    if ExituseNAOcam == 0 and ExitfacedetectTYPE != 2:
        del(capture)
        
    if len(runAVG) != 0:
        print round(float(sum(runAVG))/len(runAVG),1), "fps  (", round(1/(float(sum(runAVG))/len(runAVG)),3), "s per frame )", "on average this run"
        sys.stdout.flush()        
        
    if ExitVideoFile == 1:
        SaveCapture(EXIT=1)
    
    cv.DestroyWindow(MYWINDOW)
    
    print "Camera script successfully closed"
    sys.stdout.flush()
        
    
    
    
