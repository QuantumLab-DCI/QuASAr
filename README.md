# FMweb-K-Quantum

Unified platform for quantum simulations, machine learning, and job management using Qiskit and Cirq.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) and npm
- [Docker](https://www.docker.com/) (if containerized services are required)

## Clone the Repository

```bash
git clone <repository-url>
cd Scandia05-ML-FMweb-K-Quantum
```

---

## Backend Setup and Installation (Python)

The Flask-based backend handles API integrations and Qiskit and Cirq processes.

1. **Navigate to the Backend directory:**
   ```bash
   cd Backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source .venv/bin/activate
     ```

4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the environment variables:**
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file to add the required credentials (such as `IBM_QUANTUM_TOKEN`, `GEMINI_API_KEY`, etc.).

6. **Run the Backend server:**
   ```bash
   python main.py
   ```
   > By default, the backend will run at `http://localhost:5000` (or the configured port).

---

## Frontend Setup and Installation (React + Vite)

The frontend is built with React and Vite.

1. **Open a new terminal** (keep the backend running).

2. **Navigate to the Frontend directory:**
   ```bash
   cd Frontend
   ```

3. **Install the Node dependencies:**
   ```bash
   npm install
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```
   > The development frontend will typically open at `http://localhost:5173`. Visit that URL in your browser to view the application.
