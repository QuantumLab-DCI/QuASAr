# FMweb-K-Quantum Frontend

This React dashboard is the observation and control interface for the
FMweb-K-Quantum research artifact. It starts scenario-driven adaptation through
the Flask API and presents the MAPE-K phase trace, monitored context, selected
services, feature-model state, quantum execution evidence, and adaptation logs.

See the [project README](../README.md) for the research context, backend setup,
architecture, Docker Compose quick start, and complete API route reference.

## Requirements

- Node.js `^20.19.0` or `>=22.12.0`
- npm
- FMweb-K-Quantum backend running at `http://127.0.0.1:8000`

## Setup

From `Frontend/`:

```bash
npm ci
npm run dev
```

Open `http://localhost:5173`. Select a scenario to start an asynchronous MAPE-K
cycle. The dashboard polls `/api/state` and `/api/logs` every three seconds while
the backend performs the adaptation.

The API base URL is currently defined in `src/hooks/useSystemStatus.js`,
`src/components/ScenarioSelector.jsx`, and `src/components/ServiceInspector.jsx`.
There are no frontend environment variables; changing the backend address requires
updating those constants.

## Source layout

| Path | Responsibility |
| --- | --- |
| `src/App.jsx` | Composes the scenario controls, MAPE-K visualizer, and evidence panels. |
| `src/hooks/useSystemStatus.js` | Polls system state and logs and downloads generated evidence. |
| `src/components/ScenarioSelector.jsx` | Loads scenarios and submits scenario selections. |
| `src/components/PhaseStepper.jsx` | Displays progress through the MAPE-K phases. |
| `src/components/panels/` | Presents context, services, state graphs, quantum evidence, traces, and logs. |

## Commands

```bash
npm run dev      # Start the Vite development server on its default port, 5173
npm run lint     # Run ESLint over the frontend source
npm run build    # Create a production bundle in dist/
npm run preview  # Preview a previously built bundle
```

The repository does not define frontend tests. Its development container is
orchestrated from the root `docker-compose.yml`.
