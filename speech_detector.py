# speech_detector.py
from Audio_sound_levels import AudioRecorder, list_devices
import time
import numpy as np

SPEECH_HOLD_BUFFER = 1.5 # seconds
MIN_SPEAK_TIME_TO_SWITCH = 0.5  # seconds — increase if needed

# ---------------------------------------------------------------------------
# Legacy stub — the old state‑machine calls this once during start‑up.
# Our current speech_detector calibrates its own thresholds, so we just ignore.
# ---------------------------------------------------------------------------
def set_thresholds(*args, **kwargs):
    pass


# Global variables to maintain state
left_recorder = None
right_recorder = None
initialized = False
last_active_side = 's'     # 'l', 'r', 'b', or 's'
last_active_time = 0.0     # time.time() of last detected speech
speaker_start_time = 0.0  # when did the current speaker start

def setup_speech_detection():
    """Set up and calibrate microphones for both participants"""
    global left_recorder, right_recorder, initialized
    
    if initialized:
        return True
    
    try:
        # List available devices
        dev_list = list_devices(False)
        print("Available input devices:")
        for dev in dev_list:
            if dev['maxInputChannels'] > 0 and dev['defaultSampleRate'] == 44100:
                print(dev['index'], dev['name'], 'Inputs:', dev['maxInputChannels'])
        
        # Get device indices
        left_mic = int(input("Choose input device for left participant: "))
        right_mic = int(input("Choose input device for right participant: "))
        
        # Create recorders
        left_recorder = AudioRecorder(input_device=left_mic, verbose=False)
        right_recorder = AudioRecorder(input_device=right_mic, verbose=False)
        
        # Calibrate
        print("Calibrating microphones...")
        print("We'll calibrate the left participant's microphone first.")
        left_recorder.calibrate()
        print("Now we'll calibrate the right participant's microphone.")
        right_recorder.calibrate()
        
        initialized = True
        return True
    except Exception as e:
        print(f"Error setting up speech detection: {e}")
        return False

def detect_speaker(duration=1.0):
    """Detect who is speaking, but retain last speaker during brief silences or interruptions."""
    global left_recorder, right_recorder, initialized
    global last_active_side, last_active_time, speaker_start_time

    if not initialized:
        print("Speech detection not initialized! Call setup_speech_detection() first.")
        return 's'

    try:
        now = time.time()
        cutoff = now - duration

        # Recent RMS values
        left_recent = [r for t, r in left_recorder.rms_log if t >= cutoff]
        right_recent = [r for t, r in right_recorder.rms_log if t >= cutoff]

        left_max = max(left_recent) if left_recent else 0
        right_max = max(right_recent) if right_recent else 0

        DOMINANCE_RATIO = 1.5 

        left_spk = left_max > left_recorder.speech_threshold
        right_spk = right_max > right_recorder.speech_threshold

        if left_spk and right_spk:
            if left_max > right_max * DOMINANCE_RATIO:
                speaker = 'l'
            elif right_max > left_max * DOMINANCE_RATIO:
                speaker = 'r'
            else:
                speaker = 'b'  # true overlap
        elif left_spk:
            speaker = 'l'
        elif right_spk:
            speaker = 'r'
        else:
            speaker = 's'

        # Buffer logic: hold speaker during short silences
        if speaker != 's':
            if speaker != last_active_side:
                speaker_start_time = now  # reset timer for new speaker
            last_active_side = speaker
            last_active_time = now
        else:
            if now - last_active_time <= SPEECH_HOLD_BUFFER:
                speaker = last_active_side  # Hold previous speaker

        # Optional: Filter out ultra short speech blips
        if speaker != 's' and now - speaker_start_time < MIN_SPEAK_TIME_TO_SWITCH:
            speaker = last_active_side  # Ignore if too short

        return speaker

    except Exception as e:
        print(f"Error in detect_speaker: {e}")
        return 's'

def get_silence_duration():
    """Return silence duration, subtracting buffer to prevent premature triggers."""
    global left_recorder, right_recorder, initialized
    if not initialized:
        return 0.0

    raw = min(left_recorder.silence_duration,
              right_recorder.silence_duration)

    return max(0.0, raw - SPEECH_HOLD_BUFFER)

def get_speaking_duration():
    """Get the current speaking duration in seconds"""
    global left_recorder, right_recorder
    
    if not initialized:
        return 0
    
    # Return the maximum speaking duration between both recorders
    return max(left_recorder.speaking_duration, right_recorder.speaking_duration)

def get_speech_stats():
    """Get current speech statistics"""
    global left_recorder, right_recorder
    
    if not initialized:
        return None
    
    # Return speech stats from both recorders
    return {
        "left": {
            "speech_threshold": left_recorder.speech_threshold,
            "silence_threshold": left_recorder.silence_threshold,
            "speaking_duration": left_recorder.speaking_duration,
            "silence_duration": left_recorder.silence_duration,
            "total_speaking_duration": left_recorder.total_speaking_duration,
            "total_silence_duration": left_recorder.total_silence_duration
        },
        "right": {
            "speech_threshold": right_recorder.speech_threshold,
            "silence_threshold": right_recorder.silence_threshold,
            "speaking_duration": right_recorder.speaking_duration,
            "silence_duration": right_recorder.silence_duration,
            "total_speaking_duration": right_recorder.total_speaking_duration,
            "total_silence_duration": right_recorder.total_silence_duration
        }
    }

def terminate():
    """Clean up audio resources"""
    global left_recorder, right_recorder, initialized
    
    if initialized:
        if left_recorder:
            left_recorder.terminate()
        if right_recorder:
            right_recorder.terminate()
        initialized = False
        

def reset_timers():
    """Reset zowel stilte- als spreek­duur terug naar 0."""
    global left_recorder, right_recorder, initialized
    if initialized:
        left_recorder.silence_duration = 0
        left_recorder.speaking_duration = 0
        right_recorder.silence_duration = 0
        right_recorder.speaking_duration = 0
        
        
        
import time

#def get_silence_duration(window=2.0):
#    now = time.time()
#    all_rms = left_recorder.rms_log + right_recorder.rms_log
#    recent_rms = [r for t, r in all_rms if now - t <= window]
#    speaking = [r for r in recent_rms if r > left_recorder.speech_threshold * 0.7]  # 0.7 = marge

#   if not speaking:
#        return window
#    return 0.0



#def get_speaking_duration(window=2.0):
#    now = time.time()
#    all_rms = left_recorder.rms_log + right_recorder.rms_log
#    recent_rms = [r for t, r in all_rms if now - t <= window]
#    speaking = [r for r in recent_rms if r > left_recorder.speech_threshold * 0.7]

#    if not recent_rms:
#        return 0.0
#    return len(speaking) / len(recent_rms) * window

def get_speaking_duration_by_side(side='l'):
    """Get the speaking duration for a specific side ('l' or 'r')"""
    global left_recorder, right_recorder
    if not initialized:
        return 0.0
    if side == 'l':
        return left_recorder.speaking_duration
    elif side == 'r':
        return right_recorder.speaking_duration
    else:
        return 0.0