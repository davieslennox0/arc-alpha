# AlphaLoop Arc — Autonomous AI FX Prime Broker

> Agora Agents Hackathon · Canteen × Circle · Arc Testnet

AlphaLoop is a fully autonomous multi-agent prime broker that executes **AI-driven FX trades** on Arc — Circle's stablecoin-native L1. Agents analyze market signals and settle USDC/EURC currency pairs on-chain with sub-second finality.

## Architecture

```
Scout Agent      →  reads macro signals, RSI, momentum, news
Risk Agent       →  sizes position, approves/rejects trade
Learning Agent   →  adapts strategy based on outcome history
Execution Agent  →  settles USDC ↔ EURC FX trade on Arc
```

External agents (Alice, Bob, Charlie) pay via x402 micropayments and receive fully autonomous FX execution — no humans in the loop.

## What Makes It Agentic

- **Scout** pulls live price feeds, RSI, momentum, and Polymarket sentiment
- **Risk** runs Kelly Criterion sizing and approves/rejects based on portfolio heat
- **Learning** tracks win rates per strategy and adjusts allocation over time
- **Execution** settles two on-chain transactions per trade: fee payment + FX delivery

Every cycle is fully autonomous. No human triggers any trade.

## Stack

| Layer | Tech |
|-------|------|
| Settlement | Arc Testnet (Chain ID: 5042002) |
| FX Pair | USDC ↔ EURC (Circle native stablecoins) |
| Broker API | FastAPI |
| Agent Interface | MCP Server |
| Signal Engine | Python — RSI, VWAP, Bollinger Bands, momentum |
| Payment | x402 micropayments |

## API Endpoints

| Endpoint | Cost | Description |
|----------|------|-------------|
| `GET /preview/{asset}` | Free | Price + confidence preview |
| `POST /signal` | $0.01 USDC | Full directional signal |
| `POST /validate` | $0.02 USDC | Risk Agent validation |
| `POST /execute` | $0.05 USDC | FX trade execution |
| `POST /broker` | $0.02 USDC | Full 4-agent pipeline |
| `GET /status` | Free | Portfolio + performance |
| `GET /activity` | Free | Live trade feed |

## FX Settlement Flow

```
Agent pays $0.05 USDC → Broker (x402 fee)        [TX 1]
Scout scores signal → Risk sizes position
Broker settles EURC → Agent (FX delivery)         [TX 2]
Learning Agent records outcome → adjusts strategy
```

Every trade = 2 confirmed on-chain transactions on Arc.

## Circle Tools Used

- **USDC** — native gas token + payment settlement
- **EURC** — FX delivery token (EUR-denominated)
- **Arc Testnet** — sub-second finality, $0.01 fees

## Live Demo

**Broker:** `https://[your-domain]/`  
**Explorer:** [Broker wallet on ArcScan](https://testnet.arcscan.app/address/0xB9d62aFC43C1d62887AdDBBD159A5F774209e40d)

## Agents

| Agent | Asset | Strategy |
|-------|-------|----------|
| Alice | EURUSD | Balanced — alternates long/short |
| Bob | EURUSD | Balanced — 360s cycle |
| Charlie | EURUSD | Balanced — 420s cycle |

Each agent runs independently, pays its own fees, and accumulates its own FX position history.

## Running Locally

```bash
git clone https://github.com/davieslennox0/arc-alpha.git
cd arc-alpha
pip install -r requirements.txt
cp .env.example .env  # fill in your keys
python3 prime_broker.py   # starts broker on port 8002
python3 demo_agents.py    # starts Alice, Bob, Charlie
```

## Hackathon

Built for the [Agora Agents Hackathon](https://agora.thecanteenapp.com) by Canteen × Circle · May 2026.

**Team:** [@Syke0x](https://x.com/Syke0x)
