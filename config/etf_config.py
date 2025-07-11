# config/etf_config.py
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

# config/strategy_config.py
"""策略參數配置"""

# 基礎策略參數
BASIC_STRATEGY = {
    'buy_window_days': 7,           # 除息後買進窗口
    'target_return_pct': 5.0,       # 目標報酬率
    'max_hold_days': 60,            # 最大持有天數
    'stop_loss_pct': -3.0           # 停損點
}

# 技術分析參數
TECHNICAL_PARAMS = {
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'ma_short': 5,
    'ma_medium': 10,
    'ma_long': 20,
    'bb_period': 20,
    'bb_std_dev': 2
}

# 風險評估權重
RISK_WEIGHTS = {
    'technical_risk': 0.25,
    'market_risk': 0.25,
    'timing_risk': 0.25,
    'volatility_risk': 0.25
}

# 風險等級定義
RISK_LEVELS = {
    'very_low': (0, 20),
    'low': (20, 40),
    'medium': (40, 60),
    'high': (60, 80),
    'very_high': (80, 100)
}

# 投資配置比例
POSITION_SIZING = {
    'very_low_risk': 0.25,
    'low_risk': 0.20,
    'medium_risk': 0.15,
    'high_risk': 0.10,
    'very_high_risk': 0.05,
    'max_single_position': 0.30
}

# config/__init__.py
"""配置模組初始化"""

from .etf_config import ETF_INFO, DIVIDEND_CALENDAR, ETF_LIST
from .strategy_config import (
    BASIC_STRATEGY, 
    TECHNICAL_PARAMS, 
    RISK_WEIGHTS, 
    RISK_LEVELS, 
    POSITION_SIZING
)

__all__ = [
    'ETF_INFO',
    'DIVIDEND_CALENDAR', 
    'ETF_LIST',
    'BASIC_STRATEGY',
    'TECHNICAL_PARAMS',
    'RISK_WEIGHTS',
    'RISK_LEVELS',
    'POSITION_SIZING'
]
