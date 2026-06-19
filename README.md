# redevops.io: Agentic Competitor & Market Intelligence Platform

Open-source, self-hostable AI platform for automated competitor intelligence and market research. Designed for SME owners who need strategic insights without the operational overhead.

## The Problem: Why redevops?

### Pain → Legacy → Redevops

**Pain**: SME owners spend 80% of their day on operations, wearing multiple hats (founder, sales, marketing, HR, accounting). Strategic competitor monitoring becomes the first thing to drop. Owners report spending 6+ hours weekly on manual admin tasks alone, with competitor research adding another 10-20 hours of repetitive work.

**Legacy**: Most SMEs rely on:
- Manual Google searches (quarterly, if that)
- Ad-hoc spreadsheet tracking (outdated within weeks)
- Gut feeling and reactive customer complaints
- Occasional employee "let me check" updates

**Redevops**: Automated, continuous competitor intelligence running 24/7. Set it up once, get real-time alerts on pricing changes, new product launches, market positioning shifts, and customer sentiment changes—without lifting a finger.

## Ideal Customer Profile (ICP)

- **SME Owners & Founders** wearing multiple hats
- **Marketing Managers** at 10-200 person companies
- **Product Teams** needing competitive insights without dedicated analysts
- **Consultants & Agencies** serving multiple SME clients
- **E-commerce businesses** tracking competitor pricing and promotions

## Value Propositions

1. **Reclaim 15+ hours/week**: Automate manual competitor research and spreadsheet updates
2. **Never miss a change**: Real-time monitoring of competitor websites, pricing, and content
3. **Strategic clarity**: Get actionable insights, not just data dumps
4. **Self-hosted & private**: Your competitive intelligence stays on your infrastructure
5. **Open-source (AGPL)**: No vendor lock-in, full transparency, community-driven

## Architecture Overview

redevops follows a two-layer architecture:

```
┌─────────────────────────────────────────┐
│         Agent Layer (Intelligence)      │
│  • Competitor monitoring agents         │
│  • Content analysis & summarization     │
│  • Alert generation & routing           │
│  • LangGraph-based orchestration        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          OSS Core (Foundation)          │
│  • PageCrawl / changedetection.io       │
│  • Self-hosted agent infrastructure     │
│  • Aegra platform integration           │
│  • Data storage & retrieval             │
└─────────────────────────────────────────┘
```

- **OSS Core**: Built on open-source foundations including PageCrawl and changedetection.io for web monitoring, with Aegra as the self-hosted agent infrastructure
- **Agent Layer**: LangGraph-based agents that orchestrate competitor analysis, content extraction, and insight generation

## Quickstart

### Prerequisites

- Docker & Docker Compose
- 2GB+ RAM available
- Basic command-line familiarity

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/redevops-io/market-radar.git
   cd market-radar
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (API keys, monitoring targets, etc.)
   ```

3. **Start the platform**
   ```bash
   docker compose up -d
   ```

4. **Access the dashboard**
   Open `http://localhost:8080` in your browser

5. **Add your first competitor**
   - Navigate to Competitors → Add New
   - Enter the competitor website URL
   - Select monitoring frequency (default: hourly)
   - Choose what to track (pricing, content, features, etc.)

### First Steps After Setup

1. **Configure monitoring targets**: Add 3-5 key competitors to start
2. **Set up alerts**: Configure email/Slack notifications for significant changes
3. **Review initial insights**: Check the dashboard after 24 hours for trend analysis
4. **Customize agent behavior**: Adjust analysis depth and alert thresholds in Settings

## Pricing

redevops is **100% free and open-source** (AGPL license). No tiers, no subscriptions, no hidden costs. You pay only for your own infrastructure.

For managed hosting options (if you prefer not to self-host), see our [Partner Program](./PARTNERS.md).

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details. This is a self-hostable platform—you own your data and your deployment.

---

**Built for SMEs who need enterprise-grade intelligence without enterprise complexity.**
