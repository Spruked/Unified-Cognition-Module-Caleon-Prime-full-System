import json
import os


VAULT_PATH = "vault/cochlear_vault.jsonl"

class CochlearVault:
    def __init__(self, vault_path=VAULT_PATH):
        self.vault_path = vault_path
        vault_dir = os.path.dirname(self.vault_path)
        if not os.path.exists(vault_dir):
            os.makedirs(vault_dir, exist_ok=True)
        if not os.path.exists(self.vault_path):
            with open(self.vault_path, "w", encoding="utf-8") as f:
                f.write("")

    def analyze_history(self):
        """
        Analyze vault history to tune future integrity thresholds.
        Returns:
            dict with updated threshold values or trends.
        """
        try:
            with open(self.vault_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            scores = []
            for line in lines[-500:]:  # Last 500 percepts only
                entry = json.loads(line)
                score = entry.get("integrity_score")
                if score is not None:
                    scores.append(score)
            if not scores:
                return {}
            avg_score = sum(scores) / len(scores)
            threshold = round(min(max(avg_score - 0.05, 0.3), 0.9), 3)
            return {"learned_threshold": threshold}
        except Exception as e:
            print(f"[Vault Learning] Failed to analyze vault: {e}")
            return {}

    def store(self, percept: dict):
        with open(self.vault_path, "a", encoding="utf-8") as f:
            json.dump(percept, f)
            f.write("\n")

    def learn_from_history(self, n=50):
        try:
            with open(self.vault_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-n:]
                entries = [json.loads(line) for line in lines if '"integrity"' in line or '"integrity_score"' in line]

            # Compute average thresholds from history, filtering out None values
            integrity_scores = [e.get("integrity_score", 0.0) for e in entries if e.get("integrity_score") is not None]
            avg_integrity = sum(integrity_scores) / len(integrity_scores) if integrity_scores else 0.7
            pitch_scores = [e.get("pitch_hz", 0.0) for e in entries if e.get("pitch_hz") is not None]
            avg_pitch = sum(pitch_scores) / len(pitch_scores) if pitch_scores else 0.0

            # Global adaptive thresholds
            global ADAPTIVE_INTEGRITY_THRESHOLD, ADAPTIVE_PITCH_BASELINE
            ADAPTIVE_INTEGRITY_THRESHOLD = round(avg_integrity - 0.05, 3)
            ADAPTIVE_PITCH_BASELINE = round(avg_pitch, 1)
        except Exception:
            # Optionally log the error if needed
            return
