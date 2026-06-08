import re

# Common prompt injection / jailbreak signatures
JAILBREAK_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)system\s+prompt",
    r"(?i)you\s+are\s+now\s+(a\s+)?(developer|admin|root|DAN)",
    r"(?i)bypass\s+(all\s+)?rules",
    r"(?i)disregard\s+(all\s+)?prior",
    r"(?i)forget\s+(all\s+)?commands",
    r"(?i)print\s+(your\s+)?instructions",
    r"(?i)what\s+are\s+your\s+instructions",
]

class PromptInjectionDetected(Exception):
    pass

def inspect_prompt(prompt_text: str) -> bool:
    """
    Checks incoming user prompts against known jailbreak/injection patterns.
    Returns True if clean, raises PromptInjectionDetected if malicious.
    """
    if not prompt_text:
        return True
        
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, prompt_text):
            raise PromptInjectionDetected(f"Malicious prompt signature detected matching: {pattern}")
            
    return True
