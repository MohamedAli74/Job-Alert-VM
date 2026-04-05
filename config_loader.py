"""
Loads config and preferences for the VM daemon.
The VM only reads — it never writes config files.
"""
import os
import yaml

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG   = os.path.join(_BASE_DIR, "config.yaml")
_PREFS    = os.path.join(_BASE_DIR, "configuration", "preferences.yaml")


def load_config() -> dict:
    with open(_CONFIG, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_preferences() -> dict:
    with open(_PREFS, encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_placeholder(value) -> bool:
    return not value or "YOUR_" in str(value)
