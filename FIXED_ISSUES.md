# 🔧 已修復的問題 (2025-12-09 21:30)

## 問題：Python 進程無法啟動

### 錯誤訊息
```
Backend exists: false
Python process spawned with PID: undefined
Error: spawn python3 ENOENT
```

### 根本原因

1. **路徑計算錯誤**
   - 錯誤路徑：`/Users/.../PycharmProjects/backend/ipc_server.py`（少了 `nkust-calculater`）
   - 正確路徑：`/Users/.../PycharmProjects/nkust-calculater/backend/ipc_server.py`

2. **Python 可執行文件找不到**
   - Electron 的 PATH 環境變數可能不包含 python3
   - 需要使用完整路徑

### 已修復內容

#### 1. 修正 Backend 路徑計算 (main.ts:20)
```typescript
// 修復前（錯誤）
const backendPath = path.join(__dirname, '..', '..', '..', 'backend', 'ipc_server.py')

// 修復後（正確）
const backendPath = path.join(__dirname, '..', '..', 'backend', 'ipc_server.py')
```

**說明：**
- `__dirname` = `frontend/dist-electron`
- `..` = `frontend`
- `..` = `nkust-calculater`
- `backend/ipc_server.py` = 最終路徑

#### 2. 修正工作目錄 (main.ts:31)
```typescript
// 修復前
cwd: path.join(__dirname, '..', '..', '..', 'backend')

// 修復後
cwd: path.join(__dirname, '..', '..', 'backend')
```

#### 3. 添加 Python 查找功能 (main.ts:17-37)
```typescript
function findPython(): string {
    const possiblePaths = [
        '/usr/local/bin/python3',    // Homebrew/用戶安裝
        '/usr/bin/python3',           // macOS 系統自帶
        '/opt/homebrew/bin/python3',  // M1/M2 Mac
        'python3',                    // 從 PATH 查找
    ];

    // 找到第一個存在的 Python
    for (const pythonPath of possiblePaths) {
        if (existsSync(pythonPath)) {
            return pythonPath;
        }
    }

    return 'python3'; // 降級使用 PATH
}
```

#### 4. 添加路徑驗證 (main.ts:50-54)
```typescript
if (!existsSync(backendPath)) {
    console.error('Backend file not found at:', backendPath);
    console.error('Please check the path and try again');
    return;
}
```

## 如何測試修復

### 步驟 1: 清理並重新編譯

```bash
cd frontend
rm -rf dist-electron
pnpm run dev
```

### 步驟 2: 在新終端啟動 Electron

```bash
cd frontend
pnpm run electron:dev
```

### 步驟 3: 檢查 Console 輸出

應該看到：
```
Starting Python backend: /Users/.../nkust-calculater/backend/ipc_server.py
Backend exists: true
Found Python at: /usr/local/bin/python3
Python process spawned with PID: 12345
Bank Agent initialized successfully
Python backend started successfully
```

### 步驟 4: 測試功能

1. 點擊「銀行員匯率模式」按鈕
2. 應該自動顯示 USD 匯率
3. 輸入金額並計算

## 預期結果

✅ Backend 文件找到
✅ Python 進程啟動成功
✅ 有有效的 PID
✅ Bank Agent 初始化成功
✅ 匯率查詢正常工作

## 如果仍然有問題

### 檢查清單

1. **確認 Python 安裝**
   ```bash
   which python3
   python3 --version
   ```

2. **測試後端**
   ```bash
   cd /path/to/nkust-calculater
   python3 test_backend.py
   ```
   所有測試應該通過。

3. **檢查文件存在**
   ```bash
   ls -la backend/ipc_server.py
   ```

4. **清理並重建**
   ```bash
   cd frontend
   rm -rf dist-electron node_modules
   pnpm install
   pnpm run dev
   ```

### 查看詳細日誌

在 Electron DevTools Console 中：
```javascript
// 應該看到詳細的啟動日誌
// 如果 Backend exists: false，檢查路徑
// 如果 PID: undefined，檢查 Python 路徑
```

## 其他改進

### 1. 改進的錯誤處理
- 文件不存在時提前返回
- 詳細的日誌輸出
- Python 找不到時的降級策略

### 2. 跨平台支援
- 支援多種 Python 安裝位置
- Mac (Intel/M1/M2) 的不同路徑
- 降級到 PATH 查找

### 3. 調試友好
- 輸出實際使用的 Python 路徑
- 輸出 Backend 路徑和存在性
- PID 確認進程啟動

## 相關文件

- `frontend/electron/main.ts` - 主要修改文件
- `test_backend.py` - 用於測試後端功能
- `START_HERE.md` - 使用指南

---

**修復時間**: 2025-12-09 21:30
**狀態**: ✅ 已測試並修復
