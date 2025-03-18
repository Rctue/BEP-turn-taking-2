from Misty_commands import Misty
import time
import cv2
import numpy as np
import base64
from script_holiday_hardcoded import *
from script_dream_house_hardcoded import *
from script_timetravel_hardcoded import *
import msvcrt
import random
import datetime
from datetime import datetime
import AVData
import json
import csv

#making headposition variables global so we can extract them in the eyecontact_duration code:

robot_ip = "192.168.0.100"
misty = Misty(ip_address=robot_ip)
log_data = AVData.AVData()
log_data.init_robot(robot_ip)


def log_newstate_pressedButton(IDP1, IDP2, new_state, pressedButton):
    ct = datetime.now()
    file_name = "result_"+str(IDP1)+'_'+str(IDP2)+".txt"
    f = open(file_name,'a')
    f.write(str(new_state) + '\t' + str(pressedButton) + '\t' + str(ct) + '\t' + str(head_position_left) + '\t'  +'\n')
    f.close()

def get_headpose():
    current_date = datetime.now().strftime("%Y-%m-%d_%H:%M")
    filename = f"headposedata_{current_date}.csv"

    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=log_headpose[0].keys())
        writer.writeheader()
        writer.writerows(log_headpose)

    print(f"Data saved to {filename}")

def add_headposition():
    if head_position_left == True:
        direction = "l"
    elif head_position_left == False:
        direction = "r"
    daytime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    add_pose = {
        "time": daytime,
        "direction": direction
        }
    log_headpose.append(add_pose)

def get_eyecontact():
    with open("headposition_data.json", "r") as f:
        headposition_data = json.load(f)

    current_date = datetime.now().strftime("%Y-%m-%d_%H:%M")
    #print("Current Time: ", current_date
    #print head_position_data
    filename = f"eyecontact_data_{current_date}.csv"

    with open(filename, "w", newline='') as csvfile:
        # Get the column names from the first item if it's a list of dictionaries
        if isinstance(headposition_data, list) and headposition_data:
            #fieldnames = headposition_data[0].keys()  # Use keys of the first dict as column headers
            writer = csv.DictWriter(csvfile, fieldnames=headposition_data[0].keys())
            writer.writeheader()  
            writer.writerows(headposition_data) 
        else:
             print("Data format not supported for CSV export")

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

def main(): 
    # code of Maurice, I want to start with logging here.
    new_state = 0
    #Initialize everything
    
    log_data.init_devices()

    #Initialize headpose log:
    global log_headpose
    log_headpose =[]

    # When the states need to be reset, each time that a new state is entered, this StateManager class can fix this issue
    chosen_options = []
    
    # This still needs to be updated according to what the robot has to do. Everything that needs to be done is written in the prints.
    # It needs to check what the results of the tests are, and based on that determine the new state that the robot is in. 
    while new_state != 12:
        if (new_state == 0):
            # Start of program: the code will be started and it will start all sub-porcesses. 
            print("Initializing the program...")
            emotional_condition = input("Please give the emotional condition (n = neutral), (h = happy), (s = sad) : ")
            topic = input ("Please give the topic (h = holiday planner, d = dream house, t = time-travel): ")
            gestures = input("Please enter whether gestures are used in this experiment (y/n): ")
            NameParticipant1 = input("Please give the name of Participant 1 (sitting on the left of Misty): ")
            global IDP1 
            IDP1 = input("What is the ID of participant 1 (sitting on the left of Misty): ")
            NameParticipant2 = input("Please give the name of Participant 2 (sitting on the right of Misty): ")
            global IDP2
            IDP2 = input("What is the ID of participant 2 (sitting on the right of Misty): ")
            print("The human on the left side needs to have the audio1 input, otherwise the robot will look at the non-speaking person.")
            
            log_data.experiment_data = {'condition':emotional_condition, 'topic': topic, 'gestures': gestures.lower(), 'IDP1': IDP1, 'IDP2': IDP2}

            #Ensure that it will start with the first utterance
            current_state = 0
            # Ensure that it knows that it is neither facing participant1 nor participant2
            global head_position_left
            head_position_left = False
            head_moved_left = False
            OTHERNAME = None
            dialogstage = -1


            # Here we will start the correct topic
            misty.move_head(-20, 0, 0, 90)
            if (topic == "h"):
                introduction = ["Hi there. For this conversation the main goal is to figure out what a holiday should be like if you "+
                "have to travel and spend the entire vacation together. "+
                "I am going to ask you some questions about what your ideal holiday is. "+
                "Since the two of you are going on a hypothetical holiday together, "+
                "ask for each others opinion. "+
                "Are you ready to begin?"]
                intro = listtostr(introduction)
                misty.speak(intro)
                new_state = 4
            elif (topic == "d"):
                introduction = ["Hello. For this conversation the main goal is to figure out what your dream house "+ 
                "would be if you would live together. "+
                "I am going to ask you some questions about what your dream house would look like. "+
                "Since the two of you are going to hypothetically live there together, "+
                "ask for each others opinion. "+
                "Are you ready to begin?"]
                intro = listtostr(introduction)
                misty.speak(intro)
                new_state = 4
            elif (topic == "t"):
                introduction = ["Hi there. For this conversation the main goal is to figure out what you would do "+
                "if you had the chance to time travel together. "+
                "I am going to ask you some questions about all the things you want to do in your "+
                "time travel journey. Since the two of you are going to hypothetically time travel "+
                "together, ask for each others opinion. "+
                "Are you ready to begin?"]
                intro = listtostr(introduction)
                misty.speak(intro)
                new_state = 4
            else:
                new_state = 0
            

        elif (new_state == 1):
            if dialogstage >= 0:
                random_time = random.randint(6, 10)
                time.sleep(random_time)

            print("Here the robot will know it's emotional_condition and show the emotional_condition.")
            misty.display_image(fileName="e_DefaultContent.jpg") # It shows the image of the neutral face
            misty.move_head(-20, 0, 0, 90)
            new_state = 2

        elif (new_state == 2):
            print("Check for silence or sound.")
            print("Type s if silence. Type l if left participant is speaking, type r if right participant is speaking")
            pressedButton = msvcrt.getch().decode('ASCII')
            print(pressedButton)
            log_newstate_pressedButton(IDP1, IDP2, new_state, pressedButton)
            if pressedButton == 's':
                # If there is a silence, we will go to state 3
                new_state = 3
            elif pressedButton == "l":
                print("Button 'l' was pressed.")
                head_position_left = True
                new_state = 4
            elif pressedButton == "r":
                head_position_left= False
                new_state = 4

        elif (new_state == 3):
            misty.display_image(fileName="e_DefaultContent.jpg") # It shows the image of the neutral face
            misty.move_head(-20, 0, 0, 90)
            breaksilence = ["So who has any ideas?",
                "So what do you both think?",
                "Who of you can say something about it?",
                "Let us try to share some ideas."]
            chosen_breaksilence = random.randint(0, len(breaksilence) - 1)
            chosen_breaksilence_result = listtostr(breaksilence[chosen_breaksilence])
            misty.speak(chosen_breaksilence_result)
            new_state = 2

        elif (new_state == 4):
            # Here the robot will turn the head towards the active speaker, whom has been speaking for over 4 seconds.
            if dialogstage == -1:
                misty.move_head(-20, 0, 0, 90)
                new_state = 5
            elif head_position_left:
                misty.move_head(-20, 0, -54, 90)
                head_moved_left = True
                add_headposition()
                print("Participant 1 seemed to be talking, so I will turn my head towards them.")
                new_state = 5
            elif not head_position_left:
                misty.move_head(-20, 0, 54, 90)
                add_headposition()
                head_moved_left = False
                print("Participant 2 seemed to be talking, so I have turned my head towards them.")
                new_state = 5
            else: 
                misty.move_head(0, 0, 0, 0)
                new_state = 5

        elif (new_state == 5):
            print("Type 'c' if one person is talking too long, type 'd' if they have switched turns, type 't' for a turn-switch, type 'i' for info. Type 'v' to check the chosen verdict For the first it will just continue furhter.Type 'r' to repeat the question.")
            pressedButton = msvcrt.getch().decode('ASCII')
            log_newstate_pressedButton(IDP1, IDP2, new_state, pressedButton)
            if (pressedButton == "c"):
                    new_state = 6
            elif (pressedButton == "d"):
                if head_position_left:
                    head_position_left = False
                else:
                    head_position_left = True
                new_state = 4
            elif (pressedButton == "t"):
                new_state = 8
            elif (pressedButton == "i"):
                new_state = 9
            elif (pressedButton == 'v'):
                new_state = 10
            elif (pressedButton == 'r'):
                new_state = 11
            else:
                new_state = 5

        elif (new_state == 6):
            # The robot should pronounce a backchannel utterance
            longturnindicator = ["So to come to a conclusion, what do you prefer?",
                     "So what are your favorite options?",
                     "So to make a decision, what do you both agree on?"]
            chosen_longturnindicator = random.randint(0, len(longturnindicator) - 1)
            chosen_longturnindicator_result = listtostr(longturnindicator[chosen_longturnindicator])
            misty.speak(chosen_longturnindicator_result)
            new_state = 5


        elif (new_state == 7):
            if log_data.is_logging:
                log_data.stop_logging_data()
            
            # After the robot has said something, it will go back to showing an emotion and start again with testing whether someone is speaking, etc.
            # Here the robot will take a turn and start talking, or asking a new question, etc. It should take the correct utterance.")
            current_state += 1
            dialogstage +=1
            random_time = random.randint(5, 10)

            if (emotional_condition == "n"):
                # Show neutral face all along and no gestures.
                misty.display_image(fileName="e_DefaultContent.jpg") # It shows the image of the neutral face
                misty.move_head(-20, 0, 0, 90)
            elif (emotional_condition == "h"):
                # Happy face during talking after a question or when a turn has been given. Specify the timing of the gestures
                # Condition happy
                misty.display_image(fileName="e_Joy.jpg") # It shows the image of the 'happy' eyes
                if gestures == "y":
                    misty.move_head(-30, 0, 0, 90)       
                else:
                    misty.move_head(-20, 0, 0, 90)
            elif (emotional_condition == "s"):
                # Condition sad
                misty.display_image(fileName="e_Sadness.jpg") # It shows the image of the 'sad' eyes
                if gestures == "y":
                    misty.move_head(10, 0, 0 , 90)
                else:
                    misty.move_head(-20, 0, 0, 90)
            
            if dialogstage != 6:
               log_data.start_logging_data()
            
            # Now, the robot will start talking 
            if (topic=="h"):
                if dialogstage == 0:
                    starting_holiday = listtostr(starting)
                    misty.speak(starting_holiday)
                    new_state = 7
                elif dialogstage == 1:
                    question1_holiday = listtostr(question1)
                    misty.speak(question1_holiday) 
                    new_state = 1
                elif dialogstage == 2:
                    question2_holiday = listtostr(question2)
                    misty.speak(question2_holiday)
                    new_state = 1
                elif dialogstage == 3:
                    question3_holiday = listtostr(question3)
                    misty.speak(question3_holiday)
                    new_state = 1
                elif dialogstage == 4:
                    question4_holiday = listtostr(question4)
                    misty.speak(question4_holiday)
                    new_state = 1
                elif dialogstage == 5:
                    question5_holiday = listtostr(question5)
                    misty.speak(question5_holiday)
                    new_state = 1
                elif dialogstage == 6: 
                    ending = [["Well thats about it. With all the information combined, you have arranged yourselves a holiday for "]+[chosen_options[3]]+
                    [" that will bring you to the continent of "]+[chosen_options[0]]+[" in the accomodation type "]+[chosen_options[2]]+[" , during the "]+[chosen_options[1]]+[". "]+
                    ["Once arrived you will have a typical "]+[chosen_options[4]]+[" vacation "]+ ["Thanks for having participated in our dialogue, it would be nice if you start with filling in the questionnaire."]]
                    ending_holiday = listtostr(ending)
                    misty.speak(ending_holiday)
                    new_state = 12
            elif (topic=="d"):
                if dialogstage == 0:
                    starting_dreamhouse = listtostr(starting_d)
                    misty.speak(starting_dreamhouse)
                    new_state = 7
                elif dialogstage == 1:
                    question1_dreamhouse = listtostr(question1_d)
                    misty.speak(question1_dreamhouse) 
                    new_state = 1
                elif dialogstage == 2:
                    question2_dreamhouse = listtostr(question2_d)
                    misty.speak(question2_dreamhouse)
                    new_state = 1
                elif dialogstage == 3:
                    question3_dreamhouse = listtostr(question3_d)
                    misty.speak(question3_dreamhouse)
                    new_state = 1
                elif dialogstage == 4:
                    question4_dreamhouse = listtostr(question4_d)
                    misty.speak(question4_dreamhouse)
                    new_state = 1
                elif dialogstage == 5:
                    question5_dreamhouse = listtostr(question5_d)
                    misty.speak(question5_dreamhouse)
                    new_state = 1
                elif dialogstage == 6:
                    ending_d = [["That was about it. With all the information combined, the dream house you have built is a "]+[chosen_options[1]]+ ["in "]+[chosen_options[0]]+["with "]+[chosen_options[2]]+
                    ["Your dream house has "]+[chosen_options[3]]+["and will be a "]+[chosen_options[4]]+["style house "]+
                    ["Thanks for having participated in our dialogue, it would be nice if you could fill in the questionnaire."]]
                    ending_dreamhouse = listtostr(ending_d)
                    misty.speak(ending_dreamhouse)
                    new_state = 12
            elif(topic=="t"):
                if dialogstage == 0:
                    starting_timetravel = listtostr(starting_t)
                    misty.speak(starting_timetravel)
                    new_state = 7
                elif dialogstage == 1:
                    question1_timetravel = listtostr(question1_t)
                    misty.speak(question1_timetravel)
                    new_state = 1
                elif dialogstage == 2:
                    question2_timetravel = listtostr(question2_t)
                    misty.speak(question2_timetravel)
                    new_state = 1
                elif dialogstage == 3:
                    question3_timetravel = listtostr(question3_t)
                    misty.speak(question3_timetravel)
                    new_state = 1
                elif dialogstage == 4:
                    question4_timetravel = listtostr(question4_t)
                    misty.speak(question4_timetravel)
                    new_state = 1
                elif dialogstage == 5:
                    question5_timetravel = listtostr(question5_t)
                    misty.speak(question5_timetravel)
                    new_state = 1
                elif dialogstage == 6:
                    ending_t= [["That was already it. With all the information combined, for your time travel trip "+
                    "you will go "]+[chosen_options[2]]+[" back to "]+[chosen_options[0]]+[" for "]+[chosen_options[4]]+["."]+
                    [" In this period of time you will have "]+[chosen_options[1]]+[" and you will "]+[chosen_options[3]]+["."]+
                    ["Thanks for having participated in our dialogue, can you start filling in the questionnaires?"]]
                    ending_time_travel = listtostr(ending_t)
                    misty.speak(ending_time_travel)
                    new_state = 12
            else: 
                new_state = 0
        
            print("Misty should have given a response.")
            print("Current state:" + str(current_state))
            '''
            if (emotional_condition == "n"):
                # Show neutral face all along and no gestures.
                misty.display_image(fileName="e_DefaultContent.jpg") # It shows the image of the neutral face
                misty.move_head(-20, 0, 0, 90)
            elif (emotional_condition == "h"):
                # Condition happy bring back to neutral
                misty.display_image(fileName="e_DefaultContent.jpg") # It shows the image of the 'neutral' eyes
                misty.move_head(-20, 0, 0, 90)
            elif (emotional_condition == "s"):
                # Condition sad bring back to neutral
                misty.display_image(fileName="e_DefaultContent.jpg") # It shows the image of the 'neutral' eyes
                misty.move_head(-20, 0, 0, 90)
            '''
        
        elif (new_state == 8):
            print ("Type 'd' to direct a turn-take, type 's' to switch the turn-take.")
            pressedButton = msvcrt.getch().decode('ASCII')
            log_newstate_pressedButton(IDP1, IDP2, new_state, pressedButton)
            if head_moved_left:
                CURRENTNAME = NameParticipant1
                OTHERNAME = NameParticipant2
                log_data.experiment_data['left_pp'] = IDP1
                log_data.experiment_data['right_pp'] = IDP2
                
            else:
                CURRENTNAME = NameParticipant2
                OTHERNAME = NameParticipant1
                log_data.experiment_data['left_pp'] = IDP2
                log_data.experiment_data['right_pp'] = IDP1
                
            if (emotional_condition == "h"):
                    misty.display_image(fileName="e_Joy.jpg") # It shows the image of the 'happy' eyes
                    if gestures == "y":
                        if head_position_left:
                            misty.move_head(-30, 40, -54, 90)
                        else:
                            misty.move_head(-30, 40, 54, 90)
                    else:
                        if head_position_left:
                            misty.move_head(-20, 0, -54, 90)
                        else:
                            misty.move_head(-20, 0, 54, 90)
            elif (emotional_condition == "s"):
                    misty.display_image(fileName="e_Sadness.jpg") # It shows the image of the 'sad' eyes
                    if gestures == "y":
                        if head_position_left:
                            misty.move_head(10, 40, -54, 90)
                        else:
                            misty.move_head(10, 40, 54, 90)
                    else:
                        if head_position_left:
                            misty.move_head(-20, 0, -54, 90)
                        else:
                            misty.move_head(-20, 0, 54, 90)
            if (pressedButton == 'd'):
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
                   ["What do you think will be the opinion of "]+[OTHERNAME]+["?"]]
                direct_turn_turntake_random = random.randint(0, len(direct_turntake) - 1)
                chosen_direct_turntake_result = listtostr(direct_turntake[direct_turn_turntake_random])
                misty.speak(chosen_direct_turntake_result)
            elif (pressedButton == "s"):
                switch_turntake = [["To what degree would this also be your opinion?"], # The prefix is essential to a switch turn-take utterance!
                   ["To what extent do you agree with "]+[CURRENTNAME]+["?"],
                   ["That is interesting, what about you?"],
                   ["Ok fair enough, how about you?"],
                   ["And what is your view?"],
                   ["How do you feel about that?"],
                   ["Given what "]+[CURRENTNAME]+[" said, how would you comment on that?"],
                   ["Given what "]+[CURRENTNAME]+[" said, what would be your opinion?"]]
                switch_turn_turntake_random = random.randint(0, len(switch_turntake) - 1)
                chosen_switch_turntake_result = listtostr(switch_turntake[switch_turn_turntake_random])
                misty.speak(chosen_switch_turntake_result)
            new_state = 2

        elif(new_state == 9):
            value = 0
            val = int(input("Give the input value (1-4): "))
            if val ==1:
                value = 0
            elif val == 2:
                value = 1
            elif val == 3:
                value = 2
            elif val == 4:
                value = 3

            if (topic == 'h'):
                if dialogstage == 1:
                    info_continent = info_holiday.get(continent[value])
                    info_continent_string = listtostr(info_continent)
                    misty.speak(info_continent_string)
                    new_state = 2
                elif dialogstage == 2:
                    info_travelperiod = info_holiday.get(travelperiod[value])
                    info_travelperiod_holiday = listtostr(info_travelperiod)
                    misty.speak(info_travelperiod_holiday)
                    new_state = 2
                elif dialogstage == 3:
                    info_accomodation = info_holiday.get(accomodation[value])
                    info_accomodation_string = listtostr(info_accomodation)
                    misty.speak(info_accomodation_string)
                    new_state = 2
                elif dialogstage == 4:
                    info_tripduration = info_holiday.get(tripduration[value])
                    info_tripduration_string = listtostr(info_tripduration)
                    misty.speak(info_tripduration_string)
                    new_state = 2
                elif dialogstage == 5:
                    info_holidaytype = info_holiday.get(holidaytype[value])
                    info_holidaytype_string = listtostr(info_holidaytype)
                    misty.speak(info_holidaytype_string)
                    new_state = 2
            if (topic == "d"):
                if dialogstage == 1:
                    info_houselocation = info_dreamhouse.get(houselocation[value])
                    info_houselocation_string = listtostr(info_houselocation)
                    misty.speak(info_houselocation_string)
                    new_state = 2
                elif dialogstage == 2:
                    info_housetype = info_dreamhouse.get(housetype[value])
                    info_housetype_string = listtostr(info_housetype)
                    misty.speak(info_housetype_string)
                    new_state = 2
                elif dialogstage == 3:
                    info_housesize = info_dreamhouse.get(housesize[value])
                    info_housesize_string = listtostr(info_housesize)
                    misty.speak(info_housesize_string)
                    new_state = 2
                elif dialogstage == 4:
                    info_outside_space = info_dreamhouse.get(outside_space[value])
                    info_outside_space_string = listtostr(info_outside_space)
                    misty.speak(info_outside_space_string)
                    new_state = 2
                elif dialogstage == 5:
                    info_housestyle = info_dreamhouse.get(housestyle[value])
                    info_housestyle_string = listtostr(info_housestyle)
                    misty.speak(info_housestyle_string)
                    new_state= 2
            if (topic == "t"):
                if dialogstage == 1:
                    info_timeperiod = info_timetravel.get(timeperiod[value])
                    info_timeperiod_string = listtostr(info_timeperiod)
                    misty.speak(info_timeperiod_string)
                    new_state = 2
                elif dialogstage == 2:
                    info_influencelevel = info_timetravel.get(influencelevel[value])
                    info_influencelevel_string = listtostr(info_influencelevel)
                    misty.speak(info_influencelevel_string)
                    new_state = 2
                elif dialogstage == 3:
                    info_travelcompany = info_timetravel.get(travelcompany[value])
                    info_travelcompany_string = listtostr(info_travelcompany)
                    misty.speak(info_travelcompany_string)
                    new_state = 2
                elif dialogstage == 4:
                    info_travelactivities = info_timetravel.get(travelactivities[value])
                    info_travelactivities_string = listtostr(info_travelactivities)
                    misty.speak(info_travelactivities_string)
                    new_state = 2
                elif dialogstage == 5:
                    info_travelduration = info_timetravel.get(travelduration[value])
                    info_travelduration_string = listtostr(info_travelduration)
                    misty.speak(info_travelduration_string)
                    new_state = 2
    

        elif (new_state == 10):
            if dialogstage == -1:
                new_state = 7
            elif dialogstage == 0:
                new_state = 7
            else:
                print("Press '1' to select first option, '2' to select second option, '3'to select third option, '4' for the fourth option.")
                print(dialogstage)
                pressedButton = msvcrt.getch().decode('ASCII')
                log_newstate_pressedButton(IDP1, IDP2, new_state, pressedButton)
                if (pressedButton == "1"):
                    if (topic == 'h'):
                        if dialogstage == 1:
                            chosen_options.append(continent[0])
                        elif dialogstage == 2:
                            chosen_options.append(travelperiod[0])
                        elif dialogstage == 3:
                            chosen_options.append(accomodation[0])
                        elif dialogstage == 4:
                            chosen_options.append(tripduration[0])
                        elif dialogstage == 5:
                            chosen_options.append(holidaytype[0])
                    if (topic == "d"):
                        if dialogstage == 1:
                            chosen_options.append(houselocation[0])
                        elif dialogstage == 2:
                            chosen_options.append(housetype[0])
                        elif dialogstage == 3:
                            chosen_options.append(housesize[0])
                        elif dialogstage == 4:
                            chosen_options.append(outside_space[0])
                        elif dialogstage == 5:
                            chosen_options.append(housestyle[0])
                    if (topic == "t"):
                        if dialogstage == 1:
                            chosen_options.append(timeperiod[0])
                        elif dialogstage == 2:
                            chosen_options.append(influencelevel[0])
                        elif dialogstage == 3:
                            chosen_options.append(travelcompany[0])
                        elif dialogstage == 4:
                            chosen_options.append(travelactivities[0])
                        elif dialogstage == 5:
                            chosen_options.append(travelduration[0])
                    print(chosen_options)
                    new_state = 5
                elif (pressedButton == "2"):
                    if (topic == 'h'):
                        if dialogstage == 1:
                            chosen_options.append(continent[1])
                        elif dialogstage == 2:
                            chosen_options.append(travelperiod[1])
                        elif dialogstage == 3:
                            chosen_options.append(accomodation[1])
                        elif dialogstage == 4:
                            chosen_options.append(tripduration[1])
                        elif dialogstage == 5:
                            chosen_options.append(holidaytype[1])
                    if (topic == "d"):
                        if dialogstage == 1:
                            chosen_options.append(houselocation[1])
                        elif dialogstage == 2:
                            chosen_options.append(housetype[1])
                        elif dialogstage == 3:
                            chosen_options.append(housesize[1])
                        elif dialogstage == 4:
                            chosen_options.append(outside_space[1])
                        elif dialogstage == 5:
                            chosen_options.append(housestyle[1])
                    if (topic == "t"):
                        if dialogstage == 1:
                            chosen_options.append(timeperiod[1])
                        elif dialogstage == 2:
                            chosen_options.append(influencelevel[1])
                        elif dialogstage == 3:
                            chosen_options.append(travelcompany[1])
                        elif dialogstage == 4:
                            chosen_options.append(travelactivities[1])
                        elif dialogstage == 5:
                            chosen_options.append(travelduration[1])
                    print(chosen_options)
                    new_state = 5
                elif (pressedButton == "3"):
                    if (topic == 'h'):
                        if dialogstage == 1:
                            chosen_options.append(continent[2])
                        elif dialogstage == 2:
                            chosen_options.append(travelperiod[2])
                        elif dialogstage == 3:
                            chosen_options.append(accomodation[2])
                        elif dialogstage == 4:
                            chosen_options.append(tripduration[2])
                        elif dialogstage == 5:
                            chosen_options.append(holidaytype[2])
                    if (topic == "d"):
                        if dialogstage == 1:
                            chosen_options.append(houselocation[2])
                        elif dialogstage == 2:
                            chosen_options.append(housetype[2])
                        elif dialogstage == 3:
                            chosen_options.append(housesize[2])
                        elif dialogstage == 4:
                            chosen_options.append(outside_space[2])
                        elif dialogstage == 5:
                            chosen_options.append(housestyle[2])
                    if (topic == "t"):
                        if dialogstage == 1:
                            chosen_options.append(timeperiod[2])
                        elif dialogstage == 2:
                            chosen_options.append(influencelevel[2])
                        elif dialogstage == 3:
                            chosen_options.append(travelcompany[2])
                        elif dialogstage == 4:
                            chosen_options.append(travelactivities[2])
                        elif dialogstage == 5:
                            chosen_options.append(travelduration[2])
                    print(chosen_options)
                    new_state = 5
                elif (pressedButton == "4"):
                    if (topic == 'h'):
                        if dialogstage == 1:
                            chosen_options.append(continent[3])
                        elif dialogstage == 2:
                            chosen_options.append(travelperiod[3])
                        elif dialogstage == 3:
                            chosen_options.append(accomodation[3])
                        elif dialogstage == 4:
                            chosen_options.append(tripduration[3])
                        elif dialogstage == 5:
                            chosen_options.append(holidaytype[3])
                    if (topic == "d"):
                        if dialogstage == 1:
                            chosen_options.append(houselocation[3])
                        elif dialogstage == 2:
                            chosen_options.append(housetype[3])
                        elif dialogstage == 3:
                            chosen_options.append(housesize[3])
                        elif dialogstage == 4:
                            chosen_options.append(outside_space[3])
                        elif dialogstage == 5:
                            chosen_options.append(housestyle[3])
                    if (topic == "t"):
                        if dialogstage == 1:
                            chosen_options.append(timeperiod[3])
                        elif dialogstage == 2:
                            chosen_options.append(influencelevel[3])
                        elif dialogstage == 3:
                            chosen_options.append(travelcompany[3])
                        elif dialogstage == 4:
                            chosen_options.append(travelactivities[3])
                        elif dialogstage == 5:
                            chosen_options.append(travelduration[3])
                    print(chosen_options)
                    new_state = 5

                misty.speak("Is it correct to conclude that your chosen option was" + chosen_options[-1] +"?")

                answer = input("Was it correct?")
                input_chosen_options_correct = False
                if answer == "yes":
                    input_chosen_options_correct = True
                elif answer == "no":
                    input_chosen_options_correct = True
                while not input_chosen_options_correct:
                    answer = input("Was it correct?")
                    if answer == "yes":
                        input_chosen_options_correct = True
                    elif answer == "no":
                        input_chosen_options_correct = True
                else:
                    if (answer == "yes"):
                        Nice =  [ ["Clearly "]+[chosen_options[-1]]+[" seems to be the best choice."],
                                    ["I am glad that you found mutual agreement, "]+[chosen_options[-1]]+[" is selected for now."],
                                    ["Well this is an easy choice, I will note it is going to be "]+[chosen_options[-1]]+['.'],
                                    ["Ok, let me select option "]+[chosen_options[-1]]+[' for you'],
                                    ["It is clear to me that  "]+[chosen_options[-1]]+[' is preferred'],
                        ]
                        answer_random = random.randint(0, len(Nice) - 1)
                        chosen_answer_result = listtostr(Nice[answer_random])
                        misty.speak(chosen_answer_result)
                        new_state = 7
                    if (answer == "no"):
                        chosen_options.pop()
                        misty.speak("Sorry, I made a mistake. Let's continue the conversation.")
                        new_state = 2

        elif (new_state == 11):
            misty.speak("I will repeat the question.")
            current_state -= 1
            dialogstage -= 1
            new_state = 7

        else:
            get_eyecontact()
            get_headpose()
            quit()
    
    

if __name__ == "__main__": 
    main()