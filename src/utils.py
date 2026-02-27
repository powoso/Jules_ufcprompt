import os
import yaml

def load_config():
    """
    Loads configuration from config/config.yaml.
    """
    # Find config relative to this file
    # This assumes src/utils.py is at src/utils.py
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
