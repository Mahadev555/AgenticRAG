from flask import Flask, jsonify, request,  send_from_directory
from flask_cors import CORS
from agent_agno import RAGWorkflow
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
    history = request.json.get("history", [])  # Make history optional
    agent = RAGWorkflow()
    answer = await agent.kickoff(question, history)
    return {"answer": str(answer)}, 200

if __name__ == "__main__":
    app.run()