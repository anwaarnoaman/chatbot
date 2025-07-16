🚀 Project Setup & Execution Guide (Python 3.13.5)



Note: Inference Api 


https://avrioc_inference.jhingaai.com/



🐍 1. Run Locally with Virtual Environment (No Docker)

✅ Step 1: Create and activate virtual environment
From the project root:

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
✅ Step 2: Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
✅ Step 3: Run backend and frontend

🧪 2. Run Backend and Frontend Separately (Without Docker)
 
🔧 Backend (FastAPI):

uvicorn inference_api.app:app --reload --host 0.0.0.0 --port 8063

💬 Frontend (Streamlit):

Open another terminal/tab:
 
streamlit run chat_app/app.py

🐳 3. Run Backend and Frontend Separately with Docker (Without Compose)

Build and run each service manually.

🔧 Backend (inference_api)
 
sudo docker build -t inference_api -f Dockerfile.inference_api .
sudo docker run -p 8063:8063 inference_api
💬 Frontend (chat_app)
In a new terminal/tab:

 
sudo docker build -t chat_app -f Dockerfile.chat_app .
sudo docker run -p 8501:8501 chat_app
📦 4. Run the Full App with Docker Compose

This runs both backend and frontend together with isolated networking.

▶️ Start the full stack:
From the project root:

sudo docker compose up --build
🔗 FastAPI backend: http://localhost:8063
🔗 Streamlit frontend: http://localhost:8501
⏹️ To stop everything:
sudo docker compose down
⚙️ Environment Configuration Notes




When running locally (venv/manual):
Ensure chat_app connects to:

cloud infrence endpoint 

https://avrioc_inference.jhingaai.com/

if running locally 
http://localhost:8063


When using Docker Compose:
The frontend should connect to the backend via:
http://inference_api:8063


(Docker Compose sets up internal DNS-based networking.)


 