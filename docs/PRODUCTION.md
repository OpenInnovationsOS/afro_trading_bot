
---

## 🖼️ File: `docs/architecture.mmd`

```mermaid
%% docs/architecture.mmd
graph TD
    A[Telegram User] -->|/buy, /balance| B(Telegram Bot\naiogram)
    B -->|Log command| C[(PostgreSQL)]
    B -->|Enqueue job| D[Redis Queue]
    D --> E[RQ Worker]
    E --> F[KeyManager\n(Local / AWS KMS)]
    E --> G[TRON Client\ntronpy + SunSwap Router]
    G -->|Read| H[TRON Nile Node\n(api.nileex.io)]
    G -->|Write| H
    E -->|Update status| C
    E -->|Notify| B
    B -->|Send message| A

    I[Admin] -->|GET /trades| J[FastAPI]
    J --> C
    J -->|Metrics| K[Prometheus]
    K --> L[Grafana]
    E -->|Errors| M[Sentry]

    style A fill:#9f9,stroke:#333
    style F fill:#f96,stroke:#333
    style H fill:#69f,color:#fff
