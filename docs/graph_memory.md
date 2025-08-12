# Graph Memory

The agent stores relations between memories using a NetworkX graph.  Each
memory document is inserted into the graph as a node, and optional
relations can be defined through the ``relations`` field in the document
metadata.

```python
# example metadata when saving a memory
doc.metadata["relations"] = [{"target": other_id, "type": "ref"}]
```

Graphs are stored inside the memory directory
(``memory/<subdir>/graph.gpickle``).  To explore relationships, use the
``memory_graph_query`` tool:

```json
{"tool": "memory_graph_query", "args": {"node_id": "<id>", "relation_type": "ref"}}
```

The tool returns the documents linked to the provided node.  Omitting
``relation_type`` will return all directly related memories.
