import random
HOUSELOCATION = ['']
HOUSETYPE = ['']
HOUSESIZE = ['']
OUTSIDE_SPACE = ['']
HOUSESTYLE = ['']
INTERIORSTYLE = ['']
SUSTAINABILITY = ['']
NEIGHBORHOOD = ['']
HOUSEBUDGET = ['']
OPT = ['']
CURRENTNAME = [0]
OTHERNAME = [0]
RIGHTWRONG = [0]
max_options = 9

introduction = [
    "For this conversation the main goal is to figure out what your ideal dream house should be like if you "
    "have to live there together. "
    "I am going to ask you some questions about what your ideal dream house is. "
    "Since the two of you are designing a hypothetical dream house together, "
    "ask for each others opinion. "
    "Are you ready to begin?"
]

# 1 LOCATION
# 2 HOUSE TYPE
# 3 HOUSE SIZE
# 4 OUTSIDE SPACE
# 5 HOUSE STYLE
# 6 INTERIOR STYLE
# 7 SUSTAINABILITY
# 8 NEIGHBORHOOD
# 9 BUDGET

ending = [[
    "Well thats about it. With all the information combined, you have arranged yourselves a dream house located in the "
] + HOUSELOCATION + [
    ", and it will be a "
] + HOUSETYPE + [
    " with "
] + HOUSESIZE + [
    ". The outdoor area will include "
] + OUTSIDE_SPACE + [
    ", while the overall architectural style will be "
] + HOUSESTYLE + [
    ". Inside, the house will have a "
] + INTERIORSTYLE + [
    " atmosphere. In terms of sustainability, it will feature "
] + SUSTAINABILITY + [
    ", and it will be situated in a "
] + NEIGHBORHOOD + [
    ". Finally, the house will fit within a "
] + HOUSEBUDGET + [
    ". Thanks for having participated in our dialogue, the experiment will now continue to the next phase."
]]

houselocation = [
    "a City",
    "a Village",
    "the Countryside",
    "the Coast"
]

housetype = [
    "an Apartment",
    "a Terrace house",
    "a Semi-detached house",
    "a Detached house"
]
housesize = [
    "a 2 bedrooms",
    "a 3 bedrooms",
    "a 4 bedrooms",
    "more than 4 bedrooms"
]

outside_space = [
    "no backyard",
    "a balcony",
    "a backyard with terrace",
    "a backyard with swimming pool"
]

housestyle = [
    "Minimalistic",
    "Traditional",
    "Industrial",
    "Farmhouse"
]

interiorstyle = [
    "cozy and warm",
    "modern and sleek",
    "luxurious and elegant",
    "creative and colorful"
]

sustainability = [
    "solar panels",
    "a heat pump",
    "good insulation",
    "smart energy management"
]

neighborhood = [
    "a friendly neighborhood",
    "an urban neighborhood",
    "a green environment",
    "a neighborhood close to work and facilities"
]

housebudget = [
    "a low budget",
    "a medium budget",
    "a high budget",
    "a luxury budget"
]

def build_dream_house_question(topicID=0, alt=0):
    global option

    if alt == 0:
        if topicID == 1:
            option = [None] + houselocation
        elif topicID == 2:
            option = [None] + housetype
        elif topicID == 3:
            option = [None] + housesize
        elif topicID == 4:
            option = [None] + outside_space
        elif topicID == 5:
            option = [None] + housestyle
        elif topicID == 6:
            option = [None] + interiorstyle
        elif topicID == 7:
            option = [None] + sustainability
        elif topicID == 8:
            option = [None] + neighborhood
        elif topicID == 9:
            option = [None] + housebudget
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

    topicoptions = {
        1: [
            "First, it is important to know at what location your dream house would be in? It should fit your lifestyle and routine. Please discuss whether it should be in "
        ] + [format_options(option[1:len(houselocation)+1])] + ["."],

        2: [
            "Now it is time to decide what type of house would your dream house be? There are several options, so would you like to live together in "
        ] + [format_options(option[1:len(housetype)+1])] + ["?"],

        3: [
            "What size would you like your dream house to be, looking at the number of bedrooms? How much space do you think you would need for comfort and guests? Would you prefer "
        ] + [format_options(option[1:len(housesize)+1])] + ["?"],

        4: [
            "This is going great, only a few more steps are needed to complete your dream house. "
            "Also important to determine is how the outside area of your dream house should look. "
            "Would you like "
        ] + [format_options(option[1:len(outside_space)+1])] + ["?"],

        5: [
            "Now what kind of appearance would make your house feel alive? Decide what style your dream house has to be? Would you like your house to be "
        ] + [format_options(option[1:len(housestyle)+1])] + ["?"],

        6: [
            "What kind of interior atmosphere, think of mood or feelings, would fit your dream house best? Would you prefer something "
        ] + [format_options(option[1:len(interiorstyle)+1])] + ["?"],

        7: [
            "Should your house be environmental friendly or future-proof? What sustainability feature would you most like to include? Would you prefer "
        ] + [format_options(option[1:len(sustainability)+1])] + ["?"],

        8: [
            "What kind of neighborhood would you like to live in? What will make your everyday life more pleasant and enjoyable? Would you like it to be in "
        ] + [format_options(option[1:len(neighborhood)+1])] + ["?"],

        9: [
            "And finally, what budget would fit your decisions of comfort and features for this dream house? Would you prefer "
        ] + [format_options(option[1:len(housebudget)+1])] + ["?"],

        10: ending,
    }

    try:
        output_line = topicoptions[topicID]
    except Exception:
        output_line = "???"

    return output_line

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
    houselocation[0]: "Living in the city provides easy access to public transportation, shopping centers, and cultural attractions, making it a convenient choice for those who enjoy a vibrant lifestyle.",
    houselocation[1]: "A village setting offers a quieter lifestyle with a close-knit community feel, often surrounded by nature and less crowded than the city. It is a great option if you value peace and familiarity.",
    houselocation[2]: "The countryside provides a peaceful and spacious environment, ideal for those who enjoy nature, farming, or simply a more relaxed pace of life. It provides more space and privacy.",
    houselocation[3]: "Living near the coast means being close to the beach, offering a scenic environment and potential for water activities, as well as fresh seafood. The views can give a holiday vibe in your everyday life.",  

    housetype[0]: "An apartment is a compact living space in a multi-unit building, usually offering amenities such as security, gyms, and sometimes a shared garden. This can be a practical choice if you do not want high maintenance. ",
    housetype[1]: "A terrace house is a row of identical houses sharing side walls, popular in urban areas, offering a balance between apartment living and standalone houses. Mostly close to the city and cheaper than a standalone house.",
    housetype[2]: "A semi-detached house is connected to another house on one side but offers more space and privacy compared to apartments or terrace houses. Often affordable and less trouble with the neighbors.",
    housetype[3]: "A detached house is a standalone building that provides the most privacy and space, ideal for families who prefer a larger living area and possibly a garden. It will be less dependent from others and gives you enough space to life.",

    housesize[0]: "A 2-bedroom house provides a bit more space, which can be used for guests, a home office, or a small family. Mostly for starters, but also useful for people that do not want to have a big house.",
    housesize[1]: "A 3-bedroom house is a common choice for families, offering enough space for children or additional rooms for hobbies or work. Provides more space and it is a balance between manageable and having enough room.",
    housesize[2]: "With 4 bedrooms, there is ample space for a larger family, guests, or even creating specialized rooms like a gym or studio. It is suitable for extra flexibility and gives room for hobby's.",
    housesize[3]: "More than 4 bedrooms provide significant living space, ideal for large families, multi-generational households, or those who need extra rooms for various purposes. Fits people who dream of having a vary spacious home with enough room for everything.",

    outside_space[0]: "Having no backyard may be typical for city apartments, but it often means less maintenance and more time to enjoy other activities, but it removes your option to sit outside in your own space when it is sunny.",
    outside_space[1]: "A balcony provides a small outdoor space to enjoy fresh air, grow some plants, or have a cup of coffee in the morning. It is a good option when you want to live close to the city.",
    outside_space[2]: "A backyard with a terrace gives space for outdoor activities like gardening, dining, or playing with pets or children. This is more affordable and gives extra flexibility.",
    outside_space[3]: "A backyard with a swimming pool offers luxury and relaxation, ideal for hot summers and entertaining guests. It makes the house feel more exclusive and create possibilities for social activities.",

    housestyle[0]: "A minimalistic style emphasizes simplicity, with clean lines and minimal decorations, creating a calm and clutter-free living space. Mostly appreciated by people who value calmness and order.",
    housestyle[1]: "Traditional style houses are known for their classic architecture and cozy interiors, often featuring wood and other natural materials. It makes the house feel watm and timeless, which is attractive to many people.",
    housestyle[2]: "An industrial style is characterized by raw, unfinished materials like exposed brick and metal, giving a modern, edgy look. People choose for this when they have bold design choices. ",
    housestyle[3]: "A farmhouse style combines rustic charm with modern comforts, often featuring wooden beams, spacious kitchens, and comfortable living areas. Creating a welcoming atmosphere with a lot of character.",

    interiorstyle[0]: "A cozy and warm interior style has warm colors and soft materials making it a comfortable place. It would be a good choice if you want your home to feel inviting.",
    interiorstyle[1]: "A modern and sleek interior is a style that uses open spaces and simple features. A clean and elegant interior style makes the house feel organized and spacious.",
    interiorstyle[2]: "A luxurious and elegant interior uses good quality materials and uses aesthetic features. Making it stylish and focuses more on comfort and appearance.",
    interiorstyle[3]: "A creative and colorful interior has artistic expression, and playful design choices. This interior style makes the house feel more lively and personal.",

    sustainability[0]: "Solar panels lowers the energy bills, making the house more environmentally friendly. It helps to save energy costs, while also reducing their impact on the environment.",
    sustainability[1]: "A heat pump is great to produce heat and cool down a home without using gas. This makes it a modern and efficient option for people who want a more sustainable home system.",
    sustainability[2]: "Excellent insulation improves the climate inside the house and lowers overall energy consumption. An example is that it can make the house feel warmer in the winter and cooler in the summer.",
    sustainability[3]: "Smart energy management helps monitor and optimize energy use in the house. This can make daily living more efficient and give better control over how the home performs.",

    neighborhood[0]: "A friendly neighborhood provides a place with peace, safety and a strong sense of community. People who value connection and a safe environment often choose this option.",
    neighborhood[1]: "An urban neighborhood makes it easy to go to shops, restaurants, and social activity. It makes life more convenient, everything is closeby and it can save you energy and time.",
    neighborhood[2]: "A green environment has beautiful views and easy access to outdoor activities. It creates a peaceful environment and a living experience, making it easier to enjoy nature.",
    neighborhood[3]: "Living close to work and facilities saves travel time and make daily life more convenient. It might reduce your stress and makes it easier to manage your day.",

    housebudget[0]: "A modest budget asks to make practical choices and prioritizing of features. Meaning you have to decide on what matters most because you can not have everything. ",
    housebudget[1]: "A medium budget gives a good balance between comfort, quality, and affordability. It is the most realistic option for attractive choices without becoming excessive.",
    housebudget[2]: "A high budget allows for more customization, extra space, and premium materials. This gives more freedom to shape the house according to your personal wishes and preferences.",
    housebudget[3]: "A luxury budget offers the freedom to do what you want, to let you choose for extensive space, and exclusive features. There are no limitations and makes it possible to create your ideal house."
}

def set_derived_dream_house_details():
    if not HOUSELOCATION[0]:
        HOUSELOCATION[0] = random.choice(houselocation)

    if not HOUSETYPE[0]:
        HOUSETYPE[0] = random.choice(housetype)

    if not HOUSESIZE[0]:
        HOUSESIZE[0] = random.choice(housesize)

    if not OUTSIDE_SPACE[0]:
        OUTSIDE_SPACE[0] = random.choice(outside_space)

    if not HOUSESTYLE[0]:
        HOUSESTYLE[0] = random.choice(housestyle)

    if not INTERIORSTYLE[0]:
        INTERIORSTYLE[0] = random.choice(interiorstyle)

    if not SUSTAINABILITY[0]:
        SUSTAINABILITY[0] = random.choice(sustainability)

    if not NEIGHBORHOOD[0]:
        NEIGHBORHOOD[0] = random.choice(neighborhood)

    if not HOUSEBUDGET[0]:
        HOUSEBUDGET[0] = random.choice(housebudget)
        
def get_verdict_utterance(chosen_option, verdict_key="1", verdict_step=1):
    info_text = info.get(chosen_option, "")
    prefix = f"{random.choice(OpenPrefix)}{info_text} " if info_text else ""
    # support further discussion
    if verdict_step == 1:
        if verdict_key == '2':
            return (
                f"It sounds like multiple options could work. Let me give you some useful information. "
                f"{prefix}"
                f"What do you both think?"
            )

        elif verdict_key == '3':
            return (
                f"It seems none of the options fully fit your preferences. Let me give you some useful information. "
                f"{prefix}"
                f"What would you suggest?"
            )

        elif verdict_key == '4':
            return (
                f"I am not completely sure what your final preference is. Let me give you some useful information. "
                f"{prefix}"
                f"What do you both think about {chosen_option}?"
            )

        else:
            return f"It sounds like you both agreed on {chosen_option}. Is that correct?"

    # final decision
    else:
        if verdict_key == '2':
            return (
                f"It sounds like multiple options could work. "
                f"For now, I will select {chosen_option}. Is that okay?"
            )

        elif verdict_key == '3':
            return (
                f"It seems none of the options fully fit your preferences. "
                f"I will choose {chosen_option} as the closest option. Is that okay?"
            )

        elif verdict_key == '4':
            return (
                f"I am not completely sure what your final preference is. "
                f"I think {chosen_option} might fit best. Is that correct?"
            )

        else:
            return f"It sounds like you both agreed on {chosen_option}. Is that correct?"
        
def listtostr(listobj):
    if listobj is not None:
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
