from enum import Enum
from typing import List, Dict

class Permission(Enum):
    READ_MEMORY = "READ_MEMORY"
    WRITE_MEMORY = "WRITE_MEMORY"
    READ_FILE = "READ_FILE"
    WRITE_FILE = "WRITE_FILE"
    DELETE_FILE = "DELETE_FILE"
    EXECUTE_SCRIPT = "EXECUTE_SCRIPT"
    BROWSER_ACCESS = "BROWSER_ACCESS"
    VOICE_ACCESS = "VOICE_ACCESS"
    DATABASE_ACCESS = "DATABASE_ACCESS"
    SYSTEM_CONTROL = "SYSTEM_CONTROL"

AGENT_PROFILES: Dict[str, List[Permission]] = {
    "VISION": [
        Permission.READ_MEMORY,
        Permission.WRITE_MEMORY,
        Permission.DATABASE_ACCESS
    ],
    "STARK": [
        Permission.EXECUTE_SCRIPT,
        Permission.READ_FILE,
        Permission.WRITE_FILE
    ],
    "SPIDEY": [
        Permission.VOICE_ACCESS
    ],
    "GHOST": [
        Permission.SYSTEM_CONTROL,
        Permission.READ_FILE,
        Permission.WRITE_FILE,
        Permission.DELETE_FILE
    ],
    "BANNER": [
        Permission.READ_MEMORY,
        Permission.READ_FILE
    ],
    "CAPTAIN": [
        Permission.DATABASE_ACCESS,
        Permission.READ_MEMORY
    ],
    "FURY": [
        Permission.DATABASE_ACCESS,
        Permission.READ_MEMORY,
        Permission.SYSTEM_CONTROL
    ],
    "JARVIS": [
        Permission.SYSTEM_CONTROL,
        Permission.DATABASE_ACCESS
    ]
}

def has_permission(agent_name: str, permission: Permission) -> bool:
    """Check if an agent has a specific permission."""
    # Normalize name to match dictionary keys
    normalized_name = agent_name.split()[0].upper()
    profile = AGENT_PROFILES.get(normalized_name, [])
    return permission in profile
