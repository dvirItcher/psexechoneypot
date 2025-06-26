import os
import getpass
import socket
import platform
from datetime import datetime
import sys

LOG_PATH = "C:\\Windows\\psexec-trap.log"

def log_info():
    with open(LOG_PATH, "a") as f:
        f.write(f"Command-line args: {sys.argv}\n")
        f.write("="*40 + "\n")
        f.write(f"Time: {datetime.now()}\n")
        f.write(f"Hostname: {socket.gethostname()}\n")
        f.write(f"User running service: {getpass.getuser()}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write("Environment Variables:\n")
        for k, v in os.environ.items():
            f.write(f"{k} = {v}\n")
        f.write("="*40 + "\n\n")

if __name__ == "__main__":
    log_info()
    # Simulate service staying alive a bit
    import time
    time.sleep(30)
