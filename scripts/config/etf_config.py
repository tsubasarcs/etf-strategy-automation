"""
ETF基本配置 - 整合新的分層配置系統

此檔案整合了：
1. 原有的ETF基本資訊
2. 新的動態除息配置系統
3. 向後相容的API介面

更新日期：2025-07-22
版本：v2.0 (整合分層配置)
"""

from typing import Dict, List, Optional
import os
import sys

# ETF基本資訊（保持不變）
ETF_INFO = {
    '0056': {
        'name': '元大高股息ETF',
        'expected_return': 9.43,
        'priority': 1,
        'beta': 0.85,
        'sector': 'high_dividend',
        'success_rate': 0.625,  # 5%目標達成率
        'avg_return_period': '1-7天',
        'risk_level': 'medium'
    },
    '00878': {
        'name': '國泰永續高股息ETF',
        'expected_return': 5.56,
        'priority': 3,
        'beta': 0.75,
        'sector': 'esg_dividend',
        'success_rate': 0.526,
        'avg_return_period': '1-60天',
        'risk_level': 'low'
    },
    '00919': {
        'name': '群益台灣精選高息ETF',
        'expected_return': 6.26,
        'priority': 2,
        'beta': 0.80,
        'sector': 'selected_dividend',
        'success_rate': 0.50,
        'avg_return_period': '1-60天',
        'risk_level': 'medium'
    }
}

# ETF清單
ETF_LIST = list(ETF_INFO.keys())

# 新增配置系統狀態
CONFIG_SYSTEM = {
    'version': '2.0',
    'type': 'dynamic_layered_config',
    'features': [
        'static_base_predictions',
        'dynamic_updates', 
        'api_integration',
        'manual_override',
        'firebase_backup'
    ],
    'update_date': '2025-07-22'
}

def get_dividend_schedule() -> Dict[str, List[str]]:
    """
    獲取當前除息日程表（新版API）
    
    這個函數會：
    1. 載入基礎配置（歷史規律預測）
    2. 應用動態更新（API確認或手動更新）
    3. 返回合併後的最終日程表
    
    Returns:
        Dict[str, List[str]]: {ETF代碼: [除息日期列表]}
    """
    try:
        # 嘗試使用新的配置管理器
        current_dir = os.path.dirname(os.path.abspath(__file__))
        core_dir = os.path.join(os.path.dirname(current_dir), "core")
        
        if core_dir not in sys.path:
            sys.path.insert(0, core_dir)
        
        from config_manager import get_dividend_schedule as get_schedule
        return get_schedule()
        
    except ImportError:
        print("⚠️ 新配置系統不可用，使用緊急備用配置")
        return get_legacy_dividend_calendar()
    except Exception as e:
        print(f"❌ 配置系統錯誤: {e}")
        return get_legacy_dividend_calendar()

def update_dividend_dates(etf_code: str, dates: List[str], source: str = "manual") -> bool:
    """
    更新ETF除息日期（新版API）
    
    Args:
        etf_code: ETF代碼
        dates: 新的除息日期列表
        source: 更新來源 ('manual', 'api_verified', 'official_announcement')
    
    Returns:
        bool: 更新是否成功
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        core_dir = os.path.join(os.path.dirname(current_dir), "core")
        
        if core_dir not in sys.path:
            sys.path.insert(0, core_dir)
        
        from config_manager import update_dividend_dates as update_dates
        return update_dates(etf_code, dates, source)
        
    except ImportError:
        print("⚠️ 新配置系統不可用，無法更新")
        return False
    except Exception as e:
        print(f"❌ 更新失敗: {e}")
        return False

def get_legacy_dividend_calendar() -> Dict[str, List[str]]:
    """
    備用的除息日程表（緊急使用）
    基於策略報告的歷史分析生成
    """
    from datetime import date
    
    today = date.today()
    current_year = today.year
    
    # 基於歷史規律的緊急備用日程
    legacy_calendar = {
        "0056": [
            f"{current_year}-10-15",
            f"{current_year+1}-01-15", 
            f"{current_year+1}-04-15",
            f"{current_year+1}-07-15"
        ],
        "00878": [
            f"{current_year}-11-21",
            f"{current_year+1}-02-20",
            f"{current_year+1}-05-19", 
            f"{current_year+1}-08-16"
        ],
        "00919": [
            f"{current_year}-12-16",
            f"{current_year+1}-03-17",
            f"{current_year+1}-06-17",
            f"{current_year+1}-09-16"
        ]
    }
    
    return legacy_calendar

# 保持向後相容性 - 舊版API
DIVIDEND_CALENDAR = None  # 標記為棄用，由動態系統取代

def get_dividend_calendar() -> Dict[str, List[str]]:
    """向後相容的API - 獲取除息日程表"""
    return get_dividend_schedule()

# 配置資訊函數
def get_config_status():
    """顯示當前配置系統狀態"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        core_dir = os.path.join(os.path.dirname(current_dir), "core")
        
        if core_dir not in sys.path:
            sys.path.insert(0, core_dir)
        
        from config_manager import get_config_info
        get_config_info()
        
    except Exception as e:
        print(f"❌ 無法顯示配置狀態: {e}")
        print("\n📊 ETF基本資訊:")
        for etf_code, info in ETF_INFO.items():
            print(f"  {etf_code}: {info['name']}")
            print(f"    優先級: {info['priority']} | 預期報酬: {info['expected_return']}%")

def validate_etf_code(etf_code: str) -> bool:
    """驗證ETF代碼是否支援"""
    return etf_code in ETF_LIST

def get_etf_info(etf_code: str) -> Optional[Dict]:
    """獲取特定ETF的基本資訊"""
    return ETF_INFO.get(etf_code)

def get_supported_etfs() -> List[str]:
    """獲取所有支援的ETF清單"""
    return ETF_LIST.copy()

# 系統資訊
def print_system_info():
    """顯示系統資訊"""
    print("\n" + "="*60)
    print("📊 ETF配置系統資訊")
    print("="*60)
    print(f"🔧 系統版本: {CONFIG_SYSTEM['version']}")
    print(f"📅 更新日期: {CONFIG_SYSTEM['update_date']}")
    print(f"🎯 配置類型: {CONFIG_SYSTEM['type']}")
    print(f"📋 支援ETF: {len(ETF_LIST)} 個")
    print(f"✨ 系統特色:")
    for feature in CONFIG_SYSTEM['features']:
        print(f"   • {feature}")
    
    print(f"\n📈 ETF清單:")
    for etf_code in ETF_LIST:
        info = ETF_INFO[etf_code]
        print(f"   {etf_code}: {info['name']} (優先級: {info['priority']})")
    
    print("="*60)

# 測試和除錯功能
if __name__ == "__main__":
    print("🧪 ETF配置測試")
    print("="*50)
    
    try:
        # 顯示系統資訊
        print_system_info()
        
        # 測試基本功能
        print(f"\n🔄 測試基本功能...")
        print(f"支援的ETF: {get_supported_etfs()}")
        
        # 測試除息日程載入
        print(f"\n📅 測試除息日程載入...")
        schedule = get_dividend_schedule()
        
        if schedule:
            print("✅ 除息日程載入成功！")
            total_dates = sum(len(dates) for dates in schedule.values())
            print(f"📊 總計 {len(schedule)} 個ETF，{total_dates} 個日期")
            
            for etf_code, dates in schedule.items():
                next_dates = dates[:2]  # 顯示前2個日期
                print(f"   {etf_code}: {next_dates}")
        else:
            print("❌ 除息日程載入失敗")
        
        # 測試配置狀態
        print(f"\n🔍 配置系統狀態...")
        get_config_status()
        
    except Exception as e:
        print(f"💥 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50)
    print("🧪 測試完成")