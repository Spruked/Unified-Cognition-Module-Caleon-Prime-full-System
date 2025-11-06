"""
Exporters
=========
Universal export layer for ISS modules.

Provides:
- CSV export (UTF-8 safe)
- JSON export (pretty printed)
- Markdown export (GitHub-flavored table)

Used by:
- CaptainLog for persistence and snapshots
- ISS module for diagnostics export
- CertSig to serialize NFT metadata
- VisiDataWrapper for data analysis
"""

import csv
import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .captain_log import LogEntry, CaptainLog


# Legacy DataExporter class for backwards compatibility
class DataExporter:
    """
    Legacy data export manager for ISS Module
    Maintained for backwards compatibility
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or self._get_default_output_dir()
        self.logger = logging.getLogger('ISS.DataExporter')
        self._ensure_output_dir()
    
    def _get_default_output_dir(self) -> str:
        """Get default output directory"""
        base_dir = Path(__file__).parent.parent
        output_dir = base_dir / 'data' / 'exports'
        return str(output_dir)
    
    def _ensure_output_dir(self):
        """Ensure output directory exists"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def export_log_entries_json(
        self,
        entries: List[LogEntry],
        filename: Optional[str] = None,
        include_metadata: bool = True
    ) -> str:
        """Export log entries to JSON format"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'captain_log_export_{timestamp}.json'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert to dict format
        data = [entry.to_dict() for entry in entries]
        
        # Use new Exporters class
        success = Exporters.to_json(data, filepath)
        
        if success:
            return filepath
        else:
            raise Exception("Failed to export JSON")
    
    async def export_log_entries_csv(
        self,
        entries: List[LogEntry],
        filename: Optional[str] = None,
        include_content: bool = True
    ) -> str:
        """Export log entries to CSV format"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'captain_log_export_{timestamp}.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert to dict format
        data = [entry.to_dict() for entry in entries]
        
        # Use new Exporters class
        success = Exporters.to_csv(data, filepath)
        
        if success:
            return filepath
        else:
            raise Exception("Failed to export CSV")
    
    async def export_log_entries_markdown(
        self,
        entries: List[LogEntry],
        filename: Optional[str] = None,
        include_toc: bool = True
    ) -> str:
        """Export log entries to Markdown format"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'captain_log_export_{timestamp}.md'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert to dict format
        data = [entry.to_dict() for entry in entries]
        
        # Use new Exporters class
        success = Exporters.to_markdown(data, filepath)
        
        if success:
            return filepath
        else:
            raise Exception("Failed to export Markdown")
    """
    Data export manager for ISS Module
    
    Handles exporting data in various formats (JSON, CSV, Markdown)
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or self._get_default_output_dir()
        self.logger = logging.getLogger('ISS.DataExporter')
        self._ensure_output_dir()
    
    def _get_default_output_dir(self) -> str:
        """Get default output directory"""
        base_dir = Path(__file__).parent.parent
        output_dir = base_dir / 'data' / 'exports'
        return str(output_dir)
    
    def _ensure_output_dir(self):
        """Ensure output directory exists"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def export_log_entries_json(
        self,
        entries: List[LogEntry],
        filename: Optional[str] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export log entries to JSON format
        
        Args:
            entries: List of LogEntry objects to export
            filename: Output filename (auto-generated if None)
            include_metadata: Whether to include export metadata
        
        Returns:
            Path to the exported file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'captain_log_export_{timestamp}.json'
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Prepare data
            export_data = {
                'entries': [entry.to_dict() for entry in entries]
            }
            
            if include_metadata:
                export_data['metadata'] = {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_entries': len(entries),
                    'exporter': 'ISS Module Data Exporter v1.0',
                    'format_version': '1.0'
                }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(entries)} entries to JSON: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {e}")
            raise
    
    async def export_log_entries_csv(
        self,
        entries: List[LogEntry],
        filename: Optional[str] = None,
        include_content: bool = True
    ) -> str:
        """
        Export log entries to CSV format
        
        Args:
            entries: List of LogEntry objects to export
            filename: Output filename (auto-generated if None)
            include_content: Whether to include full content (may be large)
        
        Returns:
            Path to the exported file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'captain_log_export_{timestamp}.csv'
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Define fieldnames
            fieldnames = ['id', 'timestamp', 'stardate', 'category', 'tags', 'mood', 'location']
            if include_content:
                fieldnames.insert(3, 'content')
            
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in entries:
                    row = {
                        'id': entry.id,
                        'timestamp': entry.timestamp,
                        'stardate': entry.stardate,
                        'category': entry.category,
                        'tags': ', '.join(entry.tags) if entry.tags else '',
                        'mood': entry.mood or '',
                        'location': entry.location or ''
                    }
                    
                    if include_content:
                        # Sanitize content for CSV (remove newlines, limit length)
                        content = entry.content.replace('\n', ' ').replace('\r', '')
                        if len(content) > 500:
                            content = content[:497] + '...'
                        row['content'] = content
                    
                    writer.writerow(row)
            
            self.logger.info(f"Exported {len(entries)} entries to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to export to CSV: {e}")
            raise
    
    async def export_log_entries_markdown(
        self,
        entries: List[LogEntry],
        filename: Optional[str] = None,
        include_toc: bool = True
    ) -> str:
        """
        Export log entries to Markdown format
        
        Args:
            entries: List of LogEntry objects to export
            filename: Output filename (auto-generated if None)
            include_toc: Whether to include table of contents
        
        Returns:
            Path to the exported file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'captain_log_export_{timestamp}.md'
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Generate markdown content
            content_lines = []
            
            # Header
            content_lines.append("# Captain's Log Export")
            content_lines.append("")
            content_lines.append(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            content_lines.append(f"**Total Entries:** {len(entries)}")
            content_lines.append("")
            
            # Table of Contents
            if include_toc and entries:
                content_lines.append("## Table of Contents")
                content_lines.append("")
                
                for i, entry in enumerate(entries, 1):
                    # Create sanitized anchor link
                    anchor = entry.id.lower().replace(' ', '-')
                    title = entry.content[:50].replace('\n', ' ').strip()
                    if len(entry.content) > 50:
                        title += "..."
                    
                    content_lines.append(f"{i}. [{title}](#{anchor}) - {entry.category}")
                
                content_lines.append("")
                content_lines.append("---")
                content_lines.append("")
            
            # Entries
            content_lines.append("## Log Entries")
            content_lines.append("")
            
            for entry in entries:
                # Entry header
                content_lines.append(f"### Entry {entry.id}")
                content_lines.append("")
                
                # Metadata table
                content_lines.append("| Field | Value |")
                content_lines.append("|-------|-------|")
                content_lines.append(f"| **Stardate** | {entry.stardate} |")
                content_lines.append(f"| **Timestamp** | {entry.timestamp} |")
                content_lines.append(f"| **Category** | {entry.category} |")
                
                if entry.tags:
                    tags_str = ", ".join([f"`{tag}`" for tag in entry.tags])
                    content_lines.append(f"| **Tags** | {tags_str} |")
                
                if entry.mood:
                    content_lines.append(f"| **Mood** | {entry.mood} |")
                
                if entry.location:
                    content_lines.append(f"| **Location** | {entry.location} |")
                
                content_lines.append("")
                
                # Content
                content_lines.append("#### Content")
                content_lines.append("")
                
                # Format content (preserve paragraphs, escape markdown)
                content = entry.content.replace('*', '\\*').replace('_', '\\_').replace('#', '\\#')
                content_lines.append(content)
                content_lines.append("")
                content_lines.append("---")
                content_lines.append("")
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content_lines))
            
            self.logger.info(f"Exported {len(entries)} entries to Markdown: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to export to Markdown: {e}")
            raise
    
    async def export_statistics_json(
        self,
        captain_log: CaptainLog,
        filename: Optional[str] = None
    ) -> str:
        """
        Export log statistics to JSON
        
        Args:
            captain_log: CaptainLog instance to get statistics from
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to the exported file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'captain_log_statistics_{timestamp}.json'
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Get statistics
            stats = await captain_log.get_statistics()
            
            # Add export metadata
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'exporter': 'ISS Module Data Exporter v1.0'
                },
                'statistics': stats
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported statistics to JSON: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to export statistics: {e}")
            raise
    
    async def create_backup(
        self,
        captain_log: CaptainLog,
        include_statistics: bool = True
    ) -> str:
        """
        Create a complete backup of captain's log data
        
        Args:
            captain_log: CaptainLog instance to backup
            include_statistics: Whether to include statistics file
        
        Returns:
            Path to the backup directory
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(self.output_dir, f'backup_{timestamp}')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Get all entries
            all_entries = await captain_log.get_entries()
            
            # Export in all formats
            json_file = await self.export_log_entries_json(
                all_entries,
                filename=os.path.join(backup_dir, 'captain_log_backup.json')
            )
            
            csv_file = await self.export_log_entries_csv(
                all_entries,
                filename=os.path.join(backup_dir, 'captain_log_backup.csv')
            )
            
            md_file = await self.export_log_entries_markdown(
                all_entries,
                filename=os.path.join(backup_dir, 'captain_log_backup.md')
            )
            
            if include_statistics:
                stats_file = await self.export_statistics_json(
                    captain_log,
                    filename=os.path.join(backup_dir, 'statistics.json')
                )
            
            # Create backup manifest
            manifest = {
                'backup_timestamp': datetime.now().isoformat(),
                'total_entries': len(all_entries),
                'files': {
                    'json': 'captain_log_backup.json',
                    'csv': 'captain_log_backup.csv',
                    'markdown': 'captain_log_backup.md'
                }
            }
            
            if include_statistics:
                manifest['files']['statistics'] = 'statistics.json'
            
            manifest_file = os.path.join(backup_dir, 'manifest.json')
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            self.logger.info(f"Created complete backup at: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise
    
    def list_exports(self) -> List[Dict[str, Any]]:
        """List all export files in the output directory"""
        try:
            exports = []
            
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    exports.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return sorted(exports, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Failed to list exports: {e}")
            return []


# Convenient static class for easy usage
class Exporters:
    """
    Convenient static methods for data export
    
    Usage:
        from iss_module.captain_mode.exporters import Exporters
        Exporters.to_json(entries, "logs.json")
        Exporters.to_csv(entries, "logs.csv")
        Exporters.to_markdown(entries, "logs.md")
    """
    
    @staticmethod
    def to_json_sync(entries: List[Dict[str, Any]], filepath: str) -> str:
        """Export entries to JSON file (synchronous)"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'count': len(entries),
                    'entries': entries
                }, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            raise
    
    @staticmethod
    def to_csv_sync(entries: List[Dict[str, Any]], filepath: str) -> str:
        """Export entries to CSV file (synchronous)"""
        try:
            if not entries:
                raise ValueError("No entries to export")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Get all possible fieldnames
            fieldnames = set()
            for entry in entries:
                fieldnames.update(entry.keys())
            fieldnames = list(fieldnames)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(entries)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            raise
    
    @staticmethod
    def to_markdown_sync(entries: List[Dict[str, Any]], filepath: str) -> str:
        """Export entries to Markdown file (synchronous)"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# Captain's Log Export\n\n")
                f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Total Entries:** {len(entries)}\n\n")
                
                for entry in entries:
                    f.write(f"## {entry.get('stardate', 'Unknown Stardate')}\n\n")
                    f.write(f"**Date:** {entry.get('timestamp', 'Unknown')}\n\n")
                    f.write(f"**Category:** {entry.get('category', 'General')}\n\n")
                    
                    if entry.get('tags'):
                        f.write(f"**Tags:** {', '.join(entry.get('tags', []))}\n\n")
                    
                    content = entry.get('content', '')
                    f.write(f"{content}\n\n")
                    f.write("---\n\n")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export to Markdown: {e}")
            raise
    
    @staticmethod
    async def to_json(entries: List[LogEntry], filepath: str, include_metadata: bool = True) -> str:
        """Export entries to JSON file"""
        exporter = DataExporter(output_dir=os.path.dirname(filepath))
        return await exporter.export_log_entries_json(
            entries, 
            filename=os.path.basename(filepath),
            include_metadata=include_metadata
        )
    
    @staticmethod
    async def to_csv(entries: List[LogEntry], filepath: str, include_content: bool = True) -> str:
        """Export entries to CSV file"""
        exporter = DataExporter(output_dir=os.path.dirname(filepath))
        return await exporter.export_log_entries_csv(
            entries,
            filename=os.path.basename(filepath), 
            include_content=include_content
        )
    
    @staticmethod
    async def to_markdown(entries: List[LogEntry], filepath: str, include_toc: bool = True) -> str:
        """Export entries to Markdown file"""
        exporter = DataExporter(output_dir=os.path.dirname(filepath))
        return await exporter.export_log_entries_markdown(
            entries,
            filename=os.path.basename(filepath),
            include_toc=include_toc
        )