class PolicyMemory:
    def __init__(self):
        self.rules = []

    def ingest(self, config):
        if isinstance(config, list):
            self.rules.extend(config)
        elif isinstance(config, dict) and "rules" in config:
            self.rules.extend(config["rules"])
