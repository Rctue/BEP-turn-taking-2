import time
import websocket
import json
from Misty_commands import Misty
import threading

# Define Misty's IP address
misty_ip_address = "192.168.0.100"

# Initialize Misty
misty = Misty(ip_address=misty_ip_address)

# Variable to track if Misty is speaking
is_speaking = True
utterance_id = "greeting_1"  # Unique ID for the specific utterance

# Define the WebSocket event handler
def on_message(ws, message):
    global is_speaking
    event_data = json.loads(message)
    # Check if the event is TextToSpeechComplete and matches the utterance ID
    if event_data.get("eventName") == "TextToSpeechComplete" and event_data.get("message", {}).get("UtteranceId") == utterance_id:
        is_speaking = False  # Set speaking to False when audio is complete
        ws.close()           # Close the WebSocket connection

# Start Misty speaking with the UtteranceId
misty.speak("Hello, I am Misty. I will pause the program until I am finished speaking.", UtteranceId=utterance_id)

# Setup WebSocket connection to Misty's event listener
ws = websocket.WebSocketApp(f"ws://{misty_ip_address}/pubsub", on_message=on_message)

# Start the WebSocket connection in a separate thread
ws_thread = threading.Thread(target=ws.run_forever)
ws_thread.start()

# Loop to keep the program paused while Misty is speaking
while is_speaking:
    time.sleep(0.1)  # Pause briefly before checking again

# Wait for WebSocket thread to finish before ending the program
ws_thread.join()
print("Misty has finished speaking. Program continues...")

