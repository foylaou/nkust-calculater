from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from core.engine import CalculatorEngine
from core.units import UnitConverter
from core.commercial import CommercialCalculator
from agent.tools import AgentToolkit
from agent.llm_client import SmartCalculatorAgent

app = FastAPI(title="Smart Commercial Calculator")

# CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化元件
engine = CalculatorEngine()
units = UnitConverter()
commercial = CommercialCalculator()
toolkit = AgentToolkit(engine, units, commercial)
agent = SmartCalculatorAgent(toolkit)


# ====== API Models ======
class CalcRequest(BaseModel):
    action: str  # "digit", "operator", "equals", "clear"
    value: Optional[str] = None


class NaturalLanguageRequest(BaseModel):
    query: str


# ====== 傳統計算機 API ======
@app.post("/api/calc/action")
def calculator_action(req: CalcRequest):
    if req.action == "digit":
        engine.press_digit(req.value)
    elif req.action == "operator":
        engine.press_operator(req.value)
    elif req.action == "equals":
        engine.press_equals()
    elif req.action == "clear":
        engine.clear()

    return {"display": engine.display}


@app.get("/api/calc/display")
def get_display():
    return {"display": engine.display}


# ====== AI Agent API ======
@app.post("/api/agent/query")
def agent_query(req: NaturalLanguageRequest):
    """處理自然語言計算請求"""
    result = agent.process_query(req.query)
    return {"response": result}


# ====== WebSocket for real-time ======
@app.websocket("/ws/agent")
async def websocket_agent(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        result = agent.process_query(data)
        await websocket.send_text(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
