from textwrap import dedent
import os
from typing import Iterator, List
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.workflow import Workflow
from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings

# model = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2", model_kwargs = {"device": os.getenv("DEVICE","cpu")})

# vector_store = PGVector(
#     embeddings=model,
#     collection_name=os.getenv("COLLECTION_NAME","my_docs"),
#     connection=os.getenv("POSTGRES_CONNECTION_STRING"),
#     use_jsonb=True,
# )

# def search(self, query: str) -> list:
#         """
#         Executes a similarity search based on the provided query.

#         Args:
#             query (str): The search query.

#         Returns:
#             list: A list of search results.
#         """
#         results = vector_store.similarity_search(query)
#         return results

class RAGWorkflow(Workflow):
    def __init__(self):
        super().__init__()
        # self.search_tool = SearchToolWrapper()

        self.root_agent = Agent(
            name="Root Agent",
            role="Root coordinator that handles user interaction",
            model=OpenAIChat(api_key=os.getenv("OPENAI_API_KEY")),
            instructions=dedent("""
                You are a root agent. You will interact with user and assist with answers.
                Your job is to handover the user query to the Query Agent who will break it into multiple search queries.
                You will get the answer from the Assistant Agent - do not terminate until you get a satisfactory answer.
                Only end the conversation when you have a complete answer for the user.
            """)
        )

        self.query_agent = Agent(
            name="Query Agent",
            role="Break down user queries into search queries",
            model=OpenAIChat(api_key=os.getenv("OPENAI_API_KEY")),
            instructions=dedent("""
                You are a Query Agent. You will get user queries from the Root Agent and generate search queries.
                Follow these rules:
                - Use a maximum of 3 search queries
                - Ensure queries fetch different relevant data from knowledge base
                - Break down user query into specific search queries
                - Generate search queries in English
                - Never terminate the conversation directly
            """)
        )

        self.assistant_agent = Agent(
            name="Assistant Agent", 
            role="Search knowledge base and generate answers",
            model=OpenAIChat(api_key=os.getenv("OPENAI_API_KEY")),
            # tools=[self.search_tool.search],
            instructions=dedent("""
                You are a helpful assistant. Your job is to search information in the knowledge base and give answers.
                Follow these rules:
                - You will get search strings from the Query Agent
                - Use the search tool to retrieve information for all search strings
                - Answer based only on information retrieved from knowledge base
                After generating answer pass it to the Root Agent
            """)
        )

        self.agent_team = Team(
            name="RAG Team",
            mode="collaborate",
            model=OpenAIChat(api_key=os.getenv("OPENAI_API_KEY")),
            members=[
                self.root_agent,
                self.query_agent,
                self.assistant_agent
            ],
            instructions=[
                "Coordinate between agents to process user queries and generate answers",
                "Follow the workflow: Root Agent → Query Agent → Assistant Agent → Root Agent",
                "Ensure all answers are based on knowledge base searches",
            ],
            success_criteria="The team has provided a complete answer based on knowledge base",
            enable_agentic_context=True,
            show_tool_calls=True,
            markdown=True,
        )

    async def kickoff(self, question: str, history: List[dict] = None) -> str:
        """
        Start the RAG workflow with a user question and optional chat history
        """
        if history is None:
            history = []
            
        # Convert history to format expected by Agno
        formatted_history = []
        for msg in history:
            formatted_history.append({
                "content": msg["content"],
                "role": msg["role"]
            })

        # Run the workflow through the agent team
        response = await self.agent_team.arun(
            f"Process this user query and provide an answer: {question}",
            context={"chat_history": formatted_history}
        )
        
        if response and response.content:
            return response.content
        return "Sorry, I could not process your request."