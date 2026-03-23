"""
Roles Configuration Loader
Loads role definitions from JSON config file
"""

import json
import os
from typing import Dict, Any

def load_roles_config() -> Dict[str, Any]:
    """Load roles configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(__file__), 'roles.json')

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert roles array to dict keyed by role key
        roles_dict = {}
        for role in data.get('roles', []):
            roles_dict[role['key']] = role

        return roles_dict

    except FileNotFoundError:
        print(f"Warning: Roles config file not found at {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing roles config: {e}")
        return {}

def get_role_config(role_key: str) -> Dict[str, Any]:
    """Get configuration for a specific role"""
    roles = load_roles_config()
    return roles.get(role_key, {})

def get_all_features() -> list:
    """Get all available features across all roles"""
    roles = load_roles_config()
    all_features = set()

    for role_config in roles.values():
        features = role_config.get('features', [])
        if '*' in features:
            # If role has wildcard, it can access everything
            return ['*']
        all_features.update(features)

    return list(all_features)

if __name__ == "__main__":
    # Test the loader
    roles = load_roles_config()
    print(f"Loaded {len(roles)} roles:")
    for key, config in roles.items():
        print(f"- {key}: {config.get('name_en', key)} ({config.get('data_scope', 'unknown')} scope)")