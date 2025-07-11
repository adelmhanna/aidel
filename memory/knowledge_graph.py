import networkx as nx

class KnowledgeGraphMemory:
    def __init__(self):
        self.graph = nx.DiGraph()

    def ingest(self, config):
        # config can be LLM-generated dict of nodes/edges/entities
        # For demo, just add a node for now
        if isinstance(config, dict):
            for k, v in config.items():
                self.graph.add_node(str(k), **(v if isinstance(v, dict) else {}))
