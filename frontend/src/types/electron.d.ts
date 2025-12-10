export {};

declare global {
    interface Window {
        electron: {
            minimize: () => void;
            maximize: () => void;
            close: () => void;
            platform: string;
        };
        bankAgent: {
            getExchangeRate: (currency: string, rateType?: string) => Promise<ExchangeRateResponse>;
            calculateExchange: (currency: string, twdAmount: number, isBuying?: boolean) => Promise<CalculateExchangeResponse>;
            getMultipleRates: (currencies: string[]) => Promise<MultipleRatesResponse>;
            getBankRules: (currency?: string) => Promise<BankRulesResponse>;
            getAgentInfo: () => Promise<AgentInfoResponse>;
            chat: (query: string) => Promise<AIChatResponse>;
        };
    }
}

export interface ExchangeRateResponse {
    success: boolean;
    currency?: string;
    date?: string;
    cash_buy?: number;
    cash_sell?: number;
    spot_buy?: number;
    spot_sell?: number;
    selected_rate?: number;
    rate_type?: string;
    error?: string;
}

export interface CalculateExchangeResponse {
    success: boolean;
    currency?: string;
    twd_amount?: number;
    foreign_amount?: number;
    rate?: number;
    rate_type?: string;
    action?: string;
    date?: string;
    warning?: string;
    error?: string;
}

export interface MultipleRatesResponse {
    success: boolean;
    rates?: Record<string, ExchangeRateResponse>;
    timestamp?: string;
    error?: string;
}

export interface BankRulesResponse {
    success: boolean;
    currency?: string;
    rules?: {
        max_amount: number;
        name: string;
    };
    all_rules?: Record<string, {
        max_amount: number;
        name: string;
    }>;
    error?: string;
}

export interface AgentInfoResponse {
    success: boolean;
    info?: {
        role: string;
        description: string;
        supported_currencies: string[];
        bank_rules: Record<string, {
            max_amount: number;
            name: string;
        }>;
        services: string[];
    };
    error?: string;
}

export interface AIChatResponse {
    success: boolean;
    type?: string;
    message?: string;
    data?: any;
    error?: string;
}
