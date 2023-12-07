import sys
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"Restarting script due to change in: {event.src_path}")
            restart_script()

def restart_script():
    global process
    if process:
        process.terminate()
    process = subprocess.Popen([sys.executable, 'bot.py'])

if __name__ == "__main__":
    global process
    process = None

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    restart_script()  # Start the initial script

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
