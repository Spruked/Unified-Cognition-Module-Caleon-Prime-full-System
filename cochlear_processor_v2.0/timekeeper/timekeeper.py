class Timekeeper:
    """
    Interface for pluggable time sources.
    Any timekeeper must implement get_timecodes().
    """

    def get_timecodes(self) -> dict:
        raise NotImplementedError("Timekeeper must implement get_timecodes()")
