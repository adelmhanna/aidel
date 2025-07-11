import sqlite3
from datetime import datetime

class AuditMemory:
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS audit (decision TEXT, reason TEXT, event TEXT, timestamp TEXT)"
        )

    def log_decision(self, decision, reason, event=None):
        ts = datetime.now().isoformat()
        evt_str = str(event) if event else ""
        self.cursor.execute(
            "INSERT INTO audit (decision, reason, event, timestamp) VALUES (?, ?, ?, ?)",
            (decision, reason, evt_str, ts),
        )
        self.conn.commit()

    def ingest(self, config, event=None):
        """
        Accepts a config dictionary, typically from LLM or other module, and logs it.
        Supports log (str/dict/list) and logs (list).
        """
        if isinstance(config, dict):
            # Try keys 'log' (str or list) or 'logs' (list)
            entries = []
            if "log" in config:
                entries = config["log"]
            elif "logs" in config:
                entries = config["logs"]
            if isinstance(entries, dict):
                entries = [entries]
            if isinstance(entries, str):
                entries = [{"reason": entries}]
            if isinstance(entries, list):
                for entry in entries:
                    # entry may be dict or str
                    if isinstance(entry, dict):
                        decision = entry.get("decision", "info")
                        reason = entry.get("reason", entry.get("event", str(entry)))
                        self.log_decision(decision, reason, event)
                    elif isinstance(entry, str):
                        self.log_decision("info", entry, event)
            return
        elif isinstance(config, list):
            for entry in config:
                if isinstance(entry, dict):
                    decision = entry.get("decision", "info")
                    reason = entry.get("reason", entry.get("event", str(entry)))
                    self.log_decision(decision, reason, event)
                elif isinstance(entry, str):
                    self.log_decision("info", entry, event)
            return
        elif isinstance(config, str):
            self.log_decision("info", config, event)
            return

    def get_audit_log(self, limit=100):
        self.cursor.execute("SELECT * FROM audit ORDER BY timestamp DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()
