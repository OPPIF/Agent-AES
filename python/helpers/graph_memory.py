import os
import pickle
from typing import Dict, List, Optional

import networkx as nx
from langchain_core.documents import Document

from python.helpers import files


class GraphMemory:
    """Simple wrapper around a NetworkX graph for memory relations."""

    _instances: Dict[str, "GraphMemory"] = {}

    @classmethod
    def get(cls, memory_subdir: str) -> "GraphMemory":
        """Return a GraphMemory instance for the given memory sub-directory."""
        if memory_subdir not in cls._instances:
            cls._instances[memory_subdir] = cls(memory_subdir)
        return cls._instances[memory_subdir]

    def __init__(self, memory_subdir: str):
        self.memory_subdir = memory_subdir
        self.path = files.get_abs_path("memory", memory_subdir, "graph.gpickle")
        self.graph = nx.DiGraph()
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                self.graph = pickle.load(f)

    def add_document(self, doc: Document):
        """Insert a document node and its relations into the graph."""
        node_id = doc.metadata.get("id")
        if not node_id:
            return
        self.graph.add_node(node_id, **doc.metadata)
        relations = doc.metadata.get("relations", [])
        for rel in relations:
            target = rel.get("target")
            rel_type = rel.get("type", "related")
            if target:
                self.graph.add_edge(node_id, target, type=rel_type)
        self.save()

    def remove_document(self, doc_id: str):
        """Remove a document node from the graph."""
        if self.graph.has_node(doc_id):
            self.graph.remove_node(doc_id)
            self.save()

    def query(self, node_id: str, relation_type: Optional[str] = None) -> List[str]:
        """Return IDs of nodes related to ``node_id``.

        Args:
            node_id: Source node identifier.
            relation_type: Optional relation type filter.
        """
        if not self.graph.has_node(node_id):
            return []
        result: List[str] = []
        for target in self.graph.neighbors(node_id):
            data = self.graph.get_edge_data(node_id, target) or {}
            if relation_type is None or data.get("type") == relation_type:
                result.append(target)
        return result

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "wb") as f:
            pickle.dump(self.graph, f)
