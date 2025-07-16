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
