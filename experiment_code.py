# IMPORTS 
############################################################################
# Reduce MediaPipe warnings in terminal
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
os.environ['MEDIAPIPE_DISABLE_LOGGING'] = '1'

import argparse
import requests
import time
import random
import csv
import threading
import msvcrt
import keyboard
import sys
import json
import base64
import cv2
import numpy as np

# removes MediaPipe warnings
class suppress_stderr:
    def __enter__(self):
        self.null_fd = os.open(os.devnull, os.O_RDWR)
        self.old_fd = os.dup(2)
        os.dup2(self.null_fd, 2)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.dup2(self.old_fd, 2)
        os.close(self.null_fd)

from datetime import datetime, timedelta

import script_holiday_planner_hardcode as holiday
import script_dream_house_hardcoded as dream

import speech_detector
import AVData_new as AVData

from mp_face_pose_detect_asr import set_all_log_path

from pathlib import Path
LOG_DIR = None                
RESULTS_LOGFILE = None

# reduce MediaPipe warnings in terminal
import logging
logging.getLogger().setLevel(logging.ERROR)

import absl.logging
absl.logging.set_verbosity(absl.logging.FATAL)

# MediaPipe face tracking
ENABLE_FACE_TRACKING = True

if ENABLE_FACE_TRACKING:
    import mp_face_pose_detect_asr as tracking_model

    # dummy pose
    tracking_model.LAST_POSE = None
    tracking_model.LAST_POSE_TS = None


# Check for arguments
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--simulate", action="store_true",
                    help="Run without the real Misty robot")
args, _ = parser.parse_known_args()

# MODES ROBOT OR SIMULATED
##############################################################################

simulate = args.simulate or os.getenv("SIMULATE_MISTY", "0") == "1"

if not simulate:
    try:
        from Misty_commands import Misty
        requests.get("http://192.168.0.152/api/device", timeout=2) # Misty 2
        print("[real robot.")

    except Exception as e:
        print("Robot not reachable → switching to FakeMisty.")
        print("       Reason:", e)
        simulate = True

if simulate:
    from Amisty_stub import FakeMisty as Misty
    print("SIMULATION MODE")

# WIZARD OF OZ KEYS
##############################################################################
def check_menu_keys():
    global dialogstage
    """Override on keys M/Q/V"""
    if msvcrt.kbhit():
        k = msvcrt.getch().decode('ascii').lower()

        if k == 'm':
            print("operator menu.")
            log_state_button(11, 'm')
            return 11

        if k == 'q':
            print("next question.")
            log_state_button(11, 'q')

            skipped_stage = dialogstage
            dialogstage += 1

            if TOPIC_CONDITION == "holiday":

                if skipped_stage == 1 and not holiday.CONTINENT[0]:
                    holiday.CONTINENT[0] = random.choice(holiday.continent)

                elif skipped_stage == 2 and not holiday.CITY[0]:
                    if not holiday.CONTINENT[0]:
                        holiday.CONTINENT[0] = random.choice(holiday.continent)
                    holiday.CITY[0] = random.choice(holiday.city[holiday.CONTINENT[0]])

                elif skipped_stage == 3 and not holiday.PERIOD[0]:
                    holiday.PERIOD[0] = random.choice(holiday.travelperiod)

                elif skipped_stage == 4 and not holiday.DURATION[0]:
                    holiday.DURATION[0] = random.choice(holiday.tripduration)

                elif skipped_stage == 5 and not holiday.HOLIDAYTYPE[0]:
                    holiday.HOLIDAYTYPE[0] = random.choice(holiday.holidaytype)

                elif skipped_stage == 6 and not holiday.THINGSTODO[0]:
                    if not holiday.HOLIDAYTYPE[0]:
                        holiday.HOLIDAYTYPE[0] = random.choice(holiday.holidaytype)
                    holiday.THINGSTODO[0] = random.choice(
                        holiday.thingstodo[holiday.HOLIDAYTYPE[0]]
                    )

                elif skipped_stage == 7 and not holiday.ACCOMODATION[0]:
                    holiday.ACCOMODATION[0] = random.choice(holiday.accomodation)

                elif skipped_stage == 8 and not holiday.MOBILITY[0]:
                    holiday.MOBILITY[0] = random.choice(holiday.mobility)

                elif skipped_stage == 9 and not holiday.BUDGET[0]:
                    holiday.BUDGET[0] = random.choice(holiday.budget)

            elif TOPIC_CONDITION == "dream":
                if skipped_stage == 1 and not dream.HOUSELOCATION[0]:
                    dream.HOUSELOCATION[0] = random.choice(dream.houselocation)

                elif skipped_stage == 2 and not dream.HOUSETYPE[0]:
                    dream.HOUSETYPE[0] = random.choice(dream.housetype)

                elif skipped_stage == 3 and not dream.HOUSESIZE[0]:
                    dream.HOUSESIZE[0] = random.choice(dream.housesize)

                elif skipped_stage == 4 and not dream.OUTSIDE_SPACE[0]:
                    dream.OUTSIDE_SPACE[0] = random.choice(dream.outside_space)

                elif skipped_stage == 5 and not dream.HOUSESTYLE[0]:
                    dream.HOUSESTYLE[0] = random.choice(dream.housestyle)

                elif skipped_stage == 6 and not dream.INTERIORSTYLE[0]:
                    dream.INTERIORSTYLE[0] = random.choice(dream.interiorstyle)

                elif skipped_stage == 7 and not dream.SUSTAINABILITY[0]:
                    dream.SUSTAINABILITY[0] = random.choice(dream.sustainability)

                elif skipped_stage == 8 and not dream.NEIGHBORHOOD[0]:
                    dream.NEIGHBORHOOD[0] = random.choice(dream.neighborhood)

                elif skipped_stage == 9 and not dream.HOUSEBUDGET[0]:
                    dream.HOUSEBUDGET[0] = random.choice(dream.housebudget)

            if dialogstage >= 10:
                dialogstage = 10

            return 10

        if k == 'v':
            print("verdict.")
            log_state_button(11, 'v')
            return 7

    return None

# CONDITIONS
##############################################################################

TOPIC_CONDITION = "dream"           # "holiday" or "dream"
EYE_CONTACT_CONDITION = "broad"       # "broad" or "direct"
SILENCE_CONDITION = "1000ms"
GAZE_BEHAVIOR_CONDITION = "B"         # "A" or "B"

THRESHOLDS = {
    "broad": {"yaw": 25, "pitch": 20},
    "direct": {"yaw": 10, "pitch": 20}, 
}

SILENCE_THRESHOLDS = {
    "1000ms": 1.0,
}

INACTIVITY_THRESHOLDS = {
    "4s": 4.0,
}

# avert gaze timing
ROBOT_GAZE_REENGAGE_DELAY = 1.27

# time before acknowledgement
LONG_TURN_ACK_SECONDS = 4.0

# thresholds
EYE_CONTACT_YAW_THRESH = THRESHOLDS[EYE_CONTACT_CONDITION]["yaw"]
EYE_CONTACT_PITCH_THRESH = THRESHOLDS[EYE_CONTACT_CONDITION]["pitch"]
TURN_SILENCE_SECONDS = SILENCE_THRESHOLDS[SILENCE_CONDITION]
MOTIVATION_INACTIVITY_SECONDS = INACTIVITY_THRESHOLDS["4s"]

# accounted for participant lengths
PARTICIPANT_OFFSETS = {
    "left": {
        "robot_yaw": 58,
        "robot_pitch": -6   # ~5 cm height difference = 3 degrees pitch
    }, 
    "right": {
        "robot_yaw": -58,
        "robot_pitch": -6   # ~5 cm height difference = 3 degrees pitch
    },
    "middle": {
        "robot_yaw": 0,
        "robot_pitch": 0,
        "gaze_pitch_center": 0
    }
}

# FAKEMISTY
##############################################################################

robot_ip = "192.168.0.152" # Misty 2
misty = Misty(ip_address=robot_ip)

if simulate:
    _orig_move_head = misty.move_head

    def _dbg_move_head(pitch, roll, yaw, speed=90):
        side = "middle" if yaw == 0 else ("left" if yaw > 0 else "right")
        print(f"pitch={pitch:>3}  roll={roll:>3}  "
              f"yaw={yaw:>3}  => {side}")
        return _orig_move_head(pitch, roll, yaw, speed)

    misty.move_head = _dbg_move_head

# VARIABLES
##############################################################################

last_speaker = None
head_timer_start = None
_start_time = None

robot_is_speaking = False
last_robot_speech_end_time = None
INTERRUPTION_WINDOW = 0.10

last_eye_contact_time = 0.0
eye_contact_streak = 0
state4_testd_count = 0
state7_count = 0
state9_count = 0
longturn_ack_done = False

log_data = AVData.AVData()
log_data.init_robot(robot_ip)
log_data.init_devices()

gaze_event_start_time = None
silence_event_start_time = None

gaze_before_silence_flag = False
silence_before_gaze_flag = False
last_trigger_silence = None
last_time_since_gaze_start = None
last_time_since_silence_start = None
last_interruption_type = ""
overlap_logged = False

HUMAN_GAZE_YAW_MIN = 30
HUMAN_GAZE_YAW_MAX = 60
HUMAN_GAZE_PITCH_THRESH = 20

current_human_turn_speaker = None
current_human_turn_start_time = None

forced_attention_until = None

# logging events
RMS_LOGFILE = None
GAZE_LOGFILE = None
SPEECH_LOGFILE = None
SUMMARY_LOGFILE = None
TIMELINE_LOGFILE = None

last_logged_eye_contact_state = False
eye_contact_run_start = None
total_eye_contact_time = 0.0

previous_turn_speaker = None
previous_turn_offset_time = None
pending_human_turn = None
pending_overlap_start = None
current_trigger_source = "auto"

turn_count_human_human = 0
turn_count_human_robot = 0
turn_count_robot_human = 0
turn_count_robot_robot = 0

# Creating speech thresholds
speech_detector.set_thresholds(
    log_data.rec_left,
    log_data.rec_right,
    log_data.thresh_left,
    log_data.thresh_right
)

eye_contact_buffer = []

# Experiment state
head_position = "middle"
face_direction = "middle"
log_headpose = []
chosen_options = []
dialogstage = 0
robot_speaking_cooldown_until = None

IDP1 = IDP2 = ""
NameP1 = NameP2 = ""

recent_move = False

active_speaker = None
active_speaker_start = None

GazeShiftEnabled = True

gaze_shift_done = False
gaze_shift_target = None          # "left" or "right"
gaze_shift_origin = None
gaze_shift_active = False
gaze_shift_cooldown_until = None  


# CLASSES
##############################################################################

def listtostr(obj):
    if obj is None:
        return ""
    s = str(obj)
    for rep in ("['", "']", "], [", "[", "]", "', '", ", '", "',"):
        s = s.replace(rep, "")
    return s

def set_names(current_name, NameP1, NameP2): 
    other_name = NameP2 if current_name == NameP1 else NameP1

    holiday.CURRENTNAME[0] = current_name
    holiday.OTHERNAME[0] = other_name

    dream.CURRENTNAME[0] = current_name
    dream.OTHERNAME[0] = other_name

def classify_gaze_direction(yaw):
    if abs(yaw) <= EYE_CONTACT_YAW_THRESH:
        return "middle"
    elif yaw < 0:
        return "left"
    else:
        return "right"

def get_topic_option_list(stage=None):
    global dialogstage

    if stage is None:
        stage = dialogstage

    if TOPIC_CONDITION == "holiday":
        if stage == 1:
            return holiday.continent
        elif stage == 2:
            return holiday.city[holiday.CONTINENT[0]] if holiday.CONTINENT[0] else holiday.city[holiday.continent[0]]
        elif stage == 3:
            return holiday.travelperiod
        elif stage == 4:
            return holiday.tripduration
        elif stage == 5:
            return holiday.holidaytype
        elif stage == 6:
            chosen_type = holiday.HOLIDAYTYPE[0] if holiday.HOLIDAYTYPE[0] else holiday.holidaytype[0]
            return holiday.thingstodo[chosen_type]
        elif stage == 7:
            return holiday.accomodation
        elif stage == 8:
            return holiday.mobility
        elif stage == 9:
            return holiday.budget

    elif TOPIC_CONDITION == "dream":
        if stage == 1:
            return dream.houselocation
        elif stage == 2:
            return dream.housetype
        elif stage == 3:
            return dream.housesize
        elif stage == 4:
            return dream.outside_space
        elif stage == 5:
            return dream.housestyle
        elif stage == 6:
            return dream.interiorstyle
        elif stage == 7:
            return dream.sustainability
        elif stage == 8:
            return dream.neighborhood
        elif stage == 9:
            return dream.housebudget

    return []

def set_topic_choice(chosen_option):
    global dialogstage

    if TOPIC_CONDITION == "holiday":
        if dialogstage == 1:
            holiday.CONTINENT[0] = chosen_option
        elif dialogstage == 2:
            holiday.CITY[0] = chosen_option
        elif dialogstage == 3:
            holiday.PERIOD[0] = chosen_option
        elif dialogstage == 4:
            holiday.DURATION[0] = chosen_option
        elif dialogstage == 5:
            holiday.HOLIDAYTYPE[0] = chosen_option
        elif dialogstage == 6:
            holiday.THINGSTODO[0] = chosen_option
        elif dialogstage == 7:
            holiday.ACCOMODATION[0] = chosen_option
        elif dialogstage == 8:
            holiday.MOBILITY[0] = chosen_option
        elif dialogstage == 9:
            holiday.BUDGET[0] = chosen_option

    elif TOPIC_CONDITION == "dream":
        if dialogstage == 1:
            dream.HOUSELOCATION[0] = chosen_option
        elif dialogstage == 2:
            dream.HOUSETYPE[0] = chosen_option
        elif dialogstage == 3:
            dream.HOUSESIZE[0] = chosen_option
        elif dialogstage == 4:
            dream.OUTSIDE_SPACE[0] = chosen_option
        elif dialogstage == 5:
            dream.HOUSESTYLE[0] = chosen_option
        elif dialogstage == 6:
            dream.INTERIORSTYLE[0] = chosen_option
        elif dialogstage == 7:
            dream.SUSTAINABILITY[0] = chosen_option
        elif dialogstage == 8:
            dream.NEIGHBORHOOD[0] = chosen_option
        elif dialogstage == 9:
            dream.HOUSEBUDGET[0] = chosen_option

def get_topic_info_text(selected_option):
    if TOPIC_CONDITION == "holiday":
        if dialogstage == 3:
            lookup_key = selected_option + holiday.CONTINENT[0]
        else:
            lookup_key = selected_option
        return holiday.info.get(lookup_key)

    elif TOPIC_CONDITION == "dream":
        if isinstance(selected_option, list):
            selected_option = selected_option[0]

        selected_option = str(selected_option).strip()

        for key in dream.info.keys():
            if key.lower().strip() == selected_option.lower():
                return dream.info[key]

        return None


def log_state_button(state: int, key=""):
    global RESULTS_LOGFILE, LOG_DIR

    fn = RESULTS_LOGFILE or (
        LOG_DIR / "operator_log.csv" if LOG_DIR else
        Path(f"operator_log_{IDP1}_{IDP2}.csv")
    )

    with open(fn, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            state,
            key,
            datetime.now().isoformat(timespec="milliseconds"),
            head_position
        ])

def reset_turn_cause_flags():
    global gaze_event_start_time, silence_event_start_time
    global gaze_before_silence_flag, silence_before_gaze_flag

    gaze_event_start_time = None
    silence_event_start_time = None
    gaze_before_silence_flag = False
    silence_before_gaze_flag = False

def speaker_looks_at_other_human(speaker: str) -> bool:
    if not ENABLE_FACE_TRACKING:
        return False

    try:
        pitch, yaw = tracking_model.LAST_POSE
        pose_ts = getattr(tracking_model, "LAST_POSE_TS", None)
    except Exception:
        return False

    pose_age = time.time() - pose_ts
    if pose_age > 1.0:
        return False

    if abs(pitch) > HUMAN_GAZE_PITCH_THRESH:
        return False

    # left participant looking to right participant
    if speaker == 'l':
        return HUMAN_GAZE_YAW_MIN <= yaw <= HUMAN_GAZE_YAW_MAX

    # right participant looking to left participant
    if speaker == 'r':
        return -HUMAN_GAZE_YAW_MAX <= yaw <= -HUMAN_GAZE_YAW_MIN

    return False

def add_head_dir():
    d = head_position[0] if head_position in ("left", "right") else "m"
    log_headpose.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "direction": d,
        "participant": IDP1 if d == "l" else IDP2 if d == "r" else "both"
    })  
        
def recent_move_flag():
    global recent_move
    recent_move = True
    threading.Timer(0.5, lambda: globals().__setitem__('recent_move', False)
                   ).start()

def reset_gaze(now):
    global head_position, head_timer_start
    global gaze_shift_active, gaze_shift_target, gaze_shift_origin
    global gaze_shift_cooldown_until

    misty.move_head(0, 0, 0)
    recent_move_flag()
    head_position       = 'middle'
    head_timer_start    = now
    gaze_shift_active   = False
    gaze_shift_target   = None
    gaze_shift_origin   = None
    gaze_shift_cooldown_until = now + timedelta(seconds=2)

def participant_looks_at_robot() -> bool:
    if not ENABLE_FACE_TRACKING:
        return False

    try:
        pitch, yaw = tracking_model.LAST_POSE
        pose_ts = getattr(tracking_model, "LAST_POSE_TS", None)
    except Exception:
        return False

    pose_age = time.time() - pose_ts
    if pose_age > 1.0:
        return False

    pitch_change = PARTICIPANT_OFFSETS.get(head_position, PARTICIPANT_OFFSETS["middle"])
    target_pitch = pitch_change.get("gaze_pitch_center", 0)

    gaze_direction = classify_gaze_direction(yaw)

    return (
        gaze_direction == "middle" and
        abs(pitch) <= EYE_CONTACT_PITCH_THRESH
    )

def look_at_participant(side: str):
    global head_position, head_timer_start, recent_move

    if side == head_position:
        return

    offset = PARTICIPANT_OFFSETS[side]
    speed = 90

    misty.move_head(offset["robot_pitch"], 0, offset["robot_yaw"], speed)

    recent_move_flag()
    head_position = side

    head_timer_start = time.time() 

def face_tracking_thread():
    global face_direction, last_eye_contact_time

    try:
        tracking_model.run_continuous_tracking(
            misty=misty,
            pitch_thresh=EYE_CONTACT_PITCH_THRESH,
            yaw_thresh=EYE_CONTACT_YAW_THRESH,
            show_window=True
        )
    except Exception as e:
        print("Face-tracking stopped:", e)

def pose_logging_thread():
    global total_eye_contact_time, eye_contact_run_start, last_logged_eye_contact_state
    global head_position, GAZE_LOGFILE, last_speaker, dialogstage

    try:
        while not getattr(tracking_model, "STOP_TRACKING", False):
            try:
                pitch, yaw = tracking_model.LAST_POSE
                pose_ts = getattr(tracking_model, "LAST_POSE_TS", None)
            except Exception:
                time.sleep(0.02)
                continue

            pose_age = time.time() - pose_ts
            if pose_age <= 1.0:
                gaze_direction = classify_gaze_direction(yaw)

                participant_looking_at_robot = (
                    gaze_direction == "middle" and
                    abs(pitch) <= EYE_CONTACT_PITCH_THRESH
                )

                robot_eye_contact = participant_looking_at_robot

                now_ts = time.time()

                current_speaker = last_speaker if last_speaker in ('l', 'r') else None
                human_directed_gaze = 0
                if current_speaker is not None and speech_detector.detect_speaker(1.0) == current_speaker:
                    human_directed_gaze = int(speaker_looks_at_other_human(current_speaker))
                    
                if robot_eye_contact and not last_logged_eye_contact_state:
                    eye_contact_run_start = now_ts
                elif (not robot_eye_contact and
                    last_logged_eye_contact_state and
                    eye_contact_run_start is not None):

                    duration = now_ts - eye_contact_run_start
                    total_eye_contact_time += duration

                    with open(GAZE_LOGFILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            datetime.now().isoformat(timespec="milliseconds"),
                            gaze_direction,
                            round(yaw, 2),
                            round(pitch, 2),
                            0,
                            human_directed_gaze,
                            round(total_eye_contact_time, 3),
                            dialogstage,
                            round(duration, 3)
                        ])

                    eye_contact_run_start = None

                current_total = total_eye_contact_time
                if robot_eye_contact and eye_contact_run_start is not None:
                    current_total += now_ts - eye_contact_run_start


                with open(GAZE_LOGFILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.now().isoformat(timespec="milliseconds"),
                        gaze_direction,
                        round(yaw, 2),
                        round(pitch, 2),
                        int(robot_eye_contact),
                        human_directed_gaze,
                        round(current_total, 3),
                        dialogstage,
                        ""
                    ])

                last_logged_eye_contact_state = robot_eye_contact

            time.sleep(0.1)

    except Exception as e:
        print("Pose logging stopped:", e)

def log_speech_event(
    timestamp_start="",
    timestamp_end="",
    speaker="",
    event_type="turn",
    speaking_time="",
    silence_before="",
    turn_from="",
    turn_to="",
    offset_to_onset_interval="",
    is_turn_take=0,
    gaze_before_silence="",
    silence_before_gaze="",
    required_threshold="",
    actual_trigger_silence="",
    dialogstage="",
    time_since_gaze_start="",
    time_since_silence_start="",
    interruption_type="",
    trigger_source="auto"
):
    global SPEECH_LOGFILE

    with open(SPEECH_LOGFILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp_start,
            timestamp_end,
            speaker,
            event_type,
            round(speaking_time, 3) if speaking_time not in ("", None) else "",
            round(silence_before, 3) if silence_before not in ("", None) else "",
            turn_from,
            turn_to,
            round(offset_to_onset_interval, 3) if offset_to_onset_interval not in ("", None) else "",
            is_turn_take,
            gaze_before_silence,
            silence_before_gaze,
            required_threshold,
            actual_trigger_silence,
            dialogstage,
            round(time_since_gaze_start, 3) if time_since_gaze_start not in ("", None) else "",
            round(time_since_silence_start, 3) if time_since_silence_start not in ("", None) else "",
            interruption_type,
            trigger_source
        ])

def log_robot_turn_start():
    global previous_turn_speaker, previous_turn_offset_time
    global turn_count_human_robot, turn_count_robot_robot
    global last_trigger_silence, last_time_since_gaze_start, last_time_since_silence_start
    global current_trigger_source

    interval = ""
    if previous_turn_offset_time is not None:
        interval = time.time() - previous_turn_offset_time

    if previous_turn_speaker is not None:
        if previous_turn_speaker in ('l', 'r'):
            turn_count_human_robot += 1
        elif previous_turn_speaker == 'robot':
            pass

        log_speech_event(
            timestamp_start=datetime.now().isoformat(timespec="milliseconds"),
            timestamp_end="",
            speaker="robot",
            event_type="robot_turn_start",
            speaking_time="",
            silence_before="",
            turn_from=previous_turn_speaker,
            turn_to="robot",
            offset_to_onset_interval=interval,
            is_turn_take=1 if previous_turn_speaker in ('l', 'r') else 0,
            gaze_before_silence=int(gaze_before_silence_flag),
            silence_before_gaze=int(silence_before_gaze_flag),
            required_threshold=TURN_SILENCE_SECONDS,
            actual_trigger_silence=last_trigger_silence,
            dialogstage=dialogstage,
            time_since_gaze_start=last_time_since_gaze_start,
            time_since_silence_start=last_time_since_silence_start,
            interruption_type=last_interruption_type,
            trigger_source=current_trigger_source
        )
    else:
        log_speech_event(
            timestamp_start=datetime.now().isoformat(timespec="milliseconds"),
            timestamp_end="",
            speaker="robot",
            event_type="robot_turn_start",
            trigger_source=current_trigger_source
        )

    reset_turn_cause_flags()
    last_trigger_silence = None
    last_time_since_gaze_start = None
    last_time_since_silence_start = None
    previous_turn_speaker = "robot"

def log_timeline_event(state, speaker, silence_duration, yaw, pitch,
                       eye_contact, human_directed_gaze):
    global TIMELINE_LOGFILE, head_position, dialogstage

    with open(TIMELINE_LOGFILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(timespec="milliseconds"),
            speaker,
            round(silence_duration, 3) if silence_duration not in ("", None) else "",
            round(yaw, 2) if yaw not in ("", None) else "",
            round(pitch, 2) if pitch not in ("", None) else "",
            int(eye_contact) if eye_contact not in ("", None) else "",
            int(human_directed_gaze) if human_directed_gaze not in ("", None) else "",
            head_position,
            state,
            dialogstage
        ])

def rms_logging_thread():
    global RMS_LOGFILE

    while True:
        try:
            now = time.time()
            left_rms = (
                speech_detector.left_recorder.rms_log[-1][1]
                if speech_detector.left_recorder.rms_log else None
            )
            right_rms = (
                speech_detector.right_recorder.rms_log[-1][1]
                if speech_detector.right_recorder.rms_log else None
            )

            left_thr = speech_detector.left_recorder.speech_threshold
            right_thr = speech_detector.right_recorder.speech_threshold

            with open(RMS_LOGFILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(timespec="milliseconds"),
                    round(left_rms, 3) if left_rms is not None else "",
                    round(right_rms, 3) if right_rms is not None else "",
                    round(left_thr, 3),
                    round(right_thr, 3),
                ])

        except Exception as e:
            print("RMS logging error:", e)

        time.sleep(0.05)  # 20 Hz

def update_human_turn_logging(speaker, silence_dur):
    global pending_human_turn, previous_turn_speaker, previous_turn_offset_time
    global turn_count_human_human, turn_count_robot_human
    global current_trigger_source, robot_is_speaking, last_robot_speech_end_time
    global current_human_turn_start_time

    now_ts = time.time()
    now_iso = datetime.now().isoformat(timespec="milliseconds")

    if speaker in ('l', 'r'):

        speaking_dur = speech_detector.get_speaking_duration_by_side(speaker)

        # short utterances are not counted
        if speaking_dur < speech_detector.MIN_SPEAK_TIME_TO_SWITCH:
            return

        # Start a new human turn
        if pending_human_turn is None:
            interval = ""
            if previous_turn_offset_time is not None:
                interval = now_ts - previous_turn_offset_time

            turn_from = previous_turn_speaker if previous_turn_speaker is not None else ""

            if previous_turn_speaker in ('l', 'r'):
                turn_count_human_human += 1
            elif previous_turn_speaker == 'robot':
                turn_count_robot_human += 1

            interruption_type = ""

            robot_just_finished = (
                last_robot_speech_end_time is not None
                and time.time() - last_robot_speech_end_time <= INTERRUPTION_WINDOW
            )

            if robot_is_speaking or robot_just_finished:
                interruption_type = "human_interrupts_robot"

            pending_human_turn = {
                "timestamp_start": now_iso,
                "speaker": speaker,
                "silence_before": silence_dur,
                "turn_from": turn_from,
                "turn_to": speaker,
                "offset_to_onset_interval": interval,
                "is_turn_take": 1 if previous_turn_speaker is not None else 0,
                "interruption_type": interruption_type,
                "dialogstage": dialogstage
            }

            previous_turn_speaker = speaker

        # speaker change
        elif pending_human_turn["speaker"] != speaker:

            speaking_dur = speech_detector.get_speaking_duration_by_side(speaker)

            if speaking_dur < speech_detector.MIN_SPEAK_TIME_TO_SWITCH:
                return

            speaking_time = (
                now_ts - current_human_turn_start_time
                if current_human_turn_start_time is not None
                else ""
            )

            log_speech_event(
                timestamp_start=pending_human_turn["timestamp_start"],
                timestamp_end=now_iso,
                speaker=pending_human_turn["speaker"],
                event_type="human_turn",
                speaking_time=speaking_time,
                silence_before=pending_human_turn["silence_before"],
                turn_from=pending_human_turn["turn_from"],
                turn_to=pending_human_turn["turn_to"],
                offset_to_onset_interval=pending_human_turn["offset_to_onset_interval"],
                is_turn_take=pending_human_turn["is_turn_take"],
                dialogstage=pending_human_turn["dialogstage"],
                interruption_type=pending_human_turn["interruption_type"],
                trigger_source="auto"
            )

            interval = ""
            if previous_turn_offset_time is not None:
                interval = now_ts - previous_turn_offset_time

            previous_turn_offset_time = now_ts
            turn_from = previous_turn_speaker if previous_turn_speaker is not None else ""

            if previous_turn_speaker in ('l', 'r'):
                turn_count_human_human += 1
            elif previous_turn_speaker == 'robot':
                turn_count_robot_human += 1

            interruption_type = ""

            robot_just_finished = (
                last_robot_speech_end_time is not None
                and time.time() - last_robot_speech_end_time <= INTERRUPTION_WINDOW
            )

            if robot_is_speaking or robot_just_finished:
                interruption_type = "human_interrupts_robot"

            pending_human_turn = {
                "timestamp_start": now_iso,
                "speaker": speaker,
                "silence_before": silence_dur,
                "turn_from": turn_from,
                "turn_to": speaker,
                "offset_to_onset_interval": interval,
                "is_turn_take": 1 if previous_turn_speaker is not None else 0,
                "interruption_type": interruption_type,
                "dialogstage": dialogstage
            }

            previous_turn_speaker = speaker

    else:
        if pending_human_turn is not None:
            speaking_time = (
                now_ts - current_human_turn_start_time
                if current_human_turn_start_time is not None
                else ""
            )

            log_speech_event(
                timestamp_start=pending_human_turn["timestamp_start"],
                timestamp_end=now_iso,
                speaker=pending_human_turn["speaker"],
                event_type="human_turn",
                speaking_time=speaking_time,
                silence_before=pending_human_turn["silence_before"],
                turn_from=pending_human_turn["turn_from"],
                turn_to=pending_human_turn["turn_to"],
                offset_to_onset_interval=pending_human_turn["offset_to_onset_interval"],
                is_turn_take=pending_human_turn["is_turn_take"],
                dialogstage=pending_human_turn["dialogstage"],
                interruption_type=pending_human_turn["interruption_type"],
                trigger_source="auto"
            )

            previous_turn_offset_time = now_ts
            pending_human_turn = None

def get_current_name():
    if last_speaker == 'l':
        return NameP1
    elif last_speaker == 'r':
        return NameP2
    return NameP1 

def get_other_side():
    if last_speaker == 'l':
        return "right"
    elif last_speaker == 'r':
        return "left"
    return "middle"

def robot_speak_and_wait(
    text,
    center_head=True,
    turn_hold_after_speech=1.0,
    gaze_reengage_delay=ROBOT_GAZE_REENGAGE_DELAY,
    allow_condition_b_reengage=True
):
    global robot_speaking_cooldown_until, head_position, previous_turn_offset_time, last_interruption_type, current_trigger_source
    global robot_is_speaking, last_robot_speech_end_time

    current_speaker = speech_detector.detect_speaker(0.3)

    last_interruption_type = ""
    if current_speaker in ('l', 'r'):
        last_interruption_type = "robot_interrupts_human"
    elif current_speaker == 'b':
        last_interruption_type = "robot_interrupts_overlap"

    # robot head middle
    if center_head and allow_condition_b_reengage and head_position != "middle":
        look_at_participant("middle")

    # stop microphones
    try:
        speech_detector.left_recorder.stop_recording()
    except Exception:
        pass
    try:
        speech_detector.right_recorder.stop_recording()
    except Exception:
        pass
    try:
        if RMS_LOGFILE is not None:
            log_data.stop(RMS_LOGFILE)
    except Exception:
        pass

    log_robot_turn_start()

    # start utterance
    robot_is_speaking = True
    misty.speak(text)
    print(f"Robot started speaking: {text}")

    speech_start = time.time()

    gaze_aversion_started = False
    next_gaze_switch_time = None
    current_gaze_side = None
    GAZE_SWITCH_INTERVAL = 4.75

    # speech duration
    words = len(text.split())
    chars = len(text.replace(" ", ""))

    estimated_duration = max(1.2, max(words / 2.9, chars / 13.0))
    speech_end_time = speech_start + estimated_duration

    print(f"Estimated speech duration = {estimated_duration:.2f}s")

    while True:
        elapsed = time.time() - speech_start
        now_ts = time.time()

        # condition A
        if GAZE_BEHAVIOR_CONDITION == "A":
            if center_head and allow_condition_b_reengage and head_position != "middle":
                look_at_participant("middle")

        # condition B
        elif GAZE_BEHAVIOR_CONDITION == "B" and allow_condition_b_reengage:
                if not gaze_aversion_started and elapsed >= gaze_reengage_delay:
                    current_gaze_side = random.choice(["left", "right"])
                    print(f"CONDITION B elapsed={elapsed:.2f}s -> looking {current_gaze_side}")
                    look_at_participant(current_gaze_side)

                    gaze_aversion_started = True

                    if estimated_duration > 6.0:
                        next_gaze_switch_time = head_timer_start + GAZE_SWITCH_INTERVAL
                    else:
                        next_gaze_switch_time = None

                elif (
                    gaze_aversion_started and next_gaze_switch_time is not None and now_ts >= next_gaze_switch_time
                ):
                    current_gaze_side = "right" if current_gaze_side == "left" else "left"
                    print(f"CONDITION B elapsed={elapsed:.2f}s -> switching to {current_gaze_side}")
                    look_at_participant(current_gaze_side)

                    next_gaze_switch_time = head_timer_start + GAZE_SWITCH_INTERVAL

        # check duration with function
        try:
            is_playing = misty.get_audio_playing().json().get("result", False)
        except Exception:
            is_playing = None

        if is_playing is False and elapsed >= max(0.8, estimated_duration * 0.75):
            print("Speech ended via audio_playing")
            break

        # -
        if now_ts >= speech_end_time:
            print("Speech ended via predicted duration")
            break

        time.sleep(0.02)

    last_robot_speech_end_time = time.time()
    robot_is_speaking = False

    speech_duration = time.time() - speech_start
    speech_end_ts = datetime.now().isoformat(timespec="milliseconds")
    previous_turn_offset_time = time.time()

    log_speech_event(
        timestamp_start="",
        timestamp_end=speech_end_ts,
        speaker="robot",
        event_type="robot_turn_end",
        speaking_time=speech_duration,
        silence_before="",
        turn_from="robot",
        turn_to="",
        offset_to_onset_interval="",
        is_turn_take=0,
        dialogstage=dialogstage,
        trigger_source=current_trigger_source
    )

    # ending
    if GAZE_BEHAVIOR_CONDITION == "A":
        if center_head and head_position != "middle":
            look_at_participant("middle")

    elif GAZE_BEHAVIOR_CONDITION == "B":
        if allow_condition_b_reengage:
            time.sleep(0.4)
        pass

    # start mics
    speech_detector.reset_timers()

    try:
        speech_detector.left_recorder.start_recording()
    except Exception:
        pass
    try:
        speech_detector.right_recorder.start_recording()
    except Exception:
        pass
    try:
        log_data.start()
    except Exception:
        pass
    
    current_trigger_source = "auto"
    robot_speaking_cooldown_until = datetime.now() + timedelta(
        seconds=turn_hold_after_speech
    )


# STATES
##############################################################################

# 0 ─ Experiment initialisation
def state_0_init():
    global IDP1, IDP2, NameP1, NameP2
    global LOG_DIR, GAZE_LOGFILE, SPEECH_LOGFILE, SUMMARY_LOGFILE, RESULTS_LOGFILE, TIMELINE_LOGFILE, RMS_LOGFILE
    global _start_time, GazeShiftEnabled, dialogstage

    print("Initialising …")
    NameP1 = input("Name participant LEFT : ")
    IDP1   = input("ID LEFT  : ")
    NameP2 = input("Name participant RIGHT: ")
    IDP2   = input("ID RIGHT : ")

    gaze_choice = input("Enable gaze-shift? (y/n): ").strip().lower()
    GazeShiftEnabled = (gaze_choice == "y")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    LOG_DIR = (
        Path(__file__).parent
        / "experiment_logs"
        / f"{IDP1}-{IDP2}__{timestamp}"
    )
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Log files → {LOG_DIR.resolve()}")

    # Log files
    GAZE_LOGFILE = LOG_DIR / "gaze_log.csv"
    SPEECH_LOGFILE = LOG_DIR / "speech_log.csv"
    SUMMARY_LOGFILE = LOG_DIR / "summary_log.csv"
    RESULTS_LOGFILE = LOG_DIR / "operator_log.csv"
    TIMELINE_LOGFILE = LOG_DIR / "timeline_log.csv"
    RMS_LOGFILE = LOG_DIR / "rms_log.csv"

    with open(RMS_LOGFILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "left_rms",
            "right_rms",
            "left_threshold",
            "right_threshold"
        ])

    open(RESULTS_LOGFILE, "w").close()

    with open(GAZE_LOGFILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "direction",
            "yaw",
            "pitch",
            "robot_eye_contact",
            "human_directed_gaze",
            "total_eye_contact_time",
            "dialogstage",
            "eye_contact_duration_individually"
        ])

    with open(SPEECH_LOGFILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp_start",
            "timestamp_end",
            "speaker",
            "event_type",
            "speaking_time",
            "silence_before",
            "turn_from",
            "turn_to",
            "offset_to_onset_interval",
            "is_turn_take",
            "gaze_before_silence",
            "silence_before_gaze",
            "required_threshold",
            "actual_trigger_silence",
            "dialogstage",
            "time_since_gaze_start",
            "time_since_silence_start",
            "interruption_type",
            "trigger_source"
        ])

    with open(RESULTS_LOGFILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["state", "key", "timestamp", "head_position"])

    with open(TIMELINE_LOGFILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "speaker",
            "silence_duration",
            "yaw",
            "pitch",
            "eye_contact",
            "human_directed_gaze",
            "head_position",
            "state",
            "dialogstage"
        ])

    set_all_log_path(LOG_DIR)

    # save data
    log_data.experiment_data.update({
        "topic": "holiday",
        "IDP1": IDP1,
        "IDP2": IDP2,
        "NameP1": NameP1,
        "NameP2": NameP2,
        "gaze_shift_enabled": GazeShiftEnabled,
    })

    print("Calibrating microphones …")
    speech_detector.setup_speech_detection()

    misty.move_head(0, 0, 0, 90)   # neutral pose
    log_data.start()                 # begin RMS recording

    _start_time = datetime.now()

    print(f"Gaze enabled: {GazeShiftEnabled}")
    if ENABLE_FACE_TRACKING:
        tracking_model.LAST_POSE = None
        tracking_model.LAST_POSE_TS = None  
        tracking_model.SHOW_WINDOW = True
        tracking_model.STOP_TRACKING = False

        threading.Thread(target=face_tracking_thread, daemon=True).start()
        threading.Thread(target=pose_logging_thread, daemon=True).start()
        threading.Thread(target=rms_logging_thread, daemon=True).start()

    # introduction robot
    look_at_participant("middle")
    time.sleep(0.5)

    robot_speak_and_wait(
        "Welcome to this experiment! My name is Misty and I am really excited to do this experiment, and I hope you are too. Lets start by getting to know each other.",
        center_head=True,
        turn_hold_after_speech=0.6
    )

    look_at_participant("left")
    time.sleep(0.5)

    robot_speak_and_wait(
        "First participant, what is your name?",
        center_head=False,
        turn_hold_after_speech=0.7,
        allow_condition_b_reengage=False
    )
    time.sleep(1.5)

    look_at_participant("right")
    time.sleep(0.5)

    robot_speak_and_wait(
        "And second participant, what is your name?",
        center_head=False,
        turn_hold_after_speech=0.7,
        allow_condition_b_reengage=False
    )
    time.sleep(2.5)

    robot_speak_and_wait(
        "Thank you! Now it is clear to me who I am speaking with. Next I will explain the task to you.",
        center_head=True,
        turn_hold_after_speech=0.7
    )

    # start of script
    if TOPIC_CONDITION == "holiday":
        intro_text = listtostr(holiday.introduction)
    elif TOPIC_CONDITION == "dream":
        intro_text = listtostr(dream.introduction)
    else:
        intro_text = "I will now explain the task."

    robot_speak_and_wait(
        intro_text,
        center_head=True,
        turn_hold_after_speech=1.0
    )

    dialogstage = 1
    return 10

# STATE 1 wait
##############################################################################

def state_1_wait_for_speech():
    global robot_speaking_cooldown_until
    global last_speaker, forced_attention_until, head_position, current_human_turn_speaker, current_human_turn_start_time

    print("Waiting for speech")

    while True:
        override = check_menu_keys()
        if override is not None:
            return override

        now = datetime.now()

        if robot_speaking_cooldown_until is not None and now < robot_speaking_cooldown_until:
            speaker = speech_detector.detect_speaker(1.0)
            silence_dur = speech_detector.get_silence_duration()

            if speaker == 'l':
                last_speaker = 'l'
            elif speaker == 'r':
                last_speaker = 'r'

            hold_active = (
                forced_attention_until is not None and
                now < forced_attention_until
            )

            if speaker == 'l':
                new_pos = 'left'
            elif speaker == 'r':
                new_pos = 'right'
            elif hold_active:
                new_pos = head_position
            else:
                if GAZE_BEHAVIOR_CONDITION == "B" and head_position in ("left", "right"):
                    new_pos = head_position   # keep final gaze after speaking
                else:
                    new_pos = 'middle'

            if new_pos != head_position:
                look_at_participant(new_pos)

            update_human_turn_logging(speaker, silence_dur)

            if speaker in ('l', 'r'):
                if current_human_turn_speaker != speaker:
                    current_human_turn_speaker = speaker
                    current_human_turn_start_time = time.time()
            else:
                current_human_turn_speaker = None
                current_human_turn_start_time = None

            time.sleep(0.02)
            continue
        else:
            robot_speaking_cooldown_until = None

        speaker = speech_detector.detect_speaker(1.0)
        silence_dur = speech_detector.get_silence_duration()

        print(f"STATE 1 speaker={speaker}, silence={silence_dur:.2f}")

        # Test B
        if speaker == 'l':
            speaking_dur = speech_detector.get_speaking_duration_by_side('l')

            if speaking_dur >= speech_detector.MIN_SPEAK_TIME_TO_SWITCH:
                last_speaker = 'l'
                return 3

        elif speaker == 'r':
            speaking_dur = speech_detector.get_speaking_duration_by_side('r')

            if speaking_dur >= speech_detector.MIN_SPEAK_TIME_TO_SWITCH:
                last_speaker = 'r'
                return 3

        # Test A → inactivity
        elif speaker == 's' and silence_dur >= MOTIVATION_INACTIVITY_SECONDS:
            print(f"Test A {silence_dur:.2f}s")
            speech_detector.reset_timers()
            return 2

        time.sleep(0.02)

# STATE 2 motivate
##############################################################################
def state_2_motivate():
    utterance = listtostr(random.choice(holiday.breaksilence))

    robot_speak_and_wait(
        utterance,
        center_head=True,
        turn_hold_after_speech=1.0
    )

    return 1


# STATE 3 turn head
##############################################################################
def state_3_turn_head_to_speaker():
    global last_speaker

    if last_speaker == 'l':
        look_at_participant("left")
        return 4

    elif last_speaker == 'r':
        look_at_participant("right")
        return 4

    return 1

# STATE 4 keep looking
##############################################################################

def state_4_keep_looking_at_speaker():
    global last_speaker
    global eye_contact_streak
    global active_speaker, active_speaker_start, longturn_ack_done
    global current_trigger_source
    global gaze_event_start_time, silence_event_start_time
    global gaze_before_silence_flag, silence_before_gaze_flag
    global last_trigger_silence
    global last_time_since_gaze_start, last_time_since_silence_start
    global overlap_logged
    global current_human_turn_speaker, current_human_turn_start_time, state4_testd_count, eye_contact_buffer

    while True:
        override = check_menu_keys()
        if override is not None:
            return override

        speaker = speech_detector.detect_speaker(1.0)
        silence_dur = speech_detector.get_silence_duration()
        stats = speech_detector.get_speech_stats()

        raw_look = participant_looks_at_robot()

        eye_contact_buffer.append(raw_look)
        if len(eye_contact_buffer) > 10:
            eye_contact_buffer.pop(0)

        looks_at_robot = sum(eye_contact_buffer) >= 5

        # Logging
        if speaker == 'b':
            if not overlap_logged:
                log_speech_event(
                    timestamp_start=datetime.now().isoformat(timespec="milliseconds"),
                    timestamp_end="",
                    speaker="b",
                    event_type="overlap",
                    speaking_time="",
                    silence_before=silence_dur,
                    turn_from="",
                    turn_to="",
                    offset_to_onset_interval="",
                    is_turn_take=0,
                    dialogstage=dialogstage,
                    interruption_type="human_human_overlap",
                    trigger_source="auto"
                )
                overlap_logged = True
        else:
            overlap_logged = False

        print(f"STATE 4 speaker={speaker}, silence={silence_dur:.2f}, look={looks_at_robot}")

        now_ts = time.time()

        if speaker in ('l', 'r') and looks_at_robot:
            gaze_before_silence_flag = True

        if speaker == 's' and looks_at_robot:
            if silence_event_start_time is not None:
                silence_before_gaze_flag = True

        if looks_at_robot:
            if gaze_event_start_time is None:
                gaze_event_start_time = now_ts
        else:
            gaze_event_start_time = None

        if speaker == 's':
            if silence_event_start_time is None:
                silence_event_start_time = now_ts
        else:
            silence_event_start_time = None

        if gaze_before_silence_flag:
            silence_before_gaze_flag = False
        
        human_directed_gaze = False
        if speaker in ('l', 'r'):
            human_directed_gaze = int(speaker_looks_at_other_human(speaker))

        try:
            pitch, yaw = tracking_model.LAST_POSE
            pose_ts = getattr(tracking_model, "LAST_POSE_TS", 0.0)
            pose_age = time.time() - pose_ts
            if pose_age > 1.0:
                pitch, yaw = "", ""
        except Exception:
            pitch, yaw = "", ""

        log_timeline_event(
            state=4,
            speaker=speaker,
            silence_duration=silence_dur,
            yaw=yaw,
            pitch=pitch,
            eye_contact=looks_at_robot,
            human_directed_gaze=human_directed_gaze
        )

        if speaker in ('l', 'r'):
            if current_human_turn_speaker != speaker:
                current_human_turn_speaker = speaker
                current_human_turn_start_time = time.time()
                longturn_ack_done = False

        update_human_turn_logging(speaker, silence_dur)

        if speaker not in ('l', 'r'):
            current_human_turn_speaker = None
            current_human_turn_start_time = None
            longturn_ack_done = False

        # Update last speaker
        if speaker == 'l':
            last_speaker = 'l'
            if head_position != "left":
                look_at_participant("left")

        elif speaker == 'r':
            last_speaker = 'r'
            if head_position != "right":
                look_at_participant("right")

        # ERROR REMOVES THIS OTHERWISE TURNTAKE DURATION IS 1.5S
        if silence_dur >= TURN_SILENCE_SECONDS:
            if looks_at_robot:
                eye_contact_streak += 1
            else:
                eye_contact_streak = 0
        else:
            eye_contact_streak = 0

        # Test C: backchannel response
        if speaker in ('l', 'r') and stats:
            if speaker == 'l':
                monologue_dur = stats['left']['speaking_duration']
            else:
                monologue_dur = stats['right']['speaking_duration']

            if not longturn_ack_done and monologue_dur >= LONG_TURN_ACK_SECONDS:
                print("Test C → backchannel")
                longturn_ack_done = True
                speech_detector.reset_timers()
                return 5   

        # Test D: silence + eye contact
        if silence_dur >= TURN_SILENCE_SECONDS and eye_contact_streak >= 25:
            print("Test D → take turn")

            last_trigger_silence = silence_dur

            if gaze_event_start_time is not None:
                last_time_since_gaze_start = now_ts - gaze_event_start_time
            else:
                last_time_since_gaze_start = None

            if silence_event_start_time is not None:
                last_time_since_silence_start = now_ts - silence_event_start_time
            else:
                last_time_since_silence_start = None

            current_trigger_source = "auto_test_d"
            speech_detector.reset_timers()
            eye_contact_streak = 0
            return 13

        # Test E: silence + NO eye contact
        if (
            last_speaker in ('l', 'r')
            and head_position in ('left', 'right')
            and silence_dur >= LONG_TURN_ACK_SECONDS
            and not looks_at_robot
        ):
            print("Test E → take turn")
            last_trigger_silence = silence_dur

            if gaze_event_start_time is not None:
                last_time_since_gaze_start = now_ts - gaze_event_start_time
            else:
                last_time_since_gaze_start = None

            if silence_event_start_time is not None:
                last_time_since_silence_start = now_ts - silence_event_start_time
            else:
                last_time_since_silence_start = None
            current_trigger_source = "auto_test_e"
            speech_detector.reset_timers()
            return 9

        time.sleep(0.02)

# STATE 5 backchannel
##############################################################################
def state_5_backchannel():
    utterance = random.choice([
        "I see.",
        "Okay.",
        "Right.",
        "Go on.",
        "uh-huh."
    ])

    robot_speak_and_wait(
        utterance,
        center_head=False, 
        turn_hold_after_speech=0.7,
        allow_condition_b_reengage=False
    )

    speech_detector.reset_timers()

    return 4  

# STATE 6 information on a chosen option
##############################################################################
def state_6_info():
    global dialogstage

    if not (1 <= dialogstage <= 9):
        return 1

    opt_list = get_topic_option_list()

    if not opt_list:
        print("No options found for current topic")
        return 1

    print(f"Give info about (1-{len(opt_list)}): ", end="", flush=True)

    key = msvcrt.getch().decode('ascii')
    print(key)

    if not key.isdigit():
        print("Invalid input")
        return 1

    idx = int(key) - 1

    if not (0 <= idx < len(opt_list)):
        print("Invalid option")
        return 1

    selected_option = opt_list[idx]

    info_text = get_topic_info_text(selected_option)

    if not info_text:
        utterance = f"I do not have extra information for {selected_option}."
    else:
        utterance = listtostr(info_text)

    robot_speak_and_wait(
        utterance,
        center_head=True,
        turn_hold_after_speech=1.0
    )

    return 1

# STATE 7 verdict
##############################################################################
def state_7_verdict():
    global chosen_options, dialogstage, state7_count

    if not (1 <= dialogstage <= 9):
        return 11

    opt_list = get_topic_option_list()
    if not opt_list:
        print("No options found for current topic")
        return 11

    speech_detector.left_recorder.stop_recording()
    speech_detector.right_recorder.stop_recording()

    print("[1] single  [2] multiple  [3] none  [4] unclear [5] speedup")
    verdict_key = msvcrt.getch().decode('ascii').lower()
    print(verdict_key)

    print(f"Choose option (1-{len(opt_list)}): ", end="", flush=True)
    key = msvcrt.getch().decode('ascii')
    print(key)
    log_state_button(7, key)

    if not key.isdigit():
        print(f"Choose 1-{len(opt_list)}")
        speech_detector.reset_timers()
        speech_detector.left_recorder.start_recording()
        speech_detector.right_recorder.start_recording()
        log_data.start()
        return 11

    idx = int(key) - 1
    if not (0 <= idx < len(opt_list)):
        print(f"Choose 1-{len(opt_list)}")
        speech_detector.reset_timers()
        speech_detector.left_recorder.start_recording()
        speech_detector.right_recorder.start_recording()
        log_data.start()
        return 11

    chosen_option = opt_list[idx]

    # single and speedup
    if verdict_key in ('1', '5'):
        state7_count = 2
    else:
        state7_count += 1

    # choose utterance
    if verdict_key == '5':
        if TOPIC_CONDITION == "holiday":
            utterance = random.choice(holiday.SpeedUP)
        elif TOPIC_CONDITION == "dream":
            utterance = random.choice(dream.SpeedUP)

    else:
        if TOPIC_CONDITION == "holiday":
            utterance = holiday.get_verdict_utterance(
                chosen_option, verdict_key, state7_count
            )
        elif TOPIC_CONDITION == "dream":
            utterance = dream.get_verdict_utterance(
                chosen_option, verdict_key, state7_count
            )

    robot_speak_and_wait(
        utterance,
        center_head=True,
        turn_hold_after_speech=1.0
    )

    # first time for multiple / none / unclear:
    # give info and return to discussion
    if verdict_key in ('2', '3', '4') and state7_count == 1:
        speech_detector.reset_timers()
        speech_detector.left_recorder.start_recording()
        speech_detector.right_recorder.start_recording()
        log_data.start()
        return 1

    # second time or single: ask confirmation
    answer = input("(yes / no): ").strip().lower()

    if answer == "yes":
        chosen_options.append(chosen_option)
        set_topic_choice(chosen_option)

        if dialogstage == 9:
            if TOPIC_CONDITION == "holiday":
                holiday.set_derived_holiday_details()
            elif TOPIC_CONDITION == "dream":
                dream.set_derived_dream_house_details()

            dialogstage = 10
            state7_count = 0
            return 10

        robot_speak_and_wait(
            random.choice([
                f"Clearly {chosen_option} is the best choice.",
                f"Great, you both agree. {chosen_option} it is."
            ]),
            center_head=True,
        )

        dialogstage += 1
        state7_count = 0
        return 10

    state7_count = 0

    robot_speak_and_wait(
        "Sorry, my mistake. Can you make it clear to me what option you will choose?",
        center_head=True,
    )

    speech_detector.reset_timers()
    speech_detector.left_recorder.start_recording()
    speech_detector.right_recorder.start_recording()
    log_data.start()

    return 1

# STATE 8 repeat current question
##############################################################################
def state_8_repeat():
    global dialogstage

    if not (1 <= dialogstage <= 9):
        return 11   

    robot_speak_and_wait(
        "I'll repeat the question.",
        center_head=True,
    )

    return 10       

# STATE 9 take turn after Test E
##############################################################################
def state_9_fallback():
    global forced_attention_until, current_trigger_source, state9_count, dialogstage, head_position

    state9_count += 1

    idname = get_current_name()
    set_names(idname, NameP1, NameP2)

    if TOPIC_CONDITION == "holiday":
        holiday.OPT[0] = chosen_options[-1] if chosen_options else ""
    elif TOPIC_CONDITION == "dream":
        dream.OPT[0] = chosen_options[-1] if chosen_options else ""

    # LEVEL 1: verbal prompt
    if state9_count == 1:
        holiday.RIGHTWRONG[0] = random.choice(["right", "wrong"])
        dream.RIGHTWRONG[0] = random.choice(["right", "wrong"])
        mode = random.choice(["direct", "switch"])

        if TOPIC_CONDITION == "holiday":
            direct_turntake = holiday.direct_turntake
            switch_turntake = holiday.switch_turntake
        elif TOPIC_CONDITION == "dream":
            direct_turntake = dream.direct_turntake
            switch_turntake = dream.switch_turntake

        if mode == "direct":
            utterance = listtostr(random.choice(direct_turntake))
            current_trigger_source = "auto_test_e_direct"

            if last_speaker == "l":
                look_at_participant("left")
                time.sleep(0.3)
            elif last_speaker == "r":
                look_at_participant("right")
                time.sleep(0.3)

        else:
            utterance = listtostr(random.choice(switch_turntake))
            current_trigger_source = "auto_test_e_switch"

            other_side = get_other_side()
            if other_side in ("left", "right"):
                look_at_participant(other_side)
                time.sleep(0.3)

        robot_speak_and_wait(
            utterance,
            center_head=False,
            turn_hold_after_speech=1.0,
            allow_condition_b_reengage=False
        )

        forced_attention_until = datetime.now() + timedelta(seconds=2.0)
        return 4  

    # LEVEL 2: gaze only
    elif state9_count == 2:
        current_trigger_source = "auto_test_e_gaze_only"

        if head_position == "left":
            look_at_participant("right")
            time.sleep(0.3)

        elif head_position == "right":
            look_at_participant("left")
            time.sleep(0.3)

        elif head_position == "middle":
            if last_speaker == "l":
                look_at_participant("right")
            elif last_speaker == "r":
                look_at_participant("left")
            else:
                look_at_participant(random.choice(["left", "right"]))

            time.sleep(0.3)

        forced_attention_until = datetime.now() + timedelta(seconds=2.0)
        return 4  

    # LEVEL 3: ask to move on
    else:
        current_trigger_source = "auto_test_e_meta"

        utterance = random.choice([
            "Shall we move on to the next question?",
            "Would you like to continue to the next topic?",
            "Are you ready for the next question?"
        ])

        robot_speak_and_wait(
            utterance,
            center_head=True,
            turn_hold_after_speech=1.0,
            allow_condition_b_reengage=False
        )

        answer = input("(yes / no): ").strip().lower()

        state9_count = 0
        forced_attention_until = datetime.now() + timedelta(seconds=2.0)

        # Test F
        if answer == "yes":
            opt_list = get_topic_option_list(dialogstage)

            current_choice = ""
            if TOPIC_CONDITION == "holiday":
                if dialogstage == 1:
                    current_choice = holiday.CONTINENT[0]
                elif dialogstage == 2:
                    current_choice = holiday.CITY[0]
                elif dialogstage == 3:
                    current_choice = holiday.PERIOD[0]
                elif dialogstage == 4:
                    current_choice = holiday.DURATION[0]
                elif dialogstage == 5:
                    current_choice = holiday.HOLIDAYTYPE[0]
                elif dialogstage == 6:
                    current_choice = holiday.THINGSTODO[0]
                elif dialogstage == 7:
                    current_choice = holiday.ACCOMODATION[0]
                elif dialogstage == 8:
                    current_choice = holiday.MOBILITY[0]
                elif dialogstage == 9:
                    current_choice = holiday.BUDGET[0]

            elif TOPIC_CONDITION == "dream":
                if dialogstage == 1:
                    current_choice = dream.HOUSELOCATION[0]
                elif dialogstage == 2:
                    current_choice = dream.HOUSETYPE[0]
                elif dialogstage == 3:
                    current_choice = dream.HOUSESIZE[0]
                elif dialogstage == 4:
                    current_choice = dream.OUTSIDE_SPACE[0]
                elif dialogstage == 5:
                    current_choice = dream.HOUSESTYLE[0]
                elif dialogstage == 6:
                    current_choice = dream.INTERIORSTYLE[0]
                elif dialogstage == 7:
                    current_choice = dream.SUSTAINABILITY[0]
                elif dialogstage == 8:
                    current_choice = dream.NEIGHBORHOOD[0]
                elif dialogstage == 9:
                    current_choice = dream.HOUSEBUDGET[0]

            if not current_choice and opt_list:
                set_topic_choice(random.choice(opt_list))

            dialogstage += 1

            if dialogstage >= 10:
                if TOPIC_CONDITION == "holiday":
                    holiday.set_derived_holiday_details()
                elif TOPIC_CONDITION == "dream":
                    dream.set_derived_dream_house_details()
                dialogstage = 10

            return 10
        elif answer == "no":
            robot_speak_and_wait(
                "Okay, I will give some more information, so you can discuss further.",
                center_head=True,
                turn_hold_after_speech=1.0,
                allow_condition_b_reengage=False
            )

            return 6

# STATE 10 robot asks next question or finishes
##############################################################################
def state_10_question_utterance():
    global dialogstage, current_trigger_source, state9_count

    print(f"dialogstage is {dialogstage}")
    state9_count = 0

    # normal questions
    if 1 <= dialogstage <= 9:
        if TOPIC_CONDITION == "holiday":
            utterance = listtostr(holiday.build_holiday_question(dialogstage))
        elif TOPIC_CONDITION == "dream":
            utterance = listtostr(dream.build_dream_house_question(dialogstage))
        else:
            utterance = "I do not know which topic to ask about."

        robot_speak_and_wait(
            utterance,
            center_head=True
        )

        return 1 

    # ending
    elif dialogstage == 10:
        if TOPIC_CONDITION == "holiday":
            utterance = (
                f"Well that's about it. With all the information combined, you planned a holiday of {holiday.DURATION[0]} "
                f"to {holiday.CITY[0]} in {holiday.CONTINENT[0]} during the {holiday.PERIOD[0]}. "
                f"Once there you will have a typical {holiday.HOLIDAYTYPE[0]} vacation, primarily going to {holiday.THINGSTODO[0]}. "
                f"You will stay in a {holiday.ACCOMODATION[0]}. "
                f"To explore your surroundings you will mainly go by {holiday.MOBILITY[0]}, "
                f"and the estimated budget will be {holiday.BUDGET[0]}. "
                f"Thanks for participating in the first part of the experiment. Please fill in the questionnaire."
            )

        elif TOPIC_CONDITION == "dream":
            utterance = (
                f"Well that's about it. With all the information combined, your dream house will be located in {dream.HOUSELOCATION[0]}. "
                f"It will be {dream.HOUSETYPE[0]} with {dream.HOUSESIZE[0]}. "
                f"The outside space will include {dream.OUTSIDE_SPACE[0]}. "
                f"The overall style will be {dream.HOUSESTYLE[0]}, with an interior atmosphere of {dream.INTERIORSTYLE[0]}. "
                f"In terms of sustainability, you chose {dream.SUSTAINABILITY[0]}. "
                f"The house will be in {dream.NEIGHBORHOOD[0]}, and the budget level will be {dream.HOUSEBUDGET[0]}. "
                f"Thanks for participating. Please fill in the questionnaire."
            )

        else:
            utterance = "Thank you for participating."

        robot_speak_and_wait(
            utterance,
            center_head=True
        )

        return 12   

    print(f"Unexpected dialogstage={dialogstage}, chosen_options={chosen_options}")
    
    return 11      


# STATE 11 operator menu
##############################################################################
def state_11_operator():
    global NameP1, NameP2, last_speaker, chosen_options
    global forced_attention_until, current_trigger_source, dialogstage
    print("\n=== Operator menu ===")
    print("c = backchannel")
    print("i = info")
    print("v = verdict")
    print("q = next question")
    print("r = repeat")
    print("a = auto (resume)")
    print("d = direct turntake")
    print("s = switch turntake")
    print("m = stay in menu")

    key = msvcrt.getch().decode('ascii').lower()
    log_state_button(11, key)

    # backchannel
    if key == 'c':
        return 5

    # info
    if key == 'i':
        return 6

    # verdict
    if key == 'v':
        return 7

    # next question
    if key == 'q':
        skipped_stage = dialogstage
        dialogstage += 1

        # has to chose option when one question is skipped and participants dont get agreement
        if TOPIC_CONDITION == "holiday":

            if skipped_stage == 1 and not holiday.CONTINENT[0]:
                holiday.CONTINENT[0] = random.choice(holiday.continent)

            elif skipped_stage == 2 and not holiday.CITY[0]:
                if not holiday.CONTINENT[0]:
                    holiday.CONTINENT[0] = random.choice(holiday.continent)
                holiday.CITY[0] = random.choice(holiday.city[holiday.CONTINENT[0]])

            elif skipped_stage == 3 and not holiday.PERIOD[0]:
                holiday.PERIOD[0] = random.choice(holiday.travelperiod)

            elif skipped_stage == 4 and not holiday.DURATION[0]:
                holiday.DURATION[0] = random.choice(holiday.tripduration)

            elif skipped_stage == 5 and not holiday.HOLIDAYTYPE[0]:
                holiday.HOLIDAYTYPE[0] = random.choice(holiday.holidaytype)

            elif skipped_stage == 6 and not holiday.THINGSTODO[0]:
                if not holiday.HOLIDAYTYPE[0]:
                    holiday.HOLIDAYTYPE[0] = random.choice(holiday.holidaytype)
                holiday.THINGSTODO[0] = random.choice(
                    holiday.thingstodo[holiday.HOLIDAYTYPE[0]]
                )

            elif skipped_stage == 7 and not holiday.ACCOMODATION[0]:
                holiday.ACCOMODATION[0] = random.choice(holiday.accomodation)

            elif skipped_stage == 8 and not holiday.MOBILITY[0]:
                holiday.MOBILITY[0] = random.choice(holiday.mobility)

            elif skipped_stage == 9 and not holiday.BUDGET[0]:
                holiday.BUDGET[0] = random.choice(holiday.budget)

        elif TOPIC_CONDITION == "dream":

            if skipped_stage == 1 and not dream.HOUSELOCATION[0]:
                dream.HOUSELOCATION[0] = random.choice(dream.houselocation)

            elif skipped_stage == 2 and not dream.HOUSETYPE[0]:
                dream.HOUSETYPE[0] = random.choice(dream.housetype)

            elif skipped_stage == 3 and not dream.HOUSESIZE[0]:
                dream.HOUSESIZE[0] = random.choice(dream.housesize)

            elif skipped_stage == 4 and not dream.OUTSIDE_SPACE[0]:
                dream.OUTSIDE_SPACE[0] = random.choice(dream.outside_space)

            elif skipped_stage == 5 and not dream.HOUSESTYLE[0]:
                dream.HOUSESTYLE[0] = random.choice(dream.housestyle)

            elif skipped_stage == 6 and not dream.INTERIORSTYLE[0]:
                dream.INTERIORSTYLE[0] = random.choice(dream.interiorstyle)

            elif skipped_stage == 7 and not dream.SUSTAINABILITY[0]:
                dream.SUSTAINABILITY[0] = random.choice(dream.sustainability)

            elif skipped_stage == 8 and not dream.NEIGHBORHOOD[0]:
                dream.NEIGHBORHOOD[0] = random.choice(dream.neighborhood)

            elif skipped_stage == 9 and not dream.HOUSEBUDGET[0]:
                dream.HOUSEBUDGET[0] = random.choice(dream.housebudget)

        if dialogstage >= 10:
            dialogstage = 10

        return 10

    # repeat
    if key == 'r':
        return 8

    # automatic behavior
    if key == 'a':
        return 1

    # direct turn yield
    if key == 'd':
        current_trigger_source = "operator_d"
        idname = get_current_name()
        set_names(idname, NameP1, NameP2)
        holiday.RIGHTWRONG[0] = "right"

        utterance = listtostr(random.choice(holiday.direct_turntake))

        robot_speak_and_wait(
            utterance,
            center_head=False,
            turn_hold_after_speech=1.0,
            allow_condition_b_reengage=False
        )

        forced_attention_until = datetime.now() + timedelta(seconds=2.0)

        speech_detector.reset_timers()
        return 1

    # switch turn take
    if key == 's':
        current_trigger_source = "operator_s"
        idname = get_current_name()
        set_names(idname, NameP1, NameP2)

        holiday.OPT[0] = chosen_options[-1] if chosen_options else ""

        utterance = listtostr(random.choice(holiday.switch_turntake))

        other_side = get_other_side()
        print(f"last_speaker={last_speaker}, other_side={other_side}")

        if other_side in ("left", "right"):
            look_at_participant(other_side)
            time.sleep(0.3)
        else:
            print("other_side is middle, so no switch target found")

        robot_speak_and_wait(
            utterance,
            center_head=False,
            turn_hold_after_speech=1.0,
            allow_condition_b_reengage=False
        )

        forced_attention_until = datetime.now() + timedelta(seconds=2.0)

        speech_detector.reset_timers()
        return 1

 
    # menu
    if key == 'm':
        return 11

    return 11

# STATE 12 experiment finished
##############################################################################
def state_12_end():
    # stop speech/audio only if those methods exist
    if hasattr(misty, "stop_speaking"):
        try:
            misty.stop_speaking()
        except Exception:
            pass

    if hasattr(misty, "stop_audio"):
        try:
            misty.stop_audio()
        except Exception:
            pass

    if hasattr(misty, "stop"):
        try:
            misty.stop()
        except Exception:
            pass
    else:
        if hasattr(misty, "drive_stop"):
            try:
                misty.drive_stop()
            except Exception:
                pass

        try:
            misty.move_head(0, 0, 0, 90)
        except Exception:
            pass

    try:
        speech_detector.terminate()
    except Exception:
        pass

    if log_headpose:
        try:
            with open(LOG_DIR / "headpose_log.csv", "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=log_headpose[0].keys())
                writer.writeheader()
                writer.writerows(log_headpose)
        except Exception:
            pass

    print("Experiment finished")

    if ENABLE_FACE_TRACKING:
        tracking_model.STOP_TRACKING = True

    try:
        final_eye_contact_total = total_eye_contact_time
        if eye_contact_run_start is not None and last_logged_eye_contact_state:
            final_eye_contact_total += time.time() - eye_contact_run_start

        with open(SUMMARY_LOGFILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            writer.writerow(["turn_count_human_human", turn_count_human_human])
            writer.writerow(["turn_count_human_robot", turn_count_human_robot])
            writer.writerow(["turn_count_robot_human", turn_count_robot_human])
            writer.writerow(["turn_count_robot_robot", turn_count_robot_robot])
            writer.writerow(["total_eye_contact_time", round(final_eye_contact_total, 3)])
    except Exception as e:
        print(f"No summary log: {e}")

    return -1

def state_13_test_d_fallback():
    global state4_testd_count, current_trigger_source
    global forced_attention_until

    state4_testd_count += 1

    opt_list = get_topic_option_list()
    opt_value = random.choice(opt_list) if opt_list else ""

    if TOPIC_CONDITION == "holiday":
        holiday.OPT[0] = opt_value
        ttnone = holiday.TT_NoneFirstOPT
        switch = holiday.switch_turntake

    elif TOPIC_CONDITION == "dream":
        dream.OPT[0] = opt_value
        ttnone = dream.TT_NoneFirstOPT
        switch = dream.switch_turntake

    # LEVEL 1: first prompt about option
    if state4_testd_count == 1:
        holiday.RIGHTWRONG[0] = random.choice(["right", "wrong"])
        dream.RIGHTWRONG[0] = random.choice(["right", "wrong"])
        current_trigger_source = "auto_test_d_ttnonefirstopt"

        utterance = listtostr(random.choice(ttnone))

        robot_speak_and_wait(
            utterance,
            center_head=False,
            turn_hold_after_speech=1.5,
            allow_condition_b_reengage=False
        )

        forced_attention_until = datetime.now() + timedelta(seconds=1.0)
        return 4

    # LEVEL 2: switch turn
    elif state4_testd_count == 2:
        current_trigger_source = "auto_test_d_switch"

        idname = get_current_name()
        set_names(idname, NameP1, NameP2)

        other_side = get_other_side()
        if other_side in ("left", "right"):
            look_at_participant(other_side)
            time.sleep(0.3)

        utterance = listtostr(random.choice(switch))

        robot_speak_and_wait(
            utterance,
            center_head=False,
            turn_hold_after_speech=1.5,
            allow_condition_b_reengage=False
        )

        forced_attention_until = datetime.now() + timedelta(seconds=1.0)
        return 4

    # LEVEL 3: go to verdict
    else:
        current_trigger_source = "auto_test_d_verdict"
        state4_testd_count = 0
        return 7

##############################################################################
# State Handlers
##############################################################################
state_handlers = {
     0: state_0_init,
     1: state_1_wait_for_speech,
     2: state_2_motivate,
     3: state_3_turn_head_to_speaker,
     4: state_4_keep_looking_at_speaker,
     5: state_5_backchannel,
     6: state_6_info,
     7: state_7_verdict,
     8: state_8_repeat,
     9: state_9_fallback,
    10: state_10_question_utterance,
    11: state_11_operator,
    12: state_12_end,
    13: state_13_test_d_fallback,
}

##############################################################################
# MAIN LOOP 
##############################################################################
def main():
    state = 0
    print(f"Starting state machine (initial state={state})")
    while state != -1:
        print(f"Entering state {state}")
        handler = state_handlers.get(state)
        if handler is None:
            print("Unknown state:", state)
            break
        state = handler()


if __name__ == "__main__":
    main()