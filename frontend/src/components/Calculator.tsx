import { useState, useEffect} from 'react';
import { Send, X, DollarSign } from 'lucide-react';
import * as React from "react";
import type { ExchangeRateResponse, CalculateExchangeResponse } from '../types/electron';
import { evaluateExpression } from '../utils/calculator';

export default function Calculator() {
    const [display, setDisplay] = useState('0');
    const [equation, setEquation] = useState('');
    const [isAIMode, setIsAIMode] = useState(false);
    const [showAIProcess, setShowAIProcess] = useState(false);
    const [chatMessages, setChatMessages] = useState([
        {
            type: 'system',
            content: 'AI 銀行員助手已啟動！你可以查詢匯率和計算換匯金額',
            timestamp: new Date()
        }
    ]);
    const [inputMessage, setInputMessage] = useState('');
    const [selectedCurrency, setSelectedCurrency] = useState('USD');
    const [exchangeAmount, setExchangeAmount] = useState('1000');
    const [_exchangeResult, setExchangeResult] = useState<CalculateExchangeResponse | null>(null);
    const [currentRates, setCurrentRates] = useState<ExchangeRateResponse | null>(null);
    const [showQuickTools, setShowQuickTools] = useState(false);

    // 支援的貨幣列表
    const currencies = [
        { code: 'USD', name: '美金', symbol: '$' },
        { code: 'EUR', name: '歐元', symbol: '€' },
        { code: 'JPY', name: '日圓', symbol: '¥' },
        { code: 'CNY', name: '人民幣', symbol: '¥' },
        { code: 'GBP', name: '英鎊', symbol: '£' },
        { code: 'AUD', name: '澳洲', symbol: 'A$' },
        { code: 'HKD', name: '港幣', symbol: 'HK$' },
        { code: 'SGD', name: '新加坡', symbol: 'S$' },
    ];

    // 自動查詢匯率
    useEffect(() => {
        if (isAIMode && window.bankAgent) {
            void fetchExchangeRate(selectedCurrency);
        }
    }, [isAIMode, selectedCurrency]);

    const fetchExchangeRate = async (currency: string) => {
        try {
            const result = await window.bankAgent.getExchangeRate(currency, 'cash_sell');
            if (result.success) {
                setCurrentRates(result);
                addSystemMessage(`✅ 已取得 ${currency} 最新匯率！`);
            } else {
                addSystemMessage(`❌ 無法取得 ${currency} 匯率：${result.error}`);
            }
        } catch (error: any) {
            addSystemMessage(`❌ 查詢失敗：${error.message}`);
        }
    };

    const calculateExchange = async () => {
        if (!exchangeAmount || isNaN(Number(exchangeAmount))) {
            addSystemMessage('❌ 請輸入有效的金額');
            return;
        }

        try {
            const result = await window.bankAgent.calculateExchange(
                selectedCurrency,
                Number(exchangeAmount),
                true
            );

            if (result.success) {
                setExchangeResult(result);
                addAIMessage(
                    `💰 換匯計算結果\n\n` +
                    `貨幣：${result.currency}\n` +
                    `台幣金額：NT$ ${result.twd_amount?.toLocaleString()}\n` +
                    `可換得：${result.foreign_amount} ${result.currency}\n` +
                    `匯率：${result.rate}\n` +
                    `日期：${result.date}\n` +
                    (result.warning ? `\n⚠️ ${result.warning}` : '')
                );
            } else {
                addSystemMessage(`❌ 計算失敗：${result.error}`);
            }
        } catch (error: any) {
            addSystemMessage(`❌ 計算失敗：${error.message}`);
        }
    };

    const addSystemMessage = (content: string) => {
        setChatMessages(prev => [...prev, {
            type: 'system',
            content,
            timestamp: new Date()
        }]);
    };

    const addAIMessage = (content: string) => {
        setChatMessages(prev => [...prev, {
            type: 'ai',
            content,
            timestamp: new Date()
        }]);
    };

    const handleSendMessage = async () => {
        if (inputMessage.trim() === '') return;

        // Add user message
        const userMessage = {
            type: 'user',
            content: inputMessage,
            timestamp: new Date()
        };
        setChatMessages(prev => [...prev, userMessage]);
        setInputMessage('');

        // Show thinking message
        const thinkingMessage = {
            type: 'ai-thinking',
            content: '🤔 正在分析您的問題...',
            timestamp: new Date()
        };
        setChatMessages(prev => [...prev, thinkingMessage]);

        try {
            // Call AI chat API
            const response = await window.bankAgent.chat(inputMessage);

            // Remove thinking message and add AI response
            setChatMessages(prev => {
                const filtered = prev.filter(msg => msg.type !== 'ai-thinking');
                return [...filtered, {
                    type: 'ai',
                    content: response.message || '抱歉，我無法處理您的問題。',
                    timestamp: new Date()
                }];
            });
        } catch (error: any) {
            // Remove thinking message and show error
            setChatMessages(prev => {
                const filtered = prev.filter(msg => msg.type !== 'ai-thinking');
                return [...filtered, {
                    type: 'system',
                    content: `❌ 發生錯誤：${error.message}`,
                    timestamp: new Date()
                }];
            });
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            void handleSendMessage();
        }
    };

    const handleNumberClick = (num:string) => {
        if (display === '0') {
            setDisplay(num);
        } else {
            setDisplay(display + num);
        }
    };

    const handleOperatorClick = (operator:string) => {
        if (equation !== '') {
            // 已經有等式存在，追加當前數字和新運算符
            setEquation(equation + display + ' ' + operator + ' ');
        } else {
            // 新等式
            setEquation(display + ' ' + operator + ' ');
        }
        setDisplay('0');
    };

    const handleEquals = () => {
        try {
            // 如果 display 是 '0' 且 equation 不為空，表示用戶在運算符後直接按等號
            // 移除最後的運算符再計算
            let finalEquation = equation + display;
            if (display === '0' && equation !== '') {
                // 移除末尾的運算符和空格（例如 "6 * 6 * " → "6 * 6"）
                finalEquation = equation.trim().replace(/[+\-*/÷×]\s*$/, '').trim();
            }

            // 如果等式為空，不計算
            if (finalEquation === '' || finalEquation === display) {
                return;
            }

            // Use safe evaluator instead of eval()
            const result = evaluateExpression(finalEquation);
            setDisplay(String(result));
            setEquation('');
        } catch (error) {
            setDisplay('Error');
            setEquation('');
        }
    };

    const handleClear = () => {
        setDisplay('0');
        setEquation('');
    };

    const handleDecimal = () => {
        if (!display.includes('.')) {
            setDisplay(display + '.');
        }
    };


    const buttons = [
        { label: 'C', action: handleClear, className: 'bg-red-500 hover:bg-red-600 text-white col-span-2' },
        { label: '⌫', action: () => setDisplay(display.slice(0, -1) || '0'), className: 'bg-gray-400 hover:bg-gray-500 text-white' },
        { label: '÷', action: () => handleOperatorClick('/'), className: 'bg-blue-500 hover:bg-blue-600 text-white' },

        { label: '7', action: () => handleNumberClick('7'), className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '8', action: () => handleNumberClick('8'), className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '9', action: () => handleNumberClick('9'), className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '×', action: () => handleOperatorClick('*'), className: 'bg-blue-500 hover:bg-blue-600 text-white' },

        { label: '4', action: () => handleNumberClick('4'), className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '5', action: () => handleNumberClick('5'), className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '6', action: () => handleNumberClick('6'), className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '-', action: () => handleOperatorClick('-'), className: 'bg-blue-500 hover:bg-blue-600 text-white' },

        { label: '1', action: () => handleNumberClick('1'), className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '2', action: () => handleNumberClick('2'), className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '3', action: () => handleNumberClick('3'), className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '+', action: () => handleOperatorClick('+'), className: 'text-white bg-blue-500 hover:bg-blue-600 text-white' },

        { label: '0', action: () => handleNumberClick('0'), className: 'text-white bg-gray-700 hover:bg-gray-600 col-span-2' },
        { label: '.', action: handleDecimal, className: 'text-white bg-gray-700 hover:bg-gray-600' },
        { label: '=', action: handleEquals, className: 'bg-green-500 hover:bg-green-600 text-white' },
    ];

    return (
        <div className="flex items-center justify-center min-h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
            <div className={`flex gap-4 max-w-6xl w-full transition-all duration-700 ease-in-out ${
                showAIProcess ? 'justify-start' : 'justify-center'
            }`}>
                {/* Calculator Section */}
                <div className={`transition-all duration-700 ease-in-out ${showAIProcess ? 'w-1/2' : 'w-full max-w-md'}`}>
                    <div className="bg-gray-800 rounded-3xl shadow-2xl p-6 border border-gray-700">
                        {/* Display */}
                        <div className="mb-6">
                            <div className="text-gray-400 text-sm h-6 mb-2 text-right">
                                {equation}
                            </div>
                            <div className="bg-gray-900 rounded-2xl p-6 text-right border border-gray-700">
                                <div className="text-white text-5xl font-light tracking-tight break-all">
                                    {display}
                                </div>
                            </div>
                        </div>

                        {/* Bank Agent Mode Button */}
                        <button
                            onClick={() => {
                                setIsAIMode(!isAIMode);
                                setShowAIProcess(!showAIProcess);
                            }}
                            className={`w-full mb-4 py-4 rounded-xl font-semibold text-lg transition-all duration-300 flex items-center justify-center gap-2 ${
                                isAIMode
                                    ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg shadow-green-500/50 scale-105'
                                    : 'bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600 hover:shadow-lg hover:shadow-green-500/50'
                            }`}
                        >
                            <DollarSign className="w-6 h-6" />
                            <span>{isAIMode ? '銀行員匯率模式' : '銀行員匯率模式'}</span>
                        </button>

                        {/* Calculator Buttons */}
                        <div className="grid grid-cols-4 gap-3">
                            {buttons.map((button, index) => (
                                <button
                                    key={index}
                                    onClick={button.action}
                                    className={`${button.className} py-5 rounded-xl text-xl font-semibold transition-all duration-200 active:scale-95 shadow-lg`}
                                >
                                    {button.label}
                                </button>
                            ))}
                        </div>

                        {/* Additional Info */}
                        <div className="mt-6 text-center text-gray-500 text-xs">
                            <p>銀行員助手提供即時匯率查詢與換匯計算</p>
                        </div>
                    </div>
                </div>

                {/* AI Process Chat Panel */}
                <div className={`transition-all duration-700 ease-in-out overflow-hidden ${
                    showAIProcess ? 'w-1/2 opacity-100' : 'w-0 opacity-0 pointer-events-none'
                }`}>
                    <div className={`bg-gray-800 rounded-3xl shadow-2xl border border-gray-700 flex flex-col min-w-[400px] transition-transform duration-700 ease-out ${
                        showAIProcess ? 'translate-x-0' : 'translate-x-full'
                    }`} style={{ height: 'calc(100vh - 32px)', maxHeight: '700px' }}>
                            {/* Header */}
                            <div className="p-6 border-b border-gray-700 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center">
                                        <DollarSign className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-white font-semibold text-lg">銀行員匯率查詢</h3>
                                        <p className="text-gray-400 text-sm">台灣銀行即時匯率</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => {
                                        setShowAIProcess(false);
                                        setIsAIMode(false);
                                    }}
                                    className="text-gray-400 hover:text-white transition-colors"
                                >
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            {/* Exchange Rate Tool */}
                            <div className="border-b border-gray-700">
                                <button
                                    onClick={() => setShowQuickTools(!showQuickTools)}
                                    className="w-full p-4 flex items-center justify-between hover:bg-gray-750 transition-colors"
                                >
                                    <h4 className="text-white font-semibold">🚀 快速查詢工具</h4>
                                    <span className="text-gray-400">
                                        {showQuickTools ? '▲' : '▼'}
                                    </span>
                                </button>

                                <div className={`overflow-hidden transition-all duration-300 ${showQuickTools ? 'max-h-96' : 'max-h-0'}`}>
                                    <div className="p-6 pt-0">
                                        {/* Currency Selection */}
                                        <div className="mb-4">
                                            <label className="text-gray-400 text-sm mb-2 block">選擇貨幣</label>
                                            <select
                                                value={selectedCurrency}
                                                onChange={(e) => setSelectedCurrency(e.target.value)}
                                                className="w-full bg-gray-900 text-white rounded-lg px-4 py-2 border border-gray-700 focus:outline-none focus:border-green-500"
                                            >
                                                {currencies.map((curr) => (
                                                    <option key={curr.code} value={curr.code}>
                                                        {curr.symbol} {curr.name} ({curr.code})
                                                    </option>
                                                ))}
                                            </select>
                                        </div>

                                        {/* Current Rate Display */}
                                        {currentRates && currentRates.success && (
                                            <div className="mb-4 p-3 bg-gray-900 rounded-lg border border-gray-700">
                                                <div className="text-gray-400 text-xs mb-1">目前匯率 ({currentRates.date})</div>
                                                <div className="grid grid-cols-2 gap-2 text-sm">
                                                    <div>
                                                        <span className="text-gray-500">銀行買入：</span>
                                                        <span className="text-green-400 font-semibold ml-1">{currentRates.cash_buy}</span>
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-500">銀行賣出：</span>
                                                        <span className="text-red-400 font-semibold ml-1">{currentRates.cash_sell}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* Amount Input */}
                                        <div className="mb-4">
                                            <label className="text-gray-400 text-sm mb-2 block">台幣金額 (NT$)</label>
                                            <input
                                                type="number"
                                                value={exchangeAmount}
                                                onChange={(e) => setExchangeAmount(e.target.value)}
                                                placeholder="輸入台幣金額"
                                                className="w-full bg-gray-900 text-white rounded-lg px-4 py-2 border border-gray-700 focus:outline-none focus:border-green-500"
                                            />
                                        </div>

                                        {/* Calculate Button */}
                                        <button
                                            onClick={calculateExchange}
                                            className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white py-2 rounded-lg transition-all duration-200 active:scale-95 font-semibold"
                                        >
                                            計算換匯金額
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Chat Messages */}
                            <div className="flex-1 overflow-y-auto p-6 space-y-2">
                                {chatMessages.map((message, index) => (
                                    <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[80%] rounded-2xl p-4 ${
                                            message.type === 'user'
                                                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                                                : message.type === 'system'
                                                    ? 'bg-gray-700 text-gray-300 border border-gray-600'
                                                    : message.type === 'ai-thinking'
                                                        ? 'bg-gradient-to-r from-blue-900/50 to-cyan-900/50 text-cyan-300 border border-cyan-500/50 animate-pulse'
                                                        : 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white'
                                        }`}>
                                            <p className="text-sm whitespace-pre-line">{message.content}</p>
                                            <p className="text-xs opacity-70 mt-2">
                                                {message.timestamp.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Chat Input */}
                            <div className="p-6 border-t border-gray-700">
                                <div className="flex gap-3">
                                    <input
                                        type="text"
                                        value={inputMessage}
                                        onChange={(e) => setInputMessage(e.target.value)}
                                        onKeyDown={handleKeyPress}
                                        placeholder="試試看：「10000台幣換日圓」、「美金匯率如何？」"
                                        className="flex-1 bg-gray-900 text-white rounded-xl px-4 py-3 border border-gray-700 focus:outline-none focus:border-green-500 transition-colors placeholder-gray-500"
                                    />
                                    <button
                                        onClick={handleSendMessage}
                                        className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white px-6 py-3 rounded-xl transition-all duration-200 active:scale-95 flex items-center justify-center"
                                    >
                                        <Send className="w-5 h-5" />
                                    </button>
                                </div>
                                <p className="text-gray-500 text-xs mt-2 text-center">
                                    💡 匯率資料來自台灣銀行 FinMind API
                                </p>
                            </div>
                        </div>
                </div>
            </div>
        </div>
    );
}
