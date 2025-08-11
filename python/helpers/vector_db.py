from typing import Any, List, Sequence
import uuid
from pathlib import Path
import pickle
from langchain_community.vectorstores import FAISS

# faiss needs to be patched for python 3.12 on arm #TODO remove once not needed
from python.helpers import faiss_monkey_patch
import faiss


from langchain_core.documents import Document
from langchain.storage import LocalFileStore
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores.utils import (
    DistanceStrategy,
)
from langchain.embeddings import CacheBackedEmbeddings

from agent import Agent


MEMORY_PATH = Path("memory")
EMBED_CACHE_DIR = MEMORY_PATH / "embeddings"
VECTOR_DB_DIR = MEMORY_PATH / "vector_db"


class MyFaiss(FAISS):
    # override aget_by_ids
    def get_by_ids(self, ids: Sequence[str], /) -> List[Document]:
        # return all self.docstore._dict[id] in ids
        return [self.docstore._dict[id] for id in (ids if isinstance(ids, list) else [ids]) if id in self.docstore._dict]  # type: ignore

    async def aget_by_ids(self, ids: Sequence[str], /) -> List[Document]:
        return self.get_by_ids(ids)

    def get_all_docs(self) -> dict[str, Document]:
        return self.docstore._dict  # type: ignore


class SerializedDocstore(InMemoryDocstore):
    """Simple persistent docstore backed by a pickle file."""

    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            with open(self.path, "rb") as f:
                self._dict = pickle.load(f)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "wb") as f:
            pickle.dump(self._dict, f)


class VectorDB:

    _cached_embeddings: dict[str, CacheBackedEmbeddings] = {}

    @staticmethod
    def _get_embeddings(agent: Agent, cache: bool = True):
        model = agent.get_embedding_model()
        if not cache:
            return model  # return raw embeddings if cache is False
        namespace = getattr(
            model,
            "model_name",
            "default",
        )
        if namespace not in VectorDB._cached_embeddings:
            store_dir = EMBED_CACHE_DIR / namespace
            store_dir.mkdir(parents=True, exist_ok=True)
            store = LocalFileStore(str(store_dir))
            VectorDB._cached_embeddings[namespace] = (
                CacheBackedEmbeddings.from_bytes_store(
                    model,
                    store,
                    namespace=namespace,
                )
            )
        return VectorDB._cached_embeddings[namespace]

    def __init__(self, agent: Agent, cache: bool = True):
        self.agent = agent
        self.cache = cache  # store cache preference
        self.embeddings = self._get_embeddings(agent, cache=cache)
        self.vector_path = VECTOR_DB_DIR
        self.index_path = self.vector_path / "index.faiss"
        self.docstore_path = self.vector_path / "docstore.pkl"
        self.id_map_path = self.vector_path / "index_to_docstore_id.pkl"

        if not self.load_local():
            dim = len(self.embeddings.embed_query("example"))
            self.index = faiss.IndexFlatIP(dim)
            self.db = MyFaiss(
                embedding_function=self.embeddings,
                index=self.index,
                docstore=SerializedDocstore(self.docstore_path),
                index_to_docstore_id={},
                distance_strategy=DistanceStrategy.COSINE,
                # normalize_L2=True,
                relevance_score_fn=cosine_normalizer,
            )

    def save_local(self) -> None:
        """Persist the FAISS index and docstore to disk."""
        self.vector_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.db.index, str(self.index_path))
        if isinstance(self.db.docstore, SerializedDocstore):
            self.db.docstore.save()
        with open(self.id_map_path, "wb") as f:
            pickle.dump(self.db.index_to_docstore_id, f)

    def load_local(self) -> bool:
        """Load the FAISS index and docstore from disk if available."""
        try:
            if (
                self.index_path.exists()
                and self.docstore_path.exists()
                and self.id_map_path.exists()
            ):
                self.index = faiss.read_index(str(self.index_path))
                docstore = SerializedDocstore(self.docstore_path)
                with open(self.id_map_path, "rb") as f:
                    id_map = pickle.load(f)
                self.db = MyFaiss(
                    embedding_function=self.embeddings,
                    index=self.index,
                    docstore=docstore,
                    index_to_docstore_id=id_map,
                    distance_strategy=DistanceStrategy.COSINE,
                    relevance_score_fn=cosine_normalizer,
                )
                return True
        except Exception:
            pass
        return False

    async def search_by_similarity_threshold(
        self, query: str, limit: int, threshold: float, filter: str = ""
    ):
        comparator = get_comparator(filter) if filter else None

        # rate limiter
        await self.agent.rate_limiter(
            model_config=self.agent.config.embeddings_model, input=query
        )

        return await self.db.asearch(
            query,
            search_type="similarity_score_threshold",
            k=limit,
            score_threshold=threshold,
            filter=comparator,
        )

    async def search_by_metadata(self, filter: str, limit: int = 0) -> list[Document]:
        comparator = get_comparator(filter)
        all_docs = self.db.get_all_docs()
        result = []
        for doc in all_docs.values():
            if comparator(doc.metadata):
                result.append(doc)
                # stop if limit reached and limit > 0
                if limit > 0 and len(result) >= limit:
                    break
        return result

    async def insert_documents(self, docs: list[Document]):
        ids = [str(uuid.uuid4()) for _ in range(len(docs))]

        if ids:
            for doc, id in zip(docs, ids):
                doc.metadata["id"] = id  # add ids to documents metadata

            # rate limiter
            docs_txt = "".join(format_docs_plain(docs))
            await self.agent.rate_limiter(
                model_config=self.agent.config.embeddings_model, input=docs_txt
            )

            self.db.add_documents(documents=docs, ids=ids)
            self.save_local()
        return ids

    async def delete_documents_by_ids(self, ids: list[str]):
        # aget_by_ids is not yet implemented in faiss, need to do a workaround
        rem_docs = await self.db.aget_by_ids(
            ids
        )  # existing docs to remove (prevents error)
        if rem_docs:
            rem_ids = [doc.metadata["id"] for doc in rem_docs]  # ids to remove
            await self.db.adelete(ids=rem_ids)
            self.save_local()
        return rem_docs


def format_docs_plain(docs: list[Document]) -> list[str]:
    result = []
    for doc in docs:
        text = ""
        for k, v in doc.metadata.items():
            text += f"{k}: {v}\n"
        text += f"Content: {doc.page_content}"
        result.append(text)
    return result


def cosine_normalizer(val: float) -> float:
    res = (1 + val) / 2
    res = max(
        0, min(1, res)
    )  # float precision can cause values like 1.0000000596046448
    return res


def get_comparator(condition: str):
    def comparator(data: dict[str, Any]):
        try:
            result = eval(condition, {}, data)
            return result
        except Exception as e:
            # PrintStyle.error(f"Error evaluating condition: {e}")
            return False

    return comparator
