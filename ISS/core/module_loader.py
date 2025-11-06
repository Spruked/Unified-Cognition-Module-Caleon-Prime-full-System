"""
Dynamic module loader for ISS Module system
Handles loading, unloading, and management of system modules
"""

import importlib
import importlib.util
import sys
import os
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path


class ModuleLoader:
    """
    Dynamic module loader for ISS system components
    """
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or self._get_base_path()
        self.loaded_modules = {}
        self.module_registry = {}
        self.logger = logging.getLogger('ISS.ModuleLoader')
    
    def _get_base_path(self) -> str:
        """Get the base path for module loading"""
        current_dir = Path(__file__).parent.parent
        return str(current_dir)
    
    async def load_module(self, module_name: str, module_path: Optional[str] = None) -> Optional[Any]:
        """
        Load a module dynamically
        
        Args:
            module_name: Name of the module to load
            module_path: Optional custom path to the module
        
        Returns:
            Loaded module instance or None if failed
        """
        try:
            if module_name in self.loaded_modules:
                self.logger.info(f"Module {module_name} already loaded")
                return self.loaded_modules[module_name]
            
            # Determine module path
            if module_path is None:
                module_path = self._resolve_module_path(module_name)
            
            if not module_path or not os.path.exists(module_path):
                self.logger.error(f"Module path not found: {module_path}")
                return None
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None or spec.loader is None:
                self.logger.error(f"Failed to create spec for module: {module_name}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Initialize module if it has an init function
            module_instance = None
            if hasattr(module, 'initialize'):
                module_instance = await module.initialize()
            elif hasattr(module, 'create_instance'):
                module_instance = module.create_instance()
            else:
                module_instance = module
            
            self.loaded_modules[module_name] = module_instance
            self.module_registry[module_name] = {
                'path': module_path,
                'loaded_at': importlib.util.module_from_spec(spec),
                'instance': module_instance
            }
            
            self.logger.info(f"Successfully loaded module: {module_name}")
            return module_instance
            
        except Exception as e:
            self.logger.error(f"Failed to load module {module_name}: {e}")
            return None
    
    def _resolve_module_path(self, module_name: str) -> Optional[str]:
        """
        Resolve the file path for a given module name
        """
        # Common module mappings
        module_mappings = {
            'captain_mode': 'captain_mode/__init__.py',
            'api': 'api/__init__.py',
            'captain_log': 'captain_mode/captain_log.py',
            'exporters': 'captain_mode/exporters.py',
            'vd_wrapper': 'captain_mode/vd_wrapper.py'
        }
        
        if module_name in module_mappings:
            return os.path.join(self.base_path, module_mappings[module_name])
        
        # Try to find the module in standard locations
        possible_paths = [
            os.path.join(self.base_path, module_name, '__init__.py'),
            os.path.join(self.base_path, module_name, f'{module_name}.py'),
            os.path.join(self.base_path, f'{module_name}.py'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    async def unload_module(self, module_name: str) -> bool:
        """
        Unload a previously loaded module
        """
        try:
            if module_name not in self.loaded_modules:
                self.logger.warning(f"Module {module_name} not loaded")
                return False
            
            module_instance = self.loaded_modules[module_name]
            
            # Call shutdown if available
            if hasattr(module_instance, 'shutdown'):
                await module_instance.shutdown()
            
            # Remove from tracking
            del self.loaded_modules[module_name]
            if module_name in self.module_registry:
                del self.module_registry[module_name]
            
            # Remove from sys.modules
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            self.logger.info(f"Successfully unloaded module: {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload module {module_name}: {e}")
            return False
    
    def reload_module(self, module_name: str) -> bool:
        """
        Reload a module (unload then load)
        """
        try:
            if module_name in self.loaded_modules:
                self.unload_module(module_name)
            
            return self.load_module(module_name) is not None
            
        except Exception as e:
            self.logger.error(f"Failed to reload module {module_name}: {e}")
            return False
    
    def list_loaded_modules(self) -> List[str]:
        """Get list of currently loaded modules"""
        return list(self.loaded_modules.keys())
    
    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a loaded module"""
        if module_name not in self.module_registry:
            return None
        
        info = self.module_registry[module_name].copy()
        info['loaded'] = module_name in self.loaded_modules
        return info
    
    def discover_modules(self) -> List[str]:
        """
        Discover available modules in the system
        """
        discovered = []
        
        # Look for module directories
        for item in os.listdir(self.base_path):
            item_path = os.path.join(self.base_path, item)
            if os.path.isdir(item_path):
                init_file = os.path.join(item_path, '__init__.py')
                if os.path.exists(init_file):
                    discovered.append(item)
        
        return discovered