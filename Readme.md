C:\AI
│
├── agents       ← 可以執行、會自主工作的 AI
│
├── skills       ← AI 可以學習/調用的能力與知識
│
├── shared       ← 多個 Agent 共用的 Python library
│
├── data         ← 市場資料、SIwave 資料、報告
│
├── configs      ← 全域設定
│
├── logs         ← 執行紀錄
└── docs         ← 整個 AI Workspace 的文件

整套系統
Terminal 1  (Kurumi)
└─ python service\server\main.py
   └─ FastAPI :8000

Terminal 2  (Kurumi)
└─ python service\server\worker.py
   └─ Background Worker

Terminal 3
└─ npm run dev
   └─ React Dashboard :3000
   
   
C:\AI\agents\finance\finance-trading-agents\AI-Trader
│
├── Kurumi
│   └── Python 3.12.10
│
├── FastAPI Backend
│   └── http://localhost:8000      ✓
│
├── Worker
│   ├── Price Update               ✓
│   ├── Profit History             ✓
│   └── Market Intel               △ 缺 Alpha Vantage API Key
│
├── SQLite
│   └── clawtrader.db              ✓
│
└── React Frontend
    └── http://localhost:3000      ✓
	

