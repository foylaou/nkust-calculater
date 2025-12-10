#!/usr/bin/env python3
"""
測試 Backend Agent 功能
使用方法: python3 test_backend.py
"""

import sys
import os

# 添加 backend 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("測試 1: 檢查依賴模組")
print("=" * 60)

required_modules = [
    'dotenv',
    'google.genai',
    'requests',
    'pandas'
]

missing_modules = []

for module_name in required_modules:
    try:
        if module_name == 'google.genai':
            import google.genai
        elif module_name == 'dotenv':
            from dotenv import load_dotenv
        elif module_name == 'requests':
            import requests
        elif module_name == 'pandas':
            import pandas
        print(f"✅ {module_name} - 已安裝")
    except ImportError as e:
        print(f"❌ {module_name} - 未安裝")
        missing_modules.append(module_name)

if missing_modules:
    print("\n⚠️  缺少以下模組，請執行:")
    print(f"cd backend && pip install -r requirements.txt")
    sys.exit(1)

print("\n" + "=" * 60)
print("測試 2: 導入 ExchangeRate 類")
print("=" * 60)

try:
    from tool.ExchangeRate import TaiwanExchangeRate
    print("✅ ExchangeRate 類導入成功")
except Exception as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("測試 3: 導入 AI_Agent 類")
print("=" * 60)

try:
    from agent.agent import AI_Agent
    print("✅ AI_Agent 類導入成功")
except Exception as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("測試 4: 初始化 AI_Agent")
print("=" * 60)

try:
    agent = AI_Agent()
    print("✅ AI_Agent 初始化成功")
except Exception as e:
    print(f"❌ 初始化失敗: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("測試 5: 測試 get_bank_rules()")
print("=" * 60)

try:
    rules = agent.get_bank_rules('USD')
    print("✅ get_bank_rules() 測試成功")
    print(f"   結果: {rules}")
except Exception as e:
    print(f"❌ 測試失敗: {e}")

print("\n" + "=" * 60)
print("測試 6: 測試 roles()")
print("=" * 60)

try:
    role_info = agent.roles()
    print("✅ roles() 測試成功")
    print(f"   角色: {role_info['role']}")
    print(f"   描述: {role_info['description']}")
    print(f"   支援貨幣: {', '.join(role_info['supported_currencies'][:5])}...")
except Exception as e:
    print(f"❌ 測試失敗: {e}")

print("\n" + "=" * 60)
print("測試 7: 測試匯率查詢 (需要網路)")
print("=" * 60)

try:
    result = agent.get_exchange_rate('USD')
    if result['success']:
        print("✅ 匯率查詢成功")
        print(f"   貨幣: {result['currency']}")
        print(f"   日期: {result.get('date', 'N/A')}")
        print(f"   現金買入: {result.get('cash_buy', 'N/A')}")
        print(f"   現金賣出: {result.get('cash_sell', 'N/A')}")
    else:
        print(f"❌ 匯率查詢失敗: {result.get('error')}")
        print("   提示: 這可能是因為:")
        print("   1. 沒有設置 FINMINDTRADE_API_KEY 環境變數")
        print("   2. 網路連接問題")
        print("   3. API 限額已達上限")
except Exception as e:
    print(f"❌ 測試失敗: {e}")

print("\n" + "=" * 60)
print("測試 8: 測試 IPC Server")
print("=" * 60)

try:
    from ipc_server import IPCServer
    server = IPCServer()
    print("✅ IPC Server 初始化成功")

    # 測試處理請求
    test_request = {
        "action": "bank_agent_info"
    }
    response = server.handle_request(test_request)
    if response.get('success'):
        print("✅ IPC Server 處理請求成功")
    else:
        print(f"❌ 處理請求失敗: {response.get('error')}")
except Exception as e:
    print(f"❌ 測試失敗: {e}")

print("\n" + "=" * 60)
print("✅ 所有基本測試完成!")
print("=" * 60)
print("\n如果上面的測試都通過，則 Backend 功能正常。")
print("如果 Electron 仍然無法連接，請檢查:")
print("1. Electron DevTools Console 的錯誤信息")
print("2. Python 進程是否正確啟動 (檢查 PID)")
print("3. 確保重新編譯了前端: cd frontend && pnpm run dev")
