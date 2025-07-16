🚀 Project Setup & Execution Guide (Python 3.13.5)

🐍 1. Run Locally with Virtual Environment (No Docker)

✅ Step 1: Create and activate virtual environment
From the project root:

python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
✅ Step 2: Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
✅ Step 3: Run backend and frontend
🔧 Backend (FastAPI):

cd inference_api
uvicorn app:app --reload --host 0.0.0.0 --port 8063
💬 Frontend (Streamlit):

Open another terminal/tab:

cd chat_app
streamlit run app.py
🧪 2. Run Backend and Frontend Separately (Without Docker)

Use this if dependencies are already available locally.

✅ Backend (FastAPI)
cd inference_api
uvicorn app:app --reload --host 0.0.0.0 --port 8063
✅ Frontend (Streamlit)
cd chat_app
streamlit run app.py
🐳 3. Run Backend and Frontend Separately with Docker (Without Compose)

Build and run each service manually.

🔧 Backend (inference_api)
cd inference_api
docker build -t inference_api -f Dockerfile.inference_api .
docker run -p 8063:8063 inference_api
💬 Frontend (chat_app)
In a new terminal/tab:

cd chat_app
docker build -t chat_app -f Dockerfile.chat_app .
docker run -p 8501:8501 chat_app
📦 4. Run the Full App with Docker Compose

This runs both backend and frontend together with isolated networking.

▶️ Start the full stack:
From the project root:

docker compose up --build
🔗 FastAPI backend: http://localhost:8063
🔗 Streamlit frontend: http://localhost:8501
⏹️ To stop everything:
docker compose down
⚙️ Environment Configuration Notes

When running locally (venv/manual):
Ensure chat_app connects to:
http://localhost:8063
When using Docker Compose:
The frontend should connect to the backend via:
http://inference_api:8063
(Docker Compose sets up internal DNS-based networking.)
