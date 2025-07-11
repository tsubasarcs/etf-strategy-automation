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
