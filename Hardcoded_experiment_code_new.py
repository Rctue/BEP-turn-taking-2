# misty_state_machine_full.py
# ─────────────────────────────────────────────────────────────────────────────
# Full experiment flow (13 states) for two-participant dialogues with Misty-II
# Version: 2025-05-05  – patched with pose-cache, operator menu and nod fix
# ─────────────────────────────────────────────────────────────────────────────

##############################################################################
# ░░░ IMPORTS ░░░
##############################################################################

# --------------------------------------------------------------------------
#  Misty: echt of simulatie?
#     • cmd-vlag  : python …py --simulate
#     • env-var   : SIMULATE_MISTY=1
#  Valt terug op FakeMisty als de echte robot niet bereikbaar is.
# --------------------------------------------------------------------------
import os, sys, argparse, requests

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--simulate", action="store_true")
args, _ = parser.parse_known_args()

simulate = (
    args.simulate
    or os.getenv("SIMULATE_MISTY", "0") == "1"
)

if not simulate:
    try:
        from Misty_commands import Misty
        #quick accessibility test
        requests.get("http://192.168.0.100/api/device", timeout=2)
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

# Topic scripts
from script_holiday_hardcoded     import *
from script_dream_house_hardcoded import *
from script_timetravel_hardcoded  import *

# Optional Mediapipe face / head-pose tracking  ######################
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
            return 13
        if k == 'q':
            print("→ Next question.")
            return 7
        if k == 'v':
            print("→ Jump to verdict.")
            return 10
    return None


##############################################################################
# ░░░ GLOBAL RUNTIME STATE ░░░
##############################################################################
robot_ip = "192.168.0.100"
misty    = Misty(ip_address=robot_ip)
last_speaker = None

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
    csv.writer(_f).writerow(["timestamp","ms_since_start","speaker","rms_left","rms_right"])

import speech_detector; speech_detector.set_thresholds(
        log_data.rec_left,  log_data.rec_right,
        log_data.thresh_left, log_data.thresh_right)

head_position  = "middle"           # 'left' | 'right' | 'middle'
log_headpose   = []                 # list of dicts -> CSV at the end
chosen_options = []                 # filled in state 10
dialogstage    = -1                 # question index (-1 = not started)
IDP1 = IDP2 = "";   NameP1 = NameP2 = ""
topic = "";   emotional_condition = "";   gestures = "n"

# ──────────────────────────────────────────────────────────
# ░░░ BACK-CHANNEL FACTORS ░░░
# (chosen once in state 0 – counterbalancing comes from your spreadsheet)
BC_SAYINGS = ["uh-huh", "mmhm", "okay", "yeah"]

# run-time schedule pointer (filled in state 0)
BC_SCHEDULE: list[dict] = []
BC_PTR: int = 0

BC_LOGFILE = f"bc_log_{datetime.now():%Y%m%d_%H%M%S}.csv"
with open(BC_LOGFILE, "w", newline="") as f:
    csv.writer(f).writerow(["timestamp", "eye_contact", "backchannel", "delay_s"])


def log_backchannel(eye_contact: bool, bc: str, delay_s: int):
    """Append a back-channel event to CSV."""
    with open(BC_LOGFILE, "a", newline="") as f:
        csv.writer(f).writerow(
            [datetime.now().isoformat(timespec="seconds"),
             "YES" if eye_contact else "NO",
             bc, delay_s]
        )


##############################################################################
# ░░░ SMALL HELPERS ░░░
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


##############################################################################
# ░░░ FACE-TRACKING THREAD ░░░
##############################################################################
def face_tracking_thread():
    """Continuously run Mediapipe model and cache last pitch/yaw in tracking_model.LAST_POSE."""
    try:
        while True:
            p, y = get_pitch_yaw()          # returns (pitch, yaw)
            # store in module-level variable so state_6 can read it fast
            sys.modules["tracking_model"].LAST_POSE = (p, y)
    except Exception as e:
        print("Face-tracking stopped:", e)


if ENABLE_FACE_TRACKING:
    # tracking_model already equals mp_face_pose_detect_asr (imported above)
    tracking_model.LAST_POSE = (0.0, 0.0)  # initial dummy value
    threading.Thread(target=face_tracking_thread, daemon=True).start()



##############################################################################
# ░░░ STATE-HANDLERS ░░░
##############################################################################
# 0 ─ Experiment initialisation
def state_0_init():
    global emotional_condition, topic, gestures 
    global IDP1, IDP2, NameP1, NameP2
    global eye_controller


    print("Initialising …")
    topic   = input("Topic (h holiday / d dream-house / t time-travel): ").lower()
    NameP1  = input("Name participant LEFT : ");  IDP1 = input("ID LEFT  : ")
    NameP2  = input("Name participant RIGHT: "); IDP2 = input("ID RIGHT : ")
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
    log_data.start()          # ▶︎ begin RMS‐opname van de microfoon

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
    eye_controller.set_listening_mode()

    # Counter-balancing factors (here simple RNG demo)
    #global BACKCHANNEL_TYPE, BACKCHANNEL_DELAY
    
        # ─────────────────────────────────────────────────────────────
    #  WITHIN-subjects schedule → 12 trials  (two 2-s blocks, two 4-s blocks)
    #  Order is counter-balanced (half the Ps start with 2 s, half with 4 s).
    #  Each delay block contains the three back-channel types twice
    #  (type order is randomised but paired with its exact opposite).
    # ─────────────────────────────────────────────────────────────
    delays_order = [2, 4]
    random.shuffle(delays_order)                       # counter-balance start

    def opposite(seq: list[str]) -> list[str]:
        rev = seq.copy(); rev.reverse(); return rev

    schedule: list[dict] = []
    for d in delays_order:                             # two blocks
        types = ["none", "saying", "nod"]
        random.shuffle(types)
        full_block = types + opposite(types)           # six trials for this delay
        schedule.extend({"delay": d, "type": t} for t in full_block)

    globals()["BC_SCHEDULE"] = schedule                # store globally
    globals()["BC_PTR"]       = 0
    
    return 13                               # Wait for Q to start


# 1 ─ Wait one second in neutral expression
def state_1_wait():
    eye_controller.set_listening_mode()
    misty.move_head(-20, 0, 0, 90)
    time.sleep(1)
    speech_detector.reset_timers()
    return 2


# 2 ─ Automatic speaker tracking (tests A/B)
def state_2_track():
    global head_position
    global _start_time

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
        
        with open(RMS_LOGFILE, "a", newline="") as _f:
            csv.writer(_f).writerow([
                now.isoformat(), ms,
                {'l':'left', 'r':'right', 'b':'both', 's':'silence'}[speaker],
                left_rms, right_rms
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
            head_position = new_pos
            print(f"[AUTO] New speaker detected ({new_pos}), turning head.")
            if new_pos == "left":
                misty.move_head(0, 0, 20)
            elif new_pos == "right":
                misty.move_head(0, 0, -20)
            else:
                misty.move_head(0, 0, 0)
            
        add_head_dir()
        
    

        time.sleep(0.2)




# 3 ─ Motivate someone to start talking
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


# 4 ─ Turn head to current speaker
def state_4_turn_head():
    if head_position == "left":
        misty.move_head(-20, 0, -54, 90)
    elif head_position == "right":
        misty.move_head(-20, 0,  54, 90)
    else:
        misty.move_head(-20, 0,   0, 90)
    speech_detector.reset_timers()
    return 5


# 5 ─ Keep gaze; tests C/D/E 
def state_5_keep_gaze():
    global head_position
    global last_speaker
    global _start_time

    # 1) operator override?
    override = check_menu_keys()
    if override is not None:
        return override

    # 2) Instant snapshot of who is speaking
    speaker = speech_detector.detect_speaker(0)  # 'l', 'r', 'b', 's'
    if speaker not in ('l', 'r', 'b', 's'):
        print(f"[ERROR] Invalid speaker detected: {speaker}")
        speaker = 's'

    # 3) Correct RMS logging
    left_data  = speech_detector.left_recorder.rms_data
    right_data = speech_detector.right_recorder.rms_data
    left_rms   = float(np.median(left_data)) if left_data else 0.0
    right_rms  = float(np.median(right_data)) if right_data else 0.0
    now = datetime.now()
    ms = int((now - _start_time).total_seconds() * 1000)

    with open(RMS_LOGFILE, "a", newline="") as _f:
        csv.writer(_f).writerow([
            now.isoformat(), ms,
            {'l':'left', 'r':'right', 'b':'both', 's':'silence'}[speaker],
            left_rms, right_rms
        ])

    # 4) If speaker changes → reset timers and turn head
    if speaker != last_speaker:
        last_speaker = speaker
        speech_detector.reset_timers()

        new_pos = {
            'l': 'left',
            'r': 'right',
            'b': 'middle',
            's': 'middle'
        }[speaker]

        if new_pos != head_position:
            head_position = new_pos
            print(f"[AUTO] Speaker changed ({new_pos}), turning head.")
            if new_pos == "left":
                misty.move_head(-20, 0, -54, 90)
            elif new_pos == "right":
                misty.move_head(-20, 0, 54, 90)
            else:  # 'middle'
                misty.move_head(-20, 0, 0, 90)

    # 5) Keep gaze logic
    silence_duration = speech_detector.get_silence_duration()
    speaking_duration = speech_detector.get_speaking_duration()

    print(f"[DEBUG] same speaker={speaker}, silence={silence_duration:.2f}s, speak={speaking_duration:.2f}s")

    if speaker in ('l', 'r', 'b') and speaking_duration >= BC_SCHEDULE[BC_PTR]["delay"]:
        print("[AUTO] Speaker active for required delay → backchannel.")
        return 6

    if speaker == 's' and silence_duration > 4.0:
        print("[AUTO] Silence (>4s) → motivate.")
        return 3

    time.sleep(0.2)
    return 5


# 6 ─ Back-channel utterance / nod / none  ──────────────────────────────
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

    # 4) write log row
    log_backchannel(eye_contact, bc_out or "none", delay)
    speech_detector.reset_timers()
    return 5                                      # back to keep-gaze


# 7 ─ Robot asks next question or finishes
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

    # 1) nog vragen te gaan?
    if dialogstage < max_q:
        dialogstage += 1
        
        eye_controller.set_speaking_mode()
        speech_detector.left_recorder.stop_recording()
        speech_detector.right_recorder.stop_recording()
        
        misty.speak(listtostr(seq[dialogstage]))
        with open(RMS_LOGFILE, "a", newline="") as f:
            csv.writer(f).writerow([
                datetime.now().isoformat(), 
                int((datetime.now() - _start_time).total_seconds() * 1000),
                 "", "", "", 
                f"question: {listtostr(seq[dialogstage])}"
            ])
        time.sleep(3.0)
        
        speech_detector.reset_timers()
        eye_controller.set_listening_mode()
        
        speech_detector.left_recorder.start_recording()
        speech_detector.right_recorder.start_recording()
        log_data.start()
        return 13 if dialogstage == 0 else 1

    # 2) exact alle antwoorden verzameld? anders eerst verdict
    if len(chosen_options) < max_q:
        # we missen nog keuzes ⇒ vraag verdict
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


# 8 ─ Simple turn-taking prompt
def state_8_turn_taking():
    eye_controller.set_speaking_mode()
    misty.speak("Okay, how about you?")
    speech_detector.reset_timers()
    eye_controller.set_listening_mode()
    return 2


# 9 ─ Information on a chosen option (operator)
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
    eye_controller.set_speaking_mode()
    misty.speak(listtostr(info_dict.get(opt_list[int(val) - 1], "")))
    speech_detector.reset_timers()
    eye_controller.set_listening_mode()
    return 2


# 10 ─ Operator picks verdict for current question
def state_10_verdict():
    if not (1 <= dialogstage <= 5):
        return 13
    
    opt_list, _ = _info_sets()[dialogstage - 1]
    print("Choose option (1-4):", end = '', flush = True)
    key = msvcrt.getch().decode('ascii')
    if key not in '1234':
        return 13
    idx = int(key) - 1
    chosen_options.append(opt_list[idx])
    
    eye_controller.set_speaking_mode()

    misty.speak(f"Is it correct that you chose {opt_list[idx]}?")
    speech_detector.reset_timers()
    eye_controller.set_listening_mode()
    
    if input("(yes / no): ").strip().lower() == "yes":
        eye_controller.set_speaking_mode()
        misty.speak(random.choice([
            f"Clearly {opt_list[idx]} is the best choice.",
            f"Great, you both agree – {opt_list[idx]} it is."
        ]))
        speech_detector.reset_timers()
        eye_controller.set_listening_mode()
        return 7 #op bevestiging -> next question
    
    chosen_options.pop()
    eye_controller.set_speaking_mode()
    misty.speak("Sorry, my mistake. Let's keep discussing.")
    speech_detector.reset_timers()
    eye_controller.set_listening_mode()
    return 2


# 11 ─ Repeat current question
def state_11_repeat():
    eye_controller.set_speaking_mode()
    misty.speak("I'll repeat the question.")
    speech_detector.reset_timers()
    eye_controller.set_listening_mode()
    global dialogstage
    # ga één vraag terug
    dialogstage -= 1
    return 7


# 12 ─ Experiment finished
def state_12_end():
    misty.stop_speaking(); misty.stop_audio(); misty.stop()
    speech_detector.terminate()
    log_data.stop("audio_rms_log.csv")   # ■ stopt stream & schrijft CSV


    # write head-pose CSV
    if log_headpose:
        with open("headpose_log.csv", "w", newline="") as f:
            csv.DictWriter(f, fieldnames=log_headpose[0].keys()).writerows(log_headpose)

    print("Experiment finished – goodbye.")
    return -1


# 13 ─ Operator menu (manual override)
def state_13_operator():
    print("Operator keys: c long-turn • d switch • t turn-take • i info • v verdict • q next question • m menu • r repeat • a auto")
    key = msvcrt.getch().decode('ascii').lower()
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
# ░░░ DISPATCH TABLE ░░░
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
# ░░░ MAIN LOOP ░░░
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


