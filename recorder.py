import pyaudio
import wave
import threading
import time
import os

class AudioRecorder:
    def __init__(self, output_folder="audio_clips"):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 3
        self.output_folder = output_folder
        self.p = pyaudio.PyAudio()
        self.lock = threading.Lock()
        self.current_thread = 1

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def record_audio(self, thread_id):
        while True:
            with self.lock:
                if self.current_thread != thread_id:
                    continue

            start_time = int(time.time() * 1000)
            filename = f"{self.output_folder}/{start_time}.wav"

            stream = self.p.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 input=True,
                                 frames_per_buffer=self.CHUNK)

            print(f"Thread {thread_id} started recording")
            frames = []

            for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = stream.read(self.CHUNK)
                frames.append(data)

            print(f"Thread {thread_id} finished recording")

            stream.stop_stream()
            stream.close()

            with self.lock:
                self.save_audio(frames, filename)
                self.current_thread = 2 if thread_id == 1 else 1

    def save_audio(self, frames, filename):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Saved audio clip: {filename}")

    def start_recording(self):
        thread1 = threading.Thread(target=self.record_audio, args=(1,))
        thread2 = threading.Thread(target=self.record_audio, args=(2,))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.start_recording()