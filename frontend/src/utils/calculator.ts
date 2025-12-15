/**
 * Safe math expression evaluator
 * Replaces eval() to comply with CSP (Content Security Policy)
 */

/**
 * Evaluate a mathematical expression safely
 * Supports: +, -, *, / operators
 * @param expression - Math expression string (e.g., "5 + 3 * 2")
 * @returns Calculation result
 */
export function evaluateExpression(expression: string): number {
    // Remove whitespace
    const expr = expression.replace(/\s+/g, '');

    if (!expr) {
        throw new Error('Empty expression');
    }

    // Validate expression (only allow numbers, operators, decimal point)
    if (!/^[\d+\-*/().]+$/.test(expr)) {
        throw new Error('Invalid characters in expression');
    }

    // Parse and evaluate using operator precedence
    return parseExpression(expr);
}

/**
 * Parse expression respecting operator precedence
 * Handles addition and subtraction
 */
function parseExpression(expr: string): number {
    const terms = splitByOperator(expr, /([+-])/);
    let result = parseTerm(terms[0].value);

    for (let i = 1; i < terms.length; i += 2) {
        const operator = terms[i].value;
        const nextTerm = parseTerm(terms[i + 1].value);

        if (operator === '+') {
            result += nextTerm;
        } else if (operator === '-') {
            result -= nextTerm;
        }
    }

    return result;
}

/**
 * Parse term (handles multiplication and division)
 */
function parseTerm(term: string): number {
    const factors = splitByOperator(term, /([*/])/);
    let result = parseFactor(factors[0].value);

    for (let i = 1; i < factors.length; i += 2) {
        const operator = factors[i].value;
        const nextFactor = parseFactor(factors[i + 1].value);

        if (operator === '*') {
            result *= nextFactor;
        } else if (operator === '/') {
            if (nextFactor === 0) {
                throw new Error('Division by zero');
            }
            result /= nextFactor;
        }
    }

    return result;
}

/**
 * Parse factor (number or parenthesized expression)
 */
function parseFactor(factor: string): number {
    // Handle parentheses
    if (factor.startsWith('(') && factor.endsWith(')')) {
        return parseExpression(factor.slice(1, -1));
    }

    // Handle negative numbers
    if (factor.startsWith('-')) {
        return -parseFactor(factor.slice(1));
    }

    // Parse number
    const num = parseFloat(factor);
    if (isNaN(num)) {
        throw new Error(`Invalid number: ${factor}`);
    }

    return num;
}

/**
 * Split string by operators while preserving operator positions
 */
function splitByOperator(str: string, operatorRegex: RegExp): Array<{ value: string; isOperator: boolean }> {
    const result: Array<{ value: string; isOperator: boolean }> = [];
    let current = '';
    let depth = 0; // Parentheses depth

    for (let i = 0; i < str.length; i++) {
        const char = str[i];

        if (char === '(') {
            depth++;
            current += char;
        } else if (char === ')') {
            depth--;
            current += char;
        } else if (depth === 0 && operatorRegex.test(char)) {
            // Found operator at top level
            if (current) {
                result.push({ value: current, isOperator: false });
                current = '';
            }
            result.push({ value: char, isOperator: true });
        } else {
            current += char;
        }
    }

    if (current) {
        result.push({ value: current, isOperator: false });
    }

    return result;
}
