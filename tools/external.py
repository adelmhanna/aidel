class ExternalTool:
    def __init__(self):
        self.integrations = {}

    def ingest(self, config):
        self.integrations.update(config)
