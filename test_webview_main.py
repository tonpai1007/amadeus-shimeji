import sys
sys.path.insert(0, 'C:\\amadeus-shimeji')

import webview
import time
import threading

# pywebview must run on main thread
win = None
def check_window():
    global win
    time.sleep(3)
    if win:
        print("Window exists, trying to evaluate JS...")
        try:
            result = win.evaluate_js('document.body.innerHTML.length')
            print("JS result:", result)
        except Exception as e:
            print("JS eval failed:", e)

t = threading.Thread(target=check_window, daemon=True)
t.start()

print("Creating window on main thread...")
win = webview.create_window('Test', 'https://www.example.com', width=400, height=300)
print("Window created, starting...")
webview.start()
print("Done")
