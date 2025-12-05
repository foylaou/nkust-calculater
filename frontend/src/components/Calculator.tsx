import { useState} from 'react';
import { Sparkles, Send, X, MessageSquare } from 'lucide-react';
import * as React from "react";

export default function Calculator() {
    const [display, setDisplay] = useState('0');
    const [equation, setEquation] = useState('');
    const [isAIMode, setIsAIMode] = useState(false);
    const [showAIProcess, setShowAIProcess] = useState(false);
    const [chatMessages, setChatMessages] = useState([
        {
            type: 'system',
            content: 'AI 助手已啟動，你可以用自然語言詢問計算問題！',
            timestamp: new Date()
        }
    ]);
    const [inputMessage, setInputMessage] = useState('');

    const handleNumberClick = (num:string) => {
        if (display === '0') {
            setDisplay(num);
        } else {
            setDisplay(display + num);
        }
    };

    const handleOperatorClick = (operator:string) => {
        setEquation(display + ' ' + operator + ' ');
        setDisplay('0');
    };

    const handleEquals = () => {
        try {
            const result = eval(equation + display);
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

    const handleSendMessage = () => {
        if (inputMessage.trim() === '') return;

        // Add user message
        const userMessage = {
            type: 'user',
            content: inputMessage,
            timestamp: new Date()
        };
        setChatMessages([...chatMessages, userMessage]);

        // Simulate AI thinking process
        setTimeout(() => {
            const thinkingMessage = {
                type: 'ai-thinking',
                content: '🤔 正在分析你的問題...\n📊 識別數字和運算符...\n🧮 執行計算...',
                timestamp: new Date()
            };
            setChatMessages(prev => [...prev, thinkingMessage]);

            // Simulate AI response
            setTimeout(() => {
                const aiResponse = {
                    type: 'ai',
                    content: `根據你的問題「${inputMessage}」，我理解你想要計算的結果是：\n\n結果: ${Math.floor(Math.random() * 1000)}\n\n計算步驟：\n1. 解析自然語言輸入\n2. 識別運算類型\n3. 執行計算\n4. 返回結果`,
                    timestamp: new Date()
                };
                setChatMessages(prev => [...prev.slice(0, -1), aiResponse]);
            }, 1500);
        }, 500);

        setInputMessage('');
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const buttons = [
        { label: 'C', action: handleClear, className: 'bg-red-500 hover:bg-red-600 text-white col-span-2' },
        { label: '⌫', action: () => setDisplay(display.slice(0, -1) || '0'), className: 'bg-gray-400 hover:bg-gray-500 text-white' },
        { label: '÷', action: () => handleOperatorClick('/'), className: 'bg-blue-500 hover:bg-blue-600 text-white' },

        { label: '7', action: () => handleNumberClick('7'), className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '8', action: () => handleNumberClick('8'), className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '9', action: () => handleNumberClick('9'), className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '×', action: () => handleOperatorClick('*'), className: 'bg-blue-500 hover:bg-blue-600 text-white' },

        { label: '4', action: () => handleNumberClick('4'), className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '5', action: () => handleNumberClick('5'), className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '6', action: () => handleNumberClick('6'), className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '-', action: () => handleOperatorClick('-'), className: 'bg-blue-500 hover:bg-blue-600 text-white' },

        { label: '1', action: () => handleNumberClick('1'), className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '2', action: () => handleNumberClick('2'), className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '3', action: () => handleNumberClick('3'), className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '+', action: () => handleOperatorClick('+'), className: 'bg-blue-500 hover:bg-blue-600 text-white' },

        { label: '0', action: () => handleNumberClick('0'), className: 'bg-gray-700 hover:bg-gray-600 col-span-2' },
        { label: '.', action: handleDecimal, className: 'bg-gray-700 hover:bg-gray-600' },
        { label: '=', action: handleEquals, className: 'bg-green-500 hover:bg-green-600 text-white' },
    ];

    return (
        <div className="flex items-center justify-center min-h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
            <div className="flex gap-0 max-w-6xl w-full">
                {/* Calculator Section */}
                <div className={`transition-all duration-500 ${showAIProcess ? 'w-1/2' : 'w-full max-w-md mx-auto'}`}>
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

                        {/* AI Calculator Mode Button */}
                        <button
                            onClick={() => {
                                setIsAIMode(!isAIMode);
                                setShowAIProcess(!showAIProcess);
                            }}
                            className={`w-full mb-4 py-4 rounded-xl font-semibold text-lg transition-all duration-300 flex items-center justify-center gap-2 ${
                                isAIMode
                                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/50 scale-105'
                                    : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 hover:shadow-lg hover:shadow-purple-500/50'
                            }`}
                        >
                            <Sparkles className="w-6 h-6" />
                            <span>{isAIMode ? 'AI Calculator Mode' : 'AI 計算功能'}</span>
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
                            <p>AI 助手可以理解自然語言計算需求</p>
                        </div>
                    </div>
                </div>

                {/* AI Process Chat Panel */}
                <div className={`transition-all duration-500 overflow-hidden ${
                    showAIProcess ? 'w-1/2 ml-4 opacity-100' : 'w-0 opacity-0'
                }`}>
                    {showAIProcess && (
                        <div className="bg-gray-800 rounded-3xl shadow-2xl border border-gray-700 h-full flex flex-col">
                            {/* Chat Header */}
                            <div className="p-6 border-b border-gray-700 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
                                        <MessageSquare className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-white font-semibold text-lg">AI 計算過程</h3>
                                        <p className="text-gray-400 text-sm">查看 AI 的思考邏輯</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setShowAIProcess(false)}
                                    className="text-gray-400 hover:text-white transition-colors"
                                >
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            {/* Chat Messages */}
                            <div className="flex-1 overflow-y-auto p-6 space-y-4">
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
                                        placeholder="輸入你的計算問題..."
                                        className="flex-1 bg-gray-900 text-white rounded-xl px-4 py-3 border border-gray-700 focus:outline-none focus:border-blue-500 transition-colors"
                                    />
                                    <button
                                        onClick={handleSendMessage}
                                        className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white px-6 py-3 rounded-xl transition-all duration-200 active:scale-95 flex items-center justify-center"
                                    >
                                        <Send className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
