# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 10:50:00 2014

@author: Maurice Spiegels
"""

import random
import sys
import math
import time
#import time

dialogstage = 0
prevtopicID = 0
max_options = 9
option = [None]+['']*max_options
opt_OLD = [None]+['']*max_options
optNRs = [None,None]
totaloptNR = 0
response = []
responseMEM = None
Shuffle_Iresponses = 0
PREFIX = " " # The prefix char of length 1 that triggers state-machine actions
OPTnr = 1
OPT = ['']
CURRENTNAME = [0] # Subject names as seen from the perspective of the Nao
OTHERNAME = [0]   # Subject names as seen from the perspective of the Nao
RIGHTWRONG = [0]
VERDICTlist = [None]+['?']*max_options
PreferenceList = [None]+['?']*max_options
VERDICTindex = 1
GoToSpeedUP = False
SaySpeedUP = False
CancelSpeedUP = False

TIMEPERIOD = ['']
INFLUENCELEVEL = ['']
TRAVELCOMPANY = ['']
TRAVELACTIVITIES = ['']
TRAVELDURATION = ['']

listcopies = {}

def GetDialogProgress():
    global dialogstage
    global OPTnr
   
    return str(dialogstage)+"."+str(OPTnr)

def listtostr(listobj):
    #a = time.clock()
    if listobj != None:
        string = str(listobj)
#        string = string.replace("', ['", "")
#        string = string.replace("'], '", "")        
        string = string.replace("'], ['", "")
        string = string.replace("['", "")
        string = string.replace("']", "")
        string = string.replace("', '", "")
        string = string.replace(", '", "")
        string = string.replace("',", "")
        string = string.replace("[", "")
        string = string.replace("]", "")
    else:
        string = ''
    #b = time.clock()
    #print str(round((b-a)*1000,3))+"ms"
    return string


def DelayRepeatRandom(listwithstrings=None):
    #a = time.clock()
    global listcopies  
    listitem = '?'
    listcopy = []
    #print "************************************************************"
    if listwithstrings != None:
        ID = id(listwithstrings)
       
        if not(ID in listcopies):
            #print "ID not present", ID
            #print 'original length =', len(listwithstrings)
            listcopies[ID] = listcopy
            #print 'copy length', len(listcopies[ID]), listcopies[ID]
            #print "ID added\n"
       
        if ID in listcopies:
            #print "ID found"
            #print "Original list = ", listwithstrings
            listN = len(listwithstrings)
           
            if listN != 0:
                if listN == 1:
                    index = 0
                else:
                    index = random.randint(0,len(listwithstrings)-1)
                #print "Original index =", index

                listitem = listwithstrings.pop(index)
                listcopies[ID].append(listitem)
           
            else:
                #print "Copied list = ", listcopies[ID]
                if not(type(listcopies[ID][-1]) is int):
                    listcopies[ID].append(0)
                   
                index = listcopies[ID][-1]
                #print "Copylist index =", index
               
                if index < len(listcopies[ID])-1:
                    listitem = listcopies[ID][index]
                    listcopies[ID][-1] += 1
                else:
                    listitem = listcopies[ID][0]
                    listcopies[ID][-1] = 1                
    #print "************************************************************"
    #b = time.clock()
    #print str(round((b-a)*1000,3))+"ms"        
    return listitem
#"""
introduction = ["Hi there. For this conversation the main goal is to figure out what you would do "+
                "if you had the chance to time travel together. "+
                "I am going to ask you some questions about all the things you want to do in your "+
                "time travel journey. Since the two of you are going to hypothetically time travel "+
                "together, ask for each others opinion. "+
                "Are you ready to begin?"]
"""
introduction = ["Introduction is skipped."]
"""
starting = ["I am also ready, so let us start to talk and discuss your time travel plans together."]

#1 TIMEPERIOD
#2 INFLUENCELEVEL
#3 TRAVELCOMPANY
#4 TRAVELACTIVITIES
#5 TRAVELDURATION

ending = [["That was already it. With all the information combined, for your time travel trip "+
        "you will go "]+[TRAVELCOMPANY]+[" back to "]+[TIMEPERIOD]+[" for "]+[TRAVELDURATION]+["."]+
        [" In this period of time you will have "]+[INFLUENCELEVEL]+[" and you will "]+[TRAVELACTIVITIES]+["."]+
          ["Thanks for having participated in our dialogue, the experiment will now continue to the next phase."]]
          
                
timeperiod =["Ancient Egypt", "The classical Greece and the Roman empire", 
            "Medieval times", "The renaissance", "The industrial revolution"]

influencelevel = ["No influence", "Little interactions without major influence", 
                "Major influence", "Completely change history and future"]

travelcompany = ["Alone", "With my partner", "With friends", " With family"]

travelactivities = ["Be at big historical moments", "Meet people", 
                    "Change your own timeline", "Prevent world disasters"]

travelduration = ["A few days", "A few weeks", "A few months", "Stay forever"]
             
def newtopicANDoptions(topicID=0, alt=0):
    global option
    global optNRs
    global starting
    global ending
    global response
    global max_options
    global Shuffle_Iresponses
    max_options = 9 # For each topic no more than 9 options may be defined to choose from (due to selection limitations with a Numpad)

#    The 'RANDx_x' definitions below can be used to define partial randomness even when Shuffle_Iresponses == 0.
#    - RAND2_1 = random.sample([1,0],2)
#    - RAND3_1 = random.sample([1,0,0],3)
#    - RAND3_2 = random.sample([1,0,1],3)

#    option and optNRs:    
#    Define which list holds the options that will be chosen from, optNRs[0] must match the number of options for both the 'topicoptions'
#    sentences as well as optNRs[1] should match the alternative topicoptions sentence.
#    
#    response:    
#    User sets it's preferences here for each OPTnr, it defines how many and which type of utterances the Nao is going to say
#    before it will continue to the next OPTnr. Once all options have been discussed, it will determine a verdict. See definition below:
#    To define 'simple' sequence with no alternative:     response = [Idirect, Iswitch, Iinfo, Ialt=0]
#    To define sequence before and after the alternative: response = [Idirect, Iswitch, Iinfo, Ialt=1]+[Idirect, Iswitch, Iinfo, Ialt=0]
#    To repeat the same sequence after a alternative:     response = [Idirect, Iswitch, Iinfo, Ialt=1]
#    To define ordered sequence with no alternative:      response = [Idirect, Iswitch, Iinfo, Ialt=0]+[Idirect, Iswitch, Iinfo, Ialt=0]

    Shuffle_Iresponses = 0
    if alt == 0:
       
        if topicID == 1:   # timeperiod
                                                            # I want Misty to choose 3/5 time periods randomly, and tell these 
                                                            # to the participants, as to not overwhelm them.
                                                            # I also want it to give information about the time period
                                                            # both participants need a turn
            option = [None]+random.sample(sorted(timeperiod), len(timeperiod))
            optNRs = [3,0]
            response = [1,1,1,0]
                                    
        elif topicID == 2: # influencelevel
                                                            # Not random order, I want all options in sequential order
                                                            # I also want all options to be asked
                                                            # I want it to give information
                                                            # I want to give all 4 options at once, to avoid confusion
            option = [None]+ influencelevel
            optNRs = [4,0]
            response = [1,0,0,0]+[0,0,1,0]+[0,1,0,0]
            
        elif topicID == 3: # travelcompany
                                                            # For travel company i want them in a random order
                                                            # I want it to in total give all options, but 2 at a time
                                                            # I dont need info for this topic
            option = [None]+random.sample(sorted(travelcompany), len(travelcompany))
            optNRs = [2,2]
            response = [1,0,0,0]+[0,1,0,0]
            
        elif topicID == 4: # travelactivities
                                                            # I want Misty to choose 3/5 activities randomly, all tell these
                                                            # to the participants, as not to overwhelm them.
                                                            # I want to give some information about the activities
            option = [None]+random.sample(sorted(travelactivities), len(travelactivities))
            optNRs = [3,0]
            response = [0,1,1,0]
            
        elif topicID == 5: # travelduration  
                                                            # Not random order, I want all of them in sequential order
                                                            # Information at the end, after both participants had a turn
                                                            # I want to ask for both participants input
            option = [None]+ travelduration
            optNRs = [4,0]
            response = [1,0,0,0]+[0,1,0,0]+[0,0,1,0]
        option += ['']*(max_options-len(option)+1)
   
    print ('Option list =',option[1:])
       
    # Make sure keys share the same value between dict "topicoptions" and "alt_topicoptions" for sentences that belong to the same topic.
    #1 TIMEPERIOD
    #2 INFLUENCELEVEL
    #3 TRAVELCOMPANY
    #4 TRAVELACTIVITIES
    #5 TRAVELDURATION
    
    topicoptions = {
        0:starting,

        1:["If you had the choice, what time period in history would you travel to? Would you like to "]+
            ["travel to "]+[option[1]]+[", "]+[option[2]]+[" or "]+[option[3]]+["?"],
   
        2:["How much influence would you like to have on the time period you travel to? Do you want "]+
            ["to change anything? Would you like to have "]+[option[1]]+[", "]+[option[2]]+
            [", "]+[option[3]]+[", or would you like to "]+[option[4]]+["?"],
        
        3:["With whom would you like to time travel with, excluding your new friend sitting next to you? "]+
            ["Would you like to time travel "]+[option[1]]+[" or "]+[option[2]]+["?"],
    
        4:["We are almost there, just a few more questions. What kind of activities would you do "]+
            ["if you travelled back in time? Would you "]+[option[1]]+[", "]+[option[2]]+
            [", or maybe "]+[option[3]]+["?"],
    
        5:["As a last question, how long would you like your time travel trip to be?"]+
            [" Would you like to go "]+[option[1]]+[", "]+[option[2]]+[", "]+[option[3]]+
            [", or maybe "]+[option[4]]+["?"],
        
        6:ending
    }
   
    alt1_topicoptions = {3:["Or would you rather time travel "]+[option[3]]+[" or "]+[option[4]]+["?"]}
                
    try:    
        if alt == 0:
            output_line = topicoptions[topicID]
        elif alt == 1:
            output_line = alt1_topicoptions[topicID]
    except:
        output_line = "???"
                   
    return output_line


longturnindicator = ["Interesting",
                     "I see",
                     "Ok",
                     "Indeed",
                     "Go on"]
                     
breaksilence = ["So who has any ideas?",
                "So what do you both think?",
                "Who of you can say something about it?",
                "Let us try to share some ideas.",
                "There must be some opinion about it."]
               
TT_NoneFirstOPT = [["How about "]+[OPT]+["?"],
                   ["What about "]+[OPT]+["?"],
                   ["What do you think of "]+[OPT]+["?"],
                   ["What is your opinion about "]+[OPT]+["?"],
                   ["What can you say about "]+[OPT]+["?"],
                   ["Any other judgement about "]+[OPT]+["?"],
                   ["What is your mind on "]+[OPT]+["?"]]
                 
direct_turntake = ["Why do you think that?",
                   "Why do you see it that way?",
                   "Please elaborate a bit more.",
                   "Any more comments?",
                   "What would be another reason?",
                   "And what other reason would there be?",
                   "What could be a counterargument?",
                   "What would be a statement against?",
                   "What would your conversation partner most likely think?",
                   ["What would "]+[OTHERNAME]+["s opinion be?"],
                   ["What do you think will be the opinion of "]+[OTHERNAME]+["?"],
                   ["Why could "]+[OTHERNAME]+[" think you are "]+[RIGHTWRONG]+["?"],
                   ["Why could your partner think you are "]+[RIGHTWRONG]+["?"]]

switch_turntake = [["To what degree would this also be your opinion?"], # The prefix is essential to a switch turn-take utterance!
                   ["To what extent do you agree with "]+[CURRENTNAME]+["?"],
                   ["That is interesting, what about you?"],
                   ["Ok fair enough, how about you?"],
                   ["And what is your view?"],
                   ["How do you feel about that?"],
                   ["Anything to add on "]+[OPT]+["s opinion?"],
                   ["Given what "]+[CURRENTNAME]+[" said, how would you comment on that?"],
                   ["Given what "]+[CURRENTNAME]+[" said, what would be your opinion?"]]


VerdictUtt = {"MULTIPLE": [ ["Well it seems that more than one option is possible, so for now let us go with "]+[OPT],
                            ["You seem to are like minded, since there are multiple possibilities I will pick "]+[OPT]+[" for now "],
                            ["Well with such positive judgements for multiple options, I will have to pick one which will be "]+[OPT]+['.'],
                            ["I am glad you are both positive about several of my suggestions. To keep things simple, let us go with "]+[OPT]+['.'],
                            ["Although it would not be impossible to combine several of the proposed options, for now we will stick with "]+[OPT]+['.']],

                "SINGLE": [ ["Clearly "]+[OPT]+[" seems to be the best choice."],
                            ["I am glad that you found mutual agreement, "]+[OPT]+[" is selected for now."],
                            ["Well this is an easy choice, I will note it is going to be "]+[OPT]+['.'],
                            ["Ok, let me select option "]+[OPT]+[' for you'],
                            ["It is clear to me that  "]+[OPT]+[' is preferred']],

                "UNKNOWN":[ ["Ok, not all arguments were clear to me, so I will choose for the time being "]+[OPT]+['.'],
                            ["I am not completely sure what option would suit you best, let us just say for simplicity it will be "]+[OPT]+['.'],
                            ["Unfortunately for me it was not one hundred percent clear what your preference is, so I will take a guess for "]+[OPT]+['.'],
                            ["Maybe I was not listening close enough, but since no clear preference was given for one of the option, I will just go with "]+[OPT]+['.'],
                            ["Well this time it looks like I am forced to make the decision for you. It will therefore be  "]+[OPT]+['.']],

                "NONE":   [ ["It is unfortunate that none of the options discussed so far seem to fit. "+
                             "Therefore I will choose an fall back option that we have maybe not mentioned earlier, which is "]+[OPT]+['.'],
                            ["What a same that no options seems to suit your needs. "+
                             "Let me therefore choose an fall back option that we may not have mentioned earlier, namely "]+[OPT]+['.'],
                            ["Well it seems that you are pretty picky and none of the suggestions was adequate enough. "+
                             "As fall back option, I will select "]+[OPT]+['.'],
                            ["Did none of the options matched your thoughts? Well, then I shall for the time being just choose as fall back "]+[OPT]+['.'],                            
                            ["Ok, although unanimously decided, rejecting all possibilities leaves me no choice other than to select "]+[OPT]+[" as fall back."]]}

ProPrefix = ["It is also nice to know that ",
             "I can assure you also that ",
             "Also interesting for you to know is that ",
             "Maybe you also like to hear that ",
             "Perhaps also good to know is that ",
             "A good fact to also know is that "]
             
ConPrefix = ["It may still be valuable to know that ",
             "I would still like to say that ",
             "Did you nevertheless know that ",
             "Were you aware of the fact that ",
             "Perhaps something to still consider is that ",
             "Did you also took into account that "]
             
OpenPrefix = ["I can tell you that ",
              "Interesting to know is that ",
              "Did you know that ",
              "According to my information, ",
              "It is often said that ",
              "I like to share with you that "]
             
SpeedUP = ["You both agree to the same choice?",
           "So we have a mutual agreement?",
           "I guess the answer is clear then?",
           "It is clear then what option it should be?",
           "It seems the answer is obvious then?",
           "No need to discuss more options I guess?"]
                     
def infosentence():
    global TIMEPERIOD
#    global INFLUENCELEVEL
#    global TRAVELCOMPANY
#    global TRAVELACTIVITIES
#    global TRAVELDURATION

    global dialogstage
   
    if dialogstage == 1: #timeperiod
        key = listtostr(OPT)
    elif dialogstage == 2: #influencelevel
        key = listtostr(OPT)
    elif dialogstage == 3: #travelcompany
        pass
    elif dialogstage == 4: #travelactivities
        key = listtostr(OPT)
    elif dialogstage == 5: #travelduration
        key = listtostr(OPT)
    else:
        key = "KeyMissing???"    

    info = {

    timeperiod[0]: "Ancient Egypt was a time of grand pyramids, pharaohs, and fascinating mythology. Visiting could give you a glimpse into one of the earliest civilizations with advanced architecture and culture.",
    timeperiod[1]: "The classical Greece and Roman empire were eras of philosophy, democracy, and significant scientific advancements. This period was also marked by iconic architecture like the Parthenon and Colosseum.",
    timeperiod[2]: "Medieval times were known for castles, knights, and kingdoms, with a strong focus on chivalry, religion, and the feudal system. Life was challenging, yet the period was rich in folklore and legendary figures.",
    timeperiod[3]: "The Renaissance brought a rebirth of art, science, and literature across Europe. Figures like Leonardo da Vinci and Michelangelo left a lasting impact on culture and knowledge.",
    timeperiod[4]: "The Industrial Revolution was a time of rapid technological change, with steam engines, factories, and new ways of living and working. It was a time that transformed economies and urban life.",

    influencelevel[0]: "Choosing no influence means you’ll be an observer in history, witnessing events without affecting the course of time.",
    influencelevel[1]: "Having little interactions without major influence allows you to mingle with the locals but not enough to change significant events.",
    influencelevel[2]: "Having major influence means you could alter key historical moments, potentially changing the future significantly.",
    influencelevel[3]: "Completely changing history and future means you could rewrite entire events, creating a new timeline with unpredictable consequences.",

    travelactivities[0]: "Being at big historical moments would let you witness iconic events like the fall of Rome, the signing of important treaties, or groundbreaking discoveries.",
    travelactivities[1]: "Meeting people from the past could offer unique insights into their lives, beliefs, and day-to-day experiences.",
    travelactivities[2]: "Changing your own timeline might allow you to make different decisions in your own life, potentially altering your present and future.",
    travelactivities[3]: "Preventing world disasters could give you the power to avert wars or other catastrophic events, creating a safer future for humankind.",

    travelduration[0]: "A few days could give you a short, exciting glimpse into a different era without becoming too immersed in the time period.",
    travelduration[1]: "A few weeks would allow you to explore more thoroughly, perhaps observing daily life and significant cultural events.",
    travelduration[2]: "A few months in a time period could let you experience deeper immersion, getting accustomed to the lifestyle, culture, and customs.",
    travelduration[3]: "Staying forever means fully adapting to a new era, leaving your present life behind and starting anew in a time period of your choice." 
    }
   
#    print "key = ", key    
#    print "info[key] =", info[key]
#    print "VERDICTlist[OPTnr] =", VERDICTlist[OPTnr]

    if VERDICTlist[OPTnr] == '+':
        dictstring = DelayRepeatRandom(ProPrefix)+info[key]
    elif VERDICTlist[OPTnr] == '-':
        dictstring = DelayRepeatRandom(ConPrefix)+info[key]
    elif VERDICTlist[OPTnr] == '?':
        dictstring = DelayRepeatRandom(OpenPrefix)+info[key]
    else:
        dictstring = "???"
   
#    print "dictstring =", dictstring
    sys.stdout.flush()
   
    return dictstring
   
   
def getoptionverdict():
    global option
    global optNRs
    global VERDICTlist
    global totaloptNR

    #1 TIMEPERIOD
    #2 INFLUENCELEVEL
    #3 TRAVELCOMPANY
    #4 TRAVELACTIVITIES
    #5 TRAVELDURATION
   
    def updateCHOICES(chosenOpt):
        global dialogstage
        global option
        global nr
        global OPT
        global TIMEPERIOD
        global INFLUENCELEVEL
        global TRAVELCOMPANY
        global TRAVELACTIVITIES
        global TRAVELDURATION
       
        if dialogstage == 1:
            TIMEPERIOD[0] = chosenOpt
        elif dialogstage == 2:
            INFLUENCELEVEL[0] = chosenOpt
        elif dialogstage == 3:
            TRAVELCOMPANY[0] = chosenOpt
        elif dialogstage == 4:
            TRAVELACTIVITIES[0] = chosenOpt
        elif dialogstage == 5:
            TRAVELDURATION[0] = chosenOpt
       
        print ("Choices so far:", TIMEPERIOD, INFLUENCELEVEL, TRAVELCOMPANY, TRAVELACTIVITIES, TRAVELDURATION)
   
    verdict = "So far it is to early to draw any conclusion"
    unknown = '?'
    plus = '+'
    #print "totaloptNR =", totaloptNR
   
    # MULTIPLE = more than one option possible
    # SINGLE = only one option possible
    # UNKNOWN = all options are undecided
    # NONE = no options are possible
    if VERDICTlist[:totaloptNR].count(plus) > 1:
        nr = VERDICTlist[:totaloptNR].index(plus)
        updateCHOICES(option[nr])
        OPT[0] = option[nr]
        verdict = DelayRepeatRandom(VerdictUtt["MULTIPLE"])
    elif VERDICTlist[:totaloptNR].count(plus) == 1:
        nr = VERDICTlist[:totaloptNR].index(plus)
        updateCHOICES(option[nr])
        OPT[0] = option[nr]
        verdict = DelayRepeatRandom(VerdictUtt["SINGLE"])
    elif unknown in VERDICTlist[:totaloptNR]:
        nr = VERDICTlist[:totaloptNR].index(unknown)
        updateCHOICES(option[nr])
        OPT[0] = option[nr]
        verdict = DelayRepeatRandom(VerdictUtt["UNKNOWN"])
    else:
        updateCHOICES(option[totaloptNR])
        OPT[0] = option[totaloptNR]
        verdict = DelayRepeatRandom(VerdictUtt["NONE"])
#    print "nr, option[nr] =", nr, option[nr]
#    print "Verdict returned =", verdict
    return verdict
   
def gothroughoptions(topicID):
    global PREFIX
    global response
    global responseDONE
    global responseMEM
    global NRofQuadr
    global Shuffle_Iresponses
    global shuffled_response
    global prevtopicID
    global dialogstage
    global optNRs
    global OPTnr
    global OPT
    global GoToSpeedUP
    global SaySpeedUP
    global CancelSpeedUP

    if topicID != prevtopicID: #update response variables at the start of a new topic
           
        prevtopicID = topicID
        responseDONE = [0]*len(response)
        NRofQuadr = int(math.floor(len(response)/4.0))
        shuffled_response = []
        responseMEM = None
        if Shuffle_Iresponses !=0:
            for q in range(1,NRofQuadr+1):
                Idirect = (4*q)-4
                Iswitch = (4*q)-3
                Iinfo = (4*q)-2
                alt = (4*q)-1
                random.sample(sorted([0,1,2]), 3)
                shuffled_response += random.sample(sorted([Idirect,Iswitch,Iinfo]), 3)+[alt]
           
   
    print ("topic responce matrix     = ", response)
    print ("topic responceDONE matrix = ", responseDONE)
    print ("shuffled responce matrix  = ", shuffled_response)
   
    utterance_time_travel = ''
   
    if GoToSpeedUP:
        GoToSpeedUP = False        
        if CancelSpeedUP == False:
            for i in range(0,len(response)): # make response list complete up to alternative
                print ("response = ", response)
                print ("i = ", i)
                print ("(i+1)%4 = ", (i+1)%4)
                print ("response[i] =", response[i])
                sys.stdout.flush()
               
                if (i+1)%4 == 0 and response[i] == 1 and responseDONE[i] != 1: #indicates an alternative sentence (% = modulo operator, returns the remainder of x/y)
                    responseDONE[0:i] = response[0:i]
                    break
            else:
                responseMEM = responseDONE
                responseDONE = response  
                SaySpeedUP = True
        else:
            CancelSpeedUP = False
    #        utterance = "You both agree to the same choice?" listtostr(DelayRepeatRandom(SpeedUP))
   
    if CancelSpeedUP:
        CancelSpeedUP = False
        if responseMEM != None:
            responseDONE = responseMEM
            responseMEM = None
   
    if SaySpeedUP:
        SaySpeedUP = False
        utterance_time_travel = listtostr(DelayRepeatRandom(SpeedUP))
       
    elif responseDONE != response:
        for r in range(0,len(response)):
            if Shuffle_Iresponses != 0:
                i = shuffled_response[r]
            else:
                i = r
               
            if responseDONE[i] != response[i]:
                quadr = int(math.ceil((i+1)/4.0)) # Quadrant; every repitition sequence of the 4 parameters (Idirect, Iswitch, Iinfo, or Ialt)
                ItypeNR = i-(4*(quadr-1)) # ItypeNR will always be either 0,1,2, or 3 which represent Idirect, Iswitch, Iinfo, or Ialt.
#                print "NRofQuadr", NRofQuadr                    
#                print "current quadr =", quadr
#                print "ItypeNR =", ItypeNR  
#                print "OPTnr = ", OPTnr
               
                                   
                if not(OPTnr <= sum(optNRs[:quadr])):
                    if ItypeNR == 3:
                        OPTnr = optNRs[0]+1
                        OPT[0] = option[OPTnr]
                        utterance_time_travel = listtostr(newtopicANDoptions(topicID, alt=1))     # all options handled, go to alternative
                        responseDONE[i] = 1
                        if NRofQuadr == quadr:
                            responseDONE[i-3:i] = [0,0,0]  # Replace first three places of last quadrant with 0's
                        if utterance_time_travel != "???":
                            break
                    else:
                        responseDONE[i] = 1 # Do not break the for loop in this case!
                        if responseDONE == response:
                            # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
                            OPT[0] = option[OPTnr]
                            utterance_time_travel = 2*PREFIX+listtostr(getoptionverdict())
                            OPTnr = 1
                            dialogstage += 1
                            break
                else:                        
                    OPT[0] = option[OPTnr]
                    if ItypeNR == 0:
                        if len(optNRs) > 1:
                            firstALT = optNRs[0]+1
                        else:
                            firstALT = 0
                        if OPTnr == 1 or OPTnr == firstALT:
                            utterance_time_travel = listtostr(DelayRepeatRandom(direct_turntake))
                        else:
                            if random.randint(0,1):
                                utterance_time_travel = listtostr(DelayRepeatRandom(TT_NoneFirstOPT))
                            else:
                                utterance_time_travel = listtostr(DelayRepeatRandom(direct_turntake))
                        responseDONE[i] = 1
                        OPTnr +=1
                        break
                    elif ItypeNR == 1:
                        if len(optNRs) > 1:
                            firstALT = optNRs[0]+1
                        else:
                            firstALT = 0
                        if OPTnr == 1 or OPTnr == firstALT:
                            utterance_time_travel = PREFIX+listtostr(DelayRepeatRandom(switch_turntake))
                        else:
                            if random.randint(0,1):
                                utterance_time_travel = PREFIX+listtostr(DelayRepeatRandom(TT_NoneFirstOPT))
                            else:
                                utterance_time_travel = PREFIX+listtostr(DelayRepeatRandom(switch_turntake))
                        responseDONE[i] = 1
                        OPTnr +=1
                        break
                    elif ItypeNR == 2:
                        utterance_time_travel = listtostr(infosentence())
                        responseDONE[i] = 1
                        if utterance_time_travel != "???":
                            OPTnr +=1
                            break
                        else:
                            if responseDONE == response:
                                # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
                                OPT[0] = option[OPTnr]
                                utterance_time_travel = 2*PREFIX+listtostr(getoptionverdict())
                                OPTnr = 1
                                dialogstage += 1
                                break
                    elif ItypeNR == 3:
                        OPTnr = optNRs[0]+1
                        OPT[0] = option[OPTnr]
                        utterance_time_travel = listtostr(newtopicANDoptions(topicID, alt=1))     # go to alternative
                        responseDONE[i] = 1
                        if utterance_time_travel != "???":
                            break
                        else:
                            if responseDONE == response:
                                # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
                                OPT[0] = option[OPTnr]
                                utterance_time_travel = 2*PREFIX+listtostr(getoptionverdict())
                                OPTnr = 1
                                dialogstage += 1
                                break
                   
    else:
        # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
        OPT[0] = option[OPTnr]
        utterance_time_travel = 2*PREFIX+listtostr(getoptionverdict())
        OPTnr = 1
        dialogstage += 1
   
    return utterance_time_travel

   
def setUtteranceVARs(state, MistyLooks, nameleft, nameright, keypress, lturns, rturns):
    global PREFIX
    global RIGHTWRONG
    global CURRENTNAME
    global OTHERNAME
    global PreferenceList
    global VERDICTlist
    global VERDICTindex  
    global prev_dialogstage
    global dialogstage
    global max_options
    global option
    global opt_OLD
    global optNRs
    global totaloptNR
    global GoToSpeedUP
    global CancelSpeedUP
   
    RIGHTWRONG[0] = random.sample(sorted(["right", "wrong"]), 1)[0]
    if MistyLooks == 'L':                                                 #noalooks replaced by something else?
        CURRENTNAME[0] = nameleft
        OTHERNAME[0] = nameright
    elif MistyLooks == 'R':                                               #noalooks replaced by something else?
        CURRENTNAME[0] = nameright
        OTHERNAME[0] = nameleft
   
    if opt_OLD != option:
        totaloptNR=sum(optNRs)+1
        PreferenceList = option[:totaloptNR]
        for z in range(1,totaloptNR):
            PreferenceList[z] = '? '+str(PreferenceList[z])
        VERDICTlist = [None]+['?']*max_options
        opt_OLD = option
    else:
        for x in range(1,totaloptNR):
            if keypress == str(x):
                VERDICTindex = x
        if keypress == '+' or keypress == '-': #ONLY WORKS IF CAMERA WINDOW IS ON FOREGROUND AND ACTIVE!!! (cv.WaitKey function is used)
            VERDICTlist[VERDICTindex] = keypress    
            PreferenceList[VERDICTindex] = keypress + PreferenceList[VERDICTindex][1:]
        if keypress == '*':
            GoToSpeedUP = True
        if keypress == '/':
            CancelSpeedUP = True

#    if ord(keypress) != 255:
#        print "keypress =", keypress
#    else:
#        print "keypress = None"
   
    print ("dialogstage =", GetDialogProgress())
#    print "option list =", option
#    print 'VERDICT list =',VERDICTlist
    print ('preference list =',PreferenceList[1:])

   
def utterance_time_travel(state, MistyLooks, NameLeft, NameRight, CharKeyPress, Lturns, Rturns):
    global dialogstage
    sentence = ''
   
    setUtteranceVARs(state, MistyLooks, NameLeft, NameRight, CharKeyPress, Lturns, Rturns) # = also embedded in main State Machine loop
    
  #dit stuk heeft vlgsmij iets te maken met die testen die de hele tijd gedaan worden, maar staat niks anders over in dit bestand
    if state == 0:                              
        if dialogstage == 0:
            sentence = listtostr(introduction)
            dialogstage = 1
        elif dialogstage == 1:
            sentence = listtostr(newtopicANDoptions(0))
            #dialogstage = 6                  # Define a stage here to skip previous ones (debugging)
    elif state == 1:
        if dialogstage != 6: #vlgsmij is 6 nu end van conversation
            sentence = listtostr(newtopicANDoptions(dialogstage)) #introduce new question with new options
        else:
            sentence = PREFIX+listtostr(newtopicANDoptions(dialogstage)) #send final sentence and end conversation
       
    elif state == 4:
        sentence = listtostr(DelayRepeatRandom(breaksilence))
   
    elif state == 6:
        sentence = listtostr(DelayRepeatRandom(longturnindicator))
       
    elif state == 7:
        sentence = gothroughoptions(dialogstage) # return next option/filler/alternative or return verdict/end    
   
    return sentence
