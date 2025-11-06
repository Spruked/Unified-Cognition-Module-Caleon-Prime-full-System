# core/ISS.py
import logging
from .utils import (
    get_stardate,
    current_timecodes,
    ensure_folder,
)
from ..captain_mode.exporters import Exporters
from ..captain_mode.captain_log import CaptainLog


class ISS:
    """
    Interplanetary Stardate Synchrometer (ISS)
    -----------------------------------------
    Core orchestrator for time anchoring, captain's logs, 
    and module management. Designed for plug-and-play use 
    with Caleon and CertSig systems.
    """

    def __init__(self, system_name: str = "ISS"):
        self.system_name = system_name
        self.status = "healthy"
        self.modules = {}        # dynamically loaded modules
        self.logs = []           # local storage for logs
        self.log_folder = ensure_folder("logs")
        self.captain_log = CaptainLog()
        logging.basicConfig(level=logging.INFO)

    # ----------------------
    # Health / Heartbeat
    # ----------------------
    def heartbeat(self) -> bool:
        """
        Check system health and all loaded modules.
        """
        healthy = self.status == "healthy"
        for name, module in self.modules.items():
            hb = getattr(module, "heartbeat", None)
            if callable(hb):
                if not hb():
                    logging.warning(f"⚠️ Module {name} unhealthy")
                    healthy = False
        return healthy
