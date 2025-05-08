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
    """Detect which participant is speaking
    Returns: 'l' for left, 'r' for right, 's' for silence, 'b' for both
    """
    global left_recorder, right_recorder, initialized
    
    if not initialized:
        print("Speech detection not initialized! Call setup_speech_detection() first.")
        return 's'
    
    try:
        # Start recordings
        left_recorder.start_recording()
        right_recorder.start_recording()
        
        # Record for the specified duration
        time.sleep(duration)
        
        # Stop recordings
        left_recorder.stop_recording()
        right_recorder.stop_recording()
        
        # Calculate statistics for more robust detection
        left_rms = np.array(left_recorder.rms_data)
        right_rms = np.array(right_recorder.rms_data)
        
        # Use median and max values for more stable detection
        left_max = np.max(left_rms) if len(left_rms) > 0 else 0
        right_max = np.max(right_rms) if len(right_rms) > 0 else 0
        
        # Check if either participant is above speech threshold
        left_speaking = left_max > left_recorder.speech_threshold
        right_speaking = right_max > right_recorder.speech_threshold
        
        # Return appropriate code
        if left_speaking and right_speaking:
            # If both are speaking, check who's louder
            if left_max > right_max * 1.5:  # Left is significantly louder
                return 'l'
            elif right_max > left_max * 1.5:  # Right is significantly louder
                return 'r'
            else:
                return 'b'  # Both speaking roughly equally
        elif left_speaking:
            return 'l'  # Left speaking
        elif right_speaking:
            return 'r'  # Right speaking
        else:
            return 's'  # Silence
    except Exception as e:
        print(f"Error detecting speaker: {e}")
        return 's'  # Default to silence on error

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
