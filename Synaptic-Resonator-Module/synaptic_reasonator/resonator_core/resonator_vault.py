# resonator_vault.py - Data Vault for Synaptic Reasonator

class ResonatorVault:
    def __init__(self):
        self.storage = {}

    def store(self, key, value):
        self.storage[key] = value

    def retrieve(self, key):
        return self.storage.get(key)
import json
import time

def log_to_vault(entry: dict, vault_name: str = "SynapticVault"):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    entry["logged_at"] = timestamp
    with open(f"{vault_name.lower()}.log", "a") as f:
        f.write(json.dumps(entry) + "\n")
