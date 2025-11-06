"""
VisiDataWrapper
================
Optional module that allows ISS/Caleon to:
- Export logs/data to CSV
- Automatically open that data in VisiData (TUI)

Works as a bridge between:
- CaptainLog entries
- VisiData (via CLI)
- Data analysts, debuggers, admins

Requirements:
- VisiData installed and in $PATH
- UNIX shell or equivalent subprocess compatibility
"""

import subprocess
import logging
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.utils import ensure_folder
from .exporters import Exporters
from .captain_log import LogEntry, CaptainLog


class VisiDataWrapper:
    """
    VisiData integration wrapper for ISS Module
    """

    def __init__(self, export_folder: str = "vd_exports") -> None:
        self.export_folder = ensure_folder(export_folder)
        self.logger = logging.getLogger('ISS.VisiDataWrapper')

    def _check_visidata_available(self) -> bool:
        """Check if VisiData is available in the system"""
        try:
            result = subprocess.run(
                ['vd', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = "vd_export.csv") -> Path | None:
        """
        Export data to CSV for VisiData viewing.
        Returns path or None on failure.
        """
        file_path = Path(self.export_folder) / filename
        success = Exporters.to_csv(data, str(file_path))
        return file_path if success else None

    def export_to_json(self, data: List[Dict[str, Any]], filename: str = "vd_export.json") -> Path | None:
        """Export data to JSON for VisiData viewing"""
        file_path = Path(self.export_folder) / filename
        success = Exporters.to_json(data, str(file_path))
        return file_path if success else None

    def open_in_visidata(self, file_path: Path) -> bool:
        """
        Launch VisiData on the provided file.
        """
        try:
            self.logger.info(f"📊 Opening VisiData with {file_path}")
            subprocess.run(["vd", str(file_path)])
            return True
        except FileNotFoundError:
            self.logger.error("❌ VisiData not installed or not found in PATH")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to launch VisiData: {e}")
            return False

    def export_and_open(self, data: List[Dict[str, Any]], csv_filename: str = "vd_export.csv") -> bool:
        """
        Combined method: export to CSV then open in VisiData.
        """
        csv_path = self.export_to_csv(data, csv_filename)
        if csv_path:
            return self.open_in_visidata(csv_path)
        return False

    # Legacy methods for backwards compatibility
    async def view_log_entries(
        self,
        entries: List[LogEntry],
        format_type: str = 'csv',
        launch_immediately: bool = True
    ) -> str:
        """
        Legacy method: View log entries in VisiData
        """
        try:
            if not self._check_visidata_available():
                raise RuntimeError("VisiData is not available. Please install with: pip install visidata")
            
            # Convert LogEntry objects to dictionaries
            data = [entry.to_dict() for entry in entries]
            
            if format_type == 'csv':
                filepath = self.export_to_csv(data, 'vd_log_entries.csv')
            elif format_type == 'json':
                filepath = self.export_to_json(data, 'vd_log_entries.json')
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            if filepath and launch_immediately:
                self.open_in_visidata(filepath)
            
            self.logger.info(f"Prepared {len(entries)} entries for VisiData viewing")
            return str(filepath) if filepath else ""
            
        except Exception as e:
            self.logger.error(f"Failed to view entries in VisiData: {e}")
            raise

    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            import os
            if os.path.exists(self.export_folder):
                shutil.rmtree(self.export_folder)
            self.logger.info("Cleaned up temporary VisiData files")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp files: {e}")

    def __del__(self):
        """Ensure cleanup on object destruction"""
        # Don't auto-cleanup the export folder as user might want to keep files
        pass