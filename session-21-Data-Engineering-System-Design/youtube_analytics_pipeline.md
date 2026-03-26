# YouTube Analytics Pipeline — 系统设计（Principal DE 级别）

---

## 1️⃣ Requirement Clarification

### 1.1 Functional Requirements

**问题定义：**
YouTube 需要一个统一的 analytics platform，服务于 content creators、advertisers、内部 product teams 以及 Trust & Safety 团队——让他们能够理解 video performance、audience engagement、ad effectiveness 和 content trends，涵盖 real-time 和 historical 两种场景。

**核心 Use Cases：**

- **Creator Studio Dashboard**：实时 + 历史维度的 watch time、views、likes、comments、subscriber growth、audience demographics、traffic sources、revenue breakdown（按 video/channel 粒度）。
- **Ad Analytics**：impression counts、click-through rate (CTR)、view-through rate、cost-per-view (CPV)、advertiser ROI、audience targeting effectiveness。
- **Recommendation Feedback Loop**：将 engagement signals（watch time、skip rate、re-watch、like/dislike ratio）回传给推荐系统的 ML pipeline，用于改进 content ranking。
- **Trust & Safety**：实时 anomaly detection（view count 刷量/bot detection）、comment spam detection、content policy violation 趋势分析。
- **内部 Product Analytics**：A/B test analysis、feature adoption metrics、funnel analysis（impression → click → watch → subscribe）。

**Batch vs Streaming：**

| Use Case | 模式 | Latency 目标 |
|---|---|---|
| Creator Studio 实时计数器 | Streaming | < 5 秒 |
| 日/周级 aggregated reports | Batch | T+1（每日刷新） |
| Ad impression/click attribution | Streaming | < 30 秒 |
| ML Feature Store 更新 | Micro-batch | < 5 分钟 |
| Trust & Safety anomaly detection | Streaming | < 10 秒 |
| Historical trend analysis | Batch | T+1 |

**结论：采用 Lambda Architecture** —— 同时需要 speed layer（streaming）和 batch layer 做 reconciliation 及 backfill。Batch layer 作为 source of truth；speed layer 保证数据 freshness。

**Consumers：**

- Creator Studio 前端（REST API + WebSocket 推送 live counters）
- Ads reporting dashboard（OLAP queries）
- ML training pipelines（offline feature extraction）
- ML serving layer（online feature store）
- 内部 BI 工具（Looker / Tableau）
- Trust & Safety alerting systems
- 外部 APIs（YouTube Data API v3，面向第三方开发者）

**预期的 Query Patterns：**

- "展示 video X 过去 7 天按 country 的 watch time" → time-series aggregation + dimensional filtering
- "本月 category Y 下 engagement rate Top 10 的 videos" → ranking + pre-aggregation
- "video Z 的实时 view count" → point lookup + streaming update
- "对比 Q4 期间 ad campaigns A、B、C 的 CTR" → multi-dimensional OLAP
- "检测 video X 是否有异常的 view velocity" → streaming window aggregation + statistical model

**ML Support：**

- Feature Store integration，同时支持 batch（training）和 online（serving）features
- 特征包括：rolling 7-day/30-day engagement ratios、watch-time percentiles、audience overlap coefficients、content embedding similarity scores
- Model registry integration（MLflow）用于推荐模型版本管理
- A/B test metric pipelines 用于 model comparison

---

### 1.2 Non-Functional Requirements

| 维度 | 要求 | 理由 |
|---|---|---|
| **Data Volume** | 年均约 5000 亿次 video views，日均约 10 亿条 watch events，约 5000 万次 daily uploads，约 20 亿次 daily ad impressions | YouTube 是全球最大的视频平台 |
| **Ingestion Throughput** | 峰值约 1500 万 events/sec（watch events + ad events + interaction events） | 全球直播事件（如 World Cup）期间可达 baseline 的 3-5 倍 |
| **Latency — Streaming** | P99 < 5 秒（实时计数器） | Creator Studio 对 live view counts 的体验预期 |
| **Latency — Batch** | T+1，UTC 06:00 前完成 | 每日 Creator Analytics reports 的 SLA |
| **Latency — Ad-hoc Query** | P95 < 10 秒（OLAP 查询） | Analyst 生产力要求 |
| **Availability** | 99.99%（年停机 < 52 分钟） | Revenue-critical：ads reporting 直接关联 billing |
| **Consistency** | 实时层 eventual consistency（允许 ±2% 偏差），billing/ad revenue 要求 strong consistency | 财务 reconciliation 必须精确 |
| **Data Retention** | Hot: 90 天，Warm: 2 年，Cold: 7+ 年 | 法规要求（GDPR audit trail）、creator 历史分析需求 |
| **Compliance** | GDPR（欧盟）、COPPA（儿童保护）、CCPA（加州）、SOX（财务/广告收入） | 多司法管辖区，analytics 层必须对 PII 做 pseudonymization |
| **Fault Tolerance** | billing events 要求 zero data loss；non-critical impressions 可接受 at-most-once | Revenue events 需要 exactly-once semantics |
| **Scalability** | 无需重新架构即可 horizontal scale 到当前 10 倍负载 | 预见 Shorts、Live、Podcasts 带来的增长 |

---

## 2️⃣ High-Level Architecture

*（参见上方架构图）*

整个 pipeline 遵循 **六层架构**，各层职责清晰分离：

1. **Data Sources** — event producers（clients、servers、ads、external）
2. **Ingestion Layer** — event collection、validation、routing
3. **Storage Layer** — tiered lakehouse（Raw → Clean → Gold）
4. **Processing Layer** — batch 和 stream compute
5. **Serving Layer** — 针对每种 consumer pattern 优化的 data stores
6. **Consumers** — dashboards、APIs、ML、analysts

横切关注点贯穿所有层：**Data Quality、Governance、Monitoring、Security、Cost Management**。

---

## 3️⃣ Ingestion Layer

### 3.1 Data Sources

| 数据源 | 类型 | 体量 | Ingestion 方式 |
|---|---|---|---|
| **Client-side watch events** | Event stream（mobile/web/TV SDKs） | 约 1000 万 events/sec | Streaming：edge collectors → Kafka |
| **Server-side API logs** | Structured logs | 约 500 万 events/sec | Fluentd/Vector → Kafka |
| **Ad serving events** | Impressions、clicks、conversions | 约 200 万 events/sec | 独立 Kafka cluster（为 billing SLA 做隔离） |
| **Video metadata DB** | MySQL/Spanner（CDC） | 约 5000 万 changes/day | Debezium CDC → Kafka |
| **User profile DB** | Spanner（CDC） | 约 1 亿 changes/day | Debezium CDC → Kafka |
| **Comment/interaction events** | Event stream | 约 50 万 events/sec | Streaming via Kafka |
| **Content moderation signals** | Internal API | 约 1000 万 events/day | Batch pull + streaming alerts |
| **External data** | GeoIP databases、exchange rates、IAB taxonomy | Daily/weekly | Batch ingestion（Airflow 调度） |

### 3.2 Ingestion 方式详解

**Streaming Path（主路径）：**
- Edge collectors 部署在全球 30+ 个 PoPs，通过 HTTPS 接收 client events
- 在 edge 端进行 schema 和基础 business rules 的 validation，尽早拒绝 malformed data
- 验证通过的 events 发送到 **Apache Kafka**（multi-region clusters）
- Kafka 是整个系统的 central nervous system —— 所有下游系统均从 Kafka 消费

**CDC Path：**
- Debezium connectors 挂在 MySQL/Spanner 上，捕获 row-level changes
- Change events 发布到专用的 Kafka topics
- 使 analytics 层与 OLTP databases 保持同步，且不影响生产查询性能

**Batch Path：**
- Airflow DAGs 调度 daily pulls，拉取 slowly-changing dimensions（GeoIP、exchange rates、content categories）
- 以 Parquet/JSON 格式直接落地到 data lake 的 Raw layer

### 3.3 Kafka 设计 — 关键决策

**Topic 设计：**

| Topic | Partition Key | Partitions 数量 | Retention |
|---|---|---|---|
| `watch-events` | `video_id` | 2048 | 7 天 |
| `ad-impressions` | `campaign_id` | 512 | 14 天（billing audit） |
| `ad-clicks` | `campaign_id` | 256 | 14 天 |
| `user-interactions` | `user_id` | 1024 | 3 天 |
| `video-metadata-cdc` | `video_id` | 256 | 7 天 |
| `user-profile-cdc` | `user_id` | 512 | 7 天 |

> **I'd partition Kafka topics by business key（如 `video_id` 用于 watch events）to ensure scalability and ordering guarantees.** 同一个 video 的所有 events 落在同一个 partition 上，下游 consumers 无需 coordination 就能按序处理——这对精确的 view counting 和 deduplication 至关重要。

**关键设计要点：**

- **Schema Registry（Confluent Schema Registry）：** 所有 events 使用 **Avro** 并遵循 BACKWARD_TRANSITIVE 的 schema evolution 规则。Producers 在发布前必须注册 schema，防止 schema drift 导致下游消费失败。
- **Idempotent Producers：** 开启 `enable.idempotence=true` + `acks=all` + `max.in.flight.requests.per.connection=5`，保证 partition 内的 exactly-once delivery。
- **Exactly-Once Semantics：** 对于 ad billing pipeline（revenue-critical），使用 Kafka Transactions（`transactional.id`）实现端到端 exactly-once。消费端配合 idempotent sink，将 transaction ID 写入存储层用于 dedup。
- **Backpressure 处理：**
  - Consumer 端：调优 Kafka consumer 的 `max.poll.records` + Flink 的 credit-based backpressure
  - Producer 端：edge collectors 实现 local buffering（ring buffer）+ exponential backoff（当 Kafka 响应变慢时）
  - Circuit breaker pattern：当 Kafka 不可达超过 30 秒，events 溢出到 local disk，恢复后 replay
- **Rack-Aware Replication：** `min.insync.replicas=2`，replicas 分布在 3 个 AZs，保证 durability
- **Tiered Storage：** 启用 Kafka Tiered Storage（KIP-405），将较老的 segments offload 到 S3，在维持长 retention（满足 audit 需求）的同时控制 broker 磁盘成本

### 3.4 Kafka → Storage 的中间处理层（关键衔接）

**数据不是从 Kafka 直接落地 Storage——中间根据数据特性走不同的处理路径。** 这是整个 pipeline 最容易被忽略的一层。Kafka 输出后有三条并行路径：

**路径总览：**

| 路径 | 链路 | 适用数据 | Latency | 理由 |
|---|---|---|---|---|
| **路径 A** | Kafka → Kafka Connect S3 Sink → Bronze | 全部 topics（raw archive） | Minutes | 零处理 dump，DR 兜底 + audit trail |
| **路径 B** | Kafka → Flink → Bronze/Silver/Redis/Druid | Watch events、ad events、user interactions | Seconds | 需要实时 dedup、enrich、aggregate |
| **路径 C** | Kafka → Spark batch/micro-batch → Bronze → Silver | Server logs、moderation signals、CDC dimensions、external data | Hourly / T+1 | 对 latency 无严格要求，batch 更经济 |

---

**路径 A：Raw Archive（零处理 dump）**
- **Kafka Connect S3 Sink Connector** 直接将 Kafka 原始消息以 Parquet 格式 dump 到 S3
- 完全不做任何 transformation，保留原始 payload
- 目的：作为 Bronze 层的 disaster recovery 和 audit trail 兜底
- 即使 Flink 和 Spark 全部挂掉，这条路径也能保证 raw data 不丢失
- 所有 Kafka topics 都走这条路径（全量备份），与路径 B/C 并行运行

---

**路径 B：Flink Stream Processing（实时核心路径）**

适用于对 latency 有严格要求的高价值 events：watch events、ad impressions/clicks、user interactions（likes/comments/subscribes）。

Flink 从 Kafka 消费后，在写入 Storage 之前做了以下处理：

| 处理步骤 | 具体操作 | 目的 |
|---|---|---|
| **Schema validation** | 配合 Schema Registry 做 deserialization + field-level validation | 拦截 malformed events，路由到 DLQ |
| **Event deduplication** | 基于 `event_id` 的 stateful dedup（RocksDB state，TTL 24h） | 防止 producer retry 导致的 duplicate events |
| **Event enrichment** | Async lookup 维度数据（video metadata、channel info、GeoIP），通过 broadcast state 缓存 | 给 raw events 补齐分析所需的维度字段 |
| **Event routing** | 根据 event type 和 business rules 分流到不同 sink | 不同数据走不同的存储路径 |
| **Real-time aggregation** | Windowed aggregation（tumbling/sliding/session windows） | 产出实时计数器和聚合指标 |
| **Anomaly detection** | Streaming CEP + statistical models | Trust & Safety 实时告警 |

**Flink 的 4 个输出 sink：**

| Sink | 目标 | 写入内容 | 写入方式 |
|---|---|---|---|
| **Bronze sink** | Delta Lake on S3（Bronze 层） | 经过 validation + dedup 的 events（保留完整 payload） | Flink Delta Connector，append-only |
| **Silver sink** | Delta Lake on S3（Silver 层） | Enriched + schema-conformed 的 events | Micro-batch（每 5 分钟 trigger），Flink sink with exactly-once |
| **Real-time counter sink** | Redis Cluster | 按 `video_id` 的 live view counts、engagement counters | 直接 Redis INCR，at-least-once + idempotent（counter 天然幂等） |
| **OLAP sink** | Apache Druid | Pre-aggregated metrics（5 分钟粒度的 hourly rollups） | Druid Kafka Indexing Service（从 Flink 输出的 aggregated Kafka topic 消费） |

---

**路径 C：Spark Batch / Micro-Batch（低优先级数据路径）**

并非所有数据都值得用 Flink 的 always-on 资源来处理。以下数据走 Spark batch 更合理：

| 数据 | 消费方式 | 调度频率 | 理由 |
|---|---|---|---|
| **Server-side API logs** | Spark 从路径 A 的 S3 dump 读取 | Hourly | 请求日志、错误日志用于 operational analytics，T+1 足够 |
| **Content moderation signals** | Spark 从 Kafka 读取（`spark-sql-kafka` connector） | Hourly | 审核结果、policy violation flags 不需要毫秒级处理 |
| **CDC slowly-changing dimensions** | Spark 从 Kafka CDC topics 读取 | 每 1-4 小时 | Video metadata、user profile changes 做 SCD Type 2 MERGE 到 Silver dimension tables |
| **External reference data** | Airflow 调度 Spark 读取 S3 landing zone | Daily / weekly | GeoIP、exchange rates、IAB taxonomy 本身就是低频更新 |

**Spark 在路径 C 中的处理逻辑：**
- 从 Kafka 消费（通过 `spark-sql-kafka` connector 做 micro-batch）或从路径 A 的 S3 Parquet 文件读取
- 执行 schema validation、dedup、cleansing
- 写入 Bronze 层（如果直接从 Kafka 读取且路径 A 尚未覆盖）
- 对 dimension tables 执行 Delta Lake MERGE（SCD Type 2）写入 Silver 层

**为什么要区分路径 B 和路径 C：**

> Flink 的资源成本远高于 Spark batch——每个 Flink job 需要 always-on 的 TaskManagers、持续的 checkpoint I/O、RocksDB state 管理。如果数据本身不需要 sub-second latency，用 Flink 处理就是 over-engineering。
>
> 区分这两条路径的好处：
> - **成本**：路径 C 的 Spark jobs 可以用 Spot instances，且只在调度窗口内运行，成本是 Flink always-on 的 1/10
> - **运维简化**：batch jobs 更容易 debug、backfill、重跑
> - **职责清晰**：Flink 只处理高价值实时数据，Spark 处理其他所有——两条路径的 SLA 可以独立管理
> - **资源隔离**：低优先级数据不会抢占 Flink 的 resources，不影响实时路径的 latency

---

**三条路径的关系图：**

```
                          ┌─ 路径 A ──→ S3 raw dump (全量备份/DR)
                          │
Kafka topics ─────────────┼─ 路径 B ──→ Flink ──→ Bronze (validated)
  (watch, ads,            │                    ──→ Silver (enriched)
   logs, CDC,             │                    ──→ Redis (live counters)
   moderation,            │                    ──→ Druid (OLAP)
   external)              │
                          └─ 路径 C ──→ Spark batch ──→ Bronze ──→ Silver
                                        (logs, CDC dims, moderation, external)
```

> **面试关键点：** 体现你对 "不是所有数据都需要 streaming" 的工程判断力。Lambda Architecture 不意味着所有数据都走 speed layer——根据数据的 latency requirement 和 business value 选择合适的处理路径，是 Principal 级别的 cost-aware design thinking。

---

## 4️⃣ Storage Layer

### 4.1 Tiered Lakehouse 架构

采用 **Lakehouse 架构**，基于 **Delta Lake** 构建在 cloud object storage（S3/GCS）之上，结合 data lake 的可扩展性与 warehouse 的 ACID transactions。

**三层 Medallion Architecture：**

| 层级 | 用途 | 格式 | Retention | 更新频率 |
|---|---|---|---|---|
| **Bronze（Raw）** | Immutable landing zone——源数据的精确副本 | Parquet（append-only），按 `ingestion_date/hour` 分区 | 90 天 hot，之后 archive 到 Glacier | Continuous（streaming）+ daily（batch） |
| **Silver（Clean）** | Deduplicated、validated、schema-conformed、与 slowly-changing dimensions enriched | Delta Lake，按 `event_date/event_hour` 分区 | 2 年 | Micro-batch（每 5 分钟）+ 每日 full reconciliation |
| **Gold（Curated）** | 业务级 aggregations、star schema models、pre-computed metrics | Delta Lake，按 `date/dimension` 分区（如 `date/country/category`） | 7+ 年 | Daily batch + hourly incremental（关键指标） |

### 4.2 存储格式决策

| 关注点 | 决策 | 理由 |
|---|---|---|
| **File Format** | Parquet（Bronze）/ Delta Lake（Silver、Gold） | Parquet 提供 columnar compression；Delta 增加 ACID、time travel、schema enforcement |
| **Partitioning** | `event_date` 作为 primary partition，hot paths 增加 `hour` sub-partition | 支持高效的 partition pruning —— 90%+ 查询都有时间范围条件 |
| **Z-Ordering** | Silver 层按 `video_id`、`channel_id`；Gold 层按 `country`、`category` | 高频过滤维度受益于数据 co-location。Z-ordering 将相关数据聚集到同一 file set 内，大幅减少 I/O |
| **Compaction** | Silver 层每 4 小时执行一次 OPTIMIZE，Gold 层每日执行 | Streaming micro-batches 会产生大量 small files（< 128MB）。Compaction 将其合并为最优的 256MB–1GB 文件，提升读取性能 |
| **Small File Handling** | 写入时自动 OPTIMIZE（Delta `spark.databricks.delta.optimizeWrite.enabled=true`）+ 定时 bin-packing | 防止 "small file problem" 导致 object storage 上的查询性能退化 |
| **ACID Guarantees** | Delta Lake 通过 optimistic concurrency control 提供 serializable isolation | 支持 concurrent readers/writers、schema enforcement、以及 dimension tables 上安全的 MERGE 操作（SCD Type 2） |
| **Vacuum Policy** | Silver/Gold 层设置 `VACUUM RETAIN 168 HOURS`（7 天） | 在 time-travel 能力与存储成本之间取得平衡 |

### 4.3 辅助存储系统

Lakehouse 是 primary store，但特定的 access patterns 需要专门的存储系统：

| 系统 | 角色 | 存储内容 |
|---|---|---|
| **Delta Lake on S3/GCS** | Primary analytical store（lakehouse） | 全部 Bronze/Silver/Gold tables |
| **Redis Cluster** | 实时计数器、session state | Live view counts、trending scores、rate-limiting counters |
| **Apache Druid** | Sub-second OLAP（interactive dashboards） | Pre-aggregated metrics（hourly/daily），服务 Creator Studio |
| **Elasticsearch** | Full-text search + log analytics | Comment search、video metadata search、operational logs |
| **Cloud Spanner** | Ad billing reconciliation 的 source-of-truth | Finalized ad revenue records（strong consistency） |
| **Feature Store（Feast/Tecton）** | ML feature serving | Online：Redis-backed；Offline：Delta Lake-backed |

---

## 5️⃣ Processing Layer

### 5.1 Stream Processing — Apache Flink

Flink 是所有 real-time paths 的 primary stream processor。

**为什么选 Flink 而不是 Spark Structured Streaming：**
- 真正的 event-time processing + watermark handling（对 late-arriving 的移动端 events 至关重要）
- 更精细的 checkpointing（incremental，基于 RocksDB state backend）
- 更低 latency（毫秒级 vs Spark 的 micro-batch 秒级）
- 原生支持 complex event processing（CEP），满足 fraud detection 需求

**关键 Flink Jobs：**

| Job | Input Topic(s) | Output | Window | State |
|---|---|---|---|---|
| 实时 view counter | `watch-events` | Redis（live counts）+ Kafka（aggregated） | Tumbling 5s | Keyed by `video_id`，约 5 亿 keys |
| Ad click attribution | `ad-impressions`、`ad-clicks` | Kafka `attributed-clicks` | Session window（30 分钟 timeout） | Keyed by `(user_id, campaign_id)` |
| Anomaly detection | `watch-events` | Alerts Kafka topic | Sliding 1 min、sliding 10 min | 每个 `video_id` 的 statistical model |
| Engagement aggregator | `watch-events`、`user-interactions` | Silver layer（micro-batch sink） | Tumbling 5 min | Keyed by `(video_id, country)` |
| Comment spam detector | `comment-events` | Moderation queue | Per-event（stateless ML inference） | Stateless |

**关键 Flink 设计要点：**

- **Checkpointing：** 使用 RocksDB state backend 做 incremental checkpoints 到 S3，间隔 60 秒。在 recovery time（约 1 分钟 replay）和 checkpoint I/O overhead 之间取得平衡。Ad billing pipeline 的 checkpoint interval 缩短到 30 秒，并配合 exactly-once sink semantics。
- **Watermark Strategy：** 使用 `BoundedOutOfOrdernessTimestampExtractor`，watch events 设置 30 秒的 max lateness（移动端因网络延迟发送滞后）。超出 watermark 的 late events 路由到 side output，由后续的 batch reconciliation 处理。
- **Backpressure：** Flink 的 credit-based flow control 天然将 backpressure 从 sinks 传播到 sources。我们监控 `outPoolUsage` metrics，在 80% 时触发告警。
- **State TTL：** Keyed states（如 per-video counters）设置 24 小时 TTL。长时间没有事件的 videos 其 state 会被 evict，避免 unbounded state growth。

### 5.2 Batch Processing — Apache Spark

Spark 负责 daily reconciliation、historical backfills、重度 aggregations 以及 ML feature computation。

**关键 Batch Jobs（由 Airflow 编排）：**

| Job | 调度时间 | Input | Output | SLA |
|---|---|---|---|---|
| Daily view reconciliation | 02:00 UTC | Bronze watch events + Flink aggregates | Gold `daily_video_metrics` | 06:00 UTC 前完成 |
| Channel analytics rollup | 03:00 UTC | Silver engagement data | Gold `channel_daily_summary` | 06:00 UTC 前完成 |
| Ad revenue reconciliation | 04:00 UTC | Silver attributed clicks + billing DB | Gold `daily_ad_revenue` | 08:00 UTC 前完成 |
| ML feature computation | 05:00 UTC | Silver engagement + user profiles | Feature Store（offline） | 07:00 UTC 前完成 |
| Audience segmentation | 每周日 00:00 | Gold user engagement history | Gold `audience_segments` | 周一 06:00 UTC 前完成 |

**Spark 优化策略：**

- **Shuffle Optimization：**
  > **Shuffle defines stage boundaries and is one of the most expensive operations, so I would optimize partition size（目标 post-shuffle 每个 partition 128-256MB）and enable AQE（Adaptive Query Execution）to dynamically coalesce shuffle partitions and handle data skew at runtime.**

  具体配置：
  - `spark.sql.adaptive.enabled=true`
  - `spark.sql.adaptive.coalescePartitions.enabled=true`
  - `spark.sql.adaptive.skewJoin.enabled=true`
  - `spark.sql.shuffle.partitions=2000`（初始值，AQE 会自动 coalesce）

- **Join Strategy：**
  - **Broadcast join**：用于 < 1GB 的 dimension tables（video metadata、category taxonomy、GeoIP）。设置 `spark.sql.autoBroadcastJoinThreshold=1073741824`。
  - **Sort-merge join**：用于大表之间的 fact-to-fact joins（watch events × ad impressions）。在 join key 上预排序并 co-partition 以最小化 shuffle。
  - **Bucketed join**：用于频繁 join 的表对——Silver 层的 `watch_events` 和 `user_interactions` 按 `user_id` 分成 2048 个 buckets，彻底消除 join 时的 shuffle。

- **Data Skew Handling：**
  - **AQE Skew Join：** 运行时自动拆分 skewed partitions
  - **Salting：** 对已知 hot keys（刷爆的 viral videos，单个 partition 可能有上亿条 events），在 key 后追加随机 salt（0-99），先分散聚合再二次聚合。举例：一个爆款视频产生 1 亿条 events，不做 salting 时一个 executor 处理全部；100 个 salts 后每个 executor 仅处理约 100 万条。
  - **Two-phase aggregation：** 先在 local 做 pre-aggregation（combiner），再 shuffle 做 global aggregation——shuffle 数据量减少 90%+（针对 sum/count/avg）。

- **Window Aggregation：**
  - 用于 rolling metrics（7-day watch time、30-day subscriber growth），使用 Spark SQL window functions：`PARTITION BY video_id ORDER BY event_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`
  - 中间结果持久化到 Silver 层，避免重复计算

- **Resource Management：**
  - 启用 dynamic allocation（`spark.dynamicAllocation.enabled=true`）
  - 非 SLA 的 batch jobs（feature computation、backfills）使用 Spot instances——节省 60-70% 成本
  - SLA-critical 的 jobs（daily reconciliation、ad revenue）使用 On-demand instances

### 5.3 Orchestration — Apache Airflow

- DAG dependency management：streaming outputs 喂给 batch reconciliation
- SLA monitoring：如果 `daily_video_metrics` 在 06:00 UTC 前未完成则告警
- Backfill support：参数化 DAGs，支持通过 `execution_date` 做历史数据 reprocessing
- Sensor-based triggers：`S3KeySensor` 检测上游数据就绪后再启动依赖任务

---

## 6️⃣ Serving Layer

Serving layer 按 consumer pattern 做 purpose-built 的设计——没有单一存储能满足所有需求。

| Consumer | Serving Store | Access Pattern | 优化手段 |
|---|---|---|---|
| **Creator Studio（实时）** | Redis + WebSocket | 按 `video_id` 做 point lookup（live counters） | Pre-computed counters、pub/sub 推送更新 |
| **Creator Studio（历史）** | Apache Druid | Time-series OLAP + dimensional filters | 按 hourly/daily 粒度 pre-aggregation、bitmap indexing on dimensions |
| **Ads Reporting** | Druid + Trino over Delta Lake | Multi-dimensional OLAP、complex joins | Materialized views、result caching（Trino + Redis）、read replicas |
| **ML Feature Serving** | Feast（online: Redis，offline: Delta Lake） | Key-value lookup（inference）、bulk read（training） | TTL-based eviction、feature versioning |
| **Search（videos/comments）** | Elasticsearch | Full-text search + faceting | Inverted index + doc_values for aggregations |
| **内部 BI（Looker/Tableau）** | Trino over Gold layer | Ad-hoc SQL queries | Caching layer、query queue management、resource groups |
| **YouTube Data API v3** | Custom API layer → Redis + Druid | REST API + rate limiting | Pre-aggregation、CDN caching（热门 channels）、API response caching |
| **Trust & Safety** | Flink CEP → Alert service → Elasticsearch | Pattern matching、anomaly alerts | Stateful CEP rules、low-latency alerting pipeline |

**关键 Serving Layer 决策：**

- **Pre-aggregation：** Gold layer tables 在多种粒度上 pre-aggregate（hourly、daily、weekly、monthly）。Creator Studio 最常见的查询命中 Druid 的 pre-aggregated tables，500ms 内返回。只有非常规的 drill-down 查询才 fallthrough 到 Trino over Delta Lake。
- **Caching Strategy：**
  - L1：Application-level cache（in-process LRU，API servers 内）—— 1 分钟 TTL
  - L2：Redis cluster —— dashboard 数据 5 分钟 TTL，历史数据 1 小时 TTL
  - L3：CDN edge cache（YouTube Data API responses，针对热门 channels/videos）—— 5 分钟 TTL
- **Indexing：**
  - Druid：所有 dimension columns 自动 bitmap index，string dimensions 上建 inverted index
  - Elasticsearch：自定义 mappings，`keyword` fields 做精确匹配，`text` fields 做搜索
  - Delta Lake：在高频过滤列上做 Z-Order index
- **Read Replicas：**
  - Druid：historical nodes 设置 2x replication factor（query load balancing）
  - Redis：每个 region 部署 read replicas（geo-distributed Creator Studio）
  - Elasticsearch：每个 shard 配 1 个 replica

---

## 7️⃣ Scalability

### Horizontal Scaling 策略

| 组件 | Scaling 机制 | 触发条件 |
|---|---|---|
| **Kafka** | 增加 brokers + reassign partitions | Broker CPU > 70% 持续 |
| **Flink** | 增加 parallelism（通过 savepoint rescale） | Processing lag > 30 秒 |
| **Spark** | Dynamic allocation（增减 executors） | Job queue depth |
| **Druid** | 增加 historical/middle-manager nodes | Query latency P95 > 2 秒 |
| **Redis** | 增加 shards（consistent hashing） | Memory utilization > 75% |
| **API servers** | HPA（Kubernetes），基于 RPS/CPU | CPU > 60% 或 RPS > threshold |

### Partition-Based Scaling

整个系统按 business key 分区，支持 independent scaling：

- Kafka partitions 可以拆分（topic repartitioning）来应对特定 key range 的增长
- Flink key groups 与 Kafka partitions 对齐，实现 co-located processing
- Delta Lake partitions 支持不同 time ranges 和 dimensions 的并行读写
- Druid segments 按时间分区，recent data 和 historical data 可独立扩容

### Data Skew —— 系统级应对

Data skew 是 YouTube 级别最大的运维风险（viral videos、mega-channels）：

1. **Kafka：** 监控 partition lag skew。如果某个 partition 持续 lag，对 hot videos 使用 composite key（`video_id + shard_id`）做 re-key。
2. **Flink：** 对已知 hot keys 使用 virtual partitioning。监控每个 subtask 的 `numRecordsInPerSecond`，偏差超 10 倍时告警。
3. **Spark：** AQE skew join + salting（前文已述）。
4. **Druid：** Druid 的 scatter-gather 架构天然处理 skew，但需监控 segment sizes，单个 segment > 5GB 时触发 re-index。

### Stateless Service 设计

所有 API 和处理服务尽量保持 stateless：

- API servers：stateless，JWT-based auth，所有 state 存在 Redis/Druid 中
- Flink：by design 是 stateful 的，但 state 已 externalized（RocksDB + S3 checkpoints），支持通过 savepoints 做 rescaling
- Spark：stateless executors，所有 state 在 Delta Lake 中
- Orchestration：Airflow metadata 存在 PostgreSQL，workers 是 ephemeral Kubernetes pods

### Auto-Scaling Policies

| 服务 | Metric | Scale-Up 阈值 | Scale-Down 阈值 | Cooldown |
|---|---|---|---|---|
| Edge collectors | RPS | > 50K/instance | < 20K/instance | 5 min |
| API servers | P99 latency | > 200ms | < 50ms | 3 min |
| Flink TaskManagers | Consumer lag | > 60 秒 | < 5 秒 | 10 min |
| Spark clusters | Queue wait time | > 5 min | < 30 秒 | 15 min |
| Druid middle-managers | Pending tasks | > 100 | < 10 | 10 min |

---

## 8️⃣ Reliability

### Retry & Recovery

| Failure Mode | 应对措施 |
|---|---|
| **Transient Kafka produce failure** | Idempotent producer retries（最多 3 次），然后 spill to local disk |
| **Flink job crash** | 从最近 checkpoint 自动 restart（recovery < 60 秒）。Restart strategy：exponential backoff，10 分钟内最多 5 次 |
| **Spark job failure** | Airflow retry with exponential backoff（3 次重试）。Stage-level retry 处理 transient executor failures |
| **Downstream sink 不可用** | Circuit breaker（Hystrix/Resilience4j）+ fallback to DLQ |
| **Schema evolution mismatch** | Schema Registry 拒绝不兼容的 changes。Consumer 端做 schema negotiation + fallback |

### Dead Letter Queue (DLQ)

每个 pipeline stage 都有专用的 DLQ：

- **Ingestion DLQ：** 未通过 schema validation 的 events → `dlq-ingestion` Kafka topic → 每日 batch reprocessing job 检查并修复或丢弃
- **Processing DLQ：** 导致 deserialization 或 business logic exception 的 events → `dlq-processing` topic → 人工 review + fix 部署后自动 reprocessing
- **Sink DLQ：** 写入下游存储失败的 events → `dlq-sink-{store_name}` → retry job with exponential backoff

DLQ 相关 metrics 持续监控：任何 DLQ 在 1 小时内深度超 10K events 即 page on-call。

### Checkpointing & State Recovery

| 系统 | Checkpoint 机制 | Recovery Time |
|---|---|---|
| Flink | Incremental RocksDB → S3（每 60 秒） | < 1 分钟（从最近 checkpoint 恢复） |
| Kafka | Consumer offsets 存在 `__consumer_offsets` topic | 即时（从 committed offset 恢复消费） |
| Spark | RDD lineage + stage retry | Stage 级别重试（秒到分钟级） |
| Delta Lake | Transaction log（`_delta_log`） | Time travel 到任意历史版本 |

### Monitoring & Observability

**四大支柱：**

1. **Metrics（Prometheus + Grafana）：**
   - Pipeline lag（每个 topic/consumer group 的 Kafka consumer lag）
   - Processing throughput（每个 Flink job 的 events/sec）
   - Query latency（每个 serving store 的 P50/P95/P99）
   - Error rate（DLQ depth、failed jobs）
   - Resource utilization（每个组件的 CPU、memory、disk、network）

2. **Logging（ELK Stack）：**
   - 所有服务的 structured JSON logs
   - Correlation IDs，支持单条 event 的端到端追踪

3. **Tracing（Jaeger/OpenTelemetry）：**
   - 从 edge collector → Kafka → Flink → serving store 的端到端 trace
   - 定位 bottlenecks 和 slow stages

4. **Alerting（PagerDuty）：**

| Alert | 触发条件 | Severity |
|---|---|---|
| Pipeline lag | Kafka consumer lag > 5 分钟 | P1（page on-call） |
| Daily SLA breach | Reconciliation 在 06:00 UTC 前未完成 | P1 |
| DLQ overflow | 任何 DLQ > 10K events/hour | P2 |
| Data freshness | Gold table 超过 2 小时未更新 | P2 |
| View count 异常 | Flink anomaly detector 触发 | P3（Trust & Safety） |
| 磁盘用量 | Broker disk > 80% | P2 |

### Multi-AZ / Multi-Region Deployment

- **Kafka：** 主 region 内 3-AZ 部署，通过 MirrorMaker 2 复制到 secondary region（RPO < 30 秒）
- **Flink：** 跨 AZ 做 active-passive（Kubernetes pod anti-affinity）。Savepoints 支持 region failover。
- **Delta Lake（S3/GCS）：** 存储层做 cross-region replication。元数据（Hive Metastore / Unity Catalog）同步到 standby region。
- **Serving Layer：** Redis clusters 在 3+ regions 做 active-active（CRDTs 实现 conflict-free counters）。Druid 在 secondary regions 部署 read replicas。

### Disaster Recovery

| 场景 | RTO | RPO | 策略 |
|---|---|---|---|
| 单 AZ 故障 | < 5 分钟 | 0 | 自动 failover（Kafka ISR、Flink checkpoint、K8s reschedule） |
| Region 故障 | < 30 分钟 | < 30 秒（streaming）、< 1 小时（batch） | MirrorMaker failover、re-point consumers、从 checkpoint replay |
| 数据损坏 | < 2 小时 | 0（time travel） | Delta Lake RESTORE 到历史版本，从 Bronze 重新处理 |

---

## 9️⃣ Data Quality & Governance

### Data Quality Framework

**逐层 Validation：**

| 层级 | 校验内容 | 工具 | 失败处理 |
|---|---|---|---|
| **Ingestion** | Schema validation（Avro） | Confluent Schema Registry | Reject to DLQ |
| **Bronze → Silver** | Null checks、type casting、dedup | Great Expectations / dbt tests | 路由到 quarantine table，告警 |
| **Silver → Gold** | Business rule validation（如 watch_time ≥ 0、view_count 单调递增） | dbt tests + 自定义 Spark assertions | Halt pipeline、告警、fallback 到上一版本 Gold |
| **Serving** | Freshness checks、row count anomaly detection | Monte Carlo / 自定义 monitors | 告警，提供 stale data 并标注 staleness indicator |

**具体 Quality Checks：**

- **Deduplication：** 基于 `(event_id, timestamp)` 复合键做 event-level dedup，通过 Delta Lake MERGE 实现。Billing events 保证 exactly-once semantics。
- **Late Data Handling：** 在 batch window 之后到达的 events 在下个 cycle 处理。Silver 层使用 MERGE（upsert）来处理 late arrivals，不会产生 duplicates。
- **Referential Integrity：** 检测 fact tables（watch events）与 dimension tables（video metadata）之间的 orphans。Orphans 被 quarantine，orphan rate > 0.1% 时触发告警。
- **Metric Drift Detection：** 对关键指标（daily view counts、average watch time）做 statistical monitoring。如果当天值偏离 30-day rolling average 超过 3 个 standard deviations，在发布到 Gold 前告警。

### Data Governance

**Data Catalog（Unity Catalog / Apache Atlas）：**
- 自动注册 table schemas 及描述
- Column-level lineage，从 source 到 Gold 全链路追踪
- Business glossary（如 "engaged view" = watch time > 30 秒）
- 每个 domain 指定 data steward

**Lineage：**
- **Table-level lineage：** Airflow DAG → Spark job → Delta table，在 catalog 中可视化
- **Column-level lineage：** 通过 dbt 内置 lineage graph + OpenLineage 与 Spark/Flink 的集成来追踪
- **Impact analysis：** 修改 Silver table schema 之前，lineage graph 展示所有受影响的下游 Gold tables 和 dashboards

**Access Control（RBAC + ABAC）：**

| Role | Bronze Access | Silver Access | Gold Access | PII Access |
|---|---|---|---|---|
| Data Engineer | Read/Write | Read/Write | Read/Write | Masked |
| Data Analyst | No | Read | Read | Masked |
| ML Engineer | No | Read | Read | Pseudonymized |
| Product Manager | No | No | Read（限定 domains） | No |
| Trust & Safety | Read | Read | Read | Unmasked（audited） |

**PII 处理：**
- PII 字段（`user_id`、`ip_address`、`device_id`、`email`）在 Silver 层边界做 pseudonymization（SHA-256 + per-field rotating salts）
- 原始 PII 保留在 Bronze 层（at rest encryption、access-logged），保留 90 天用于 debugging/compliance
- GDPR Right to Erasure：deletion requests 触发所有层的 Delta Lake `DELETE` + cache invalidation，维护 audit log
- COPPA：对 13 岁以下用户走独立处理路径——更严格的 data minimization，不产出 behavioral targeting features

**Schema Evolution Policy：**
- 所有 schema changes 经过 review process（基于 PR，附带 downstream impact analysis）
- Schema Registry 强制 BACKWARD_TRANSITIVE compatibility
- Breaking changes 需要新建 topic version（如 `watch-events-v2`）并设置 migration period

---

## 🔟 Cost Optimization

### Compute Cost

| 策略 | 节省幅度 | 适用于 |
|---|---|---|
| **Spot / Preemptible Instances** | 60-70% | 非 SLA 的 Spark jobs（ML features、backfills、audience segmentation） |
| **Reserved Instances** | 30-40% | SLA-critical 的 Flink clusters、Druid historical nodes、Kafka brokers |
| **Auto-scaling** | 20-30% | API servers、Spark clusters（off-peak 时 scale down） |
| **Right-sizing** | 15-25% | 基于 GC metrics 和 shuffle spill 定期调优 Spark executor size |
| **Graviton / ARM instances** | 20% | 所有兼容 ARM 的 workloads（Kafka、Spark、Flink） |

### Storage Cost

| 策略 | 节省幅度 | 详情 |
|---|---|---|
| **Storage Tiering** | 50-70% | Bronze > 90 天 → S3 Glacier。Gold > 2 年 → S3 Glacier Deep Archive。Druid historical segments > 90 天 → deep storage（S3） |
| **Compaction** | 20-30%（I/O 成本） | 定期 OPTIMIZE 将文件数量减少 10-50 倍，减少 list/GET operations |
| **Partition Pruning** | 40-60%（scan 成本） | 按时间分区确保查询只扫描相关的 date ranges |
| **Z-Ordering** | 20-40%（scan 成本） | 按常见 filter patterns 做数据 co-location，减少 bytes scanned |
| **Column Pruning** | 30-50%（scan 成本） | Parquet columnar format + query pushdown，只读取所需 columns |
| **Compression** | 50-70%（原始大小） | Parquet 文件使用 Zstandard compression（analytics workloads 下比 Snappy 压缩率更优） |
| **Vacuum** | 回收 10-20% | 定期 VACUUM 删除过期的 Delta Lake file versions |

### Network Cost

- **Regional affinity：** compute 和 storage 保持在同一 region/AZ，避免 cross-AZ transfer 费用
- **Kafka compression：** producers 启用 `lz4` compression（网络带宽减少 50-70%）
- **Druid query result caching：** 避免相同 dashboard 查询的重复大范围 scan

### 运营成本

- **Self-service analytics：** Gold layer + BI 工具减少 60% 的 ad-hoc 工程需求
- **自动化 backfill：** 参数化 Airflow DAGs 消除人工介入的 reprocessing
- **主动 monitoring：** 在 SLA breach 之前发现问题，降低 incident response 成本

### Cost Monitoring

- 所有 cloud resources 按 team/pipeline/environment 打 tag
- 每周 cost anomaly reports（日支出偏离 7-day average > 20% 时自动告警）
- Chargeback model：每个 team 根据其 data volume 和 query patterns 分配 cost budget
- 每季度 cost review：识别 underutilized reserved capacity、oversized clusters、stale data

---

## Bonus：技术选型总结

| 层级 | 技术 | 考虑过的替代方案 | 选择理由 |
|---|---|---|---|
| Message Bus | Apache Kafka | Pub/Sub、Kinesis、Pulsar | YouTube 级别验证过、生态丰富、支持 exactly-once |
| Stream Processing | Apache Flink | Spark Structured Streaming、Kafka Streams | 真正的 event-time、更低 latency、更强的 state management |
| Batch Processing | Apache Spark | Presto/Trino、Hive | 大规模 batch ETL 的最佳选择、AQE、ML 集成 |
| Table Format | Delta Lake | Apache Iceberg、Apache Hudi | ACID、time travel、MERGE 支持、与 Spark 深度集成 |
| Orchestration | Apache Airflow | Dagster、Prefect | 行业标准、成熟、社区强大 |
| OLAP Engine | Apache Druid | ClickHouse、Pinot | Sub-second ingestion + query、为 time-series at scale 而生 |
| Ad-hoc SQL | Trino | Presto、Athena | 跨 Delta Lake + Druid 的 federation、活跃社区 |
| Feature Store | Feast / Tecton | Hopsworks、SageMaker FS | 开源灵活、与 Delta Lake 集成 |
| Data Quality | Great Expectations + dbt tests | Monte Carlo、Soda | 可编程、与 Spark/Airflow 集成 |
| Catalog | Unity Catalog / Apache Atlas | DataHub、Amundsen | Lineage + RBAC + schema management 一体化 |
| CDC | Debezium | AWS DMS、Fivetran | 开源、Kafka-native、schema-aware |

---

## 面试收尾总结

> "这个 YouTube Analytics Pipeline 采用 Lambda-style lakehouse architecture，以 Kafka 作为 central event backbone，Flink 处理 real-time processing，Spark 做 batch reconciliation，Delta Lake 作为 unified storage layer。三层 Medallion design（Bronze → Silver → Gold）通过 progressive refinement 确保 data quality，而 purpose-built 的 serving stores（Redis、Druid、Elasticsearch、Feature Store）针对每种 consumer 的 access pattern 做了优化。
>
> 系统通过 partition-based design 在每一层实现 horizontal scaling，通过 AQE 和 salting 应对 data skew，通过 multi-AZ deployment 和 automated failover 达到 99.99% availability，并为 revenue-critical 的 ad billing 维持 exactly-once semantics。
>
> 在 governance 方面，PII 在 Silver 层边界做 pseudonymization，RBAC 按角色控制访问权限，column-level lineage 支持 impact analysis。成本通过 storage tiering、Spot instances（非 SLA workloads）以及激进的 partition/column pruning 来管控。"