import random
import msvcrt
CONTINENT = ['']
CITY = ['']
PERIOD = ['']
DURATION = ['']
HOLIDAYTYPE = ['']
THINGSTODO = ['']
MOBILITY = ['']
BUDGET = ['']
ACCOMODATION = [''] 
OPT = ['']
CURRENTNAME = [0]
OTHERNAME = [0]
RIGHTWRONG = [0]
max_options = 9

introduction = ["For this conversation the main goal is to figure out what a holiday should be like if you "+
                "have to travel and spend the entire vacation together. "+
                "I am going to ask you some questions about what your ideal holiday is. "+
                "Since the two of you are going on a hypothetical holiday together, "+
                "ask for each others opinion. "+
                "Are you ready to begin?"]
                
#1 CONTINENT
#2 CITY
#3 PERIOD
#4 DURATION
#5 HOLIDAYTYPE
#6 THINGSTODO
#7 ACCOMODATION
#8 MOBILITY
#9 BUDGET
                
ending = [[
    "Well thats about it. With all the information combined, you have arranged yourselves a holiday for "
] + DURATION + [
    " that will bring you to the continent of "
] + CONTINENT + [
    " in the city "
] + CITY + [
    ", during the "
] + PERIOD + [
    ". Once arrived you will have a typical "
] + HOLIDAYTYPE + [
    " vacation primarily going to "
] + THINGSTODO + [
    ". You will stay in a comfortable "
] + ACCOMODATION + [
    ". To explore your surroundings you will mainly go by "
] + MOBILITY + [
    ", which means the estimated budget will be "
] + BUDGET + [
    ". Thanks for having participated in our dialogue, the experiment will now continue to the next phase."
]]

holidaytype = [
    "Active",
    "Relaxing",
    "Partying"
]

thingstodo = {
    holidaytype[0]: [
        "visiting famous architectural buildings",
        "seeking adventure and entertainment"
    ],
    holidaytype[1]: [
        "exploring green areas of local nature",
        "simply enjoying good sunny weather"
    ],
    holidaytype[2]: [
        "simply enjoying good sunny weather",
        "visiting popular clubs and enjoying nightlife"
    ]
}

mobility = [
    "Public transfer",
    "Hitchhiking",
    "Car",
    "Foot",
    "Bike"
]

budget = [
    "less than 1000 euros",
    "up to 1500 euros",
    "up to 2000 euros",
    "more than 2000 euros"
]    

accomodation = [
    "Hostel",
    "Camping",
    "Bed and Breakfast",
    "Hotel",
    "Holiday resort",
    "Local residence"
]
   
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

def build_holiday_question(topicID=0, alt=0):
    global option

    if alt == 0:
        if topicID == 1:
            option = [None] + continent
        elif topicID == 2:
            chosen_continent = CONTINENT[0] if CONTINENT[0] else continent[0]
            option = [None] + city[chosen_continent]
        elif topicID == 3:
            option = [None] + travelperiod
        elif topicID == 4:
            option = [None] + tripduration
        elif topicID == 5:
            option = [None] + holidaytype
        elif topicID == 6:
            chosen_type = HOLIDAYTYPE[0] if HOLIDAYTYPE[0] else holidaytype[0]
            option = [None] + thingstodo[chosen_type]
        elif topicID == 7:
            option = [None] + accomodation
        elif topicID == 8:
            option = [None] + mobility
        elif topicID == 9:
            option = [None] + budget
        else:
            raise ValueError(f"Invalid topicID: {topicID}")

        option += [''] * (max_options - len(option) + 1)

    def format_options(opts):
        opts = [str(x) for x in opts if x]
        if len(opts) == 0:
            return ""
        elif len(opts) == 1:
            return opts[0]
        elif len(opts) == 2:
            return f"{opts[0]} or {opts[1]}"
        else:
            return ", ".join(opts[:-1]) + f" or {opts[-1]}"

    current_continent = CONTINENT[0] if CONTINENT[0] else ""
    current_city = CITY[0] if CITY[0] else ""
    current_period = PERIOD[0] if PERIOD[0] else ""
    current_type = HOLIDAYTYPE[0] if HOLIDAYTYPE[0] else ""

    topicoptions = {
        1: [
            "What continent or worldpart would you prefer to visit, and what are your reasons for choosing it? Please discuss your ideas together and try to reach an agreement on whether it should be "
        ] + [format_options(option[1:len(continent)+1])] + ["."],

        2: [
            "What city in "
        ] + [current_continent] + [
            " would you like to see? There are several options that are available, and each city has it own culture and experiences. The options are "
        ] + [format_options([x for x in option[1:] if x])] + ["."],

        3: [
            "During which time period of the year would you think is best to be in "
        ] + [current_city] + [
            "? Considering factors like the weather and the atmosphere. As these factors can have a positive or negative impact on your holiday. Would you prefer "
        ] + [format_options([x for x in option[1:] if x])] + ["?"],

        4: [
            "This is going great, only a few more steps are needed to complete your holiday destination. "
            "Also important to determine is the total duration of your holiday stay. Staying longer gives you opportunities to see more of the city, but shorter holidays have their own advantages, such as being more flexible and less demanding.  "
            "Would you prefer to go for "
        ] + [format_options([x for x in option[1:] if x])] + ["?"],

        5: [
            "Now that you have decided how long you will be staying on holiday. "
            "What type of vacation would you prefer to have? Different types of vacations can give you different experiences of the city. Would you like an ",
        ] + [format_options([x for x in option[1:] if x])] + [
            " vacation?"],

        6: [
            "What would you mainly like to do during this ",
        ] + [current_type] + [
            " holiday? Would you prefer ",
        ] + [format_options([x for x in option[1:] if x])] + [
            ", and what kind of activities or experiences are you most interested in while you are there?"
        ],

        7: [
            "What type of accommodation would fit this holiday best? Would you prefer ",
        ] + [format_options([x for x in option[1:] if x])] + [
            ". Will you go for more comfort, or would you rather keep the costs as low as possible and give up some comfort?"
        ],

        8: [
            "How would you mainly like to travel around at the destination? You can choose from the following options, each offering a different way to explore the area: ",
        ] + [format_options([x for x in option[1:] if x])],

        9: [
            "And finally, what budget would suit this holiday best? Would you prefer ",
        ] + [format_options([x for x in option[1:] if x])] + [
            ", and how does that fit with what you would like to do and experience during your trip?"
        ],

        10: ending
    }

    try:
        output_line = topicoptions[topicID]
    except:
        output_line = "???"

    return output_line

def set_derived_holiday_details():

    if not CONTINENT[0]:
        CONTINENT[0] = random.choice(continent)

    if not CITY[0]:
        CITY[0] = random.choice(city[CONTINENT[0]])

    if not PERIOD[0]:
        PERIOD[0] = random.choice(travelperiod)

    if not DURATION[0]:
        DURATION[0] = random.choice(tripduration)

    if not HOLIDAYTYPE[0]:
        HOLIDAYTYPE[0] = random.choice(holidaytype)

    chosen_type = HOLIDAYTYPE[0]

    if not THINGSTODO[0]:
        THINGSTODO[0] = random.choice(thingstodo[chosen_type])

    if chosen_type == "Active":
        if not MOBILITY[0]:
            MOBILITY[0] = random.choice(["Foot", "Bike", "Car"])
        if not BUDGET[0]:
            BUDGET[0] = random.choice(["up to 1500 euros", "up to 2000 euros"])
        if not ACCOMODATION[0]:
            ACCOMODATION[0] = random.choice(["Hostel", "Camping", "Local residence"])

    elif chosen_type == "Relaxing":
        if not MOBILITY[0]:
            MOBILITY[0] = random.choice(["Public transfer", "Foot", "Car"])
        if not BUDGET[0]:
            BUDGET[0] = random.choice(["less than 1000 euros", "up to 1500 euros"])
        if not ACCOMODATION[0]:
            ACCOMODATION[0] = random.choice(["Hotel", "Holiday resort", "Bed and Breakfast"])

    elif chosen_type == "Partying":
        if not MOBILITY[0]:
            MOBILITY[0] = random.choice(["Public transfer", "Car"])
        if not BUDGET[0]:
            BUDGET[0] = random.choice(["up to 1500 euros", "more than 2000 euros"])
        if not ACCOMODATION[0]:
            ACCOMODATION[0] = random.choice(["Hotel", "Local residence"])

    if not MOBILITY[0]:
        MOBILITY[0] = random.choice(mobility)

    if not BUDGET[0]:
        BUDGET[0] = random.choice(budget)

    if not ACCOMODATION[0]:
        ACCOMODATION[0] = random.choice(accomodation)
                     
breaksilence = ["So who has any ideas?",
                "So what do you both think?",
                "Who of you can say something about it?",
                "Let us try to share some ideas.",
                "There must be some opinion about it."]
                 
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

switch_turntake = [["To what degree would this also be your opinion?"], 
                   ["To what extent do you agree with "]+[CURRENTNAME]+["?"],
                   ["That is interesting, what about you?"],
                   ["Ok fair enough, how about you?"],
                   ["And what is your view?"],
                   ["How do you feel about that?"],
                   ["Anything to add on "]+[CURRENTNAME]+["s opinion?"],
                   ["Given what "]+[CURRENTNAME]+[" said, how would you comment on that?"],
                   ["Given what "]+[CURRENTNAME]+[" said, what would be your opinion?"]]

OpenPrefix = ["I can tell you that ",
              "Interesting to know is that ",
              "Did you know that ",
              "According to my information, ",
              "It is often said that ",
              "I like to share with you that "]

                
TT_NoneFirstOPT = [["How about "]+[OPT]+["?"],
                   ["What about "]+[OPT]+["?"],
                   ["What do you think of "]+[OPT]+["?"],
                   ["What is your opinion about "]+[OPT]+["?"],
                   ["What can you say about "]+[OPT]+["?"],
                   ["Any other judgement about "]+[OPT]+["?"],
                   ["What is your mind on "]+[OPT]+["?"]]

SpeedUP = [
    "You both agree to the same choice?",
    "So we have a mutual agreement?",
    "I guess the answer is clear then?",
    "Is it clear then what option it should be?",
    "It seems the answer is obvious then?",
    "No need to discuss more options, I guess?"
]

info = {
    continent[0]:"Asias culture is rich in every sense, from heritage, architecture, and way of life, to the intense spirituality of the people. This means a trip there can feel both culturally immersive and very different from what you may be used to.",
    continent[1]:"Travelling to Africa offers many vacation options. From a boat tour and safari in the jungle, to a relaxing spa and viewing the wildlife. It can therefore be a destination that combines adventure, nature, and relaxation in a unique way.",                
    continent[2]:"The USA is a versatile land, which is not surprising when nearly 4800 kilometres separate people on the west coast from those on the east coast. Because of this, travelling there can offer very different holiday experiences depending on where you choose to go.",
    continent[3]:"America is a super colourful continent, meaning that the people, their clothes, the music, and just life itself there is very diverse. That diversity can make the holiday feel lively, surprising, and full of different cultural influences.",
    continent[4]:"With 27 countries located within the European Union alone, Europe offers a big cultural variety of travel experiences. This allows you to choose between atmosperes and traditions that lies relatively closeby.",
    continent[5]:"With its vast and varied landscapes, unique wildlife, and white sand beaches, Australia is one of the most interesting continents around. It provides a lot of different cultures and cities to visit, where you can combine nature and city life.",
   
    city[continent[0]][0]:"You can enjoy both urban and natural attractions in the mega metropolis Singapore. This makes it a destination where modern city life and calm green spaces can both be part of the same holiday experience.",
    city[continent[0]][1]:"It is said that Hong Kong will no doubt surprise you, and that there is an inspiring view of the Symphony of the Stars lightshow from the promenade. Hong Kong has an amazing skyline and gives you an modern and luxury experience.",
    city[continent[0]][2]:"No matter which resort in Bali you would choose, it will most likely boast a beautiful beach, an exotic spa, and an array full of dining options. This makes Bali especially suitable for travellers who enjoy comfort, relaxation, and a tropical atmosphere.",
    city[continent[0]][3]:"No trip to Tokyo would be complete without visiting some of the Buddhist and Shinto temples and shrines. At the same time, the city is very modern and known for its anime, which is a style of animation.",
    city[continent[0]][4]:"Despite the numerous options for things to do in the Maladives, most visitors simply lounge on the palatial resort island of their choice. This would be very relaxing, laying on the beach and escaping the daily stress.",
   
    city[continent[1]][0]:"Your could start a day in Cape Town with a morning trip up the Table Mountain from where you will be able to enjoy spectacular views of the city. It is a place where you can also book day trips to see wild life.",
    city[continent[1]][1]:"Many visitors of Cairo go for a tour to the Pyramids of Giza, and see more of its ancient Egyptian ruins. This makes the city especially attractive for people who are interested in history and see one of the seven wonders of the world.",
    city[continent[1]][2]:"If you like history you can spend most of your time in or around the Medina, Marrakechs fortified old city. The city is often appreciated for its atmosphere, markets, and strong sense of local culture.",
    city[continent[1]][3]:"Tanzania is mainly known for Serengeti National Park, which houses a huge population of wildlife large mammals. The people are very kind and the local food is something you have to try.",
    city[continent[1]][4]:"Famous for its white idyllic beaches, even the most popular stretches of sand in Seychelles are never crowded. Making it a calm and peaceful destination",
   
    city[continent[2]][0]:"The Golden Gate Bridge is a must see in San Francisco, just like a visit to Alcatraz Island to tour the infamous federal prison. The city provides several experiences that has to be visited once in your life.",
    city[continent[2]][1]:"You will be surprised by New Yorks flourishing art, night life scenes, and the many huge skyscrapers and monuments. It is a really big city with a lot of people, and you will see extremely much yellow cabs driving around.",
    city[continent[2]][2]:"A visit to Las Vegas will most likely revolve around the Strip, this is the place where you will find all the iconic neon lights and famous sights. The city is especially suitable for travellers looking for entertainment, nightlife, but it is mostly known for gambling.",
    city[continent[2]][3]:"Night-life and rolling good times are the main attractions in New Orleans, plentiful live music clubs of nearly every style. This gives the city a lively and distinctive atmosphere that stands out from many other destinations.",
    city[continent[2]][4]:"Relaxing at the beach is truly the best free activity possible in Miami. At the same time, the city also offers nightlife, warm weather, and a very recognisable holiday vibe.",
   
    city[continent[3]][0]:"Buenos Aires has much to offer like boutique-shopping, opera-watching, and tango-dancing. It is a place that loves football and a must do is visiting one of the matches.",
    city[continent[3]][1]:"If it is your first trip to Rio, you will want to savour a chilled coconut as you survey Copacabana beach. You can travel through one of the many favelas with a gids, seeing how the local live overthere.",
    city[continent[3]][2]:"Whale watching and horseback riding are for the adventurous traveller ways you can get acquainted with Argentine. It is therefore a destination that can appeal strongly to people who want outdoor activities and variety.",
    city[continent[3]][3]:"Impressive skyscrapers, colonial architecture and spectacular peaks all jockey for your attention in Santiago. Climbing the Cerro Santa Lucía has to be on your bucket list.",
    city[continent[3]][4]:"Costa Ricas strikingly diverse terrain of forests, wildlife reserves, and tropical beaches, offers something for every traveller. A place where backpacking is very common.",
   
    city[continent[4]][0]:"Berlins history of battling ideologies makes for some of the most fascinating sightseeing in Europe. Besides its history, the city is also known for its creative atmosphere and the main music is techno.",
    city[continent[4]][1]:"If it is your first time to Paris, you will probably want to spend some time at the Eiffel Tower. Paris is seen as a romantic city, taking a ferry over the seine will give you the perfect view over the city.",
    city[continent[4]][2]:"You do not want to miss out on seeing Gaudis La Sagrada Familia in Barcelona. The city is often appreciated for its mix of beach life and city life. Eating paella and drinking sangria gives you an impression of their local dishes.",
    city[continent[4]][3]:"A must-see in ancient Rome on many travellers agenda is the Trevi Fountain. Rome can offer a strong sense of history as the Colloseum is located there as well.",
    city[continent[4]][4]:"You should definitely visit the Tivoli gardens in Copenhagen located nearby the Central Train Station. The city is very expensive, but it gives a modern look.",
   
    city[continent[5]][0]:"Quite fascinating to see in Darwin are the big termite mounds in Litchfield natural park. This makes the area especially appealing for travellers who enjoy unusual natural sights and warm outdoor settings.",
    city[continent[5]][1]:"If you are not afraid to get wet feet, maybe rent a kayak to paddle across the twisty river of Brisbane. Giving adventures experiences when visiting this place.",
    city[continent[5]][2]:"In Sydney you should make time for the beach, Bondi and Coogee beach are favourites. Sydney also has the Opera House which has to be visited when you are there.",
    city[continent[5]][3]:"If you are a sports fan, visiting the Cricket Ground in Melbourne is essential. This is one of the main sports in Australia.",
    city[continent[5]][4]:"Rottnest Island in Perth is a protected Class A nature reserve, perhaps nice to enjoy a little nature. This will give you views of wild animals.",
   
    travelperiod[0]+continent[0]:"In the summer, Asia is for a large part pretty hot, muggy, and typhoon-prone. That means this period may be less comfortable for travellers who prefer mild weather and predictable conditions.",
    travelperiod[1]+continent[0]:"It is a good period to enjoy daytime temps of around thirty degrees with below average room rates in autumn. This combination can make autumn attractive for travellers who want pleasant weather and better value.",
    travelperiod[2]+continent[0]:"While cool temperatures during winter will discourage some travellers, maybe you will actually think it is ok. For some people this can be a welcome change from extreme heat and humidity.",
    travelperiod[3]+continent[0]:"If you wish to avoid both winters climate and summers humidity, spring is an exceptional time to visit. It is often seen as one of the more balanced periods of the year.",
   
    travelperiod[0]+continent[1]:"Spending summertime in a desert climate is not really advised for travellers. The heat can strongly affect the activities you can do.",
    travelperiod[1]+continent[1]:"Late fall marks a sweet spot in the tourism calendar, the summer heat retreats and the crowds have yet to arrive. This can make travelling feel more relaxed and manageable.",
    travelperiod[2]+continent[1]:"Winter is prime tourist season in Africa, with visitors hoping to pair sightseeing with pleasant weather. For many travellers this makes it one of the most convenient times to go.",
    travelperiod[3]+continent[1]:"Springtime is a great time to visit Africa since the winter crowds are waning and the weather is gorgeous. This can create a nice balance between comfort and a less crowded experience.",
   
    travelperiod[0]+continent[2]:"People from all over the country are drawn by the hope for nice weather and the promise of summertime activities in autumn. This can make it an appealing period, although busier in some destinations and more expensive.",
    travelperiod[1]+continent[2]:"Fall marks a sweet spot for North Americas tourism. Believe it or not, the weather is often warmer now than it is in the summer. It can therefore be a very comfortable and attractive time to travel.",
    travelperiod[2]+continent[2]:"If you do not mind the chilly winds, you will find that winter is a great time to spend in the United States. This period may especially suit travellers who enjoy seasonal atmosphere and lower crowds making it less expensive as well.",
    travelperiod[3]+continent[2]:"You can beat the tourist rush by visiting the USA in the spring, when the weather is mild and hotel prices have yet to rise. This makes spring one of the best periods to go.",
   
    travelperiod[0]+continent[3]:"South America winter season is great if you want to meet more locals that enjoy the moderate weather. This can make the destination feel lively without the discomfort of extreme heat.",
    travelperiod[1]+continent[3]:"South America spring is an ideal time for seeking sun and adventure. It is often a period in which the weather supports both exploration and outdoor activities.",
    travelperiod[2]+continent[3]:"Peak season is autumn in South America, hotel prices can be inflated during these months. This means it may be attractive, but possibly less ideal for travellers with a tighter budget.",
    travelperiod[3]+continent[3]:"Crowds and hot summer weather dissipate in May, but still expect high humidity. Depending on your preferences, this can feel either manageable or slightly uncomfortable.",
   
    travelperiod[0]+continent[4]:"Be aware that summer forms the tourist season with high temperatures, high humidity and high prices for everything. Summer provides a lot of sun and almost no rain, but it will be busier and more expensive.",
    travelperiod[1]+continent[4]:"In autumn tourist season slows and hotel rates fall a little bit while still having comfortable temperatures. This period provides a good balance between comfort and costs.",
    travelperiod[2]+continent[4]:"You will find some great deals if you travel during the winter season, but it will be a little chilly. This period is more suitable if budget matters.",
    travelperiod[3]+continent[4]:"Spring season is possibly the ideal time to travel in Europe due to low prices and pleasant temperatures. It is often considered one of the most attractive periods if you want to have a holiday for sighteeing.",
   
    travelperiod[0]+continent[5]:"Although wintertime in Australia, do not let that label fool you since the calendar is filled with mostly sunny days. This can make the season feel much milder and more pleasant than expected.",
    travelperiod[1]+continent[5]:"While autumn season here, the springtime in Australia is marked by warm days and breezy nights with an occasional serious rainfall. Many travellers may find this a pleasant and lively time to visit.",
    travelperiod[2]+continent[5]:"Australias wet, humid summer season comes with temperatures reaching up to thirty degrees. This may be ideal for some sun-seeking travellers, but less comfortable for others.",
    travelperiod[3]+continent[5]:"There is no need to pack anything more than a light jacket if you visit Australia during autumn. This can make travelling feel easy and comfortable without extreme weather conditions.",
   
    tripduration[0]:"Sometimes shorter vacations make a more memorable experience. They can feel intense, efficient, and easier to fit into a busy schedule.",
    tripduration[1]:"Going for a few weeks will allow for more extensive sightseeing. It also gives you more flexibility to combine relaxation with multiple activities.",
    tripduration[2]:"Going away for a few months can really change your perspective on things. A longer stay often allows you to settle in more and experience the destination in a deeper way.",

    holidaytype[0]: "Being active will make sure you experience a lot on your vacation. It can be a good fit if you prefer movement, variety, and making the most of your time there.",
    holidaytype[1]: "Relaxing is a good way to clear your head from stress and your day-to-day life. It may suit you best if you want comfort, calmness, and time to unwind.",
    holidaytype[2]: "It will be an oppurtunity to meet a lot of new people and make friends. This type of holiday can be especially attractive if you enjoy energy, nightlife, and social experiences.",
}

def get_verdict_utterance(chosen_option, verdict_key="1", verdict_step=1):
    info_text = info.get(chosen_option, "")
    prefix = f"{random.choice(OpenPrefix)}{info_text} " if info_text else ""

    # support further discussion
    if verdict_step == 1:
        if verdict_key == '2':
            return (
                f"It sounds like multiple options could work. "
                f"What do you both think?"
            )

        elif verdict_key == '3':
            return (
                f"It seems none of the options fully fit your preferences. "
                f"What would you suggest?"
            )

        elif verdict_key == '4':
            return (
                f"I am not completely sure what your final preference is. "
                f"What do you both think about {chosen_option}?"
            )

        else:
            return f"It sounds like you both agreed on {chosen_option}. Is that correct?"

    # final decision
    else:
        if verdict_key == '2':
            return (
                f"It sounds like multiple options could work. "
                f"{prefix}"
                f"For now, I will select {chosen_option}. Is that okay?"
            )

        elif verdict_key == '3':
            return (
                f"It seems none of the options fully fit your preferences. "
                f"{prefix}"
                f"I will choose {chosen_option} as the closest option. Is that okay?"
            )

        elif verdict_key == '4':
            return (
                f"I am not completely sure what your final preference is. "
                f"{prefix}"
                f"I think {chosen_option} might fit best. Is that correct?"
            )

        else:
            return f"It sounds like you both agreed on {chosen_option}. Is that correct?"
    
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
