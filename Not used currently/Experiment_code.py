'''
Questions:
When running the Audio_sound_levels code, I came to the conclusion that the normal microphone of my laptop gives very different values than the
sound levels that are detected when I use the two microphones of the headphones. These just seem quite random to me and vary from around 50-60,
but I do not feel like these are increasing when someone is saying something. But this should happen. Do you have any idea on how to fix this?
'''


from Misty_commands import Misty
import time
from Audio_sound_levels import AudioRecorder
import cv2
import numpy as np
import base64
from script_holiday_hardcoded import *
from script_dream_house_hardcoded import *
from script_timetravel_hardcoded import *
import random
import msvcrt
    

#making headposition variables global so we can extract them in the eyecontact_duration code:
head_moved_left = False
head_moved_right = False

misty = Misty(ip_address="192.168.0.100")

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
 
def testA(audiochannel1, audiochannel2, sec):
    # In test A, Misty checked whether speech had been detected for over 4 seconds, and if so, it would move to step 3.
    _, silence_duration1 = audiochannel1.record_audio()
    _, silence_duration2 = audiochannel2.record_audio()
    if (silence_duration1 > sec) & (silence_duration2 > sec):
        silence = True
        return silence
    else:
        silence = False
        return silence
    
def testB(audiochannel1, audiochannel2, sec):
    # Test B: tested whether a speaker was speaking for over 500 ms. If this was the case, Misty would move to step 4, else, it would move back to step 1.
    continuous_speaking_duration1, _ = audiochannel1.record_audio()
    continuous_speaking_duration2, _ = audiochannel2.record_audio()
    if (continuous_speaking_duration1 > sec) | (continuous_speaking_duration2 > sec):
        test_result = True
        if (continuous_speaking_duration1 > sec):
            audio_from = "audio1"
        elif (continuous_speaking_duration2 > sec):
            audio_from = "audio2"
        else:
            audio_from = "both" # I hope this will never be returned, as it is not supposed to happen.
    else: 
        test_result = False
        audio_from = None
    return test_result, audio_from

def GetKey(duration_in_ms):
    k = cv2.waitKey(duration_in_ms)
    if k == 2490368:        #Up-arrow key
        offset_pitch -= 0.2
    elif k == 2621440:      #Down-arrow key
        offset_pitch += 0.2
    elif k == 2555904:      #Right-arrow key
        offset_yaw -= 0.2
    elif k == 2424832:      #Left-arrow key
        offset_yaw += 0.2
    KeyPress = chr(k & 255)
    return KeyPress


def main(): 
        # Looking at the h
        # code of Maurice, I want to start with logging here.
    new_state = 0
    # When the states need to be reset, each time that a new state is entered, this StateManager class can fix this issue
    audio1 = AudioRecorder(input_device = 1, record_seconds=5, output_filename="pp1.wav") # This code needs to be adapted such that the audio input from the microphone of human1's headphone is used to calculate rms values
    audio2 = AudioRecorder(input_device = 7, record_seconds=5, output_filename="pp2.wav") # This code needs to be adapted such that the audio input from the microphone of human2's headphone is used to calculate rms values
    
    # This still needs to be updated according to what the robot has to do. Everything that needs to be done is written in the prints.
    # It needs to check what the results of the tests are, and based on that determine the new state that the robot is in. 
    while not new_state == "quit":
        
        if (new_state == 0):
            # Start of program: the code will be started and it will start all sub-porcesses. 
            print("Initializing the program...")
            emotional_condition = input("Please give the emotional condition (n = neutral), (h = happy), (s = sad) : ")
            topic = input ("Please give the topic (h = holiday planner, d = dream house, t = time-travel): ")
            NameParticipant1 = input("Please give the name of Participant 1 (sitting on the left of Misty): ")
            NameParticipant2 = input("Please give the name of Participant 2 (sitting on the right of Misty): ")
            print("The human on the left side needs to have the audio1 input, otherwise the robot will look at the non-speaking person.")

            #Ensure that it will start with the first utterance
            current_state = 0
            # Ensure that it knows that it is neither facing participant1 nor participant2
            head_moved_left = False
            head_moved_right = False
            chosen_options = []
            OTHERNAME = None
            dialogstage = -1


            # Here we will start the correct topic
            if (topic == "h"):
                introduction = ["Hi there. For this conversation the main goal is to figure out what a holiday should be like if you "+
                "have to travel and spend the entire vacation together. "+
                "I am going to ask you some questions about what your ideal holiday is. "+
                "Since the two of you are going on a hypothetical holiday together, "+
                "ask for each others opinion. "+
                "Are you ready to begin?"]
                intro = listtostr(introduction)
                misty.speak(intro)
                new_state = 1
            elif (topic == "d"):
                introduction = ["Hello. For this conversation the main goal is to figure out what your dream house "+ 
                "would be if you would live together. "+
                "I am going to ask you some questions about what your dream house would look like. "+
                "Since the two of you are going to hypothetically live there together, "+
                "ask for each others opinion. "+
                "Are you ready to begin?"]
                intro = listtostr(introduction)
                misty.speak(intro)
                new_state = 1
            elif (topic == "t"):
                #response = utterance_time_travel(state=current_state, NameLeft = NameParticipant1, NameRight = NameParticipant2, MistyLooks = "L", CharKeyPress = "-" )
                #misty.speak(response)
                print("Misty should have given a response.")
                new_state = 1
            else:
                new_state = 0
            

        elif (new_state == 1):
            print("Here the robot will know it's emotional_condition and show the emotional_condition.")
            if (emotional_condition == "n"):
                # Show neutral face all along and no gestures.
                misty.display_image(fileName="e_DefaultContent.jpg") # It shows the image of the neutral face
                misty.move_head(0, 0, 20, 90)
                new_state = 2
            elif (emotional_condition == "h"):
                # Happy face during talking after a question or when a turn has been given. Specify the timing of the gestures
                # Condition happy
                misty.display_image(fileName="e_Joy.jpg") # It shows the image of the 'happy' eyes
                misty.move_head(0, 0, -20, 90)
                new_state = 2
            elif (emotional_condition == "s"):
                # Condition sad
                misty.display_image(fileName="e_Sadness.jpg") # It shows the image of the 'sad' eyes
                new_state = 2
            else: 
                print("Type n, h or s and enter.")
                new_state = 1

        elif (new_state == 2):
            # Test A: test if there is a silence for over 4 seconds.
            silence = testA(audio1, audio2, 4)

            silence = False #comment out when audio is working

            if silence:
                # If there is a silence for over 4 seconds we will move to state 3
                print("Silence detected.")
                new_state = 3
            else: 
                # There was no silence, so lets check whether someone has been speaking for over 5 seconds.
                print("Here I will run test B")
                test_result, _ = testB(audio1, audio2, 5)
                
                #
                test_result = True 
                #audio_from = "audio1"
                #side_testB = "speaker_audio1"
                #remove when audio detection is working

                if test_result:
                    new_state = 4
                else:
                    new_state = 2

        elif (new_state == 3):
            print("in state 3")
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
            print("state 4")
            _, audio_from = testB(audio1, audio2, 5)

            audio_from = "audio1" #remove when audio is working

            if (audio_from == "audio1"):
                misty.move_head(-20, 65, 0, 90)
                head_moved_left = True
                head_moved_right = False
                side_testB = "speaker_audio1"
                print("Participant 1 is talking.")
                new_state = 5
            elif (audio_from == "audio2"):
                misty.move_head(-20, -65, 0, 90)
                head_moved_right = True
                head_moved_left = False
                side_testB = "speaker_audio2"
                print("Participant 2 seemed to be talking, so I have turned my head towards them.")
                new_state = 5
            else: 
                misty.move_head(-20, 0, 0, 90)
                new_state = 5

        elif (new_state == 5):
            # testB() is equal to testC(), only the duration of the seconds changes to 5.
            silence_duration_testE = 3 # If this is too short, we should update this.
            if (side_testB == "speaker_audio1"):
                _, side = testB(audio1, audio2, 5)
                side == "audio1" #remove when audio is working.
                if (side == "audio1"):
                    new_state = 6
                elif (side == "audio2"): # Thus, this is test D, as it tests whether the active speaker has been changed from person.
                    new_state = 4
                    print ("Code should be added such that the code goes to state 4.")
                else: 
                    if testA(audio1, audio2, silence_duration_testE):
                        if dialogstage != 7: # test F(): check whether there are any utterances left.
                            new_state = 7
                        else:
                            new_state = 11
                    else: 
                        new_state = 4
            elif (side_testB == "speaker_audio2"):
                _, side = testB(audio1, audio2, 5)
                if(side == "audio2"):
                    new_state = 6
                elif(side == "audio1"):
                    new_state = 4
                else: 
                    if testA(audio1, audio2, silence_duration_testE):
                        if dialogstage != 7: # test F(): check whether there are any utterances left.
                            new_state = 7
                        else:
                            new_state = 11
                    else: 
                        new_state = 4
            else: 
                # TestD won't be run if there is no speaker speaking for over 5 seconds, because then Misty can still keep looking at the person Misty was looking at before
                if testA(audio1, audio2, silence_duration_testE):
                    print("Adapt code for test F.")
                    if dialogstage != 7: # test F(): check whether there are any utterances left.
                            new_state = 7
                    else:
                        new_state = 11
                else: 
                    new_state = 4

        elif (new_state == 6):
            # The robot should pronounce a backchannel utterance
            longturnindicator = ["Interesting",
                     "I see",
                     "Ok",
                     "Indeed",
                     "Go on"]
            chosen_longturnindicator = random.randint(0, len(longturnindicator) - 1)
            chosen_longturnindicator_result = listtostr(longturnindicator[chosen_longturnindicator])
            misty.speak(chosen_longturnindicator_result)
            new_state = 5

        elif (new_state == 7):
            # After the robot has said something, it will go back to showing an emotion and start again with testing whether someone is speaking, etc.
            # Here the robot will take a turn and start talking, or asking a new question, etc. It should take the correct utterance.")
            current_state += 1

            dialogstage +=1

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
                    ["Once arrived you will have a typical "]+[chosen_options[4]]+[" vacation "]+ ["Thanks for having participated in our dialogue, the experiment will now continue to the next phase."]]
                    ending_holiday = listtostr(ending)
                    misty.speak(ending_holiday)
                    new_state = 11
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
                    ["Thanks for having participated in our dialogue, the experiment will now continue to the next phase."]]
                    ending_dreamhouse = listtostr(ending_d)
                    misty.speak(ending_dreamhouse)
                    new_state = 11
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
                    ["Thanks for having participated in our dialogue, the experiment will now continue to the next phase."]]
                    ending_time_travel = listtostr(ending_t)
                    misty.speak(ending_time_travel)
                    new_state = 11
                new_state = 1
            else: 
                new_state = 0
        
            print("Misty should have given a response.")
            print("Current state:" + str(current_state))
            #new_state = 2

        elif (new_state == 8):
            print ("Type 'd' to direct a turn-take, type 's' to switch the turn-take.")
            pressedButton = msvcrt.getch().decode('ASCII')
            if head_moved_left:
                CURRENTNAME = NameParticipant1
                OTHERNAME = NameParticipant2
            else:
                CURRENTNAME = NameParticipant2
                OTHERNAME = NameParticipant1
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
            val = input("Give the input value:")
            if val =="1":
                value = 0
            elif val == "2":
                value = 1
            elif val == "3":
                value = 2
            elif val == "4":
                value = 3

            if (topic == 'h'):
                if dialogstage == 1:
                    info_continent = info.get(continent[value])
                    info_continent_string = listtostr(info_continent)
                    misty.speak(info_continent_string)
                    new_state = 2
                elif dialogstage == 2:
                    info_travelperiod = info.get(travelperiod[value])
                    info_travelperiod_holiday = listtostr(info_travelperiod)
                    misty.speak(info_travelperiod_holiday)
                    new_state = 2
                elif dialogstage == 3:
                    info_accomodation = info.get(accomodation[value])
                    info_accomodation_string = listtostr(info_accomodation)
                    misty.speak(info_accomodation_string)
                    new_state = 2
                elif dialogstage == 4:
                    info_tripduration = info.get(tripduration[value])
                    info_tripduration_string = listtostr(info_tripduration)
                    misty.speak(info_tripduration_string)
                    new_state = 2
                elif dialogstage == 5:
                    info_holidaytype = info.get(holidaytype[value])
                    info_holidaytype_string = listtostr(info_holidaytype)
                    misty.speak(info_holidaytype_string)
                    new_state = 2
            if (topic == "d"):
                if dialogstage == 1:
                    info_houselocation = info.get(houselocation[value])
                    info_houselocation_string = listtostr(info_houselocation)
                    misty.speak(info_houselocation_string)
                    new_state = 2
                elif dialogstage == 2:
                    info_housetype = info.get(housetype[value])
                    info_housetype_string = listtostr(info_housetype)
                    misty.speak(info_housetype_string)
                    new_state = 2
                elif dialogstage == 3:
                    info_housesize = info.get(housesize[value])
                    info_housesize_string = listtostr(info_housesize)
                    misty.speak(info_housesize_string)
                    new_state = 2
                elif dialogstage == 4:
                    info_outside_space = info.get(outside_space[value])
                    info_outside_space_string = listtostr(info_outside_space)
                    misty.speak(info_outside_space_string)
                    new_state = 2
                elif dialogstage == 5:
                    info_housestyle = info.get(housestyle[value])
                    info_housestyle_string = listtostr(info_housestyle)
                    misty.speak(info_housestyle_string)
                    new_state= 2
            if (topic == "t"):
                if dialogstage == 1:
                    info_timeperiod = info.get(timeperiod[value])
                    info_timeperiod_string = listtostr(info_timeperiod)
                    misty.speak(info_timeperiod_string)
                    new_state = 2
                elif dialogstage == 2:
                    info_influencelevel = info.get(influencelevel[value])
                    info_influencelevel_string = listtostr(info_influencelevel)
                    misty.speak(info_influencelevel_string)
                    new_state = 2
                elif dialogstage == 3:
                    info_travelcompany = info.get(travelcompany[value])
                    info_travelcompany_string = listtostr(info_travelcompany[value])
                    misty.speak(info_travelcompany_string)
                    new_state = 2
                elif dialogstage == 4:
                    info_travelactivities = info.get(travelactivities[value])
                    info_travelactivities_string = listtostr(info_travelactivities)
                    misty.speak(info_travelactivities_string)
                    new_state = 2
                elif dialogstage == 5:
                    info_travelduration = info.get(travelduration[value])
                    info_travelduration_string = listtostr(info_travelduration)
                    misty.speak(info_travelduration_string)
                    new_state = 2
    

        elif (new_state == 10):
            print("Press '1' to select first option, '2' to select second option, '3'to select third option, '4' for the fourth option.")
            print(dialogstage)
            pressedButton = msvcrt.getch().decode('ASCII')
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

        else:
            quit()
    

if __name__ == "__main__": 
    main()