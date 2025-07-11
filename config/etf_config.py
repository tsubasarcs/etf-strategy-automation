"""ETF基本配置"""

ETF_INFO = {
    '0056': {
        'name': '元大高股息ETF',
        'expected_return': 9.43,
        'priority': 1,
        'beta': 0.85,
        'sector': 'high_dividend'
    },
    '00878': {
        'name': '國泰永續高股息ETF',
        'expected_return': 5.56,
        'priority': 3,
        'beta': 0.75,
        'sector': 'esg_dividend'
    },
    '00919': {
        'name': '群益台灣精選高息ETF',
        'expected_return': 6.26,
        'priority': 2,
        'beta': 0.80,
        'sector': 'selected_dividend'
    }
}

DIVIDEND_CALENDAR = {
    "0056": ["2025-07-15", "2025-10-15", "2026-01-15", "2026-04-15"],
    "00878": ["2025-08-16", "2025-11-21", "2026-02-20", "2026-05-19"], 
    "00919": ["2025-09-16", "2025-12-16", "2026-03-17", "2026-06-17"]
}

ETF_LIST = list(ETF_INFO.keys())
