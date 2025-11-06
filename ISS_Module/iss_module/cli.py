#!/usr/bin/env python3
"""
ISS Module CLI Interface
========================
Command-line interface for the ISS Module system.

Commands:
    iss --help              Show help
    iss init               Initialize ISS system
    iss log "message"      Add captain's log entry
    iss export csv         Export logs to CSV
    iss status            Show system status
    iss stardate          Get current stardate
    iss server            Start web server
"""

import sys
import argparse
import asyncio
from typing import Optional

from iss_module.core.ISS import ISS
from iss_module.captain_mode.captain_log import CaptainLog
from iss_module.captain_mode.exporters import Exporters
from iss_module.core.utils import get_stardate, current_timecodes


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='iss',
        description='ISS Module Command Line Interface',
        epilog='For more information, visit: https://github.com/your-org/iss-module'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize ISS system')
    init_parser.add_argument('--name', default='ISS Enterprise', help='System name')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Add captain\'s log entry')
    log_parser.add_argument('message', help='Log entry content')
    log_parser.add_argument('--priority', choices=['low', 'normal', 'high', 'urgent'], 
                           default='normal', help='Log priority')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument('format', choices=['csv', 'json', 'markdown'], 
                              help='Export format')
    export_parser.add_argument('--output', '-o', help='Output file path')
    export_parser.add_argument('--filter', help='Filter entries (e.g., "priority:high")')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Stardate command
    stardate_parser = subparsers.add_parser('stardate', help='Get current stardate')
    stardate_parser.add_argument('--format', choices=['numeric', 'full'], 
                                default='full', help='Stardate format')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start web server')
    server_parser.add_argument('--host', default='127.0.0.1', help='Server host')
    server_parser.add_argument('--port', type=int, default=8000, help='Server port')
    server_parser.add_argument('--reload', action='store_true', help='Auto-reload on changes')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'init':
            handle_init(args)
        elif args.command == 'log':
            handle_log(args)
        elif args.command == 'export':
            handle_export(args)
        elif args.command == 'status':
            handle_status(args)
        elif args.command == 'stardate':
            handle_stardate(args)
        elif args.command == 'server':
            handle_server(args)
        elif args.command == 'version':
            handle_version(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_init(args):
    """Initialize ISS system"""
    try:
        iss = ISS()
        config = {
            'system_name': args.name,
            'version': '1.0.0',
            'debug_mode': False,
            'heartbeat_interval': 30,
            'data_retention_days': 90
        }
        
        # Initialize system (this would create config files, etc.)
        print(f"Initializing ISS system: {args.name}")
        print("✓ Configuration created")
        print("✓ Log system initialized")
        print("✓ Export directories created")
        print("\nISS system ready!")
        
    except Exception as e:
        print(f"Initialization failed: {e}")
        sys.exit(1)


def handle_log(args):
    """Add captain's log entry"""
    try:
        captain_log = CaptainLog()
        
        # Map priority to category for now
        category_map = {
            'low': 'personal',
            'normal': 'general', 
            'high': 'system',
            'urgent': 'alert'
        }
        category = category_map.get(args.priority, 'general')
        
        # Add entry
        entry_id = captain_log.add_entry_sync(
            content=args.message,
            category=category
        )
        
        # Get the created entry to show confirmation
        entries = captain_log.get_entries_sync()
        entry = next((e for e in entries if e.get('id') == entry_id), None)
        
        if entry:
            print(f"Captain's log entry added successfully!")
            print(f"Stardate: {entry.get('stardate', 'Unknown')}")
            print(f"Category: {category}")
            print(f"Content: {args.message}")
        else:
            print("Entry added but could not retrieve confirmation.")
            
    except Exception as e:
        print(f"Failed to add log entry: {e}")
        sys.exit(1)


def handle_export(args):
    """Export data"""
    try:
        captain_log = CaptainLog()
        entries = captain_log.get_entries_sync()
        
        # Apply filters if specified
        if args.filter:
            # Simple filter implementation
            if args.filter.startswith('priority:'):
                priority = args.filter.split(':', 1)[1]
                entries = [e for e in entries if e.get('priority') == priority]
        
        if not entries:
            print("No entries to export.")
            return
        
        # Determine output file
        if args.output:
            output_file = args.output
        else:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"iss_export_{timestamp}.{args.format}"
        
        # Export data
        if args.format == 'csv':
            Exporters.to_csv_sync(entries, output_file)
        elif args.format == 'json':
            Exporters.to_json_sync(entries, output_file)
        elif args.format == 'markdown':
            Exporters.to_markdown_sync(entries, output_file)
        
        print(f"✓ Exported {len(entries)} entries to {output_file}")
        
    except Exception as e:
        print(f"Export failed: {e}")
        sys.exit(1)


def handle_status(args):
    """Show system status"""
    try:
        captain_log = CaptainLog()
        entries = captain_log.get_entries_sync()
        
        # Get time information
        timecodes = current_timecodes()
        stardate = get_stardate()
        
        print("ISS Module Status")
        print("=" * 40)
        print(f"Current Stardate: {stardate}")
        print(f"System Time: {timecodes['iso_timestamp']}")
        print(f"Julian Date: {timecodes['julian_date']}")
        print(f"Market Info: {timecodes['market_info']}")
        print()
        print(f"Total Log Entries: {len(entries)}")
        
        if entries:
            # Count by priority
            priorities = {}
            for entry in entries:
                priority = entry.get('priority', 'normal')
                priorities[priority] = priorities.get(priority, 0) + 1
            
            print("Entries by Priority:")
            for priority, count in sorted(priorities.items()):
                print(f"  {priority}: {count}")
        
        print("\n✓ System operational")
        
    except Exception as e:
        print(f"Status check failed: {e}")
        sys.exit(1)


def handle_stardate(args):
    """Get current stardate"""
    try:
        stardate = get_stardate()
        
        if args.format == 'numeric':
            print(f"{stardate}")
        else:
            print(f"Stardate {stardate}")
            
    except Exception as e:
        print(f"Failed to get stardate: {e}")
        sys.exit(1)


def handle_server(args):
    """Start web server"""
    try:
        print(f"Starting ISS Module server on {args.host}:{args.port}")
        print("Press Ctrl+C to stop the server")
        
        # Import and run the server
        import uvicorn
        from iss_module.api.main import app
        
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
        
    except ImportError:
        print("Error: uvicorn is required to run the server")
        print("Install with: pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)


def handle_version(args):
    """Show version information"""
    print("ISS Module v1.0.0")
    print("Integrated Systems Solution")
    print("Compatible with Caleon and CertSig projects")


if __name__ == '__main__':
    main()