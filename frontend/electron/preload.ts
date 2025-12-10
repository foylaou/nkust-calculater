import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
    minimize: () => ipcRenderer.send('window-minimize'),
    maximize: () => ipcRenderer.send('window-maximize'),
    close: () => ipcRenderer.send('window-close'),
    platform: process.platform,
});

// Expose Bank Agent API for Exchange Rate queries
contextBridge.exposeInMainWorld('bankAgent', {
    // Get exchange rate for a specific currency
    getExchangeRate: (currency: string, rateType: string = 'cash_sell') =>
        ipcRenderer.invoke('bank-agent:get-exchange-rate', { currency, rateType }),

    // Calculate exchange amount
    calculateExchange: (currency: string, twdAmount: number, isBuying: boolean = true) =>
        ipcRenderer.invoke('bank-agent:calculate-exchange', { currency, twdAmount, isBuying }),

    // Get multiple currencies rates
    getMultipleRates: (currencies: string[]) =>
        ipcRenderer.invoke('bank-agent:get-multiple-rates', { currencies }),

    // Get bank rules
    getBankRules: (currency?: string) =>
        ipcRenderer.invoke('bank-agent:get-bank-rules', { currency }),

    // Get bank agent info
    getAgentInfo: () =>
        ipcRenderer.invoke('bank-agent:get-info'),

    // AI Chat - Natural language query
    chat: (query: string) =>
        ipcRenderer.invoke('bank-agent:chat', { query }),
});
