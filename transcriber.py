import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AudioTranscriber:
    def __init__(self, api_key, watch_directory="audio_clips", transcription_directory="transcriptions"):
        self.groq = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        self.watch_directory = watch_directory
        self.transcription_directory = transcription_directory
        
        # Ensure transcription directory exists
        if not os.path.exists(self.transcription_directory):
            os.makedirs(self.transcription_directory)

    def transcribe_audio(self, audio_file_path):
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.groq.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file,
                    response_format="text",
                    language="sv"  # Specify Swedish language
                )
            return transcript
        except Exception as e:
            print(f"Error transcribing {audio_file_path}: {str(e)}")
            return None

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, transcriber):
        self.transcriber = transcriber

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.wav'):
            #print(f"New file detected: {event.src_path}")
            time.sleep(1)  # Small delay to ensure file is fully written
            transcript = self.transcriber.transcribe_audio(event.src_path)
            if transcript:
                #print(f"Transcript for {os.path.basename(event.src_path)}:")
                print(transcript)
                self.save_transcript(event.src_path, transcript)

    def save_transcript(self, audio_file_path, transcript):
        audio_filename = os.path.basename(audio_file_path)
        base_name = os.path.splitext(audio_filename)[0]
        transcript_file = os.path.join(self.transcriber.transcription_directory, f"{base_name}.txt")
        with open(transcript_file, 'w') as f:
            f.write(transcript)
            #print (transcript)
            #print(f"Transcript saved to {transcript_file}")

def main():
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY not found in .env file")
        return

    transcriber = AudioTranscriber(GROQ_API_KEY)
    event_handler = NewFileHandler(transcriber)
    observer = Observer()
    observer.schedule(event_handler, transcriber.watch_directory, recursive=False)
    observer.start()

    print(f"Monitoring folder: {transcriber.watch_directory}")
    print(f"Saving transcriptions to: {transcriber.transcription_directory}")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()