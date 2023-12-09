import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pyttsx3

class MyHandler(FileSystemEventHandler):
    def __init__(self, filename):
        self.filename = filename
        self.last_word = ''

    def on_modified(self, event):
        if event.src_path == self.filename:
            with open(self.filename, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line != self.last_word:
                        self.last_word = last_line
                        self.speak(self.last_word)

    @staticmethod
    def speak(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

if __name__ == "__main__":
    path = "C:\\Users\\harry\\OneDrive\\Desktop\\Code"
    file_to_watch = "C:\\Users\\harry\\OneDrive\\Desktop\\Code\\prompt.txt"

    event_handler = MyHandler(file_to_watch)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
