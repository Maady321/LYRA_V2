from prometheus_client import Counter, Gauge, Histogram

# 1. Guardian Metrics
GUARDIAN_BLOCKS_TOTAL = Counter(
    'lyra_guardian_blocks_total', 
    'Total number of actions blocked by the Zero-Trust Guardian',
    ['agent', 'action']
)

# 2. Prompt Firewall Metrics
FIREWALL_EVENTS_TOTAL = Counter(
    'lyra_firewall_events_total',
    'Total number of prompt injections or jailbreak attempts intercepted',
    ['threat_level']
)

# 3. Voice Guardian Metrics
VOICE_AUTHORIZATIONS_TOTAL = Counter(
    'lyra_voice_authorizations_total',
    'Total number of voice commands processed',
    ['category', 'authorized']
)

# 4. System Latency
EXECUTION_LATENCY_SECONDS = Histogram(
    'lyra_execution_latency_seconds',
    'Execution latency for LLM generation or agent actions',
    ['agent']
)

# 5. Live Security Score
SECURITY_SCORE_GAUGE = Gauge(
    'lyra_security_score',
    'Real-time enterprise security health score (0-100)'
)
