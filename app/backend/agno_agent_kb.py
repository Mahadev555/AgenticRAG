"""
AgenticRAG Knowledge Base and Agent Configuration

This module sets up the RAG (Retrieval Augmented Generation) system using the Agno framework.
It configures the vector database, knowledge bases, and intelligent agents for document processing.
"""

import os
from dotenv import load_dotenv
from typing import Optional

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.postgres import PostgresStorage
from agno.workflow.workflow import Workflow
from agno.run.response import RunResponse, RunEvent
from agno.vectordb.pgvector import PgVector, SearchType
from agno.embedder.google import GeminiEmbedder
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.utils.log import logger

from knowledge_base import create_knowledge_base

# Load environment variables
load_dotenv()
db_url = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"

# Initialize Gemini model
gemini_model = Gemini(id='gemini-2.0-flash')

# Create storage for agent sessions
storage = PostgresStorage(
    db_url=db_url,
    table_name="rag_agent_sessions"
)

# Initialize vector database configuration
vector_db_config = PgVector(
    table_name="local_pdfs",
    db_url=db_url,
    search_type=SearchType.hybrid,
    embedder=GeminiEmbedder()
)

# Create knowledge base from local PDF files
local_knowledge = create_knowledge_base(
    source="data/pdfs",
    table_name="local_pdfs",
    recreate=False,
    chunk=True,
    embedder=GeminiEmbedder(),
    vector_db=vector_db_config
)

# Create knowledge base from PDF URLs
url_knowledge = create_knowledge_base(
    source=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    table_name="url_pdfs",
    recreate=False,
    embedder=GeminiEmbedder(),
    vector_db=vector_db_config
)

# Create a combined knowledge base
combined_knowledge = CombinedKnowledgeBase(
    sources=[local_knowledge, url_knowledge],
    vector_db=local_knowledge.vector_db
)



class RAGWorkflow(Workflow):  
    """Workflow that combines query processing and RAG agents."""  
    description: str = "Process user queries through query refinement and knowledge base search."  
  
    # Initialize the RAG Agent
    rag_agent = Agent(
        name="RAG Agent",
        agent_id="rag-agent",
        model=gemini_model,
        knowledge=combined_knowledge,
        search_knowledge=True,
        read_chat_history=True,
        storage=storage,
        instructions=[
            "Always search your knowledge base first and use it if available.",
            "Share the page number or source URL of the information you used in your response.",
            "If values are mentioned, include them in the response.",
            "Important: Use tables where possible.",
        ],
        markdown=True,
        debug_mode=True
    )

    # Initialize the Query Processing Agent
    query_processor = Agent(
        name="Query Processor",
        agent_id="query-processor",
        model=gemini_model,
        instructions=[
            "You are a query processing agent that helps improve and refine user queries.",
            "Your task is to analyze the user's query and create a more detailed and structured query.",
            "Extract key information and parameters from the user's query.",
            "Format the query in a way that will get the best results from the knowledge base.",
            "If the query is ambiguous, try to make it more specific.",
            "Maintain the core intent of the original query while improving its clarity."
        ],
        markdown=True,
        debug_mode=True
    )
  
    def run(self, query: str) -> RunResponse:  
        """  
        Process a user query through the agent team.  
  
        Args:  
            query (str): The user's query to process  
  
        Returns:  
            RunResponse: The processed response from the agent team  
        """  
  
        # Process query through query processor  
        query_response = self.query_processor.run(  
            query  
        )  
  
        if not query_response or not query_response.content:  
            return RunResponse(  
                run_id=self.run_id,  
                event=RunEvent.workflow_completed,  
                content="Sorry, could not process your query."  
            )  
  
        # Use processed query to search knowledge base  
        rag_response: RunResponse = self.rag_agent.run(  
            message=query_response.content,  
            session_id=self.session_id,  
            user_id=self.user_id  
        )  
  
        return rag_response

# Create workflow instance
rag_workflow = RAGWorkflow(
    session_id="rag-workflow",
    storage=storage
)

query = "What is Container as a Service (CaaS)?"
response = rag_workflow.run(query)
print(response.content)