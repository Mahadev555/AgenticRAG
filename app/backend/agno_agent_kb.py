"""
AgenticRAG Knowledge Base and Agent Configuration

This module sets up the RAG (Retrieval Augmented Generation) system using the Agno framework.
It configures the vector database, knowledge bases, and intelligent agents for document processing.
"""

import os
from pathlib import Path
from shutil import rmtree
from textwrap import dedent
from typing import Iterator, Optional
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.postgres import PostgresStorage
from agno.workflow.workflow import Workflow
from agno.run.response import RunResponse, RunEvent
from agno.vectordb.pgvector import PgVector, SearchType
from agno.embedder.google import GeminiEmbedder
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response

# Load environment variables
load_dotenv()
db_url = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"

# Setup reporting directories
reports_dir = Path(__file__).parent.joinpath("reports", "rag")
if reports_dir.is_dir():
    rmtree(path=reports_dir, ignore_errors=True)
reports_dir.mkdir(parents=True, exist_ok=True)

# Report file paths
query_report = str(reports_dir.joinpath("query_report.json"))
search_report = str(reports_dir.joinpath("search_report.json"))
final_report = str(reports_dir.joinpath("final_report.md"))

class RAGWorkflow(Workflow):
    """Advanced workflow for Retrieval Augmented Generation."""

    description: str = dedent("""\
    An intelligent RAG system that processes queries through query refinement 
    and knowledge base search while maintaining accuracy and relevance.""")

    def __init__(self, session_id: str, storage: PostgresStorage):
        """Initialize the RAG workflow with required components."""
        super().__init__(session_id=session_id, storage=storage)

        # Initialize Gemini model
        self.gemini_model = Gemini(id='gemini-2.0-flash')

        # Initialize vector database configuration
        self.vector_db = PgVector(
            table_name="local_pdfs",
            db_url=db_url,
            search_type=SearchType.hybrid,
            embedder=GeminiEmbedder()
        )

        # Create knowledge bases
        self.local_knowledge = self._create_local_knowledge()
        self.url_knowledge = self._create_url_knowledge()
        self.combined_knowledge = CombinedKnowledgeBase(
            sources=[self.local_knowledge, self.url_knowledge],
            vector_db=self.local_knowledge.vector_db
        )

        # Initialize agents
        self.query_processor = Agent(
            name="Query Processor",
            agent_id="query-processor",
            model=self.gemini_model,
            instructions=dedent("""\
                You are a query processing agent that helps improve and refine user queries.
                Your task is to:
                - Analyze and enhance user queries for better clarity
                - Extract key information and parameters
                - Make ambiguous queries more specific
                - Maintain the original query intent
                """),
            markdown=True,
            debug_mode=True,
            save_response_to_file=query_report
        )

        self.rag_agent = Agent(
            name="RAG Agent",
            agent_id="rag-agent",
            model=self.gemini_model,
            knowledge=self.combined_knowledge,
            search_knowledge=True,
            read_chat_history=True,
            storage=storage,
            instructions=dedent("""\
                - Always search knowledge base first
                - Include source references (page numbers/URLs)
                - Include specific values when mentioned
                - Use tables where appropriate for clarity
                """),
            markdown=True,
            debug_mode=True,
            save_response_to_file=search_report
        )

    def _create_local_knowledge(self):
        """Create knowledge base from local PDF files."""
        from knowledge_base import create_knowledge_base
        return create_knowledge_base(
            source="data/pdfs",
            table_name="local_pdfs",
            recreate=False,
            chunk=True,
            embedder=GeminiEmbedder(),
            vector_db=self.vector_db
        )

    def _create_url_knowledge(self):
        """Create knowledge base from PDF URLs."""
        from knowledge_base import create_knowledge_base
        return create_knowledge_base(
            source=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
            table_name="url_pdfs",
            recreate=False,
            embedder=GeminiEmbedder(),
            vector_db=self.vector_db
        )

    def run(self, query: str) -> Iterator[RunResponse]:
        """
        Process a user query through the agent team.

        Args:
            query (str): The user's query to process

        Yields:
            Iterator[RunResponse]: The processed responses from the agent team
        """
        logger.info(f"Processing query: {query}")

        # Process query through query processor
        query_response = self.query_processor.run(query)
        if not query_response or not query_response.content:
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content="Sorry, could not process your query."
            )
            return

        # Use processed query to search knowledge base
        rag_response: RunResponse = self.rag_agent.run(
            message=query_response.content,
            session_id=self.session_id,
            user_id=self.user_id
        )

        if rag_response and rag_response.content:
            yield RunResponse(
                event=RunEvent.workflow_completed,
                content=rag_response.content,
            )
        else:
            yield RunResponse(
                event=RunEvent.workflow_completed,
                content="Sorry, could not process the search results.",
            )

if __name__ == "__main__":
    from rich.prompt import Prompt

    # Get query from user
    query = Prompt.ask("[bold]Enter your query[/bold]\n✨")

    # Initialize workflow
    workflow = RAGWorkflow(
        session_id=f"rag-query-{hash(query)}",
        storage=PostgresStorage(
            db_url=db_url,
            table_name="rag_agent_sessions"
        )
    )

    # Execute workflow
    response = workflow.run(query=query)

    # Print response
    pprint_run_response(response, markdown=True)
