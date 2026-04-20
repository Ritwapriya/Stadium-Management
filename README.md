# 🏟️ Smart Stadium AI – Multi-Agent Experience Optimizer

A production-grade, real-time multi-agent system designed to optimize the attendee experience during large-scale events. The system uses a **hybrid event-driven + shared-state architecture**, where Redis acts both as a pub/sub bus and a low-latency context store, enabling agents to operate independently while maintaining global awareness.

---

## 🏗️ Architecture Overview

The system is built on a clean event-driven pipeline:

1.  **Simulators**: Emission of raw data (`sensor.raw`, `queue.raw`, `user.context`).
2.  **Redis PubSub**: The high-speed event bus routing raw data to agents.
3.  **Agents**: Independent, asynchronous workers that:
    *   Read from a raw input topic.
    *   Process data (e.g., compute densities, predict wait times).
    *   Write the processed state to **Shared Context** (Redis) with a 30s TTL.
    *   Publish results back to output topics (e.g., `crowd.density`).
4.  **WebSocket Manager**: Bridges Redis output topics directly to active UI clients.
5.  **Streamlit UI**: A live, interactive dashboard displaying hotspots, wait times, recommendations, and a grounded AI chat.

---

## 📂 Project Structure

```text
stadium/
├── docker-compose.yml       # Redis & MongoDB setup
├── .env                     # Configuration keys
├── backend/
│   ├── main.py              # FastAPI Entry Point
│   ├── agents/              # Multi-agent workers
│   ├── bus/                 # Event bus & Shared context logic
│   ├── core/                # WebSocket & Match phase logic
│   ├── routers/             # API Endpoints (WS, Chat, Context)
│   └── simulators/          # Data generation scripts
└── frontend/
    └── app.py               # Streamlit Dashboard
```

---

## 🚀 Quick Start

### 1. Prerequisite: Infrastructure
Start the Redis and MongoDB containers:
```bash
docker-compose up -d
```

### 2. Backend Setup
Install dependencies and run the FastAPI server:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Simulator Setup
Start the data simulations in a new terminal:
```bash
python backend/simulators/run_simulators.py
```

### 4. Frontend Setup
Launch the dashboard in another terminal:
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

---

## 🎯 Key Features

*   **Match Phase Engine**: Dynamically shifts strategies based on `PRE`, `LIVE`, `HALFTIME`, and `POST` match phases.
*   **Confidence-Driven Recommendations**: Every recommendation comes with a explainable reason and a confidence score.
*   **Staff Alert Triggers**: Automatically flags issues (e.g., >10m wait times) to a staff alert system.
*   **Grounded AI Chat**: Powered by Gemini, the chat agent "sees" the entire live stadium context before answering.

---

## ⚖️ License
MIT
