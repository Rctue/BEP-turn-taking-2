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

HOUSELOCATION = ['']
HOUSETYPE = ['']
HOUSESIZE = ['']
OUTSIDE_SPACE = ['']
HOUSESTYLE = ['']

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
introduction = ["Hello. For this conversation the main goal is to figure out what your dream house "+ 
                "would be if you would live together. "+
                "I am going to ask you some questions about what your dream house would look like. "+
                "Since the two of you are going to hypothetically live there together, "+
                "ask for each others opinion. "+
                "Are you ready to begin?"]

                
"""
introduction = ["Introduction is skipped."]
"""
starting = ["I am also ready, so let us start to talk and discuss your dream house together."]

#1 HOUSELOCATION
#2 HOUSETYPE
#3 HOUSESIZE
#4 OUTSIDE_SPACE
#5 HOUSESTYLE

ending = [["That was about it. With all the information combined, the dream house you have built is a "]+[HOUSETYPE]+
          ["in "]+[HOUSELOCATION]+["with "]+[HOUSESIZE]+
          ["Your dream house has "]+[OUTSIDE_SPACE]+["and will be a "]+[HOUSESTYLE]+["style house "]+
          ["Thanks for having participated in our dialogue, the experiment will now continue to the next phase."]]
          
                
houselocation = ["City", "Village", "Countryside", "Coast"]
             
housetype = ["Student house", "Apartment", "Terrace house", "Semi-detached house", "Detached house"]

housesize = ["1 bedroom", "2 bedrooms", "3 bedrooms", "4 bedrooms", "More than 4 bedrooms"]

outside_space = ["No backyard", "Balcony", "Rooftop terrace",
                 "Backyard with terrace", "Backyard with swimmingpool"]

housestyle = ["Minimalistic", "Traditional", "Industrial", "Scandinavian", "A farmhouse"]
               

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
       
        if topicID == 1:   # houselocation
                                                            #There are 4 house location options, it will now randomly choose 3 options out of these 4,
                                                            # and thats whats Misty is going to use in the convo. In  the 3rd line response = [1,1,1,0]
                                                            # it means that Misty will say the three options, then give a turn to one of the two participants
                                                            # directly, then Misty will switch and give the other participant a turn.
                                                            # Misty will then give information about the current location being discussed.
            option = [None]+random.sample(sorted(houselocation), len(houselocation))
            optNRs = [3,0]
            response = [1,1,1,0]
                                                            #why not response = [1,0,0,0]+[0,1,0,0]+[0,0,1,0], would that not be better for the flow? 
                                                            #doesn't he do all three things at once now?
        
        elif topicID == 2: # housetype
                                                            #There are 5 different house types, i want the participants to hear 4 out of the 5 options
                                                            #Misty will ask first about the first two options, and then after disccusing that
                                                            #about the next two options
            option = [None]+random.sample(sorted(housetype), len(housetype))
            optNRs = [2,2]
            response = [0,1,1,1]+[0,1,1,0]
            
        elif topicID == 3: # housesize
                                                            #For housesize, i do not want them to be in a random order, i want them to be
                                                            # in the same original order, and Misty has to ask about all of them
            option = [None]+ housesize
            optNRs = [5,0]
            response = [1,0,0,0]+[0,0,1,0]+[0,1,0,0]
            
        elif topicID == 4: # outside_space
                                                            #For the outside space we have 5 options, i want the participants to hear 3 out of the 5 options                                         
            option = [None]+random.sample(sorted(outside_space), len(outside_space))
            optNRs = [3,0]
            response = [0,1,1,0]
            
        elif topicID == 5: # housestyle  
                                                            #For the housestyle we have 5 options, i want the participants to hear 4 options
                                                            #but 2 by 2, because they might be a bit difficult
            option = [None]+random.sample(sorted(housestyle), len(housestyle))
            optNRs = [2,2]
            response = [0,1,1,1]+[0,1,1,0] #This is different in the other files, check whether this needs to be changed?
        option += ['']*(max_options-len(option)+1)
   
    print ('Option list =',option[1:])
       
    # Make sure keys share the same value between dict "topicoptions" and "alt_topicoptions" for sentences that belong to the same topic.
    #1 HOUSELOCATION
    #2 HOUSETYPE
    #3 HOUSESIZE
    #4 OUTSIDE_SPACE
    #5 HOUSESTYLE
    
    topicoptions = {
    0:starting,

    1:["What location would your dream house be in? Would you like your house to be in a "]+[option[1]]+
        [", in a"]+[option[2]]+["or a"]+[option[3]]+["?"],
   
    2:["What type of house would your dream house be? Would you like to live together in a "]+[option[1]]+
        ["or maybe a "]+[option[2]]+["?"],
    
    3:["What size would you like your dream house to be, looking at the number of bedrooms. "]+
        ["Would you like a house with "]+[option[1]]+[","]+[option[2]]+[","]+[option[3]]+[","]+
        [option[4]]+["or even "]+[option[5]]+["?"],
   
    4:["This is going great, only a few more steps are needed to complete your dream house. "]+
    ["Also important to determine is how the outside area of your dream house would look like. "]+
    ["Would you like to have a "]+[option[1]]+[", a " ]+[option[2]]+[", or rather a "]+[option[3]]+["?"],
   
    5:["And finally, what would be the style of your dream house? Would you like your house to be "]+
        [option[1]]+["or rather "]+[option[2]]+["?"],
    
    6:ending}
   
    alt1_topicoptions = {2:["What about living in a "]+[option[3]]+[" or in a "]+[option[4]]+["together?"],
                         5:["Your house could also be "]+[option[3]]+["or "]+[option[4]]+["?"]}
                
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
    global HOUSELOCATION
#    global HOUSETYPE
#    global HOUSESIZE
#    global OUTSIDE_SPACE
#    global HOUSESTYLE

    global dialogstage
   
    if dialogstage == 1: #houselocation
        key = listtostr(OPT)
    elif dialogstage == 2: #housetype
        key = listtostr(OPT)
    elif dialogstage == 3: #housesize
        key = listtostr(OPT)
    elif dialogstage == 4: #outside_space
        key = listtostr(OPT)
    elif dialogstage == 5: #housestyle
        key = listtostr(OPT)
    else:
        key = "KeyMissing???"    

    info = {
        houselocation[0]: "Living in the city provides easy access to public transportation, shopping centers, and cultural attractions, making it a convenient choice for those who enjoy a vibrant lifestyle.",
        houselocation[1]: "A village setting offers a quieter lifestyle with a close-knit community feel, often surrounded by nature and less crowded than the city.",
        houselocation[2]: "The countryside provides a peaceful and spacious environment, ideal for those who enjoy nature, farming, or simply a more relaxed pace of life.",
        houselocation[3]: "Living near the coast means being close to the beach, offering a scenic environment and potential for water activities, as well as fresh seafood.",  

        housetype[0]: "A student house is typically shared accommodation with individual rooms and shared common areas, often located near universities or colleges.",
        housetype[1]: "An apartment is a compact living space in a multi-unit building, usually offering amenities such as security, gyms, and sometimes a shared garden.",
        housetype[2]: "A terrace house is a row of identical houses sharing side walls, popular in urban areas, offering a balance between apartment living and standalone houses.",
        housetype[3]: "A semi-detached house is connected to another house on one side but offers more space and privacy compared to apartments or terrace houses.",
        housetype[4]: "A detached house is a standalone building that provides the most privacy and space, ideal for families who prefer a larger living area and possibly a garden.",

        housesize[0]: "A house with 1 bedroom is suitable for singles or couples, offering a cozy and manageable living space.",
        housesize[1]: "A 2-bedroom house provides a bit more space, which can be used for guests, a home office, or a small family.",
        housesize[2]: "A 3-bedroom house is a common choice for families, offering enough space for children or additional rooms for hobbies or work.",
        housesize[3]: "With 4 bedrooms, there is ample space for a larger family, guests, or even creating specialized rooms like a gym or studio.",
        housesize[4]: "More than 4 bedrooms provide significant living space, ideal for large families, multi-generational households, or those who need extra rooms for various purposes.",

        outside_space[0]: "Having no backyard may be typical for city apartments, but it often means less maintenance and more time to enjoy other activities.",
        outside_space[1]: "A balcony provides a small outdoor space to enjoy fresh air, grow some plants, or have a cup of coffee in the morning.",
        outside_space[2]: "A rooftop terrace offers a larger outdoor area with more privacy, suitable for barbecues, gatherings, or sunbathing.",
        outside_space[3]: "A backyard with a terrace gives space for outdoor activities like gardening, dining, or playing with pets or children.",
        outside_space[4]: "A backyard with a swimming pool offers luxury and relaxation, ideal for hot summers and entertaining guests.",

        housestyle[0]: "A minimalistic style emphasizes simplicity, with clean lines and minimal decorations, creating a calm and clutter-free living space.",
        housestyle[1]: "Traditional style houses are known for their classic architecture and cozy interiors, often featuring wood and other natural materials.",
        housestyle[2]: "An industrial style is characterized by raw, unfinished materials like exposed brick and metal, giving a modern, edgy look.",
        housestyle[3]: "Scandinavian style focuses on light, natural materials, and functionality, promoting a cozy atmosphere with a modern touch.",
        housestyle[4]: "A farmhouse style combines rustic charm with modern comforts, often featuring wooden beams, spacious kitchens, and comfortable living areas."
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

    #1 HOUSELOCATION
    #2 HOUSETYPE
    #3 HOUSESIZE
    #4 OUTSIDE_SPACE
    #5 HOUSESTYLE
   
    def updateCHOICES(chosenOpt):
        global dialogstage
        global option
        global nr
        global OPT
        global HOUSELOCATION
        global HOUSETYPE
        global HOUSESIZE
        global OUTSIDE_SPACE
        global HOUSESTYLE
       
        if dialogstage == 1:
            HOUSELOCATION[0] = chosenOpt
        elif dialogstage == 2:
            HOUSETYPE[0] = chosenOpt
        elif dialogstage == 3:
            HOUSESIZE[0] = chosenOpt
        elif dialogstage == 4:
            OUTSIDE_SPACE[0] = chosenOpt
        elif dialogstage == 5:
            HOUSESTYLE[0] = chosenOpt
       
        print ("Choices so far:", HOUSELOCATION, HOUSETYPE, HOUSESIZE, OUTSIDE_SPACE, HOUSESTYLE)
   
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
   
    utterance_dream_house = ''
   
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
        utterance_dream_house = listtostr(DelayRepeatRandom(SpeedUP))
       
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
                        utterance_dream_house = listtostr(newtopicANDoptions(topicID, alt=1))     # all options handled, go to alternative
                        responseDONE[i] = 1
                        if NRofQuadr == quadr:
                            responseDONE[i-3:i] = [0,0,0]  # Replace first three places of last quadrant with 0's
                        if utterance_dream_house != "???":
                            break
                    else:
                        responseDONE[i] = 1 # Do not break the for loop in this case!
                        if responseDONE == response:
                            # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
                            OPT[0] = option[OPTnr]
                            utterance_dream_house = 2*PREFIX+listtostr(getoptionverdict())
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
                            utterance_dream_house = listtostr(DelayRepeatRandom(direct_turntake))
                        else:
                            if random.randint(0,1):
                                utterance_dream_house = listtostr(DelayRepeatRandom(TT_NoneFirstOPT))
                            else:
                                utterance_dream_house = listtostr(DelayRepeatRandom(direct_turntake))
                        responseDONE[i] = 1
                        OPTnr +=1
                        break
                    elif ItypeNR == 1:
                        if len(optNRs) > 1:
                            firstALT = optNRs[0]+1
                        else:
                            firstALT = 0
                        if OPTnr == 1 or OPTnr == firstALT:
                            utterance_dream_house = PREFIX+listtostr(DelayRepeatRandom(switch_turntake))
                        else:
                            if random.randint(0,1):
                                utterance_dream_house = PREFIX+listtostr(DelayRepeatRandom(TT_NoneFirstOPT))
                            else:
                                utterance_dream_house = PREFIX+listtostr(DelayRepeatRandom(switch_turntake))
                        responseDONE[i] = 1
                        OPTnr +=1
                        break
                    elif ItypeNR == 2:
                        utterance_dream_house = listtostr(infosentence())
                        responseDONE[i] = 1
                        if utterance_dream_house != "???":
                            OPTnr +=1
                            break
                        else:
                            if responseDONE == response:
                                # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
                                OPT[0] = option[OPTnr]
                                utterance_dream_house = 2*PREFIX+listtostr(getoptionverdict())
                                OPTnr = 1
                                dialogstage += 1
                                break
                    elif ItypeNR == 3:
                        OPTnr = optNRs[0]+1
                        OPT[0] = option[OPTnr]
                        utterance_dream_house = listtostr(newtopicANDoptions(topicID, alt=1))     # go to alternative
                        responseDONE[i] = 1
                        if utterance_dream_house != "???":
                            break
                        else:
                            if responseDONE == response:
                                # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
                                OPT[0] = option[OPTnr]
                                utterance_dream_house = 2*PREFIX+listtostr(getoptionverdict())
                                OPTnr = 1
                                dialogstage += 1
                                break
                   
    else:
        # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
        OPT[0] = option[OPTnr]
        utterance_dream_house = 2*PREFIX+listtostr(getoptionverdict())
        OPTnr = 1
        dialogstage += 1
   
    return utterance_dream_house

   
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

   
def utterance_dream_house(state, MistyLooks, NameLeft, NameRight, CharKeyPress, Lturns, Rturns):
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
