# FMweb-K-Quantum

FMweb-K-Quantum is a research artifact for studying self-adaptation in a hybrid
quantum-classical (HQC) system. It models an air-quality management product line,
observes stochastic operating scenarios, and uses a MAPE-K feedback loop to select
and enact a feature configuration. The artifact combines Gemini-assisted decision
making, feature-model validation, Qiskit or Cirq simulation, optional Docker
service reconfiguration, and a React dashboard for inspecting each adaptation.

<div align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?logo=python&logoColor=white" alt="Python 3.10 or 3.11"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white" alt="Flask 3.0"></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-19-20232A?logo=react&logoColor=61DAFB" alt="React 19"></a>
  <a href="https://www.ibm.com/quantum/qiskit"><img src="https://img.shields.io/badge/Qiskit-0.45-6929C4?logo=qiskit&logoColor=white" alt="Qiskit 0.45"></a>
  <a href="https://quantumai.google/cirq"><img src="https://img.shields.io/badge/Cirq-1.3-4285F4" alt="Cirq 1.3"></a>
</div>

## Contents

- [Research context](#research-context)
- [Architecture](#architecture)
- [MAPE-K feedback loop](#mape-k-feedback-loop)
- [Setup](#setup)
- [API routes](#api-routes)
- [Verification](#verification)
- [Documentation](#documentation)
- [Reproducibility notes](#reproducibility-notes)

## Research context

The artifact supports experimentation with runtime variability in an HQC software
product line. A selected scenario supplies simulated environmental, workload,
infrastructure, and user observations. The system derives a configuration that
must satisfy the feature model, applies available classical service changes, and
runs a QAOA or VQE workload when the selected configuration enables the quantum
branch. The dashboard exposes the monitored context, decision rationale,
configuration graph, execution evidence, logs, and phase trace.

## Architecture

| Component | Responsibility |
| --- | --- |
| `Frontend/` | React 19 and Vite dashboard; selects scenarios and polls backend state and logs every three seconds. |
| `Backend/run.py` | Primary Flask entry point; loads `.env`, creates the application, generates the feature-model visualization, and listens on port `8000`. |
| `Backend/app/api/` | Dashboard, control, artifact, and transitional HTTP routes under `/api`. |
| `Backend/app/core/` | Feature model, variation point, process-local knowledge base, MAPE-K controller, and phase implementations. |
| `Backend/app/services/` | Gemini integration, Qiskit/Cirq adapters, Docker API bridge, file access, and graph generation. |
| `Backend/data/` | Scenario definitions and generated runtime logs, graphs, and quantum evidence. |

Scenario selection starts one background adaptation thread. Shared runtime state is
held by the process-local `KnowledgeBase`; this implementation is therefore a
single-process research prototype rather than a distributed state service.

## MAPE-K feedback loop

MAPE-K denotes **Monitor, Analyze, Plan, Execute over shared Knowledge**:

1. **Monitor** samples the selected scenario's air-quality index, problem
   complexity, Qiskit queue time, SLA priority, and user profile.
2. **Analyze** combines those observations with backend metrics, requests a
   Gemini configuration, and rejects configurations that violate feature-model
   constraints.
3. **Plan** converts the accepted features into a runtime `VariationPoint` and
   records it as knowledge.
4. **Execute** starts or stops matching Docker containers when available and runs
   the selected Qiskit or Cirq workload when HQC features are enabled.
5. **Knowledge** retains the feature model, current variation point, monitored
   context, selected scenario, running status, and trace exposed by the API.

## Setup

### Prerequisites

For the Docker Compose setup:

- Docker with the Compose plugin
- A Google API key with access to `models/gemini-2.5-flash`

For the manual setup:

- `uv` (Python 3.10 is pinned and installed automatically when needed)
- Node.js `^20.19.0` or `>=22.12.0` and npm, as required by the locked Vite package
- [Graphviz](https://graphviz.org/) with the `dot` executable on `PATH`
- A Google API key with access to `models/gemini-2.5-flash`
- Optional: a running Docker daemon if the experiment should inspect or
  reconfigure containers

TensorFlow Quantum provides the required wheel for Linux x86_64. Docker Compose
runs the backend as `linux/amd64`, including through Docker Desktop emulation on
ARM hosts. The manual backend setup therefore requires a Linux x86_64 environment.

Docker Compose is the recommended option for a reproducible development setup. It
does not require host installations of Python, Node.js, or Graphviz because the
application dependencies are installed inside the images.

### Docker Compose

From the repository root, create the backend environment file and set a valid
Google API key:

```bash
cp Backend/.env.example Backend/.env
```

Then build and start both services:

```bash
docker compose up --build
```

Open `http://localhost:5173`. The backend API remains available at
`http://localhost:8000`. Source directories are mounted into the containers, so
Vite and Flask reload when their source files change. Stop the services with
`docker compose down`.

The backend mounts `/var/run/docker.sock` so the MAPE-K executor can inspect,
start, and stop existing containers. Access to this socket effectively grants the
backend control over the host Docker daemon; only run trusted backend code with
this configuration.

The first backend image build can take several minutes because it installs the
TensorFlow, Qiskit, and Cirq stacks. Later builds reuse Docker's dependency cache.

The manual setup below remains available when Docker Compose is not desired.

### Backend

From the repository root:

```bash
cd Backend
uv sync --locked
cp .env.example .env
```

Set the variable copied from `Backend/.env.example`:

| Variable | Purpose |
| --- | --- |
| `GOOGLE_API_KEY` | Authenticates Gemini requests made during the Analyze phase. |

Do not commit the populated `.env` file. Start the backend through the primary
entry point:

```bash
uv run --locked python run.py
```

The API is available at `http://127.0.0.1:8000`. The server binds to `0.0.0.0`;
the host and port are constants in `Backend/app/config.py`, not environment
variables.

### Frontend

In a second terminal, from the repository root:

```bash
cd Frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. The current frontend has no `.env` configuration
and connects directly to `http://127.0.0.1:8000`; run the backend on its configured
port. See the [frontend README](Frontend/README.md) for interface-specific details.

## API routes

All routes are served by the Flask backend on port `8000`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/scenarios` | Return the stochastic scenarios defined in `Backend/data/scenarios.json`. |
| `POST` | `/api/select-scenario` | Start a MAPE-K cycle; JSON body: `{"scenario_id": 1}`. Returns `423` while another cycle is running. |
| `GET` | `/api/state` | Return context, configuration, artifact URLs, running status, and the MAPE-K trace. Returns `503` before a cycle establishes state. |
| `GET` | `/api/logs` | Return the adaptation log content. |
| `GET` | `/api/static/<filename>` | Serve a generated graph or quantum evidence file. |
| `GET` | `/api/links/<name>` | Return a named configuration level through the transitional service API. |
| `GET` | `/api/link/<name>` | Return the state of a named feature through the transitional service API. |
| `GET` | `/api/adaptation-rule` | Return the current monitored context and adaptation rationale. |
| `GET` | `/api/container_logs/<container_name>` | Return recent output from a Docker container through the API bridge. |

For a running backend, initiate and inspect a cycle with:

```bash
curl http://127.0.0.1:8000/api/scenarios
curl -X POST http://127.0.0.1:8000/api/select-scenario \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id": 1}'
curl http://127.0.0.1:8000/api/state
```

The adaptation runs asynchronously; wait until `is_running` is `false` before
interpreting the final state.

## Verification

The repository provides a backend architecture verifier and frontend static
checks, but no automated test suite:

```bash
cd Backend
uv run --locked python verify_backend.py

cd ../Frontend
npm run lint
npm run build
```

`verify_backend.py` checks imports, application initialization, MAPE-K phase
construction, and required route registration. It does not execute a complete
Gemini or quantum adaptation cycle.

## Documentation

- [Frontend README](Frontend/README.md): dashboard setup, integration behavior,
  source layout, and available npm commands.
- Backend implementation documentation is maintained in module docstrings under
  `Backend/app/`; no separate backend README is present.

## Reproducibility notes

Scenario observations and backend metrics are sampled at runtime, and adaptation
decisions depend on an external Gemini model. Results can therefore differ across
runs even for the same scenario. Generated evidence and logs are written under
`Backend/data/`. Docker reconfiguration affects only pre-existing containers whose
names match selected English feature keys; this repository does not provision them.
The dashboard integrations expect `air_quality_manager`, `tourism`, `sports`, and
`hybrid_quantum_computing` when those managed-service containers are deployed.
