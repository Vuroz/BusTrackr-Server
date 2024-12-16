from bustrackr_server.routes import session_states
from threading import Timer, Lock
import os
from bustrackr_server.live_parser import process_live_data
from bustrackr_server import Config
import requests

curr_timer = None
timer_lock = Lock()

def do_fetch():
    global curr_timer

    # Ensure only one thread can modify the timer at a time
    with timer_lock:
        if curr_timer is not None:
            curr_timer.cancel()

        # Schedule the next fetch after 5 seconds
        curr_timer = Timer(2, do_fetch)
        curr_timer.daemon = True # If we quit we quit
        curr_timer.start()

    if len(session_states) == 0:
        return  # If we have no "active" users, no need to fetch realtime
    
    with requests.get(Config.API_URL) as response:
        process_live_data(response.text)
    