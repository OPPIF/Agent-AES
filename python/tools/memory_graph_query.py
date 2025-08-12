from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response


class MemoryGraphQuery(Tool):
    async def execute(self, node_id: str, relation_type: str = "", **kwargs):
        db = await Memory.get(self.agent)
        docs = await db.query_graph(node_id=node_id, relation_type=relation_type or None)

        if len(docs) == 0:
            result = self.agent.read_prompt("fw.memories_not_found.md", query=node_id)
        else:
            text = "\n\n".join(Memory.format_docs_plain(docs))
            result = str(text)

        return Response(message=result, break_loop=False)
