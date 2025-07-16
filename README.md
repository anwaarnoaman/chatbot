🚀 Project Setup & Execution Guide

📦 1. Run the Full App with Docker Compose

    This launches both the FastAPI backend and Streamlit frontend in isolated containers.

# From project root (where docker-compose.yml is)
docker compose up --build

    FastAPI backend (inference API): http://localhost:8063

    Streamlit frontend (chat UI): http://localhost:8501

To stop:

docker compose down

🧪 2. Run Backend and Frontend Separately (Without Docker)
✅ Backend (FastAPI)

cd inference_api
uvicorn app:app --reload --host 0.0.0.0 --port 8063

✅ Frontend (Streamlit)

cd chat_app
streamlit run app.py

🐍 3. Run Locally with Virtual Environment (No Docker)
Step 1: Create and activate virtual environment

# From project root
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

Step 2: Install dependencies

pip install --upgrade pip
pip install -r requirements.txt

Step 3: Run backend and frontend

# In one terminal/tab
cd inference_api
uvicorn app:app --reload --host 0.0.0.0 --port 8063

# In another terminal/tab
cd chat_app
streamlit run app.py

⚙️ Environment Configuration

    Ensure chat_app uses the correct API URL (e.g., http://localhost:8063) for local development.

    For Docker, the compose network allows inference_api to be reached at http://inference_api:8063.

