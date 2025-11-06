from datetime import datetime, timezone
from .timekeeper import Timekeeper

class StandardTimekeeper(Timekeeper):
    """
    Backup timekeeper.
    Falls back to simple UTC + Unix epoch if ISS is unavailable.
    """

    def get_timecodes(self) -> dict:
        now = datetime.now(timezone.utc)
        return {
            "stardate": None,
            "julian_date": None,
            "market_time": {
                "iso_8601": now.isoformat().replace("+00:00", "Z"),
                "unix_epoch": round(now.timestamp(), 6)
            }
        }
