import random
CONTINENT = ['']
CITY = ['']
PERIOD = ['']
DURATION = ['']
HOLIDAYTYPE = ['']
OPT = ['']
CURRENTNAME = [0] # Subject names as seen from the perspective of the Nao
OTHERNAME = [0]   # Subject names as seen from the perspective of the Nao
RIGHTWRONG = [0]
max_options=9

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

def newtopicANDoptions(topicID=0, alt =0):
    global option

    if alt == 0:
        if topicID == 1: 
            option = [None] + continent
            chosen_option_continent = input("which option did the participants choose: ")
        elif topicID == 2:
            option = [None] + city
        elif topicID == 3:
            option = [None] + travelperiod
        elif topicID == 4:
            option = [None] + tripduration
        elif topicID == 5:
            option = [None] + holidaytype
        option += ['']*(max_options - len(option)+1)

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

def listtostr(listobj):
    if listobj != None:
        string = str(listobj)
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
    return string

def get_option_input_and_judge(topicID, options):
    
    while options:  # Continue as long as there are options to discuss
        # Display options with numbers
        option_map = {str(i + 1): option for i, option in enumerate(options)}
        print("\nOptions:")
        for number, option in option_map.items():
            print(f"{number}: {option}")

        # Input the option number being discussed
        option_number = input("Enter the number of the option the participants are discussing: ").strip()

        if option_number not in option_map:
            print(f"Invalid number. Please choose a number from: {', '.join(option_map.keys())}")
            continue

        # Get the corresponding option
        option = option_map[option_number]
        print(f"Option being discussed: {option}")
        print("Input participant agreement using '++', '+-', or '--':")

        # Wait for the agreement input
        while True:
            agreement = input("Enter agreement (++ for both agree, +- for one agrees, -- for both disagree): ").strip()
            if agreement not in ["++", "+-", "--"]:
                print("Invalid input. Please use '++', '+-', or '--'.")
                continue

            if agreement == "++":
                print("Both participants agree.")
                return f"The chosen option is '{option}' due to agreement."
            elif agreement == "+-":
                print("One participant agrees, the other disagrees. Provide more information and reassess.")
                break  # Ask for the next option after giving more information
            elif agreement == "--":
                print(f"Both participants disagree. Removing '{option}' from the options.")
                options.remove(option)  # Remove the option from the list
                break  # Move on to the next option

    return "No options left to discuss. All options were rejected."

def newtopicANDoptions(topicID=0, alt=0):
    global option

    if alt == 0:
        if topicID == 1:
            option = continent
        elif topicID == 2:
            option = city
        elif topicID == 3:
            option = travelperiod
        elif topicID == 4:
            option = tripduration
        elif topicID == 5:
            option = holidaytype
        else:
            option = []

    verdict = get_option_input_and_judge(topicID, option)
    print("\nVerdict:", verdict)


def utterance_holiday_planner(state, NameLeft, NameRight, MistyLooks):
    dialogstage = 0 # Dit moet elke keer als we een verdict hebben geüpdate worden
    if dialogstage == 0:
        sentence = listtostr(introduction)
        dialogstage = 1
    elif dialogstage != 1:
        sentence = listtostr(newtopicANDoptions)

    return sentence
        