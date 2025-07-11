class MetaMemory:
    def __init__(self):
        self.entries = []

    def ingest(self, config):
        self.entries.append(config)
