import os  
from agno.agent import Agent  
from agno.models.azure import AzureOpenAI  
from agno.storage.postgres import PostgresStorage  
from dotenv import load_dotenv
from agno.team.team import Team

from knowledge_base import create_knowledge_base  
  
# Load environment variables  
load_dotenv()  
db_url = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  
  
# Initialize Azure OpenAI model  
azure_model = AzureOpenAI(  
    id=os.getenv("AZURE_OPENAI_MODEL_NAME"),  
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  
    max_tokens=16384,  
)  
  
# Create storage for the agent sessions  
storage = PostgresStorage(  
    db_url=db_url,  
    table_name="rag_agent_sessions"  
)  
  
# Example 1: Create knowledge base from local PDF files  
local_knowledge = create_knowledge_base(  
    source="data/pdfs",  
    table_name="local_pdfs",  
    recreate=False,  
    chunk=True  
)  
  
# Example 2: Create knowledge base from PDF URLs  
url_knowledge = create_knowledge_base(  
    source=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],  
    table_name="url_pdfs",  
    recreate=False  
)  
  
# Create a combined agent that can use both knowledge bases  
from agno.knowledge.combined import CombinedKnowledgeBase  
  
combined_knowledge = CombinedKnowledgeBase(  
    sources=[local_knowledge, url_knowledge],  
    vector_db=local_knowledge.vector_db  # Reuse the vector DB from the first knowledge base  
)  
  
# Initialize the Agent with the combined knowledge base  
rag_agent = Agent(  
    name="RAG Agent",  
    agent_id="rag-agent",  
    model=azure_model,  
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
    debug_mode=True,  
)  

# Create a query processing agent
query_processor = Agent(
    name="Query Processor",
    agent_id="query-processor",
    model=azure_model,
    instructions=[
        "You are a query processing agent that helps improve and refine user queries.",
        "Your task is to analyze the user's query and create a more detailed and structured query.",
        "Extract key information and parameters from the user's query.",
        "Format the query in a way that will get the best results from the knowledge base.",
        "If the query is ambiguous, try to make it more specific.",
        "Maintain the core intent of the original query while improving its clarity."
    ],
    markdown=True,
    debug_mode=True,
)

# Create a team of agents
agent_team = Team(
    name="RAG Team",
    mode="sequential",
    model=azure_model,
    members=[query_processor, rag_agent],
    instructions=[
        "Work together to process and answer user queries effectively.",
        "Query Processor will first refine the query.",
        "RAG Agent will then use the refined query to search the knowledge base.",
    ],
    success_criteria="The team has provided a clear and accurate response based on the knowledge base.",
    enable_agentic_context=True,
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
)

# Process a query using the agent team
def process_user_query(query, session_id="default-session", user_id="default-user"):
    response = agent_team.run(
        message=query,
        session_id=session_id,
        user_id=user_id,
    )
    return response.content

# Example usage  
if __name__ == "__main__":  
    query = "Pressure of Series 31H"  
    response = process_user_query(query)  
    print(response.content)