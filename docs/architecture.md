# Architecture Documentation

## Overview

redevops.io is an open-source (AGPL), self-hostable agentic competitor intelligence platform designed for SMEs. This document describes the system architecture, including the OSS core components and agent layer orchestration.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           redevops.io Platform                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        OSS CORE LAYER                                │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │   │
│  │  │ changedetection.io│   │  Custom Web     │    │   Data          │  │   │
│  │  │ (Website Monitor)│   │  Scrapers       │    │   Collector     │  │   │
│  │  └────────┬────────┘    │  (Python/Scrapy)│    │                 │  │   │
│  │           │             └────────┬────────┘    └────────┬────────┘  │   │
│  │           │                      │                      │           │   │
│  │           └──────────────────────┼──────────────────────┘           │   │
│  │                                  │                                  │   │
│  │                         ┌────────▼────────┐                        │   │
│  │                         │   PostgreSQL    │                        │   │
│  │                         │   (Persistence) │                        │   │
│  │                         └─────────────────┘                        │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      AGENT LAYER (LangGraph)                         │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│  │  │ Collector   │───▶│ Analyzer    │───▶│ Context     │              │   │
│  │  │ Agent       │    │ Agent       │    │ Agent       │              │   │
│  │  └─────────────┘    └─────────────┘    └─────────────┘              │   │
│  │                                  │                                   │   │
│  │                                  ▼                                   │   │
│  │                         ┌─────────────┐                             │   │
│  │                         │ Summarizer  │                             │   │
│  │                         │ Agent       │                             │   │
│  │                         └─────────────┘                             │   │
│  │                                  │                                   │   │
│  │                                  ▼                                   │   │
│  │                         ┌─────────────┐                             │   │
│  │                         │ Dispatcher  │                             │   │
│  │                         │ Agent       │                             │   │
│  │                         └─────────────┘                             │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                    LLM Layer (Ollama)                        │   │   │
│  │  │              (Local Models - No API Costs)                   │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      OUTPUT CHANNELS                                 │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │ Slack   │  │ Discord │  │ Email   │  │ Webhook │  │ Dashboard│   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### OSS Core Layer

#### changedetection.io
- **Purpose**: Website change monitoring and alerting
- **Type**: Open-source Docker container
- **Function**: Monitors competitor websites for changes (pricing pages, product updates, blog posts)
- **Configuration**: Customizable check intervals (hourly, daily, weekly)
- **Integration**: Webhooks to trigger agent workflows

#### Custom Web Scrapers
- **Purpose**: Targeted data extraction from various sources
- **Type**: Python/Scrapy-based scrapers
- **Sources**: Competitor sites, review platforms, job boards, news sites
- **Features**: 
  - Respects robots.txt and rate limiting
  - Handles dynamic content (Playwright/Selenium for JavaScript)
  - Ethical scraping practices

#### PostgreSQL
- **Purpose**: Structured data persistence
- **Type**: Relational database
- **Usage**: Stores all collected intelligence, agent state, configuration
- **Benefits**: Full data ownership, no vendor lock-in

### Agent Layer (LangGraph)

The agent layer uses LangGraph for stateful, multi-agent orchestration:

#### Collector Agent
- Aggregates raw changes from all monitoring sources
- Normalizes data formats
- Routes to appropriate analyzers

#### Analyzer Agent
- Identifies patterns across data points
- Detects pricing trends, feature launches, hiring signals
- Flags significant changes for human review

#### Context Agent
- Compares current changes against historical data
- Calculates business impact
- Provides contextual relevance scoring

#### Summarizer Agent
- Generates business-outcome-focused insights
- Creates daily digests and weekly deep dives
- Formats outputs for different audiences

#### Dispatcher Agent
- Routes alerts to appropriate channels
- Manages notification preferences
- Handles human-in-the-loop approval workflows

### LLM Layer (Ollama)
- **Purpose**: Natural language processing and insight generation
- **Type**: Local LLM inference
- **Benefits**: No API costs, data privacy, offline operation
- **Models**: Configurable local models via Ollama

## Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  changedetect│     │   Web        │     │   External   │
│  ion.io      │     │  Scrapers    │     │   Sources    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                     │
       └────────────────────┼─────────────────────┘
                            │
                            ▼
                   ┌──────────────┐
                   │  Collector   │
                   │    Agent     │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Analyzer    │
                   │    Agent     │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │   Context    │
                   │    Agent     │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Summarizer  │
                   │    Agent     │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ Dispatcher   │
                   │    Agent     │
                   └──────┬───────┘
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
  ┌────────┐        ┌────────┐         ┌────────┐
  │ Slack  │        │ Email  │         │ Webhook│
  └────────┘        └────────┘         └────────┘
```

## Human-in-the-Loop Guardrails

The system implements human oversight for critical operations:

1. **Critical Alert Approval**: Pricing changes >10%, new competitor entries require acknowledgment
2. **Review Flags**: All automated outputs include "review before sharing" indicators
3. **Approval Thresholds**: Configurable alert sensitivity per user preference
4. **Audit Trail**: Complete logging of all agent actions for compliance

## Deployment Architecture

### Self-Hosted Stack

```
┌─────────────────────────────────────────────────────┐
│              Customer Infrastructure                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │           Docker Compose / Kubernetes        │   │
│  ├──────────────────────────────────────────────┤   │
│  │                                              │   │
│  │  ┌─────────────┐  ┌─────────────┐          │   │
│  │  │ changedetect│  │   Ollama    │          │   │
│  │  │ ion.io      │  │   (LLM)     │          │   │
│  │  └─────────────┘  └─────────────┘          │   │
│  │                                              │   │
│  │  ┌─────────────┐  ┌─────────────┐          │   │
│  │  │  PostgreSQL │  │  LangGraph  │          │   │
│  │  │             │  │  Agents     │          │   │
│  │  └─────────────┘  └─────────────┘          │   │
│  │                                              │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Security Considerations

- **Data Ownership**: All data stored in customer infrastructure
- **No External API Calls**: LLM runs locally, no data sent to third parties
- **Configurable Access Control**: Integration with existing authentication systems
- **Audit Logging**: Complete traceability of all system actions

## Scalability

The architecture supports:
- Unlimited competitors (configurable by deployment resources)
- Horizontal scaling of scraper workers
- Configurable check intervals based on infrastructure capacity
- Database sharding for large deployments
