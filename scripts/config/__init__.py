"""配置模組初始化 - v2.0 完整整合新配置系統"""

# 從ETF配置導入基本資訊和新函數
from .etf_config import (
    ETF_INFO, 
    ETF_LIST,
    get_dividend_schedule,
    update_dividend_dates,
    get_config_status,
    validate_etf_code,
    get_etf_info,
    get_supported_etfs
)

# 從策略配置導入參數
from .strategy_config import (
    BASIC_STRATEGY, 
    TECHNICAL_PARAMS, 
    RISK_WEIGHTS, 
    RISK_LEVELS, 
    POSITION_SIZING
)

# 向後相容性 - 提供舊版API的替代
def get_dividend_calendar():
    """向後相容：獲取除息日程表（舊版API名稱）"""
    return get_dividend_schedule()

# 如果有舊代碼還在使用DIVIDEND_CALENDAR，提供一個動態載入的版本
class DynamicDividendCalendar:
    """動態除息日程表 - 向後相容舊版代碼"""
    
    def __init__(self):
        self._schedule = None
    
    def __getitem__(self, key):
        if self._schedule is None:
            self._schedule = get_dividend_schedule()
        return self._schedule[key]
    
    def __iter__(self):
        if self._schedule is None:
            self._schedule = get_dividend_schedule()
        return iter(self._schedule)
    
    def items(self):
        if self._schedule is None:
            self._schedule = get_dividend_schedule()
        return self._schedule.items()
    
    def keys(self):
        if self._schedule is None:
            self._schedule = get_dividend_schedule()
        return self._schedule.keys()
    
    def values(self):
        if self._schedule is None:
            self._schedule = get_dividend_schedule()
        return self._schedule.values()
    
    def get(self, key, default=None):
        if self._schedule is None:
            self._schedule = get_dividend_schedule()
        return self._schedule.get(key, default)

# 向後相容：創建動態DIVIDEND_CALENDAR
DIVIDEND_CALENDAR = DynamicDividendCalendar()

__all__ = [
    # 基本資訊
    'ETF_INFO',
    'ETF_LIST',
    
    # 除息相關（新系統）
    'get_dividend_schedule',
    'update_dividend_dates',
    'get_config_status',
    
    # 向後相容
    'DIVIDEND_CALENDAR',
    'get_dividend_calendar',
    
    # ETF資訊查詢
    'validate_etf_code',
    'get_etf_info', 
    'get_supported_etfs',
    
    # 策略參數
    'BASIC_STRATEGY',
    'TECHNICAL_PARAMS',
    'RISK_WEIGHTS',
    'RISK_LEVELS',
    'POSITION_SIZING'
]

# 版本資訊
__version__ = "2.0"
__description__ = "ETF策略配置系統 - 完整整合分層配置，包含向後相容性"

# 系統初始化提示
def _print_config_info():
    """顯示配置系統資訊"""
    print(f"📊 ETF配置系統 v{__version__} 已載入")
    try:
        schedule = get_dividend_schedule()
        print(f"   支援ETF: {len(ETF_LIST)} 個")
        print(f"   除息日期: {sum(len(dates) for dates in schedule.values())} 個")
    except Exception:
        print("   ⚠️ 除息日程載入中...")

# 可選：在導入時顯示資訊（除錯時有用）
# _print_config_info()