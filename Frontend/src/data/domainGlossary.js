export const glossaryTerms = [
    {
        key: 'dspl',
        term: 'DSPL',
        expanded: 'Dynamic Software Product Line',
        description: 'A feature-based model that supports changing the active software configuration at runtime while preserving its structural constraints.'
    },
    {
        key: 'mapek',
        term: 'MAPE-K',
        expanded: 'Monitor, Analyze, Plan, Execute over Knowledge',
        description: 'The feedback loop that observes runtime context, selects a valid configuration, plans the required changes, and applies them using shared knowledge.'
    },
    {
        key: 'monitoredContext',
        term: 'Monitored context',
        description: 'The latest simulated runtime observations used by the analyzer. AQI and problem complexity are generated within the selected scenario ranges; SLA priority and Qiskit queue time influence the adaptation decision.'
    },
    {
        key: 'stochasticScenario',
        term: 'Stochastic scenario',
        description: 'A runtime situation defined by AQI and problem-complexity ranges plus an SLA priority. Selecting one generates a new simulated context within those ranges, so repeated runs may produce different decisions.'
    }
];

export const glossaryByKey = Object.fromEntries(
    glossaryTerms.map((entry) => [entry.key, entry])
);
