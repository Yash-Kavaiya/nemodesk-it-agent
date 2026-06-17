# SPDX-License-Identifier: Apache-2.0
"""Knowledge-base retrieval tool (RAG over the IT runbook corpus).

Loads markdown runbooks from a directory, embeds them with an NAT-managed embedder
(NVIDIA NIM embedder by default), and exposes a semantic search tool the agents use
to ground their resolutions in approved runbooks.
"""

from __future__ import annotations

import logging
from pathlib import Path

from nat.builder.builder import Builder
from nat.builder.framework_enum import LLMFrameworkEnum
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.component_ref import EmbedderRef
from nat.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


class KbSearchConfig(FunctionBaseConfig, name="kb_search"):
    """Semantic search over the IT knowledge-base / runbook corpus."""

    kb_dir: str
    embedder_name: EmbedderRef = "nvidia/nv-embedqa-e5-v5"
    chunk_size: int = 800
    top_k: int = 4


@register_function(config_type=KbSearchConfig, framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])
async def kb_search(config: KbSearchConfig, builder: Builder):
    from langchain_community.vectorstores import USearch
    from langchain_core.documents import Document
    from langchain_core.embeddings import Embeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    embeddings: Embeddings = await builder.get_embedder(config.embedder_name,
                                                        wrapper_type=LLMFrameworkEnum.LANGCHAIN)

    kb_path = Path(config.kb_dir)
    raw_docs: list[Document] = []
    for md in sorted(kb_path.glob("*.md")):
        raw_docs.append(Document(page_content=md.read_text(encoding="utf-8"),
                                 metadata={"source": md.name}))
    logger.info("KB search loaded %d runbook file(s) from %s", len(raw_docs), kb_path)

    splitter = RecursiveCharacterTextSplitter(chunk_size=config.chunk_size, chunk_overlap=100)
    chunks = splitter.split_documents(raw_docs) if raw_docs else [
        Document(page_content="No runbooks found.", metadata={"source": "empty"})]

    vector = await USearch.afrom_documents(chunks, embeddings)
    retriever = vector.as_retriever(search_kwargs={"k": config.top_k})

    async def _search(query: str) -> str:
        """Search approved IT runbooks for a problem and return the most relevant excerpts."""
        docs = await retriever.ainvoke(query)
        if not docs:
            return "No matching runbook found."
        out = []
        for d in docs:
            out.append(f"[{d.metadata.get('source', '?')}]\n{d.page_content.strip()}")
        return "\n\n---\n\n".join(out)

    yield FunctionInfo.from_fn(
        _search,
        description=(
            "Search the approved IT knowledge base / runbooks for resolution steps. "
            "Input: a short description of the problem. Output: relevant runbook excerpts."
        ),
    )
