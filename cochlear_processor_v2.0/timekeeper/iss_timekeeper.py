from ISS.core.utils import current_timecodes
from .timekeeper import Timekeeper

class ISSTimekeeper(Timekeeper):
    """
    Primary timekeeper, powered by ISS.
    Provides 4D time anchors (stardate, julian, ISO, epoch).
    """

    def get_timecodes(self) -> dict:
        return current_timecodes()
