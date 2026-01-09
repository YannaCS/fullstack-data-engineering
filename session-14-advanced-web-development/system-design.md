# System Design Interview
## Focused Steps for Interview Success

## PHASE 1: PROBLEM CLARIFY & SCOPE

### MOST IMPORTANT
Clarify the functional & non-functional requirements
- What to focus (MVP features)
- What can be skip for now

### Must-Ask Questions
- **Features**: Clarify the MVP vs follow up feature
- **Scale**: How many users? (1K, 100K, 1M, 100M?)
- **Usage Pattern**: Read-heavy or write-heavy?
- **Real-time Need**: Real-time updates or eventual consistency?
- **Data Loss Tolerance**: Can we lose 1 hour of data? Forever?


## PHASE 2: ESTIMATE CAPACITY 
- DAU
- RPS
- Data volume

### Common number as reference
- 1 server handles ~1,000 RPS
- At 600 RPS → Need 2-3 servers minimum
- Single database fine until 100M+ data rows
- Storage estimate: (Users × Data per user per day × 365 × Years)


## PHASE 3: HIGH-LEVEL ARCHITECTURE
![alt text](./pic/high-level-system-diagram.png "Title")

- Load Balancer
- App Servers
- Cache Layer
- Database
- message queue(if necessary)

## PHASE 4: DATA MODEL & SCHEMA

### MUST HAVE
- SQL schema
- Proper primary keys
- Indexes
- Foreign keys
- Relationship(1-1, 1-many, many-1, many-many)

## PHASE 5: API DESIGN

### MUST-HAVE Endpoints
- Restful
- GraphQL (most likely not needed)

### API Decisions
- Request & Response structure in JSON
- Pagination: Use `limit` + `offset` or cursor
- Error codes if asked
- Rate limiting if asked or needed

## PHASE 6: CACHING STRATEGY

### Cache Decision Tree

"Should we cache this?"

Does it change often?
- YES (changes every second) → Don't cache
- NO (changes daily/weekly) → Consider caching

Is it expensive to fetch?
- YES (complex joins, multiple queries) → Cache it
- NO (simple lookup) → Doesn't matter

Is it accessed frequently?
- YES (100x per minute) → Definitely cache
- NO (once a day) → Probably not worth it

Caching pattern?
- Most of time -> Cache aside
- Write-through for high consistency requirement

## PHASE 7: SCALING HANDLING

### Scenario: Traffic Increases 10x
- Add more app servers
- Add cache layer for frequent queries
- Add message queue to off load heavy work

### Scenario : Database Too Slow
- Add indexes
- Cache frequent queries
- Add read replica
- Eventually: Shard by user_id

### Scenario : One Server Dies
- Load balancer health check
- Stops sending traffic to dead server

### Scenario : Real-Time Updates Needed
- WebSocket


## PHASE 8: MONITORING & ALERTING

### MUST-HAVE Metrics to Monitor
- API Response Time -> Track P50, P95, P99 latencies
    - alert if latency > x ms

- Request Throughput -> RPS
    - Alert if drops suddenly
    -  Alert if spikes beyond capacity

- Error Rate
    - Alert if > 3% errors

- Resource Metrics
    - CPU rate
    - Memory
    - Disk Space

- Database Metrics
    - Query Latency
    - Connection Pool

- Cache Metrics
    - Hit Ratio
    - Eviction Rate

### Monitoring Tools Mention
- Metrics: Datadog, New Relic
- Logging: Datadog, Splunk
- Alerting: PagerDuty, Opsgenie

## PHASE 9: TRADE-OFFS DISCUSSION

### For Each Major Decision, Understand:
```
Option A:
Pros: X, Y, Z
Cons: A, B, C
When to use: [scenario]

Option B:
Pros: X, Y, Z
Cons: A, B, C
When to use: [scenario]
```

### Common Trade-Offs
- Consistency vs Availability (CAP theorem)
- SQL vs NoSQL
- Restful vs graphQL
- Synchronous vs Asynchronous



## QUICK DECISION MATRIX

| Decision | What to choose for most of time | Why |
|----------|-----------|-----|
| Database | SQL (PostgreSQL) | Simple, relational, scalable |
| Cache | Redis | Fast, simple, TTL support |
| API | REST | Easiest to explain, standard |
| Load Balancer | Simple round-robin | Works for scale |
| Message Queue | Skip (unless slow ops) | Don't over-engineer |
| Sharding | Skip | Needed at 100M+ users only |
| Microservices | Skip | Too complex for this scale |
| CDN | Mention (don't deep-dive) | For static files if global |


## Interview CHECKLIST
- ✅ Did I ask clarifying questions?
- ✅ Did I draw a diagram?
- ✅ Did I discuss performance?
- ✅ Did I mention trade-offs?
- ✅ Did I consider edge cases?
- ✅ Did I think about scalability?