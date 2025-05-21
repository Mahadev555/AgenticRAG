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
from agno.storage.sqlite import SqliteStorage
from agno.knowledge.pdf import PDFKnowledgeBase   

# Load environment variables
load_dotenv()
db_url = "postgresql+psycopg://agno:agno@localhost:6024/agno"

# Setup reporting directories

gemini_model = Gemini(id='gemini-2.0-flash')

class RAGWorkflow(Workflow):
    """Advanced workflow for Retrieval Augmented Generation."""

    description: str = dedent("""\
    An intelligent RAG system that processes queries through query refinement 
    and knowledge base search while maintaining accuracy and relevance.""")

    knowledge_base  = PDFKnowledgeBase(
    path="data/pdfs",
    vector_db=PgVector(
            table_name="bray_mtr",
            db_url=db_url,
            search_type=SearchType.hybrid,
            embedder=GeminiEmbedder()
        )
    
    )


    """Advanced workflow for Retrieval Augmented Generation with multiple specialized agents."""
    # knowledge_base.load(recreate=False)


    rag_agent :Agent = Agent(
    name="RAG Agent",
    agent_id="rag-agent",
    model=gemini_model,
    knowledge=knowledge_base,
    search_knowledge=True,
    read_chat_history=True,
    instructions=[
        "You are a helpful assistant that answers questions based on the provided knowledge base.",
        "Always search and reference the knowledge base for accurate information.",
        "When responding, follow these rules:",
        "- Always cite the source PDF filename and page number for each piece of information",
        "- For table data: Extract and present exact values from tables in a structured format",
        "- For tabular information, maintain the original column headers and row relationships ad dyou logic to handle table format cause there is not boundry is given ",
        "- When numerical values are found in tables, ensure accuracy in reporting numbers and units",
        "- For paragraph information, summarize key points concisely",
        "- Include specific values, measurements, and numbers when available",
        "- Keep responses focused and under 10 sentences",
        "- If information is not found in knowledge base, clearly state that",
        "- Format the reference as: [Source: {PDF_name}, Page {number}]"
    ],
    markdown=True,
    debug_mode=True
)


    def run(self, question: str) -> Iterator[RunResponse]:
        import asyncio
        logger.info(f"Processing question: {question}")


        search_response: RunResponse = self.rag_agent.run(question)

        if search_response and search_response.content:
            yield RunResponse(
                event=RunEvent.workflow_completed,
                content=search_response.content,
            )
        else:
            yield RunResponse(
                event=RunEvent.workflow_completed,
                content="Sorry, could not process the search results.",
            )



# Run the workflow if the script is executed directly
if __name__ == "__main__":
    from rich.prompt import Prompt
    import json

    # Get question from user
    question = "Hii"

    # Initialize the RAG workflow
    rag_workflow = RAGWorkflow(
        session_id=f"rag-query-{hash(question)}",
        storage=SqliteStorage(
            table_name="rag_workflows",
            db_file="tmp/agno_workflows.db",
        ),
    )

    # Execute the workflow
    response: Iterator[RunResponse] = rag_workflow.run(question=question)

    # Print the response
    pprint_run_response(response, markdown=True)

 