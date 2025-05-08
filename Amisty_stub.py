# Amisty_stub.py

import time
try:
    import pyttsx3
    TTS = pyttsx3.init()
except ImportError:
    TTS = None          # no TTS available, stub will just print

class FakeMisty:
    def __init__(self, ip_address="0.0.0.0"):
        print(f"[FakeMisty] init (ip={ip_address})")

    def move_head(self, pitch, roll, yaw, velocity=90):
        print(f"[FakeMisty] move_head p={pitch} r={roll} y={yaw}")

    def display_image(self, fileName):
        print(f"[FakeMisty] display_image({fileName})")

    def speak(self, text):
        print(f"[FakeMisty] speak: {text}")
        if TTS:
            TTS.say(text)
            TTS.runAndWait()

    def stop_speaking(self): pass
    def stop_audio(self):    pass
    def stop(self):          pass

    def get_head_position(self):
        return {"result": {"pitch": -20, "yaw": 0, "roll": 0}}
