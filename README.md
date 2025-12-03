# SUNDOG-CLONE — Telegram TRON Trading Bot

> **LEGAL & SAFETY NOTICE**: This software handles crypto assets and may move or custody funds. Do not run in production without a legal review, compliance with local laws (KYC/AML), a security audit, and secure key management (KMS/HSM). The author is not responsible for financial or legal consequences.

A production-grade, testnet-first Telegram bot for trading TRC-20 tokens on TRON (Nile → Mainnet), inspired by SUNBOT.

## ✅ Features

- `/start`, `/wallet`, `/balance`, `/buy <token> <amount_TRX> [slippage%]`
- Real-time quoting via on-chain `getAmountsOut`
- Async job queue (RQ + Redis) with nonce-safe signing
- Full audit logging (user commands + tx lifecycle)
- Testnet-ready (TRON Nile); easy switch to mainnet
- Docker + Kubernetes ready

## 🚀 Quick Start (Local Dev)

### Prerequisites
- Docker + Docker Compose
- Python 3.11+ (for smoke test)

### 1. Clone & Setup
```bash
git clone https://github.com/yourname/sundog-clone.git
cd sundog-clone
cp .env.example .env
# Edit .env: set BOT_TOKEN (create via @BotFather), leave LOCAL_PRIVATE_KEY blank
