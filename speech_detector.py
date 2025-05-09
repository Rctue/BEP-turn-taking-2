# speech_detector.py
from Audio_sound_levels import AudioRecorder, list_devices
import time
import numpy as np

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
    """Detect who is speaking based on last duration seconds of RMS values."""
    global left_recorder, right_recorder, initialized

    if not initialized:
        print("Speech detection not initialized! Call setup_speech_detection() first.")
        return 's'

    try:
        # Tijdgrens
        now = time.time()
        cutoff = now - duration

        # Verzamel RMS-logdata uit beide recorders
        left_recent = [r for t, r in left_recorder.rms_log if t >= cutoff]
        right_recent = [r for t, r in right_recorder.rms_log if t >= cutoff]

        # Geen data?
        if not left_recent and not right_recent:
            return 's'

        # Maxwaarden per kanaal
        left_max = max(left_recent) if left_recent else 0
        right_max = max(right_recent) if right_recent else 0

        # Sprekers bepalen
        left_speaking = left_max > left_recorder.speech_threshold
        right_speaking = right_max > right_recorder.speech_threshold

        if left_speaking and right_speaking:
            return 'b'
        elif left_speaking:
            return 'l'
        elif right_speaking:
            return 'r'
        else:
            return 's'

    except Exception as e:
        print(f"Error in detect_speaker: {e}")
        return 's'


def get_silence_duration():
    """Get the current silence duration in seconds"""
    global left_recorder, right_recorder
    
    if not initialized:
        return 0
    
    # Return the maximum silence duration between both recorders
    return max(left_recorder.silence_duration, right_recorder.silence_duration)

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
