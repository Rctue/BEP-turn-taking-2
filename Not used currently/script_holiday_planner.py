# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 10:50:00 2014

@author: Maurice Spiegels
"""

import random
import sys
import math
import time
import cv2

dialogstage = 0.0
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

CONTINENT = ['']
CITY = ['']
PERIOD = ['']
DURATION = ['']
HOLIDAYTYPE = ['']

listcopies = {}

def GetDialogProgress():
    global dialogstage
    global OPTnr
   
    return str(dialogstage)+"."+str(OPTnr)

def listtostr(listobj):
    #this function simply turns listobject into a string.
    #input: list object, output: list object as string type
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
    #this function has as input a list of items (Strings), and randomly removes a few of the options. This shortened list is also the output.
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
introduction = ["Hi there. For this conversation the main goal is to figure out what a holiday should be like if you "+
                "have to travel and spend the entire vacation together. "+
                "I am going to ask you some questions about what your ideal holiday is. "+
                "Since the two of you are going on a hypothetical holiday together, "+
                "ask for each others opinion. "+
                "Are you ready to begin?"]
                
"""
introduction = ["Introduction is skipped."]
"""
starting = ["I am also ready, so let us start to talk and discuss your holiday options together."]

#1 CONTINENT
#2 CITY
#3 PERIOD
#4 DURATION
#5 HOLIDAYTYPE
                
ending = [["Well thats about it. With all the information combined, you have arranged yourselves a holiday for "]+[DURATION]+
          [" that will bring you to the continent of "]+[CONTINENT]+[" in the city "]+[CITY]+[" , during the "]+[PERIOD]+[". "]+
          ["Once arrived you will have a typical "]+[HOLIDAYTYPE]+[" vacation "]+
          ["Thanks for having participated in our dialogue, the experiment will now continue to the next phase."]] #Make Nao turn to both participants on this sentence (future work)
               
   
continent = ["Asia",
             "Africa",
             "United States",
             "Central South America",
             "Europe",
             "Australia"]
             
city = {continent[0]: ["Singapore", "Hong Kong", "Bali", "Tokyo", "Maldives"],
        continent[1]: ["Cape Town", "Cairo", "Marrakech", "Tanzania", "Seychelles"],
        continent[2]: ["San Francisco", "New York", "Las Vegas", "New Orleans", "Miami"],
        continent[3]: ["Buenos Aires", "Rio de Janeiro", "Argentine", "Santiago", "Costa Rica"],
        continent[4]: ["Berlin", "Paris", "Barcelona", "Rome", "Copenhagen"],
        continent[5]: ["Darwin", "Brisbane", "Sydney", "Melbourne", "Perth"]}

travelperiod = ["Summer",
                "Autumn",
                "Winter",
                "Spring"]
               
               
tripduration = ["a few days",
                "a few weeks",
                "a few months"]

               
holidaytype = ["Active",
               "Relaxing",
               "Partying"]
               

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
       
        if topicID == 1:   # Continent
            option = [None]+random.sample(sorted(continent), len(continent))
            optNRs = [3,0]
            response = [1,1,1,0]
        elif topicID == 2: # City
            option = [None]+random.sample(sorted(city[CONTINENT[0]]), len(city[CONTINENT[0]]))
            optNRs = [2,2]
            response = [1,1,1,1]+[1,1,1,0]
        elif topicID == 3: # Travelperiod
            option = [None]+random.sample(sorted(travelperiod), len(travelperiod))
            optNRs = [4,0]
            response = [1,1,1,0]
        elif topicID == 4: # Trip duration
            option = [None]+tripduration
            optNRs = [3,0]
            response = [0,0,1,0]+[0,1,0,0]
        elif topicID == 5: # Holiday type  
            option = [None]+random.sample(sorted(holidaytype), len(holidaytype))
            optNRs = [3,0]
            response = [0,1,0,0]+[0,1,0,0]+[1,0,0,0] # has NO Iinfo utterances!!
        option += ['']*(max_options-len(option)+1)
   
    print('Option list =',option[1:])
       
    # Make sure keys share the same value between dict "topicoptions" and "alt_topicoptions" for sentences that belong to the same topic.
    #1 CONTINENT
    #2 CITY
    #3 PERIOD
    #4 DURATION
    #5 HOLIDAYTYPE          
    topicoptions = {
    0:starting,

    1:["What continent or worldpart would you prefer to visit, please discuss if it is going to be "]+
    [option[1]]+[", "]+[option[2]]+[", or "]+[option[3]]+["."],
   
    2:["What city in "]+[CONTINENT]+[" would you like to see, I have four options. "]+[option[1]]+[", "]+
    [option[2]]+[", "]+[option[3]]+[" and "]+[option[4]]+[". Let us first talk about "]+[option[1]]+[" and "]+[option[2]]+["?"],
   
    3:["During which time period of the year would you think is best to be in "]+[CITY]+[", in the "]+
    [option[1]]+[", "]+[option[2]]+[", "]+[option[3]]+[" or perhaps in the "]+[option[4]]+["?"],
   
    4:["This is going great, only a few more steps are needed to complete your holiday definition. "]+
    ["Also important to determine is the total duration of your holiday stay. "]+
    ["Would you prefer to go "]+[option[1]]+[", " ]+[option[2]]+[", or rather "]+[option[3]]+["?"],
   
    5:["While keeping in mind the travel period in "]+[PERIOD]+[", what type of vacation would you prefer? "]+
    ["An "]+[option[1]]+[", "]+[option[2]]+[" or "]+[option[3]]+[" vacation?"],
    
    6:ending}
   
    alt1_topicoptions = {2:["And regarding "]+[option[3]]+[" and "]+[option[4]]+["?"]}
                
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
    global CONTINENT
#    global CITY
#    global PERIOD
#    global DURATION
#    global HOLIDAYTYPE

    global dialogstage
   
    if dialogstage == 1: #continent
        key = listtostr(OPT)
    elif dialogstage == 2: #city
        key = listtostr(OPT)
    elif dialogstage == 3: #travelperiod
        key = listtostr(OPT+CONTINENT)
    elif dialogstage == 4: #duration
        key = listtostr(OPT)
    elif dialogstage == 5: #holidaytype
        key = listtostr(OPT)
    else:
        key = "KeyMissing???"    

    info = {
    continent[0]:"Asias culture is rich in every sense, from heritage, architecture, and way of life, to the intense spirituality of the people.",
    continent[1]:"Travelling to Africa offers many vacation options. From a boat tour and safari in the jungle, to a relaxing spa and viewing the wildlife.",                
    continent[2]:"The USA is a versatile land, which is not surprising when nearly 4800 kilometres separate people on the west coast from those on the east coast.",
    continent[3]:"America is a super colourful continent, meaning that the people, their clothes, the music, and just life itself there is very diverse.",
    continent[4]:"With 27 countries located within the European Union alone, Europe offers a big cultural variety of travel experiences.",
    continent[5]:"With its vast and varied landscapes, unique wildlife, and white sand beaches, Australia is one of the most interesting continents around.",
   
    city[continent[0]][0]:"You can enjoy both urban and natural attractions in the mega metropolis Singapore.",
    city[continent[0]][1]:"It is said that Hong Kong will no doubt surprise you, and that there is an inspiring view of the Symphony of the Stars lightshow from the promenade.",
    city[continent[0]][2]:"No matter which resort in Bali you would choose, it will most likely boast a beautiful beach, an exotic spa, and an array full of dining options.",
    city[continent[0]][3]:"No trip to Tokyo would be complete without visiting some of the Buddhist and Shinto temples and shrines.",
    city[continent[0]][4]:"Despite the numerous options for things to do in the Maladives, most visitors simply lounge on the palatial resort island of their choice.",
   
    city[continent[1]][0]:"Your could start a day in Cape Town with a morning trip up the Table Mountain from where you will be able to enjoy spectacular views of the city.",
    city[continent[1]][1]:"Many visitors of Cairo go for a tour to the Pyramids of Giza, and see more of its ancient Egyptian ruins.",
    city[continent[1]][2]:"If you like history you can spend most of your time in or around the Medina, Marrakechs fortified old city.",
    city[continent[1]][3]:"Tanzania is mainly known for Serengeti National Park, which houses a huge population of wildlife large mammals.",
    city[continent[1]][4]:"Famous for its white idyllic beaches, even the most popular stretches of sand in Seychelles are never crowded.",
   
    city[continent[2]][0]:"The Golden Gate Bridge is a must see in San Francisco, just like a visit to Alcatraz Island to tour the infamous federal prison.",
    city[continent[2]][1]:"You will be surprised by New Yorks flourishing art, night life scenes, and the many huge skyscrapers and monuments.",
    city[continent[2]][2]:"A visit to Las Vegas will most likely revolve around the Strip, this is the place where you will find all the iconic neon lights and famous sights.",
    city[continent[2]][3]:"Night-life and rolling good times are the main attractions in New Orleans, plentiful live music clubs of nearly every style.",
    city[continent[2]][4]:"Relaxing at the beach is truly the best free activity possible in Miami.",
   
    city[continent[3]][0]:"Buenos Aires has much to offer like boutique-shopping, opera-watching, and tango-dancing.",
    city[continent[3]][1]:"If it is your first trip to Rio, you will want to savour a chilled coconut as you survey Copacabana beach.",
    city[continent[3]][2]:"Whale watching and horseback riding are for the adventurous traveller ways you can get acquainted with Argentine.",
    city[continent[3]][3]:"Impressive skyscrapers, colonial architecture and spectacular peaks all jockey for your attention in Santiago.",
    city[continent[3]][4]:"Costa Ricas strikingly diverse terrain of forests, wildlife reserves, and tropical beaches, offers something for every traveller.",
   
    city[continent[4]][0]:"Berlins history of battling ideologies makes for some of the most fascinating sightseeing in Europe.",
    city[continent[4]][1]:"If it is your first time to Paris, you will probably want to spend some time at the Eiffel Tower.",
    city[continent[4]][2]:"You do not want to miss out on seeing Gaudis La Sagrada Familia in Barcelona.",
    city[continent[4]][3]:"A must-see in ancient Rome on many travellers agenda is the Trevi Fountain.",
    city[continent[4]][4]:"You should definitely visit the Tivoli gardens in Copenhagen located nearby the Central Train Station.",
   
    city[continent[5]][0]:"Quite fascinating to see in Darwin are the big termite mounds in Litchfield natural park.",
    city[continent[5]][1]:"If you are not afraid to get wet feet, maybe rent a kayak to paddle across the twisty river of Brisbane.",
    city[continent[5]][2]:"In Sydney you should make time for the beach, Bondi and Coogee beach are favourites.",
    city[continent[5]][3]:"If you are a sports fan, visiting the Cricket Ground in Melbourne is essential.",
    city[continent[5]][4]:"Rottnest Island in Perth is a protected Class A nature reserve, perhaps nice to enjoy a little nature.",
   
    travelperiod[0]+continent[0]:"In the summer, Asia is for a large part pretty hot, muggy, and typhoon-prone.",
    travelperiod[1]+continent[0]:"It is a good period to enjoy daytime temps of around thirty degrees with below average room rates in autumn.",
    travelperiod[2]+continent[0]:"While cool temperatures during winter will discourage some travellers, maybe you will actually think it is ok.",
    travelperiod[3]+continent[0]:"If you wish to avoid both winters climate and summers humidity, spring is an exceptional time to visit.",
   
    travelperiod[0]+continent[1]:"Spending summertime in a desert climate is not really advised for travellers.",
    travelperiod[1]+continent[1]:"Late fall marks a sweet spot in the tourism calendar, the summer heat retreats and the crowds have yet to arrive.",
    travelperiod[2]+continent[1]:"Winter is prime tourist season in Africa, with visitors hoping to pair sightseeing with pleasant weather.",
    travelperiod[3]+continent[1]:"Springtime is a great time to visit Africa since the winter crowds are waning and the weather is gorgeous.",
   
    travelperiod[0]+continent[2]:"People from all over the country are drawn by the hope for nice weather and the promise of summertime activities in autumn.",
    travelperiod[1]+continent[2]:"Fall marks a sweet spot for North Americas tourism. Believe it or not, the weather is often warmer now than it is in the summer.",
    travelperiod[2]+continent[2]:"If you do not mind the chilly winds, you will find that winter is a great time to spend in the United States.",
    travelperiod[3]+continent[2]:"You can beat the tourist rush by visiting the USA in the spring, when the weather is mild and hotel prices have yet to rise.",
   
    travelperiod[0]+continent[3]:"South America winter season is great if you want to meet more locals that enjoy the moderate weather",
    travelperiod[1]+continent[3]:"South America spring is an ideal time for seeking sun and adventure.",
    travelperiod[2]+continent[3]:"Peak season is autumn in South America, hotel prices can be inflated during these months.",
    travelperiod[3]+continent[3]:"Crowds and hot summer weather dissipate in May, but still expect high humidity.",
   
    travelperiod[0]+continent[4]:"Be aware that summer forms the tourist season with high temperatures, high humidity and high prices for everything.",
    travelperiod[1]+continent[4]:"In autumn tourist season slows and hotel rates fall a little bit while still having comfortable temperatures.",
    travelperiod[2]+continent[4]:"You will find some great deals if you travel during the winter season, but it will be a little chilly.",
    travelperiod[3]+continent[4]:"Spring season is possibly the ideal time to travel in Europe due to low prices and pleasant temperatures.",
   
    travelperiod[0]+continent[5]:"Although wintertime in Australia, do not let that label fool you since the calendar is filled with mostly sunny days.",
    travelperiod[1]+continent[5]:"While autumn season here, the springtime in Australia is marked by warm days and breezy nights with an occasional serious rainfall.",
    travelperiod[2]+continent[5]:"Australias wet, humid summer season comes with temperatures reaching up to thirty degrees.",
    travelperiod[3]+continent[5]:"There is no need to pack anything more than a light jacket if you visit Australia during autumn.",
   
    tripduration[0]:"Sometimes shorter vacations make a more memorable experience.",
    tripduration[1]:"Going for a few weeks will allow for more extensive sightseeing.",
    tripduration[2]:"Going away for a few months can really change your perspective on things.",

    holidaytype[0]: "Being active will make sure you experience a lot on your vacation.",
    holidaytype[1]: "Relaxing is a good way to clear your head from stress and your day-to-day life.",
    holidaytype[2]: "It will be an oppurtunity to meet a lot of new people and make friends.",
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

    #1 CONTINENT
    #2 CITY
    #3 PERIOD
    #4 DURATION
    #5 HOLIDAYTYPE  
   
    def updateCHOICES(chosenOpt):
        #Hier moet het gekozen list item gestored worden. Deze functie wordt aangeroepen in line 548
        global dialogstage
        global option
        global nr
        global OPT
        global CONTINENT
        global CITY
        global PERIOD
        global DURATION
        global HOLIDAYTYPE
       
        if dialogstage == 1:
            CONTINENT[0] = chosenOpt
        elif dialogstage == 2:
            CITY[0] = chosenOpt
        elif dialogstage == 3:
            PERIOD[0] = chosenOpt
        elif dialogstage == 4:
            DURATION[0] = chosenOpt
        elif dialogstage == 5:
            HOLIDAYTYPE[0] = chosenOpt
       
        print ("Choices so far:", CONTINENT, CITY, PERIOD, DURATION, HOLIDAYTYPE)
   
    verdict = "So far it is to early to draw any conclusion"
    unknown = '?'
    plus = '+'
    #print "totaloptNR =", totaloptNR
   
    # MULTIPLE = more than one option possible
    # SINGLE = only one option possible
    # UNKNOWN = all options are undecided
    # NONE = no options are possible

    #deze code returned een verdict, gebasseerd op VERDICTlist en roept functie updateCHOICES aan om het door particpants gekozen item te storen.
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
                random.sample(set([0,1,2]), 3)
                shuffled_response += random.sample(sorted([Idirect,Iswitch,Iinfo]), 3)+[alt]

   
    print ("topic responce matrix     = ", response)
    print ("topic responceDONE matrix = ", responseDONE)
    print ("shuffled responce matrix  = ", shuffled_response)
   
    utterance_holiday_planner = ''
   
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
        utterance_holiday_planner = listtostr(DelayRepeatRandom(SpeedUP))
       
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
                        utterance_holiday_planner = listtostr(newtopicANDoptions(topicID, alt=1))     # all options handled, go to alternative
                        responseDONE[i] = 1
                        if NRofQuadr == quadr:
                            responseDONE[i-3:i] = [0,0,0]  # Replace first three places of last quadrant with 0's
                        if utterance_holiday_planner != "???":
                            break
                    else:
                        responseDONE[i] = 1 # Do not break the for loop in this case!
                        if responseDONE == response:
                            # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
                            OPT[0] = option[OPTnr]
                            utterance_holiday_planner = 2*PREFIX+listtostr(getoptionverdict())
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
                            utterance_holiday_planner = listtostr(DelayRepeatRandom(direct_turntake))
                        else:
                            if random.randint(0,1):
                                utterance_holiday_planner = listtostr(DelayRepeatRandom(TT_NoneFirstOPT))
                            else:
                                utterance_holiday_planner = listtostr(DelayRepeatRandom(direct_turntake))
                        responseDONE[i] = 1
                        OPTnr +=1
                        break
                    elif ItypeNR == 1:
                        if len(optNRs) > 1:
                            firstALT = optNRs[0]+1
                        else:
                            firstALT = 0
                        if OPTnr == 1 or OPTnr == firstALT:
                            utterance_holiday_planner = PREFIX+listtostr(DelayRepeatRandom(switch_turntake))
                        else:
                            if random.randint(0,1):
                                utterance_holiday_planner = PREFIX+listtostr(DelayRepeatRandom(TT_NoneFirstOPT))
                            else:
                                utterance_holiday_planner = PREFIX+listtostr(DelayRepeatRandom(switch_turntake))
                        responseDONE[i] = 1
                        OPTnr +=1
                        break
                    elif ItypeNR == 2:
                        utterance_holiday_planner = listtostr(infosentence())
                        responseDONE[i] = 1
                        if utterance_holiday_planner != "???":
                            OPTnr +=1
                            break
                        else:
                            if responseDONE == response:
                                # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
                                OPT[0] = option[OPTnr]
                                utterance_holiday_planner = 2*PREFIX+listtostr(getoptionverdict())
                                OPTnr = 1
                                dialogstage += 1
                                break
                    elif ItypeNR == 3:
                        OPTnr = optNRs[0]+1
                        OPT[0] = option[OPTnr]
                        utterance_holiday_planner = listtostr(newtopicANDoptions(topicID, alt=1))     # go to alternative
                        responseDONE[i] = 1
                        if utterance_holiday_planner != "???":
                            break
                        else:
                            if responseDONE == response:
                                # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
                                OPT[0] = option[OPTnr]
                                utterance_holiday_planner = 2*PREFIX+listtostr(getoptionverdict())
                                OPTnr = 1
                                dialogstage += 1
                                break
                   
    else:
        # Run verdict code, and return verdict sentence precedented with 2xPREFIX!
        OPT[0] = option[OPTnr]
        utterance_holiday_planner = 2*PREFIX+listtostr(getoptionverdict())
        OPTnr = 1
        dialogstage += 1
   
    return utterance_holiday_planner

   
def setUtteranceVARs(state, nameleft, nameright, MistyLooks, keypress):
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
        keypress=cv2.waitKey(0)
        for x in range(1,totaloptNR):
            if keypress == str(x):
                VERDICTindex = x
        if keypress == ord("+") or keypress == ord("-"): #ONLY WORKS IF CAMERA WINDOW IS ON FOREGROUND AND ACTIVE!!! (cv.WaitKey function is used)
            VERDICTlist[VERDICTindex] = keypress    
            PreferenceList[VERDICTindex] = keypress + PreferenceList[VERDICTindex][1:]
        if keypress == ord("*"):
            GoToSpeedUP = True
        if keypress == ord("/"):
            CancelSpeedUP = True

#    if ord(keypress) != 255:
#        print "keypress =", keypress
#    else:
#        print "keypress = None"
    print(str(dialogstage))
    print ("dialogstage =", GetDialogProgress())
    print(dialogstage)
#    print "option list =", option
#    print 'VERDICT list =',VERDICTlist
    print ('preference list =',PreferenceList[1:])

   
def utterance_holiday_planner(state, NameLeft, NameRight, MistyLooks, CharKeyPress):
    global dialogstage
    sentence = ''
   
    setUtteranceVARs(state, NameLeft, NameRight, MistyLooks, CharKeyPress) # = also embedded in main State Machine loop
    
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
