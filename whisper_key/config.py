import os
import yaml

_CONFIG_DIR = os.path.join(os.environ.get('APPDATA', '.'), 'whisper-key')
_CONFIG_FILE = os.path.join(_CONFIG_DIR, 'config.yaml')

DEFAULTS = {
    'hotkeys': {
        'start': 'ctrl+shift',
        'stop_modifier': 'ctrl',
        'auto_enter': 'alt',
        'cancel': 'esc',
    },
    'whisper': {
        'model': 'medium',
        'device': 'cpu',
        'compute_type': 'int8',
        'language': 'fr',
    },
    'audio': {
        'device': None,
        'sample_rate': 16000,
        'max_duration': 300,
    },
    'clipboard': {
        'auto_paste': True,
        'max_retries': 5,
    },
    'logging': {
        'level': 'INFO',
    },
}

def load():
    if not os.path.exists(_CONFIG_FILE):
        save(DEFAULTS)
        return DEFAULTS

    with open(_CONFIG_FILE, 'r', encoding='utf-8') as f:
        user = yaml.safe_load(f) or {}

    merged = dict(DEFAULTS)
    for section, values in user.items():
        if section in merged and isinstance(merged[section], dict):
            merged[section] = {**merged[section], **values}
        else:
            merged[section] = values
    return merged

def save(cfg):
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    with open(_CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)

def get_log_path():
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    return os.path.join(_CONFIG_DIR, 'app.log')

def get_fallback_dir():
    path = os.path.join(_CONFIG_DIR, 'transcriptions')
    os.makedirs(path, exist_ok=True)
    return path
