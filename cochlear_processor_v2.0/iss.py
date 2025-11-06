# iss.py
"""
ISS Time Module – Interplanetary Stardate Synchrometer
Provides multi-format temporal anchors for vault and cognition modules.
"""

from datetime import datetime, timezone
import time

def get_stardate() -> dict:
    """
    Generate a standardized timestamp packet:
    - stardate: scaled epoch for compact symbolic reference
    - iso: ISO 8601 UTC timestamp
    - epoch: UNIX epoch seconds
    """
    epoch = time.time()
    stardate = round(epoch / 10000, 4)
    iso_time = datetime.now(timezone.utc).isoformat()
    return {
        "stardate": stardate,
        "iso": iso_time,
        "epoch": epoch
    }

if __name__ == "__main__":
    while True:
        print(get_stardate())
        time.sleep(5)
