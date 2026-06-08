import shlex
from typing import List, Tuple
from backend.security.risk_engine import RiskLevel, assess_risk
import re

# explicitly allowed base commands
ALLOWED_COMMANDS = {
    "git", "python", "python3", "pip", "npm", "node", "ls", "dir", 
    "echo", "mkdir", "cat", "type", "ping", "curl", "wget", "uvicorn",
    "pytest"
}

# forbidden substrings/arguments
FORBIDDEN_ARGS = [
    r";", r"&&", r"\|\|", r"\|", r">", r"<", r"`", r"\$\("
]

class CommandValidationError(Exception):
    pass

def validate_command(command_line: str) -> Tuple[List[str], RiskLevel]:
    """
    Parses a shell command string into a list of arguments (for shell=False).
    Validates the base command against an allowlist.
    Validates arguments against forbidden shell injection tokens.
    Returns the parsed command array and its assessed risk level.
    """
    if not command_line or not command_line.strip():
        raise CommandValidationError("Empty command provided.")
        
    # Check for obvious shell chaining characters
    for forbidden in FORBIDDEN_ARGS:
        if re.search(forbidden, command_line):
            raise CommandValidationError(f"Command contains forbidden shell chaining tokens: {command_line}")
            
    try:
        # Using posix=False to support Windows paths better, but it may behave weirdly with quotes.
        # Given we want shell=False, we must provide an array.
        args = shlex.split(command_line, posix=False)
    except ValueError as e:
        raise CommandValidationError(f"Invalid command syntax: {str(e)}")
        
    if not args:
        raise CommandValidationError("Could not parse command.")
        
    base_cmd = args[0].lower().replace('.exe', '')
    
    if base_cmd not in ALLOWED_COMMANDS:
        raise CommandValidationError(f"Command '{base_cmd}' is not in the allowlist. Allowed commands: {', '.join(ALLOWED_COMMANDS)}")
        
    risk = assess_risk(base_cmd, " ".join(args[1:]))
    
    if risk == RiskLevel.CRITICAL:
        raise CommandValidationError("CRITICAL risk command rejected by Command Validator.")
        
    return args, risk
