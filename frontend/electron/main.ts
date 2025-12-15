import { app, BrowserWindow, ipcMain, Menu } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn, ChildProcess } from 'child_process';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow: BrowserWindow | null;
let pythonProcess: ChildProcess | null = null;

// Check if running in development mode
const isDev = !app.isPackaged;

// Find Python executable
function findPython(backendDir: string): string {
    // Priority 1: Virtual environment in backend directory
    const venvPython = path.join(backendDir, '.venv', 'bin', 'python3');
    if (existsSync(venvPython)) {
        console.log('Found Python in venv at:', venvPython);
        return venvPython;
    }

    // Priority 2: Common system locations
    const possiblePaths = [
        '/usr/local/bin/python3',
        '/usr/bin/python3',
        '/opt/homebrew/bin/python3',
        'python3', // Fallback to PATH
    ];

    for (const pythonPath of possiblePaths) {
        if (pythonPath === 'python3') {
            return pythonPath; // Let system try to find it
        }
        if (existsSync(pythonPath)) {
            console.log('Found Python at:', pythonPath);
            return pythonPath;
        }
    }

    console.warn('Python3 not found in common locations, using "python3" from PATH');
    return 'python3';
}

// Python Backend Management
function startPythonBackend() {
    // In dev mode: use Python script, in production: use PyInstaller executable
    let backendPath: string;
    let backendDir: string;
    let backendArgs: string[];

    if (isDev) {
        // Development: dist-electron -> frontend -> nkust-calculater -> backend
        backendDir = path.join(__dirname, '..', '..', 'backend');
        backendPath = findPython(backendDir);
        backendArgs = [path.join(backendDir, 'ipc_server.py')];
    } else {
        // Production: use PyInstaller executable
        backendDir = path.join(process.resourcesPath, 'backend', 'ipc_server');
        backendPath = path.join(backendDir, 'ipc_server');
        backendArgs = [];
    }

    console.log('Starting Python backend:', backendPath);
    console.log('Backend arguments:', backendArgs);
    console.log('Current directory:', __dirname);
    console.log('Backend exists:', existsSync(backendPath));

    if (!existsSync(backendPath)) {
        console.error('Backend file not found at:', backendPath);
        console.error('Please check the path and try again');
        return;
    }

    try {
        pythonProcess = spawn(backendPath, backendArgs, {
            stdio: ['pipe', 'pipe', 'pipe'],
            env: { ...process.env },
            cwd: backendDir
        });

        console.log('Python process spawned with PID:', pythonProcess.pid);

        // Set up response handler for stdout
        setupPythonResponseHandler();

        if (pythonProcess.stderr) {
            pythonProcess.stderr.on('data', (data) => {
                const errorMsg = data.toString();
                console.error('Python stderr:', errorMsg);

                // Check for common errors
                if (errorMsg.includes('ModuleNotFoundError')) {
                    console.error('Missing Python module. Run: cd backend && pip install -r requirements.txt');
                } else if (errorMsg.includes('SyntaxError')) {
                    console.error('Python syntax error in backend code');
                }
            });
        }

        pythonProcess.on('error', (error) => {
            console.error('Failed to start Python process:', error);
            console.error('Make sure python3 is installed and in PATH');
        });

        pythonProcess.on('exit', (code, signal) => {
            console.log(`Python process exited with code ${code}, signal ${signal}`);
            if (code !== 0 && code !== null) {
                console.error('Python process crashed!');
            }
            pythonProcess = null;
        });

        // Give Python some time to start
        setTimeout(() => {
            if (pythonProcess && pythonProcess.pid) {
                console.log('Python backend started successfully');
            } else {
                console.error('Python backend failed to start');
            }
        }, 1000);

    } catch (error) {
        console.error('Exception while starting Python:', error);
    }
}

// Queue to handle pending requests
let requestQueue: Array<{
    resolve: (value: any) => void;
    reject: (reason?: any) => void;
    timer: NodeJS.Timeout;
}> = [];

// Set up response handler once
function setupPythonResponseHandler() {
    if (!pythonProcess || !pythonProcess.stdout) return;

    pythonProcess.stdout.on('data', (data: Buffer) => {
        const lines = data.toString().trim().split('\n');

        for (const line of lines) {
            if (!line) continue;

            // Skip non-JSON lines (logs, errors, etc.)
            if (!line.startsWith('{')) {
                console.log('Python output:', line);
                continue;
            }

            try {
                const response = JSON.parse(line);
                const pending = requestQueue.shift();
                if (pending) {
                    clearTimeout(pending.timer);
                    pending.resolve(response);
                }
            } catch (error) {
                console.error('Failed to parse Python response:', error, 'Line:', line);
                const pending = requestQueue.shift();
                if (pending) {
                    clearTimeout(pending.timer);
                    pending.reject(error);
                }
            }
        }
    });
}

function sendToPython(request: any): Promise<any> {
    return new Promise((resolve, reject) => {
        if (!pythonProcess || !pythonProcess.stdin || !pythonProcess.stdout) {
            console.error('Python process not available');
            reject(new Error('Python process not available'));
            return;
        }

        // Timeout after 30 seconds
        const timer = setTimeout(() => {
            const index = requestQueue.findIndex(r => r.resolve === resolve);
            if (index !== -1) {
                requestQueue.splice(index, 1);
            }
            reject(new Error('Request timeout'));
        }, 30000);

        // Add to queue
        requestQueue.push({ resolve, reject, timer });

        const requestStr = JSON.stringify(request) + '\n';
        console.log('Sending to Python:', request.action);

        // Send request
        try {
            pythonProcess.stdin.write(requestStr, (error) => {
                if (error) {
                    console.error('Failed to write to Python:', error);
                    const index = requestQueue.findIndex(r => r.resolve === resolve);
                    if (index !== -1) {
                        clearTimeout(requestQueue[index].timer);
                        requestQueue.splice(index, 1);
                    }
                    reject(error);
                }
            });
        } catch (error) {
            console.error('Exception while writing to Python:', error);
            const index = requestQueue.findIndex(r => r.resolve === resolve);
            if (index !== -1) {
                clearTimeout(requestQueue[index].timer);
                requestQueue.splice(index, 1);
            }
            reject(error);
        }
    });
}

function stopPythonBackend() {
    // Reject all pending requests
    requestQueue.forEach(({ reject, timer }) => {
        clearTimeout(timer);
        reject(new Error('Python process shutting down'));
    });
    requestQueue = [];

    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }
}

// Suppress security warnings in development (they're expected with Vite)
if (isDev) {
    process.env.ELECTRON_DISABLE_SECURITY_WARNINGS = 'true';
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 800,
        minWidth: 1000,
        minHeight: 800,
        frame: false, // Remove default window frame (like Discord)
        titleBarStyle: 'hidden', // Hide title bar on macOS
        trafficLightPosition: { x: 15, y: 15 }, // Position macOS window controls
        backgroundColor: '#1e1e1e', // Dark background
        webPreferences: {
            preload: path.join(__dirname, 'preload.cjs'),
            nodeIntegration: false,
            contextIsolation: true,
        },
        title: '',
    });

    // Set Content Security Policy
    // Note: 'unsafe-eval' is required for Vite HMR in development mode
    // This warning will not appear in production builds
    mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
        callback({
            responseHeaders: {
                ...details.responseHeaders,
                'Content-Security-Policy': [
                    isDev
                        ? "default-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:* ws://localhost:*; connect-src 'self' http://localhost:* ws://localhost:*"
                        : "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:"
                ]
            }
        });
    });

    // Load the app
    if (isDev ) {
        // Development mode: load from Vite dev server
        const devServerUrl = 'http://localhost:5173';
        mainWindow.loadURL(devServerUrl);
        mainWindow.webContents.openDevTools();

        // Show error if Vite dev server is not running

        mainWindow.webContents.on('did-fail-load', () => {
            if (!mainWindow) return;
            mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(`
        <html>
          <body style="font-family: sans-serif; padding: 50px; text-align: center;">
            <h1>開發伺服器未啟動</h1>
            <p>請先在終端執行：<code>npm run dev</code></p>
            <p>然後重新啟動此應用程式</p>
          </body>
        </html>
      `)}`);
        });
    } else {
        // Production mode: load from built files
        // __dirname is dist-electron, frontend files are in ../dist
        mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// IPC handlers for window controls
ipcMain.on('window-minimize', () => {
    if (mainWindow) mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow.maximize();
        }
    }
});

ipcMain.on('window-close', () => {
    if (mainWindow) mainWindow.close();
});

// Bank Agent IPC Handlers
ipcMain.handle('bank-agent:get-exchange-rate', async (event, { currency, rateType }) => {
    try {
        return await sendToPython({
            action: 'exchange_rate',
            currency,
            rate_type: rateType
        });
    } catch (error: any) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('bank-agent:calculate-exchange', async (event, { currency, twdAmount, isBuying }) => {
    try {
        return await sendToPython({
            action: 'calculate_exchange',
            currency,
            twd_amount: twdAmount,
            is_buying: isBuying
        });
    } catch (error: any) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('bank-agent:get-multiple-rates', async (event, { currencies }) => {
    try {
        return await sendToPython({
            action: 'get_multiple_rates',
            currencies
        });
    } catch (error: any) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('bank-agent:get-bank-rules', async (event, { currency }) => {
    try {
        return await sendToPython({
            action: 'get_bank_rules',
            currency
        });
    } catch (error: any) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('bank-agent:get-info', async () => {
    try {
        return await sendToPython({
            action: 'bank_agent_info'
        });
    } catch (error: any) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('bank-agent:chat', async (event, { query }) => {
    try {
        return await sendToPython({
            action: 'ai_chat',
            query
        });
    } catch (error: any) {
        return { success: false, error: error.message };
    }
});

app.whenReady().then(() => {
    // Hide application menu
    Menu.setApplicationMenu(null);

    // Start Python backend first
    startPythonBackend();

    // Then create window
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    stopPythonBackend();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    stopPythonBackend();
});
