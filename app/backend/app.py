from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from agno_agent_kb import process_user_query
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
    
    # Process the query through our agent team
    response = process_user_query(
        query=question,
        session_id=session_id,
        user_id=user_id
    )
    
    return {"answer": str(response.content)}, 200

if __name__ == "__main__":
    app.run()