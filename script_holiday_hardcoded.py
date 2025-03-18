CONTINENT = None
HOLIDAYTYPE = None
DURATION = None
PERIOD = None
ACCOMODATION = None
option = None


starting = ["I am also ready, so let us start to talk and discuss your holiday options together."]

ending = [["Well thats about it. With all the information combined, you have arranged yourselves a holiday for "]+[DURATION]+
        [" that will bring you to the continent of "]+[CONTINENT]+[" in the accomodation type "]+[ACCOMODATION]+[" , during the "]+[PERIOD]+[". "]+
        ["Once arrived you will have a typical "]+[HOLIDAYTYPE]+[" vacation "]+
        ["Thanks for having participated in our dialogue, the experiment will now continue to the next phase."]] #Make Nao turn to both participants on this sentence (future work)
            

continent = ["Azia",
            "United States",
            "Europe",
            "Australia"]

travelperiod = ["Summer",
                "Autumn",
                "Winter",
                "Spring"]

accomodation = ["Camping",
                "Bed and Breakfast",
                "Hotel",
                "Holiday resort"]
            
            
tripduration = ["a few days",
                "a few weeks",
                "a few months"]

            
holidaytype = ["Active",
            "Relaxing",
            "Partying"]


question1 = "What continent or worldpart would you prefer to visit, please discuss if it is going to be "+ continent[0]+", "+continent[1]+", "+continent[2]+", or "+continent[3]+"."

question2 = "During which time period of the year would you think is best to go, in the "+ travelperiod[0]+", "+ travelperiod[1]+", "+travelperiod[2]+" or perhaps in the "+travelperiod[3]+"?",

question3 ="Now we know where and during which time period, would you want to go to a" + accomodation[0]+", " + accomodation[1] +", " +accomodation[2] + "or would you prefer the luxury of a" +accomodation[3]+"?"

question4 = "This is going great, only a few more steps are needed to complete your holiday definition. "+ "Also important to determine is the total duration of your holiday stay. "+ "Would you prefer to go "+tripduration[0]+", " +tripduration[1]+", or rather "+tripduration[2]+"?"

question5 = "While keeping in mind the travel period what type of vacation would you prefer? "+ "An "+holidaytype[0]+", "+holidaytype[1]+" or "+holidaytype[2]+" vacation?",



info_holiday = {
continent[0]:"Asias culture is rich in every sense, from heritage, architecture, and way of life, to the intense spirituality of the people.",           
continent[1]:"The USA is a versatile land, which is not surprising when nearly 4800 kilometres separate people on the west coast from those on the east coast.",
continent[2]:"With 27 countries located within the European Union alone, Europe offers a big cultural variety of travel experiences.",
continent[3]:"With its vast and varied landscapes, unique wildlife, and white sand beaches, Australia is one of the most interesting continents around.",

travelperiod[0]+continent[0]:"In the summer, Asia is for a large part pretty hot, muggy, and typhoon-prone.",
travelperiod[1]+continent[0]:"It is a good period to enjoy daytime temps of around thirty degrees with below average room rates in autumn.",
travelperiod[2]+continent[0]:"While cool temperatures during winter will discourage some travellers, maybe you will actually think it is ok.",
travelperiod[3]+continent[0]:"If you wish to avoid both winters climate and summers humidity, spring is an exceptional time to visit.",

travelperiod[0]+continent[1]:"People from all over the country are drawn by the hope for nice weather and the promise of summertime activities in autumn.",
travelperiod[1]+continent[1]:"Fall marks a sweet spot for North Americas tourism. Believe it or not, the weather is often warmer now than it is in the summer.",
travelperiod[2]+continent[1]:"If you do not mind the chilly winds, you will find that winter is a great time to spend in the United States.",
travelperiod[3]+continent[1]:"You can beat the tourist rush by visiting the USA in the spring, when the weather is mild and hotel prices have yet to rise.",

travelperiod[0]+continent[2]:"Be aware that summer forms the tourist season with high temperatures, high humidity and high prices for everything.",
travelperiod[1]+continent[2]:"In autumn tourist season slows and hotel rates fall a little bit while still having comfortable temperatures.",
travelperiod[2]+continent[2]:"You will find some great deals if you travel during the winter season, but it will be a little chilly.",
travelperiod[3]+continent[2]:"Spring season is possibly the ideal time to travel in Europe due to low prices and pleasant temperatures.",

travelperiod[0]+continent[3]:"Although wintertime in Australia, do not let that label fool you since the calendar is filled with mostly sunny days.",
travelperiod[1]+continent[3]:"While autumn season here, the springtime in Australia is marked by warm days and breezy nights with an occasional serious rainfall.",
travelperiod[2]+continent[3]:"Australias wet, humid summer season comes with temperatures reaching up to thirty degrees.",
travelperiod[3]+continent[3]:"There is no need to pack anything more than a light jacket if you visit Australia during autumn.",

accomodation[0]:"A camping often offers multiple ways to stay like in a tent, caravan, or in a bungalow.",
accomodation[1]:"A Bed and Breakfast is a perfect choice if you want to save money and join in on an already served breakfast.",
accomodation[2]:"A hotel is a sound choice if you aim for a more catered holiday.",
accomodation[3]:"If you like the safe environment with extra leisure options, a holiday resort is a good option.",

tripduration[0]:"Sometimes shorter vacations make a more memorable experience.",
tripduration[1]:"Going for a few weeks will allow for more extensive sightseeing.",
tripduration[2]:"Going away for a few months can really change your perspective on things.",

holidaytype[0]: "Being active will make sure you experience a lot on your vacation.",
holidaytype[1]: "Relaxing is a good way to clear your head from stress and your day-to-day life.",
holidaytype[2]: "It will be an oppurtunity to meet a lot of new people and make friends."
}