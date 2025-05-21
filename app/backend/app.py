from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from agno_agent_kb import RAGWorkflow  # Import the workflow instance
import os
import dotenv 
from dotenv import load_dotenv
from document_upload import handle_file_upload, handle_url_upload

from agno.storage.sqlite import SqliteStorage 
# Load environment variables
load_dotenv()
db_url = "postgresql+psycopg://agno:agno@localhost:6024/agno"

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
def agno_ask():
    data = request.get_json()
    print(f"==>> data: {data}")
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    
    question = request.json["question"]
    # history = request.json["history"]
    # if not isinstance(history, str):
    #     history = json.dumps(history)
    # print(history)
    # Initialize the RAG workflow
    workflow = RAGWorkflow(
        session_id=f"rag-query-{hash(question)}",
        storage=SqliteStorage(
            table_name="rag_workflows",
            db_file="tmp/agno_workflows.db",
        ),
    )
    # Execute the workflow and get response iterator
    workflow_result = list(
        workflow.run(
            question=question,  # Pass the history to the workflow
        )
    )

    last_result = "No result found"
    if workflow_result:  # Ensure the list is not empty
        last_result = workflow_result[-1]
        print("Workflow result: %s", last_result.content)
        return {"answer": last_result.content}, 200
    
    else:
        print("Workflow result: No result found")
        return {"error": "No result found, Please try reformulating your question"}, 404

@app.route("/upload/file", methods=["POST"])
def upload_file():
    """Handle file uploads."""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
        
    recreate_kb = request.form.get('recreate', 'false').lower() == 'true'
    response, status_code = handle_file_upload(file, recreate_kb)
    return jsonify(response), status_code

@app.route("/upload/url", methods=["POST"])
def upload_url():
    """Handle URL-based document additions."""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"success": False, "message": "No URL provided"}), 400
        
    url = data['url']
    recreate_kb = data.get('recreate', False)
    response, status_code = handle_url_upload(url, recreate_kb)
    return jsonify(response), status_code

if __name__ == "__main__":
    app.run()