# Corporate Finance Autopilot

An automated AI agent and financial reasoning engine. 
It assesses the financial health of public companies and delivers strategic advisory.
Built for the Weekend Student Hackathon.

## 1. How to Run

Built with a production-first mindset. Fully containerized.

### Prerequisites
- Docker & Docker Compose installed
- An active OpenAI API Key

### Quick Start
1. Clone this repository.
2. Create an environment file:
   ```bash
   cp .env.example .env
   ```
3. Insert your `OPENAI_API_KEY` into the `.env` file.
4. Build and start the container:
   ```bash
   docker-compose up --build
   ```
5. Open your browser at `http://localhost:8501`.

## 2. Architecture

The system decouples deterministic math from probabilistic AI analysis. 
Pipeline flow: `Ingest → Validate → Reason → Output`.

### Core Components
- **Data Ingestion (`app/services/scraper/`):**
  - Extracts data via `yfinance`.
  - No HTML scraping required.
  - Network calls wrapped with `Tenacity` for retries.
- **Data Validation (`app/models/`):**
  - Enforces strict schemas using `Pydantic`.
  - Prevents downstream LLM hallucination.
- **Financial Engine (`app/services/finance/`):**
  - Deterministic Python module.
  - Calculates historical CAGR.
  - Projects Base, Upside, and Downside scenarios.
- **Agentic Orchestration (`app/services/agent/`):**
  - Custom `StateGraph` built with LangGraph.
  - Implements a ReAct state machine.
  - LLM plans, invokes tools, and synthesizes the final memo.
- **Visualization (`frontend/`):**
  - Streamlit dashboard.
  - Renders interactive Plotly charts.
  - Displays real-time agent reasoning traces.

## 3. Limitations & Trade-offs

- **Simplified Financial Model:** - Revenue is extrapolated using top-line CAGR. 
  - Does not account for complex balance sheet items or D&A.
- **Data Depth:** - Relies on `yfinance` news summaries. 
  - Parsing full 10-K SEC filings would provide deeper context.
- **Single Agent Pattern:** - Uses one agent to plan, execute, and write. 
  - A multi-agent system (e.g., Researcher + Analyst) would be more robust.
- **Latency:** - Sequential ReAct tool-calling introduces delay. 
  - Tool executions are currently not parallelized.

## 4. Third-Party Data & Libraries

Adheres to "Open source first" guidelines. No unauthorized web scraping.

### Major Open Source Libraries
- **LangGraph & LangChain:** Orchestrates the state machine.
- **Pydantic:** Enforces data validation.
- **Streamlit / FastAPI:** Rapid UI and API structuring.
- **Plotly:** Interactive data visualization.

### Data Sources & APIs
- **Yahoo Finance (`yfinance`):** - Used for market data and company news. 
  - Open-source wrapper over public endpoints.
- **OpenAI API (`gpt-4o`):** - Powers the core reasoning engine.

---
**🚨 DISCLAIMER:** 
All outputs are AI-generated, hypothetical, and subject to uncertainty. 
This is NOT investment advice. Do not use for real-world trading.
