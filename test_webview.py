import sys
sys.path.insert(0, 'C:\\amadeus-shimeji')

import webview
import threading
import time

def create_window():
    print("Creating window...")
    win = webview.create_window('Test', 'https://www.example.com', width=400, height=300)
    print("Window created, starting webview...")
    webview.start()
    print("Webview stopped")

t = threading.Thread(target=create_window, daemon=True)
t.start()
time.sleep(5)
print("Main thread exiting - window should be visible if it opened")
