import types
import sys
import importlib

# stub langchain Document to avoid heavy dependency
class Document:
    def __init__(self, page_content: str, metadata: dict | None = None):
        self.page_content = page_content
        self.metadata = metadata or {}

module = types.ModuleType("langchain_core.documents")
module.Document = Document
sys.modules["langchain_core"] = types.ModuleType("langchain_core")
sys.modules["langchain_core.documents"] = module

# ensure real files module (not stubbed by other tests)
if "python.helpers.files" in sys.modules:
    del sys.modules["python.helpers.files"]
importlib.import_module("python.helpers.files")

from python.helpers.graph_memory import GraphMemory


def test_graph_memory_relations(tmp_path):
    subdir = "test_graph"
    graph = GraphMemory.get(subdir)
    graph.graph.clear()
    graph.save()

    doc1 = Document("first", {"id": "1"})
    graph.add_document(doc1)

    doc2 = Document("second", {"id": "2", "relations": [{"target": "1", "type": "ref"}]})
    graph.add_document(doc2)

    assert graph.query("2", "ref") == ["1"]

    graph.remove_document("1")
    assert not graph.graph.has_node("1")
