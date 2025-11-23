```mermaid
graph TD
    subgraph "External"
        User[👤 User / Trading Bot]
        CG[🦎 CoinGecko API]
    end

    subgraph "AWS Cloud (eu-central-1)"
        EB[⏰ EventBridge] -->|Trigger Every 1h| Lambda
        
        User -->|HTTPS Request| FURL[🌐 Function URL]
        FURL -->|Invoke| Lambda[λ AWS Lambda\n(Docker/Python)]
        
        Lambda -->|1. Fetch Price| CG
        Lambda -->|2. Calc Volatility| Lambda
        Lambda -->|3. Store History| DDB[(DynamoDB\nHistory Table)]
        
        Lambda -->|4. Return JSON| FURL
    end

    style Lambda fill:#ff9900,stroke:#232f3e,stroke-width:2px,color:white
    style DDB fill:#3b48cc,stroke:#232f3e,stroke-width:2px,color:white
    style EB fill:#ff4f8b,stroke:#232f3e,stroke-width:2px,color:white
    style FURL fill:#8c4fff,stroke:#232f3e,stroke-width:2px,color:white
```