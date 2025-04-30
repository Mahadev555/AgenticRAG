from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from agno_agent_kb import rag_workflow  # Import the workflow instance
import os
import dotenv

dotenv.load_dotenv()
app = Flask(__name__, static_folder="static")
CORS(app)  # Enable CORS for all routes

@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

@app.route("/agno_ask", methods=["POST"])
async def agno_ask():
    question = request.json["question"]
    session_id = request.json.get("session_id", "default-session")
    user_id = request.json.get("user_id", "default-user")
    
    # Use the RAG workflow to process the query
    response = rag_workflow.run(question)
    
    return {"answer": str(response.content)}, 200

if __name__ == "__main__":
    app.run()