import time
import os
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def clear_terminal():
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

class Translator:
    def __init__(self, api_key, target_language, watch_directory="transcriptions", translation_directory="translations"):
        self.client = OpenAI(api_key=api_key)
        self.target_language = target_language
        self.watch_directory = watch_directory
        self.translation_directory = translation_directory
        self.message_history = [
            {"role": "system", "content": f"You are a professional translator. Treat the full history as a single text. Adjust the punctuation and paragraphs to make the text naturally flowing. Translate the full message history to {target_language}. Maintain the original meaning and tone as closely as possible. Always reply with the full message history translation."}
        ]
        
        # Ensure translation directory exists
        if not os.path.exists(self.translation_directory):
            os.makedirs(self.translation_directory)

    def translate_text(self, text):
        self.message_history.append({"role": "user", "content": f"{text}"})
        model = "gpt-4o-mini"
        try:
            chat_completion = self.client.chat.completions.create(
                model=model, 
                messages=self.message_history,
                temperature=0.7
            )
            
            reply = chat_completion.choices[0].message.content
            
            # Keep the message history to a reasonable size
            if len(self.message_history) > 10:
                self.message_history = self.message_history[:1] + self.message_history[-9:]
            
            return reply
        except Exception as e:
            print(f"Error in translation: {str(e)}")
            return None

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, translator):
        self.translator = translator

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            time.sleep(0.1)  # Small delay to ensure file is fully written
            self.translate_file(event.src_path)

    def translate_file(self, file_path):
        with open(file_path, 'r') as f:
            text = f.read()
        
        translation = self.translator.translate_text(text)
        if translation:
            self.save_translation(file_path, translation)

    def save_translation(self, original_file_path, translation):
        filename = os.path.basename(original_file_path)
        base_name = os.path.splitext(filename)[0]
        translation_file = os.path.join(self.translator.translation_directory, f"{base_name}_{self.translator.target_language}.txt")
        with open(translation_file, 'w') as f:
            f.write(translation)
        clear_terminal()
        print(translation)

def main():
    parser = argparse.ArgumentParser(description="Translate text files to a specified language.")
    parser.add_argument("target_language", help="The language to translate the text into")
    args = parser.parse_args()

    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found in .env file")
        return

    translator = Translator(OPENAI_API_KEY, args.target_language)
    event_handler = NewFileHandler(translator)
    observer = Observer()
    observer.schedule(event_handler, translator.watch_directory, recursive=False)
    observer.start()

    print(f"Monitoring folder: {translator.watch_directory}")
    print(f"Translating to: {translator.target_language}")
    print(f"Saving translations to: {translator.translation_directory}")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()