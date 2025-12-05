# 開發注意事項 (NOTES.md)

本文件記錄開發過程中需要特別注意的細節和常見問題。

---

## 🔴 關鍵注意事項

### 1. IPC 通訊機制

本專案使用 **stdin/stdout IPC** 而非 HTTP Port 通訊。

#### 為什麼選擇 IPC？

| 問題 | Port 方案 | IPC 方案 |
|------|-----------|----------|
| Port 衝突 | ❌ 可能失敗 | ✅ 不需要 |
| 防火牆 | ❌ 可能被擋 | ✅ 不經網路 |
| 其他程式干擾 | ❌ 可能 | ✅ 不會 |
| 跨平台 | ✅ 都支援 | ✅ 都支援 |

#### IPC 運作原理

```
Electron App
    │
    │ spawn('python', ['ipc_server.py'])
    │
    ├──── stdin ────► Python 接收 JSON 請求
    │
    ◄──── stdout ──── Python 回傳 JSON 回應
```

每個 spawn 出來的 Python 進程都是**完全獨立**的：
- 獨立的 PID
- 獨立的 stdin/stdout
- 獨立的記憶體空間
- **不會干擾**其他 Python 程式

---

### 2. 進程生命週期管理

#### ⚠️ 必須處理的退出情境

```javascript
// main.js - 必須在所有退出點清理 Python 進程

app.on('before-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill('SIGTERM');
    }
});

app.on('window-all-closed', () => {
    if (pythonProcess) {
        pythonProcess.kill('SIGTERM');
    }
    app.quit();
});

// 處理意外崩潰
process.on('exit', () => {
    if (pythonProcess) {
        pythonProcess.kill('SIGKILL');
    }
});

// 處理未捕捉的例外
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    if (pythonProcess) {
        pythonProcess.kill('SIGKILL');
    }
    app.quit();
});
```

#### 如果沒有正確清理會發生什麼？

- 殭屍 Python 進程持續運行
- 記憶體洩漏
- 用戶需要手動從工作管理員結束進程

---

### 3. 跨平台差異

#### Python 執行檔名稱

| 平台 | 開發模式 | 打包後 |
|------|----------|--------|
| Windows | `python` | `calculator-backend.exe` |
| Linux | `python3` | `calculator-backend` |
| macOS | `python3` | `calculator-backend` |

```javascript
function getPythonCommand() {
    if (app.isPackaged) {
        const exeName = process.platform === 'win32' 
            ? 'calculator-backend.exe' 
            : 'calculator-backend';
        return path.join(process.resourcesPath, 'backend', exeName);
    }
    return process.platform === 'win32' ? 'python' : 'python3';
}
```

#### Windows CMD 視窗

```javascript
// Windows 必須加這個，否則會彈出黑色 CMD 視窗
spawn(command, args, { 
    windowsHide: true 
});
```

#### 路徑分隔符

```javascript
// ✅ 正確 - 使用 path.join
const backendPath = path.join(__dirname, '..', 'backend');

// ❌ 錯誤 - 硬編碼分隔符
const backendPath = __dirname + '/../backend';  // Linux 才 work
const backendPath = __dirname + '\\..\\backend'; // Windows 才 work
```

---

### 4. JSON 通訊編碼

#### Python 端

```python
import json
import sys

# 輸出時確保中文正確
response = {"message": "計算完成", "result": 157.50}
print(json.dumps(response, ensure_ascii=False), flush=True)
#                         ^^^^^^^^^^^^^^^^      ^^^^^^^^^^
#                         中文不轉 escape        立即輸出

# 讀取時使用 UTF-8
for line in sys.stdin:
    request = json.loads(line.strip())
```

#### Electron 端

```javascript
// 設定 encoding
pythonProcess = spawn(command, args, {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
});

// 處理多行輸出的情況
let buffer = '';
pythonProcess.stdout.on('data', (data) => {
    buffer += data.toString();
    const lines = buffer.split('\n');
    buffer = lines.pop(); // 保留不完整的行
    
    for (const line of lines) {
        if (line.trim()) {
            const response = JSON.parse(line);
            // 處理 response
        }
    }
});
```

---

### 5. Decimal 精度問題

#### ⚠️ 浮點數陷阱

```python
from decimal import Decimal

# ✅ 正確 - 從字串建立
price = Decimal("19.99")
tax = Decimal("0.05")

# ❌ 錯誤 - 浮點數精度問題
price = Decimal(19.99)  # 會得到 19.989999999999998...
```

#### 控制輸出精度

```python
result = Decimal("100") / Decimal("3")
# 33.33333333333333...

result = result.quantize(Decimal("0.01"))
# 33.33
```

---

### 6. API Key 安全

#### ⚠️ 絕對禁止

```python
# ❌ 絕對不要這樣做
api_key = "sk-ant-api03-xxxxx"  # 寫死在程式碼
```

#### ✅ 正確做法

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("Missing ANTHROPIC_API_KEY")
```

#### 確保 .gitignore 包含

```
.env
.env.local
.env.*.local
```

---

### 7. Electron 安全設定

#### Context Isolation

```javascript
// main.js
mainWindow = new BrowserWindow({
    webPreferences: {
        contextIsolation: true,   // 必須啟用
        nodeIntegration: false,   // 必須禁用
        preload: path.join(__dirname, 'preload.js')
    }
});
```

#### 為什麼重要？

- `contextIsolation: true` 隔離 preload 和渲染進程
- `nodeIntegration: false` 禁止渲染進程存取 Node.js API
- 防止 XSS 攻擊直接存取系統資源

---

### 8. 錯誤處理

#### Python 端 - 必須捕捉所有例外

```python
# ipc_server.py
for line in sys.stdin:
    try:
        request = json.loads(line.strip())
        result = handle_request(request)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}), flush=True)
    except Exception as e:
        print(json.dumps({"error": str(e)}), flush=True)
```

#### Electron 端 - 處理 Python 錯誤

```javascript
// 監聽 Python stderr
pythonProcess.stderr.on('data', (data) => {
    console.error('Python Error:', data.toString());
    // 可選：通知用戶或嘗試重啟
});

// 監聯 Python 退出
pythonProcess.on('close', (code) => {
    if (code !== 0) {
        console.error(`Python exited with code ${code}`);
        // 嘗試重啟或通知用戶
    }
});
```

#### React 端 - 顯示錯誤給用戶

```typescript
const askAgent = async (query: string) => {
    try {
        setLoading(true);
        const result = await window.calculator.askAgent(query);
        
        if (result.error) {
            setError(result.error);
        } else {
            setResponse(result.response);
        }
    } catch (error) {
        setError('系統發生錯誤，請稍後再試');
        console.error(error);
    } finally {
        setLoading(false);
    }
};
```

---

### 9. 打包注意事項

#### PyInstaller Hidden Imports

某些套件需要手動指定：

```bash
pyinstaller --onefile ipc_server.py \
    --hidden-import=anthropic \
    --hidden-import=anthropic._client \
    --hidden-import=httpx \
    --hidden-import=httpcore
```

#### Electron Builder extraResources

```json
{
    "build": {
        "extraResources": [
            {
                "from": "../backend/dist/",
                "to": "backend/",
                "filter": ["**/*"]
            }
        ]
    }
}
```

打包後的結構：

```
MyApp.app/  (macOS)
├── Contents/
│   ├── MacOS/
│   │   └── MyApp
│   └── Resources/
│       └── backend/
│           └── calculator-backend  ← Python 執行檔在這

MyApp/  (Windows)
├── MyApp.exe
└── resources/
    └── backend/
        └── calculator-backend.exe  ← Python 執行檔在這
```

---

## 📝 開發檢查清單

### 開始開發前

- [ ] Python 3.10+ 已安裝
- [ ] Node.js 18+ 已安裝
- [ ] `.env` 已建立並填入 API Key
- [ ] 虛擬環境已建立並啟動
- [ ] 依賴已安裝

### 提交程式碼前

- [ ] 沒有硬編碼的 API Key
- [ ] 沒有 `.env` 被提交
- [ ] Python 程式碼已格式化 (`black .`)
- [ ] 測試通過 (`pytest`)
- [ ] ESLint 無錯誤 (`npm run lint`)

### 打包發布前

- [ ] 後端已用 PyInstaller 打包
- [ ] `extraResources` 路徑正確
- [ ] 在目標平台測試過
- [ ] 進程清理邏輯正確
- [ ] 錯誤處理完善

---

## 🔧 常見問題速查

| 問題 | 原因 | 解決方法 |
|------|------|----------|
| Python 沒有回應 | stdout 沒 flush | 加 `flush=True` |
| 中文亂碼 | 編碼問題 | 設定 `PYTHONIOENCODING=utf-8` |
| Windows 彈出黑框 | spawn 設定 | 加 `windowsHide: true` |
| 打包後找不到 Python | 路徑錯誤 | 用 `process.resourcesPath` |
| Decimal 精度錯誤 | 用 float 建立 | 用字串建立 `Decimal("0.1")` |
| 進程殘留 | 沒清理 | 在所有退出點 kill |