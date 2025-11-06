"""
Validators
==========
Data validation and safety checks for ISS Module.

Provides:
- Stardate validation (needed for NFT minting + symbolic cognition)
- CaptainLog entry validation (used before exports)
- Export list safety checks (essential for Docker endpoints or CertSig backends)
- Input sanitization and structural integrity checks

Used by:
- ISS core system for configuration validation
- CaptainLog for entry validation before storage
- API endpoints for request validation
- CertSig for NFT metadata validation
- Export systems for data integrity
"""

import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging


logger = logging.getLogger('ISS.Validators')


def validate_stardate(stardate: Union[str, float, int]) -> bool:
    """
    Validate stardate format and range
    
    Args:
        stardate: Stardate to validate
    
    Returns:
        True if valid stardate
    """
    try:
        if isinstance(stardate, str):
            # Remove 'Stardate' prefix if present
            if stardate.startswith('Stardate '):
                stardate = stardate[9:]
            stardate = float(stardate)
        
        if not isinstance(stardate, (int, float)):
            return False
        
        # TNG era stardates (approximately -300000 to 150000)
        if stardate < -300000 or stardate > 150000:
            return False
        
        return True
        
    except (ValueError, TypeError):
        return False


def validate_timestamp(timestamp: str) -> bool:
    """
    Validate ISO timestamp format
    
    Args:
        timestamp: Timestamp string to validate
    
    Returns:
        True if valid ISO timestamp
    """
    try:
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False


def validate_log_entry(entry: Dict[str, Any]) -> bool:
    """
    Validate captain's log entry structure
    
    Args:
        entry: Log entry dictionary to validate
    
    Returns:
        True if valid log entry
    """
    required_fields = ['timestamp', 'stardate', 'content']
    
    for field in required_fields:
        if field not in entry:
            return False
    
    # Validate individual fields
    if not validate_timestamp(entry['timestamp']):
        return False
    
    if not validate_stardate(entry['stardate']):
        return False
    
    if not isinstance(entry['content'], str) or len(entry['content'].strip()) == 0:
        return False
    
    return True


def validate_export_list(data: List[Dict[str, Any]]) -> bool:
    """
    Validate a list of dictionaries for export safety
    
    Args:
        data: List of dictionaries to validate
    
    Returns:
        True if safe to export
    """
    if not isinstance(data, list):
        logger.error("Export data must be a list")
        return False
    
    if len(data) == 0:
        logger.warning("Export data is empty")
        return True  # Empty is valid
    
    # Check if all items are dictionaries
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            logger.error(f"Export item {i} is not a dictionary")
            return False
    
    # Check for consistent keys (basic structure validation)
    if len(data) > 1:
        first_keys = set(data[0].keys())
        for i, item in enumerate(data[1:], 1):
            if set(item.keys()) != first_keys:
                logger.warning(f"Export item {i} has different keys than first item")
                # Don't fail, just warn - some variation is okay
    
    return True


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate system configuration
    
    Args:
        config: Configuration dictionary to validate
    
    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        required_fields = ['system_name', 'version']
        
        # Check required fields
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required config field: {field}")
                return False
        
        # Validate field types and values
        validations = [
            _validate_system_name(config.get('system_name')),
            _validate_version(config.get('version')),
            _validate_debug_mode(config.get('debug_mode', False)),
            _validate_heartbeat_interval(config.get('heartbeat_interval', 30)),
            _validate_data_retention(config.get('data_retention_days', 90))
        ]
        
        return all(validations)
        
    except Exception as e:
        logger.error(f"Config validation error: {e}")
        return False


def _validate_system_name(name: Any) -> bool:
    """Validate system name"""
    if not isinstance(name, str):
        logger.error("System name must be a string")
        return False
    
    if len(name.strip()) == 0:
        logger.error("System name cannot be empty")
        return False
    
    if len(name) > 100:
        logger.error("System name too long (max 100 characters)")
        return False
    
    return True


def _validate_version(version: Any) -> bool:
    """Validate version string"""
    if not isinstance(version, str):
        logger.error("Version must be a string")
        return False
    
    # Simple semantic version pattern (x.y.z)
    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, version):
        logger.error("Version must follow semantic versioning (x.y.z)")
        return False
    
    return True


def _validate_debug_mode(debug_mode: Any) -> bool:
    """Validate debug mode setting"""
    if not isinstance(debug_mode, bool):
        logger.error("Debug mode must be a boolean")
        return False
    return True


def _validate_heartbeat_interval(interval: Any) -> bool:
    """Validate heartbeat interval"""
    if not isinstance(interval, (int, float)):
        logger.error("Heartbeat interval must be a number")
        return False
    
    if interval <= 0:
        logger.error("Heartbeat interval must be positive")
        return False
    
    if interval > 3600:  # 1 hour max
        logger.error("Heartbeat interval too long (max 3600 seconds)")
        return False
    
    return True


def _validate_data_retention(days: Any) -> bool:
    """Validate data retention period"""
    if not isinstance(days, int):
        logger.error("Data retention days must be an integer")
        return False
    
    if days < 1:
        logger.error("Data retention must be at least 1 day")
        return False
    
    if days > 3650:  # 10 years max
        logger.error("Data retention too long (max 3650 days)")
        return False
    
    return True


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def validate_file_path(path: str) -> bool:
    """
    Validate file path for security
    
    Args:
        path: File path to validate
    
    Returns:
        True if path is safe to use
    """
    if not isinstance(path, str):
        return False
    
    # Prevent path traversal
    if '..' in path or path.startswith('/'):
        return False
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    if any(char in path for char in dangerous_chars):
        return False
    
    return True


# Convenient static class for easy usage
class Validator:
    """
    Convenient static methods for validation
    
    Usage:
        from iss_module.core.validators import Validator
        Validator.check_stardate(12345.6)
        Validator.check_timestamp("2024-01-01T00:00:00Z")
    """
    
    @staticmethod
    def check_stardate(stardate) -> bool:
        """Validate stardate format and range"""
        return validate_stardate(stardate)
    
    @staticmethod  
    def check_timestamp(timestamp: str) -> bool:
        """Validate ISO timestamp format"""
        return validate_timestamp(timestamp)
    
    @staticmethod
    def check_config(config: Dict[str, Any]) -> bool:
        """Validate system configuration"""
        return validate_config(config)
    
    @staticmethod
    def check_log_entry(entry: Dict[str, Any]) -> bool:
        """Validate captain's log entry structure"""
        return validate_log_entry(entry)
    
    @staticmethod
    def check_export_list(data: List[Dict[str, Any]]) -> bool:
        """Validate export data list"""
        return validate_export_list(data)
    
    @staticmethod
    def clean_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input text"""
        return sanitize_input(text, max_length)