# misty_state_machine_full.py
# ─────────────────────────────────────────────────────────────────────────────
# Full experiment flow (13 states) for two-participant dialogues with Misty-II
# Version: 2025-05-05  – patched with pose-cache, operator menu and nod fix
# ─────────────────────────────────────────────────────────────────────────────

##############################################################################
# IMPORTS 
##############################################################################


import sys, argparse, requests
import os
os.environ['MEDIAPIPE_DISABLE_LOGGING'] = '1'

import logging
logging.getLogger().setLevel(logging.ERROR)

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)
absl.logging.set_stderrthreshold('fatal')


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--simulate", action="store_true")
args, _ = parser.parse_known_args()


#___________________________________________________________________________________
#  Misty: real or simulated?
#     • Command-line flag : python …py --simulate
#     • Environment variable: SIMULATE_MISTY=1
# If the real Misty robot cannot be reached, the program automatically falls back
# to using the FakeMisty class from Amisty_stub.py as a simulation.
#____________________________________________________________________________________

simulate = (
    args.simulate
    or os.getenv("SIMULATE_MISTY", "0") == "1"
)

if not simulate:
    try:
        from Misty_commands import Misty
        #quick accessibility test
        requests.get("http://192.168.0.101/api/device", timeout=2)
    except Exception as e:
        print("[WARN] Robot niet bereikbaar → schakel naar FakeMisty:", e)
        simulate = True

if simulate:
    from Amisty_stub import FakeMisty as Misty
    print("[INFO]  Running in SIMULATE_MISTY mode (FakeMisty).")



import time, random, csv, threading, msvcrt, keyboard, sys
import cv2
import numpy as np
import json 
import base64
import datetime
from datetime import datetime
import speech_detector                     # uses AVData_new internally
import AVData_new as AVData                # <- renamed module
from new_videos import Video_player        #video display for the eye transitions

from pathlib import Path          # NEW
LOG_DIR = None                    # gets its value in state_0_init()

# Topic scripts
from script_holiday_hardcoded     import *
from script_dream_house_hardcoded import *
from script_timetravel_hardcoded  import *


# Optional Mediapipe face / head-pose tracking __________________________________________________________
ENABLE_FACE_TRACKING = False 
if ENABLE_FACE_TRACKING:
    # <<  use the file name that contains your Mediapipe code  >>
    from mp_face_pose_detect_asr import get_pitch_yaw           # returns (pitch,yaw)
    import mp_face_pose_detect_asr as tracking_model            # alias → used for cache

#emergency override
def check_menu_keys():
    """Return a state override on M/Q/V, or None if no key pressed."""
    if msvcrt.kbhit():
        k = msvcrt.getch().decode('ascii').lower()
        if k == 'm':
            print("→ Paused: operator menu.")
            log_state_button(13, 'm')
            return 13
        if k == 'q':
            print("→ Next question.")
            log_state_button(13, 'q')
            return 7
        if k == 'v':
            print("→ Jump to verdict.")
            log_state_button(13, 'v')
            return 10
    return None


##############################################################################
# GLOBAL RUNTIME STATE 
##############################################################################
robot_ip = "192.168.0.101"
misty    = Misty(ip_address=robot_ip)
last_speaker = None
head_timer_start = None

# A/V & RMS logging helper
log_data = AVData.AVData()
log_data.init_robot(robot_ip)
log_data.init_devices()

from datetime import datetime as _dt
# RMS logfile (only during discussion)
RMS_LOGFILE = f"rms_log_{_dt.now():%Y%m%d_%H%M%S}.csv"
_start_time = None
import csv
with open(RMS_LOGFILE, "w", newline="") as _f:
    csv.writer(_f).writerow(["timestamp","ms_since_start","speaker","rms_left","rms_right","head_position","head_duration"])


GAZE_LOGFILE = f"gaze_log_{_dt.now():%Y%m%d_%H%M%S}.csv"
with open(GAZE_LOGFILE, "w", newline="") as f:
    csv.writer(f).writerow(["timestamp", "head_position", "duration_s"])


import speech_detector; speech_detector.set_thresholds(
        log_data.rec_left,  log_data.rec_right,
        log_data.thresh_left, log_data.thresh_right)

head_position  = "middle"           # 'left' | 'right' | 'middle'
face_direction = "middle"           #'left', 'right', or  middle' on basis of face
log_headpose   = []                 # list of dicts -> CSV at the end
chosen_options = []                 # filled in state 10
dialogstage    = -1                 # question index (-1 = not started)
IDP1 = IDP2 = "";   NameP1 = NameP2 = ""
topic = "";   emotional_condition = "";   gestures = "n"

# ──────────────────────────────────────────────────────────
# BACK-CHANNEL FACTORS 
# (chosen once in state 0)
BC_SAYINGS = ["uh-huh", "mmhm", "okay", "yeah"]

# run-time schedule pointer (filled in state 0)
BC_SCHEDULE: list[dict] = []
BC_PTR: int = 0

BC_LOGFILE = f"bc_log_{datetime.now():%Y%m%d_%H%M%S}.csv"
with open(BC_LOGFILE, "w", newline="") as f:
    csv.writer(f).writerow(["timestamp", "eye_contact", "backchannel", "delay_s", "head_position", "gaze_duration"])



def log_backchannel(eye_contact: bool, bc: str, delay_s: int, direction: str, duration: float):
    if direction not in ("left", "right"):
        return  # Logging only at active orientation

    try:
        pitch, yaw = sys.modules["tracking_model"].LAST_POSE
    except KeyError:
        pitch, yaw = (0.0, 0.0)  # fallback if face-tracking is false


    with open(BC_LOGFILE, "a", newline="") as f:
        csv.writer(f).writerow([
            datetime.now().isoformat(timespec="seconds"),
            "YES" if eye_contact else "NO",
            bc,
            delay_s,
            direction,
            round(duration, 2),
            round(pitch, 2),
            round(yaw, 2)
        ])




##############################################################################
# SMALL HELPERS 
##############################################################################
def listtostr(obj):
    """Convert nested list to plain sentence string."""
    if obj is None:
        return ""
    s = str(obj)
    for rep in ("['", "']", "], [", "[", "]", "', '", ", '", "',"):
        s = s.replace(rep, "")
    return s


def log_state_button(state: int, key=""):
    """Log any manual button/state transition for debugging."""
    fn = f"result_{IDP1}_{IDP2}.txt"
    with open(fn, "a") as f:
        f.write(f"{state}\t{key}\t{datetime.now()}\t{head_position}\n")


def add_head_dir():
    """Append current head direction to pose list."""
    d = head_position[0] if head_position in ("left", "right") else "m"
    log_headpose.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "direction": d,
        "participant": IDP1 if d == "l" else IDP2 if d == "r" else "both"
    })
  
    
def log_gaze_duration(position: str, duration: float):
    with open(GAZE_LOGFILE, "a", newline="") as f:
        csv.writer(f).writerow([
            datetime.now().isoformat(timespec="seconds"),
            position,
            round(duration, 2)
        ])



##############################################################################
# FACE-TRACKING THREAD 
##############################################################################
def face_tracking_thread():
    global face_direction
    try:
        while True:
            try:
                is_playing = misty.get_audio_playing().json().get('result', False)
            except:
                is_playing = False

            if is_playing:
                time.sleep(0.5)
                continue

            pitch, yaw = get_pitch_yaw(misty)
            sys.modules["tracking_model"].LAST_POSE = (pitch, yaw)

            if yaw < -20:
                face_direction = "left"
            elif yaw > 20:
                face_direction = "right"
            else:
                face_direction = "middle"

            time.sleep(1.0)
    except Exception as e:
        print("Face-tracking stopped:", e)



if ENABLE_FACE_TRACKING:
    # tracking_model already equals mp_face_pose_detect_asr (imported above)
    tracking_model.LAST_POSE = (0.0, 0.0)  # initial dummy value
    threading.Thread(target=face_tracking_thread, daemon=True).start()



##############################################################################
# STATE-HANDLERS 
##############################################################################
# 0 ─ Experiment initialisation___________________________________________________________________________________________________
def state_0_init():
    global emotional_condition, topic, gestures 
    global IDP1, IDP2, NameP1, NameP2
    global eye_controller


    print("Initialising …")
    topic   = input("Topic (h holiday / d dream-house / t time-travel): ").lower()
    NameP1  = input("Name participant LEFT : ");  IDP1 = input("ID LEFT  : ")
    NameP2  = input("Name participant RIGHT: "); IDP2 = input("ID RIGHT : ")
    
        # ─── Create per-session log folder ─────────────────────────────────
    global LOG_DIR, RMS_LOGFILE, GAZE_LOGFILE, BC_LOGFILE
    import datetime as dt

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # folder:  <script dir>/experiment_logs/ID1-ID2__YYYY-MM-DD_HH-MM-SS
    LOG_DIR = (
        Path(__file__).parent
        / "experiment_logs"
        / f"{IDP1}-{IDP2}__{timestamp}"
    )
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Log files → {LOG_DIR.resolve()}")   # visible in GUI

    # point the three main log variables to that new folder
    RMS_LOGFILE  = LOG_DIR / f"rms_log_{timestamp}.csv"
    GAZE_LOGFILE = LOG_DIR / f"gaze_log_{timestamp}.csv"
    BC_LOGFILE   = LOG_DIR / f"bc_log_{timestamp}.csv"

    # ─── ensure the three CSVs exist with their header row ──────────────
    headers = [
        (RMS_LOGFILE,  ["timestamp","ms_since_start","speaker",
                        "rms_left","rms_right","head_position","head_duration"]),
        (GAZE_LOGFILE, ["timestamp","head_position","duration_s"]),
        (BC_LOGFILE,   ["timestamp","eye_contact","backchannel",
                        "delay_s","head_position","gaze_duration"]),
    ]
    for path, hdr in headers:
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(hdr)
            
            
    eye_choice = input("Eye condition(s smooth / d direct): ").lower()
    
    transition_style = Video_player.SMOOTH if eye_choice == "s" else Video_player.DIRECT
    eye_controller = Video_player(misty, transition_style=transition_style)
    
    log_data.experiment_data.update({
        "condition": emotional_condition, "topic": topic,
        "gestures": gestures, "IDP1": IDP1, "IDP2": IDP2
    })

    print("Calibrating microphones …")
    speech_detector.setup_speech_detection()

    misty.move_head(-20, 0, 0, 90)         # neutral pose
    log_data.start()          # begin RMS recording of the microphone

    #start RMS-timer
    global _start_time
    _start_time = _dt.now()


    intro_map = {
        "h": ["Hi there. For this conversation the main goal is to figure out what a holiday should be like if you have to travel together. "
              "I will ask you some questions about your ideal holiday. Since you are going on a hypothetical holiday together, please ask for each other's opinion. "
              "Are you ready to begin?"],
        "d": ["Hello. Our goal is to design your dream house if you would live together. "
              "I will ask you some questions about how the house should look. Ask for your partner's opinion as well. Are you ready to begin?"],
        "t": ["Hi there. Our goal is to figure out what you would do if you could time-travel together. "
              "I will ask you about your journey. Ask for each other's opinion. Are you ready to begin?"]
    }
    
    eye_controller.set_speaking_mode()
    speech_detector.left_recorder.stop_recording()
    speech_detector.right_recorder.stop_recording()
    
    misty.speak(listtostr(intro_map[topic]))
    
    speech_detector.reset_timers()
    speech_detector.left_recorder.start_recording()
    speech_detector.right_recorder.start_recording()
    

#___________________________________________________________________________________
# Counterbalancing factors (backchannel schedule generation)

# A within-subjects schedule is used with 12 trials, where each trial 
# specifies a backchannel delay (2 or 4 seconds) and a backchannel type 
# ('none', 'nod', or 'saying').

# Instead of fixed blocks, both delays and types are randomly shuffled 
# and paired into trial entries. This ensures a varied and unpredictable 
# order of delay–type combinations across trials, without a fixed pattern.

# Each participant experiences 12 backchannel moments with randomized timing 
# and behavior, allowing for a more natural and balanced interaction.
#____________________________________________________________________________________  
    
    # Creating balanced combinations
    delays = [2]*6 + [4]*6
    types  = ["none"]*4 + ["saying"]*4 + ["nod"]*4

    # Shuffle separately
    random.shuffle(delays)
    random.shuffle(types)

    # Combine to list dicts
    schedule = [{"delay": d, "type": t} for d, t in zip(delays, types)]

    # Shuffle whole schedule again to mix
    random.shuffle(schedule)

    globals()["BC_SCHEDULE"] = schedule
    globals()["BC_PTR"] = 0
        
    return 13                               # Wait for Q to start


# 1 ─ Wait one second in neutral expression______________________________________________________________________________________________________________
def state_1_wait():
    eye_controller.set_listening_mode()
    misty.move_head(-20, 0, 0, 90)
    time.sleep(1)
    speech_detector.reset_timers()
    return 5


# 2 ─ Automatic speaker tracking (tests A/B)____________________________________________________________________________________________________________
def state_2_track():
    global head_position
    global _start_time
    global head_timer_start
    
    speech_detector.left_recorder.start_recording()
    speech_detector.right_recorder.start_recording()
    log_data.start()


    print("AUTOTRACK active — press M menu, Q next, or V verdict …")
    
    
    while True:
        override = check_menu_keys()
        if override is not None:
            return override

        speaker = speech_detector.detect_speaker(1.0)
        if speaker not in ('l', 'r', 'b', 's'):
            print(f"[ERROR] Invalid speaker detected: {speaker}")
            speaker = 's'

        silence_duration = speech_detector.get_silence_duration()
        speaking_duration = speech_detector.get_speaking_duration()
        
        # English debug output:
        print(f"[DEBUG] Detected speaker: {speaker}, Silence duration: {silence_duration:.2f}s, Speaking duration: {speaking_duration:.2f}s")

        # Log RMS data correctly
        left_rms  = float(np.median(speech_detector.left_recorder.rms_data)) if speech_detector.left_recorder.rms_data else 0.0
        right_rms = float(np.median(speech_detector.right_recorder.rms_data)) if speech_detector.right_recorder.rms_data else 0.0
        now = datetime.now()
        ms = int((now - _start_time).total_seconds() * 1000)
        
        head_duration = (now - head_timer_start).total_seconds() if head_timer_start else 0.0

        with open(RMS_LOGFILE, "a", newline="") as _f:
            csv.writer(_f).writerow([
                now.isoformat(), ms,
                {'l':'left', 'r':'right', 'b':'both', 's':'silence'}[speaker],
                left_rms, right_rms,
                head_position,
                round(head_duration, 2)
            ])
            
        # Check explicitly for silence
        if silence_duration > 4.0:
            print("[AUTO] Silence detected (>4s), moving to motivate state.")
            return 3

        new_pos = {
            'l': 'left',
            'r': 'right',
            'b': 'middle',
            's': 'middle'
        }[speaker]

        if new_pos != head_position:
            if head_timer_start:
                duration = (now - head_timer_start).total_seconds()
                log_gaze_duration(head_position, duration)
            head_timer_start = datetime.now()
            head_position = new_pos
            print(f"[AUTO] New speaker detected ({new_pos}), turning head.")
            if new_pos == "left":
                misty.move_head(0, 0, 20)
            elif new_pos == "right":
                misty.move_head(0, 0, -20)
            else:
                misty.move_head(0, 0, 0)
            
        add_head_dir()
        
        #backchanneling
        if head_timer_start:
            head_duration = (now - head_timer_start).total_seconds()
        else:
            head_duration = 0.0

        bc_delay = BC_SCHEDULE[BC_PTR]["delay"] if BC_PTR < len(BC_SCHEDULE) else 2
        if head_position in ('left', 'right') and head_duration >= bc_delay:
            log_gaze_duration(head_position, head_duration)
            print(f"[AUTO] Head direction held for {head_duration:.2f}s → backchannel.")
            return 6

        time.sleep(0.2)





# 3 ─ Motivate someone to start talking___________________________________________________
def state_3_motivate():
    misty.move_head(-20, 0, 0, 90)
    eye_controller.set_speaking_mode()
    misty.speak(random.choice([
        "So who has any ideas?",
        "So what do you both think?",
        "Who of you can say something about it?",
        "Let us try to share some ideas."
    ]))
    speech_detector.reset_timers()
    eye_controller.set_listening_mode()
    return 2


# 4 ─ Turn head to current speaker________________________________________________________
def state_4_turn_head():
    if head_position == "left":
        misty.move_head(-20, 0, -54, 90)
    elif head_position == "right":
        misty.move_head(-20, 0,  54, 90)
    else:
        misty.move_head(-20, 0,   0, 90)
    speech_detector.reset_timers()
    return 5


# 5 ─ Keep gaze; tests C/D/E (not really being used at the moment, because we don't have those tests in our state machine) ____________________________________________________________
def state_5_keep_gaze():
    global head_position
    global last_speaker
    global _start_time
    global head_timer_start

    # 1) operator override?
    override = check_menu_keys()
    if override is not None:
        return override

    # 2) Detect candidate speaker, with threshold
    candidate = speech_detector.detect_speaker(0)
    MIN_TURN_DURATION = 1.0

    if candidate != last_speaker and candidate in ('l', 'r'):
        duration = speech_detector.get_speaking_duration_by_side(candidate)
        if duration >= MIN_TURN_DURATION:
            speaker = candidate
        else:
            speaker = last_speaker
    else:
        speaker = candidate

    if speaker not in ('l', 'r', 'b', 's'):
        print(f"[ERROR] Invalid speaker detected: {speaker}")
        speaker = 's'

    # 3) RMS logging + how long Misty looks at current side
    now = datetime.now()
    silence_duration = speech_detector.get_silence_duration()
    head_duration = (datetime.now() - head_timer_start).total_seconds() if head_timer_start else 0.0
    print(f"[CHECK] head_position={head_position}, head_duration={head_duration:.2f}, BC delay={BC_SCHEDULE[BC_PTR]['delay']}")
    print(f"[DEBUG] same speaker={speaker}, silence={silence_duration:.2f}s, head_duration={head_duration:.2f}s")
    ms = int((now - _start_time).total_seconds() * 1000)
    left_rms = float(np.median(speech_detector.left_recorder.rms_data)) if speech_detector.left_recorder.rms_data else 0.0
    right_rms = float(np.median(speech_detector.right_recorder.rms_data)) if speech_detector.right_recorder.rms_data else 0.0
    head_duration = (now - head_timer_start).total_seconds() if head_timer_start else 0.0

    with open(RMS_LOGFILE, "a", newline="") as _f:
        csv.writer(_f).writerow([
            now.isoformat(), ms,
            {'l': 'left', 'r': 'right', 'b': 'both', 's': 'silence'}[speaker],
            left_rms, right_rms,
            head_position,
            round(head_duration, 2)
        ])

    # 4) Check if the head of Misty needs to be turned
    new_pos = {
        'l': 'left',
        'r': 'right',
        'b': 'middle',
        's': 'middle'
    }[speaker]



    if new_pos != head_position:
        # log the time that Misty looked at the other side
        if head_timer_start:
            duration = (now - head_timer_start).total_seconds()
            log_gaze_duration(head_position, duration)

        head_position = new_pos
        head_timer_start = datetime.now()
        print(f"[AUTO] Speaker changed ({new_pos}), turning head.")
        if new_pos == "left":
            misty.move_head(-20, 0, -54, 90)
        elif new_pos == "right":
            misty.move_head(-20, 0, 54, 90)
        else:
            misty.move_head(-20, 0, 0, 90)

        last_speaker = speaker
        speech_detector.reset_timers()

    # 5) Determine the head duration (head at the same side) for the backchannel
    if not head_timer_start:
        print("[DEBUG] head_timer_start was None, setting it now")
        

    head_duration = (datetime.now() - head_timer_start).total_seconds() if head_timer_start else 0.0
    

    bc_delay = BC_SCHEDULE[BC_PTR]["delay"] if BC_PTR < len(BC_SCHEDULE) else 2
    if head_position in ('left', 'right') and head_duration >= bc_delay:
        log_gaze_duration(head_position, head_duration)
        print(f"[AUTO] Head direction held for {head_duration:.2f}s → backchannel.")
        return 6

    if speaker == 's' and silence_duration > 4.0:
        print("[AUTO] Silence (>4s) → motivate.")
        return 3
    
    
    if head_timer_start:
        duration = (datetime.now() - head_timer_start).total_seconds()
        if duration > 1.0:  
            log_gaze_duration(head_position, duration)


    if not head_timer_start:
        head_timer_start = datetime.now()

    time.sleep(0.2)
    return 5



# 6 ─ Back-channel utterance / nod / none_____________________________________________________________________
def state_6_backchannel():
    print("[BC] Entered state 6 (backchannel)")
    """Run the *next* trial from the within-subjects schedule."""
    global BC_PTR
    if BC_PTR >= len(BC_SCHEDULE):              # safety – recycle if needed
        BC_PTR = 0
    trial   = BC_SCHEDULE[BC_PTR];  BC_PTR += 1
    delay   = trial["delay"]                   # 2 s or 4 s
    bc_type = trial["type"]      # none | nod | saying

        
    # 1) wait the required delay
    time.sleep(delay)
    
    # 2) perform the back-channel
    if bc_type == "none":
        bc_out = ""

    elif bc_type == "nod":
        # smooth nod while keeping current yaw
        pos = misty.get_head_position()
        if isinstance(pos, dict):
            pos = pos.get('result', pos)
        current_yaw = pos.get('yaw', 0) or 0
        misty.move_head(-30, 0, current_yaw, 90)   # quick down
        time.sleep(0.4)
        misty.move_head(-20, 0, current_yaw, 90)   # back to neutral
        bc_out = "nod"

    elif bc_type == "saying":
        bc_out = random.choice(BC_SAYINGS)
        eye_controller.set_speaking_mode()
        misty.speak(bc_out)
        speech_detector.reset_timers()
        eye_controller.set_listening_mode()

    else:                                          # should never happen
        bc_out = ""
        print("⚠ Unknown bc_type in schedule!")

    # 3) obtain last cached pose → eye-contact flag
    pitch, yaw = (0, 0)
    if ENABLE_FACE_TRACKING:
        pitch, yaw = sys.modules["tracking_model"].LAST_POSE
    eye_contact = abs(pitch) < 20 and abs(yaw) < 20

    # 4) Determine how long Misty has been looking this way
    from datetime import datetime as dt
    gaze_duration = (dt.now() - head_timer_start).total_seconds() if head_timer_start else 0.0

    # 5) write log line
    log_backchannel(
        eye_contact=eye_contact,
        bc=bc_out or "none",
        delay_s=delay,
        direction=head_position,
        duration=gaze_duration
    )
    speech_detector.reset_timers()
    return 2                                    # back to active tracking


# 7 ─ Robot asks next question or finishes_________________________________________________________________________________________
def _question_sequence():
    if topic == 'h':
        return [starting, question1, question2, question3, question4, question5]
    if topic == 'd':
        return [starting_d, question1_d, question2_d, question3_d, question4_d,
                question5_d]
    return [starting_t, question1_t, question2_t, question3_t, question4_t,
            question5_t]


def state_7_robot_talk():
    global dialogstage
    print(f"[DEBUG] → in state_7_robot_talk, dialogstage was {dialogstage}")
    seq = _question_sequence()
    max_q = len(seq) - 1

    # 1) still question to ask?
    if dialogstage < max_q:
        dialogstage += 1
        
        #stop recording before robot talks
        speech_detector.left_recorder.stop_recording()
        speech_detector.right_recorder.stop_recording()
        
        log_data.stop(RMS_LOGFILE)
        
        #ask question
        misty.speak(listtostr(seq[dialogstage]))
        
        #log the question
        with open(RMS_LOGFILE, "a", newline="") as f:
            csv.writer(f).writerow([
                datetime.now().isoformat(), 
                int((datetime.now() - _start_time).total_seconds() * 1000),
                 "", "", "",
                 "", "", 
                f"question: {listtostr(seq[dialogstage])}"
            ])
        time.sleep(3.0)
        
        #after speaking: reset timers and record again
        speech_detector.reset_timers()
        eye_controller.set_listening_mode()
        
        speech_detector.left_recorder.start_recording()
        speech_detector.right_recorder.start_recording()
        log_data.start()
        return 13 if dialogstage == 0 else 2

    # 2) all answers collected? othwerwise verdict first
    if len(chosen_options) < max_q:
        # we still miss choices -> ask questoin
        return 10
    
    # closing summary
    if topic == "h":
        closing = [["Well that's about it. With all the information combined you planned a ",
                    chosen_options[3], " holiday to ", chosen_options[0], " in a ",
                    chosen_options[2], " during the ", chosen_options[1],
                    ". Once there you will have a ", chosen_options[4],
                    " vacation. Thanks for participating – please fill in the questionnaire."]]
    elif topic == "d":
        closing = [["That was about it. Your dream house is a ", chosen_options[1],
                    " in ", chosen_options[0], " with ", chosen_options[2],
                    ". It features ", chosen_options[3], " and has a ",
                    chosen_options[4], " style. Thanks for participating – please fill in the questionnaire."]]
    else:
        closing = [["That was it. Your time-travel trip goes ", chosen_options[2],
                    " back to ", chosen_options[0], " for ", chosen_options[4],
                    ". During that period you will have ", chosen_options[1],
                    " and you will ", chosen_options[3],
                    ". Thanks for participating – please fill in both questionnaires."]]
    
    eye_controller.set_speaking_mode()
    speech_detector.left_recorder.stop_recording()
    speech_detector.right_recorder.stop_recording()
    
    misty.speak(listtostr(closing))
    time.sleep(3.0)
    
    speech_detector.reset_timers()
    speech_detector.left_recorder.start_recording()
    speech_detector.right_recorder.start_recording()
    eye_controller.set_listening_mode()
    return 12


# 8 ─ Simple turn-taking prompt___________________________________________________________________________________________________________
def state_8_turn_taking():
    eye_controller.set_speaking_mode()
    misty.speak("Okay, how about you?")
    speech_detector.reset_timers()
    eye_controller.set_listening_mode()
    return 2


# 9 ─ Information on a chosen option (operator)_____________________________________________________________________________________________
def _info_sets():
    if topic == 'h':
        return (continent, info_holiday), (travelperiod, info_holiday),\
               (accomodation, info_holiday), (tripduration, info_holiday),\
               (holidaytype, info_holiday)
    if topic == 'd':
        return (houselocation, info_dreamhouse), (housetype, info_dreamhouse),\
               (housesize, info_dreamhouse), (outside_space, info_dreamhouse),\
               (housestyle, info_dreamhouse)
    return (timeperiod, info_timetravel), (influencelevel, info_timetravel),\
           (travelcompany, info_timetravel), (travelactivities, info_timetravel),\
           (travelduration, info_timetravel)


def state_9_info():
    val = input("Give option number (1-4): ")
    if not val.isdigit() or not 1 <= int(val) <= 4 or not (1 <= dialogstage <= 5):
        return 13
    
    opt_list, info_dict = _info_sets()[dialogstage - 1]
    
    speech_detector.left_recorder.stop_recording()
    speech_detector.right_recorder.stop_recording()
    log_data.stop(RMS_LOGFILE)
    
    eye_controller.set_speaking_mode()
    misty.speak(listtostr(info_dict.get(opt_list[int(val) - 1], "")))
    speech_detector.reset_timers()
    eye_controller.set_listening_mode()
    
    speech_detector.reset_timers()
    speech_detector.left_recorder.start_recording()
    speech_detector.right_recorder.start_recording()
    log_data.start()
    
    return 2


# 10 ─ Operator picks verdict for current question________________________________________________________________________________________________
def state_10_verdict():
    if not (1 <= dialogstage <= 5):
        return 13
    
    opt_list, _ = _info_sets()[dialogstage - 1]
    print("Choose option (1-4):", end = '', flush = True)
    key = msvcrt.getch().decode('ascii')
    log_state_button(10, key)
    if key not in '1234':
        return 13
    idx = int(key) - 1
    chosen_options.append(opt_list[idx])
    
    # Stop recording before Misty speaks
    speech_detector.left_recorder.stop_recording()
    speech_detector.right_recorder.stop_recording()
    log_data.stop(RMS_LOGFILE)
    
    # Misty asks question
    misty.speak(f"Is it correct that you chose {opt_list[idx]}?")
    
    # Recording starts again after Misty asked question
    speech_detector.reset_timers()
    speech_detector.left_recorder.start_recording()
    speech_detector.right_recorder.start_recording()
    log_data.start()
    
    if input("(yes / no): ").strip().lower() == "yes":
        speech_detector.left_recorder.stop_recording()
        speech_detector.right_recorder.stop_recording()
        log_data.stop(RMS_LOGFILE)
        
        misty.speak(random.choice([
            f"Clearly {opt_list[idx]} is the best choice.",
            f"Great, you both agree – {opt_list[idx]} it is."
        ]))
        
        speech_detector.reset_timers()
        speech_detector.left_recorder.start_recording()
        speech_detector.right_recorder.start_recording()
        log_data.start()
        
        return 7 #on confirmation -> nex question 
    
    chosen_options.pop()
    speech_detector.left_recorder.stop_recording()
    speech_detector.right_recorder.stop_recording()
    log_data.stop(RMS_LOGFILE)
    
    misty.speak("Sorry, my mistake. Let's keep discussing.")
    
    speech_detector.reset_timers()
    speech_detector.left_recorder.start_recording()
    speech_detector.right_recorder.start_recording()
    log_data.start()
    
    return 2


# 11 ─ Repeat current question_____________________________________________________________________________________________________________
def state_11_repeat():
    speech_detector.left_recorder.stop_recording()
    speech_detector.right_recorder.stop_recording()
    log_data.stop(RMS_LOGFILE)
    
    misty.speak("I'll repeat the question.")
    
    speech_detector.reset_timers()
    speech_detector.left_recorder.start_recording()
    speech_detector.right_recorder.start_recording()
    log_data.start()
    global dialogstage
    # go back 1 question, so you stay at the same question
    dialogstage -= 1
    return 7


# 12 ─ Experiment finished_________________________________________________________________________________________________________________________
def state_12_end():
    misty.stop_speaking(); misty.stop_audio(); misty.stop()
    speech_detector.terminate()
    log_data.stop(str(LOG_DIR /"audio_rms_log.csv"))  #stops stream and writes CSV


    # write head-pose CSV
    if log_headpose:
        with open(LOG_DIR / "headpose_log.csv", "w", newline="") as f:
            csv.DictWriter(f, fieldnames=log_headpose[0].keys()).writerows(log_headpose)

    print("Experiment finished - goodbye.")
    return -1


# 13 ─ Operator menu (manual override)_______________________________________________________________________________________________________________
def state_13_operator():
    print("Operator keys: c long-turn • d switch • t turn-take • i info • v verdict • q next question • m menu • r repeat • a auto")

    try:
        key = msvcrt.getch().decode('ascii').lower()
    except:
        key = '?'  # fallback voor logging

    log_state_button(13, key)

    if key == 'c':
        return 6
    if key == 'd':
        global head_position
        head_position = 'right' if head_position=='left' else 'left'
        return 4
    if key == 't':
        return 8
    if key == 'i':
        return 9
    if key == 'v':
        return 10
    if key == 'q':
        return 7
    if key == 'm':
        return 13   # no-op, blijf in menu
    if key == 'r':
        return 11
    if key == 'a':
        return 2
    return 13



##############################################################################
# DISPATCH TABLE 
##############################################################################
state_handlers = {
     0: state_0_init,
     1: state_1_wait,
     2: state_2_track,
     3: state_3_motivate,
     4: state_4_turn_head,
     5: state_5_keep_gaze,
     6: state_6_backchannel,
     7: state_7_robot_talk,
     8: state_8_turn_taking,
     9: state_9_info,
    10: state_10_verdict,
    11: state_11_repeat,
    12: state_12_end,
    13: state_13_operator            #operator state
}


##############################################################################
# MAIN LOOP 
##############################################################################
def main():
    state = 0
    print(f"[DEBUG] → starting state machine (initial state={state})")
    while state != -1:
        print(f"[DEBUG] entering state {state}")
        handler = state_handlers.get(state)
        if handler is None:
            print("Unknown state:", state)
            break
        state = handler()


if __name__ == "__main__":
    main()


