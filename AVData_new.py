import sounddevice as sd
import numpy as np
import time
import csv

class AudioRecorder:
    def __init__(self, input_device, samplerate=44100, chunk_size=1024):
        self.input_device = input_device
        self.samplerate = samplerate
        self.chunk_size = chunk_size
        self.stream = None
        self.recording = False
        self.rms_data = []

    def calibrate(self):
        print(f"Calibrating device {self.input_device}... (speak for a few seconds)")
        self.start_recording()
        time.sleep(2)
        self.stop_recording()
        print("Calibration complete.\n")

    def start_recording(self):
        self.rms_data = []
        self.recording = True
        self.stream = sd.InputStream(device=self.input_device,
                                     channels=1,
                                     samplerate=self.samplerate,
                                     blocksize=self.chunk_size,
                                     callback=self._callback)
        self.stream.start()

    def stop_recording(self):
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def _callback(self, indata, frames, time_info, status):
        if self.recording:
            rms = float(np.sqrt(np.mean(indata**2)))
            timestamp = time.time()
            self.rms_data.append((timestamp, rms))

    def save_rms_data(self, filename):
        if not self.rms_data:
            print("Geen RMS-data om op te slaan.")
            return

        start_time = self.rms_data[0][0]

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp_unix', 'timestamp_readable', 'ms_since_start', 'rms'])
            for timestamp, rms in self.rms_data:
                t_local = time.localtime(timestamp)
                ms = int((timestamp % 1) * 1000)
                readable_time = time.strftime('%H:%M:%S', t_local) + f'.{ms:03d}'
                ms_since_start = round((timestamp - start_time) * 1000, 3)
                writer.writerow([
                    round(timestamp, 3),
                    readable_time,
                    f"{ms_since_start:.3f}",
                    f"{rms:.9f}"
                ])

                
                
############################################################################################## to test
if __name__ == "__main__":
    import sounddevice as sd

    # Toon beschikbare input devices
    print("Available input devices:")
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{idx}: {dev['name']} (Inputs: {dev['max_input_channels']})")

    # Laat gebruiker kiezen
    device_index = int(input("Kies het input device indexnummer dat je wilt testen: "))

    # Start opname
    rec = AudioRecorder(input_device=device_index)
    print("Opname gestart... (3 seconden)")
    rec.start_recording()
    time.sleep(3)
    rec.stop_recording()
    print("Opname gestopt.")

    # Sla op naar CSV
    rec.save_rms_data("test_rms_output.csv")
    print("CSV opgeslagen als test_rms_output.csv")
