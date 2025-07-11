# memory/working_mem.py

class WorkingMemory:
    def __init__(self):
        self.state = {}

    def ingest(self, config, event=None):
        """
        Normalize config (from LLM) to a flat dict state, always.
        Accepts:
          - { "variables": [ {"id": "...", "value": ...}, ... ] }
          - { ... } dict
          - [ {"id": "...", "value": ...}, ... ] list
        """
        state = {}
        if isinstance(config, dict):
            if "variables" in config and isinstance(config["variables"], list):
                for var in config["variables"]:
                    if isinstance(var, dict) and "id" in var and "value" in var:
                        state[var["id"]] = var["value"]
            else:
                # Flat dict, just take all keys/values
                state = dict(config)
        elif isinstance(config, list):
            for var in config:
                if isinstance(var, dict) and "id" in var and "value" in var:
                    state[var["id"]] = var["value"]
        # Merge in event fields (LLM may omit)
        if event:
            for k, v in event.items():
                if k not in state:
                    state[k] = v
        self.state = state

    def get_state(self, event=None):
        # Return latest state, merge with event if present
        if not event:
            return dict(self.state)
        merged = dict(self.state)
        for k, v in event.items():
            if k not in merged:
                merged[k] = v
        return merged
