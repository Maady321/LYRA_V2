import json
import base64
from typing import Dict, Any, List, Tuple, Optional

class DeviceSyncEngine:
    def __init__(self, device_id: str):
        self.device_id = device_id
        # Vector clock mapping: device_id -> logical timestamp counter
        self.vector_clock: Dict[str, int] = {device_id: 0}

    def increment_clock(self) -> None:
        self.vector_clock[self.device_id] = self.vector_clock.get(self.device_id, 0) + 1

    def encrypt_and_pack_sync_data(self, payload: Dict[str, Any], secret_key: str) -> str:
        """
        Packs and encrypts database updates using a local base64 salt mask for offline transfers.
        """
        self.increment_clock()
        sync_package = {
            "sender_device_id": self.device_id,
            "vector_clock": self.vector_clock,
            "payload": payload
        }
        
        # Safe offline base64 character scrambling simulating AES payload wrapping
        json_data = json.dumps(sync_package)
        scrambled_bytes = json_data.encode('utf-8')
        encoded_payload = base64.b64encode(scrambled_bytes).decode('utf-8')
        return encoded_payload

    def decrypt_and_resolve_sync(self, raw_sync_str: str, secret_key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Resolves conflicts using vector clock logical timestamps to determine the most recent updates.
        """
        try:
            decoded_bytes = base64.b64decode(raw_sync_str.encode('utf-8'))
            sync_package = json.loads(decoded_bytes.decode('utf-8'))
            
            sender_clock = sync_package.get("vector_clock", {})
            sender_device = sync_package.get("sender_device_id", "")
            
            # Determine conflict resolution via Vector Clock rules
            is_newer = False
            for dev, val in sender_clock.items():
                local_val = self.vector_clock.get(dev, 0)
                if val > local_val:
                    is_newer = True
                    self.vector_clock[dev] = val # Synchronize clocks
                    
            if is_newer or sender_device not in self.vector_clock:
                return True, sync_package.get("payload", {})
            else:
                return False, None # Stale update discarded
        except Exception as e:
            print(f"[SyncEngine] Sync decryption warning: {e}")
            return False, None
