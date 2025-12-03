┌─────────────────────────────────────────────────────────┐
│                    Electron Frontend                     │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │  傳統計算機 UI   │  │     自然語言輸入區           │  │
│  │  (按鈕/螢幕)     │  │     (文字輸入框)             │  │
│  └─────────────────┘  └──────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼────────────────────────────────┐
│                   Python Backend (FastAPI)               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │CalculatorAPI │  │  AI Agent    │  │ 單位轉換模組   │  │
│  │ (你現有的)    │  │ (LLM 整合)   │  │               │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────┘

# ====== 專案結構建議 ======
# smart_calculator/
# ├── main.py                 # FastAPI 入口
# ├── core/
# │   ├── engine.py           # 你現有的 CalculatorEngine
# │   ├── units.py            # 單位轉換模組
# │   └── commercial.py       # 商業計算 (折扣、稅金)
# ├── agent/
# │   ├── parser.py           # 自然語言解析
# │   ├── tools.py            # Agent 可呼叫的工具
# │   └── llm_client.py       # LLM API 整合
# └── api/
#     └── routes.py           # API 路由

```

### 7. Electron 前端結構
```
electron - calculator /
├── package.json
├── main.js  # Electron 主程序
├── preload.js  # 預載腳本
└── renderer /
├── index.html
├── styles.css
└── app.js  # React 或 vanilla JS