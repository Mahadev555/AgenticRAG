# 🤖 Agno-AgenticRAG

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15.2.4-black.svg)](https://nextjs.org/)
[![FlaskAPI](https://img.shields.io/badge/FlaskAPI-latest-teal.svg)](http://flask.palletsprojects.com/en/stable/)
[![Agno](https://img.shields.io/badge/Agno-0.1.0-orange.svg)](https://github.com/agno-agi/agno)

A modern web application that combines RAG (Retrieval-Augmented Generation) with agentic capabilities for intelligent document processing and querying. This project uses the [Agno framework](https://docs.agno.com/introduction) for building intelligent agents that can understand and process documents effectively.

## About Agno Integration

This project leverages the [Agno framework](https://github.com/agno-agi/agno) to create intelligent agents that can:
- Process and understand documents contextually
- Handle complex queries with multi-step reasoning
- Combine knowledge from multiple sources
- Provide accurate and relevant responses

## 📋 Table of Contents

- [Project Structure](#-project-structure)
- [Diagram](#-diagram)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Running the Application](#-running-the-application)
- [Development Notes](#-development-notes)
- [Dependencies](#-dependencies)

## 📁 Project Structure

```
AgenticRAG/
├── app/
│   ├── backend/           # Python backend server
│   │   ├── agno_agent_kb.py       # Agent implementation
│   │   ├── app.py         # FastAPI server
│   │   └── knowledge_base.py  # Tabular data parsing
│   └── frontend/          # Next.js frontend application
│       ├── src/           # Source code
│       ├── public/        # Static assets
│       └── package.json   # Frontend dependencies
├── data/                  # Data directory
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

## Diagram
<img src="./image.png"></img>

## ✨ Features

- 📄 **Document preprocessing** and parsing
- 📊 **Tabular data support** (Excel, CSV) (Upcoming)
- 🔍 **Intelligent search** capabilities
- 🧠 **Agent-based** query processing
- 💻 **Modern web interface**

## 🛠️ Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Docker (for running pgvector database)

## 🚀 Installation

### 1. Set up PostgreSQL Vector Database

```bash
# Start the pgvector container
docker run --name pgvector-container -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain -p 6024:5432 -d pgvector/pgvector:pg16

# Verify the container is running
docker ps
```

The vector database will be accessible at:
- Host: localhost
- Port: 6024
- User: langchain
- Password: langchain
- Database: langchain

### 2. Clone the repository

```bash
git clone https://github.com/mahadev555/AgenticRAG.git
cd AgenticRAG
```

### 3. Set up the Python environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate

# Install dependencies (from backend directory)
cd app/backend
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory with the following variables:

```bash
# OpenAI API Key for the Agno framework
OPENAI_API_KEY=your-openai-api-key-here

# Azure OpenAI Configuration (if using Azure)
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=your-azure-endpoint
AZURE_OPENAI_MODEL_NAME=your-model-deployment-name
AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# PostgreSQL Vector Database Configuration (using pgvector)
DB_URL=postgresql+psycopg://langchain:langchain@localhost:6024/langchain

# Computing Device (cpu or cuda for GPU)
DEVICE=cpu
```

Make sure to:
- Replace `your-openai-api-key-here` with your actual OpenAI API key
- Update the PostgreSQL connection string with your database credentials
- Set DEVICE to "cuda" if you want to use GPU acceleration (requires CUDA-compatible GPU)

### 5. Install and build frontend

```bash
cd ../frontend
npm install
npm run build
```

## 🖥️ Running the Application

### 1. Start the backend server

```bash
# Make sure you're in the backend directory
cd app/backend
python -m app
```
The backend server will start running on `http://localhost:5000`

### 2. Access the Application

After starting the backend server, you can access the application directly at `http://localhost:5000`. The frontend is served by the Flask backend, so you don't need to run a separate frontend development server.

## 💻 Development Notes

- Backend runs on Flask server at port 5000
- Frontend is built and served statically through the Flask backend
- The application uses a unified server approach where Flask serves both the API and static frontend files
- To make frontend changes, rebuild using `npm run build` in the frontend directory
- Use `pip install --upgrade pip` to keep pip updated to the latest version

## 📦 Dependencies

### Backend
- Flask >= 3.1.0
- flask-cors >= 5.0.1
- uvicorn >= 0.34.0
- langchain-postgres >= 0.0.13
- pgvector >= 0.3.6
- PyMuPDF >= 1.25.4
- pandas >= 2.2.3
- agno == 0.1.0
- openai >= 1.1.0
- python-dotenv >= 1.1.0

### Frontend
- React 19
- Next.js 15.2.4
- TypeScript

---

Made with ❤️ and 🧠 by Mahadev Manerikar (Atharv)
