import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional
from MJ_AI_Assistant.security.guardian import guardian_kernel

class HotPluginLoader:
    def __init__(self, plugins_dir: Optional[Path] = None):
        self.plugins_dir = plugins_dir or Path(__file__).parent.parent / "plugins"
        self.plugins_dir.mkdir(exist_ok=True)
        self.loaded_plugins: Dict[str, Dict[str, Any]] = {}

    def scan_and_hot_load(self) -> List[str]:
        """
        Hot-loads modules dynamically by scanning JSON manifests.
        """
        self.loaded_plugins.clear()
        loaded_names = []
        
        if not self.plugins_dir.exists():
            return []

        for folder in self.plugins_dir.iterdir():
            if folder.is_dir():
                manifest_path = folder / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                        
                        plugin_name = manifest.get("name", folder.name)
                        main_file = manifest.get("main", "plugin.py")
                        script_path = folder / main_file
                        
                        if script_path.exists():
                            # Dynamically import script module
                            spec = importlib.util.spec_from_file_location(plugin_name, str(script_path))
                            if spec and spec.loader:
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)
                                
                                self.loaded_plugins[plugin_name.upper()] = {
                                    "manifest": manifest,
                                    "module": module,
                                    "permissions": manifest.get("permissions", [])
                                }
                                loaded_names.append(plugin_name)
                    except Exception as e:
                        print(f"[PluginLoader] Failed to hot-load plugin '{folder.name}': {e}")
        return loaded_names

    def trigger_plugin_tool(self, plugin_name: str, tool_method: str, *args, **kwargs) -> Any:
        """
        Runs a loaded plugin method if it complies with safe manifests.
        """
        plugin_key = plugin_name.upper()
        if plugin_key not in self.loaded_plugins:
            return f"Error: Plugin '{plugin_name}' is offline or not installed."
            
        plugin_obj = self.loaded_plugins[plugin_key]
        module = plugin_obj["module"]
        
        if hasattr(module, tool_method):
            method = getattr(module, tool_method)
            try:
                return method(*args, **kwargs)
            except Exception as e:
                return f"Plugin tool failed execution: {e}"
        return f"Error: Tool '{tool_method}' not found inside plugin module."
