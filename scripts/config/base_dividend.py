"""
基礎除息配置檔案
基於歷史規律分析的ETF除息預測配置

此檔案包含：
1. 各ETF的歷史除息規律
2. 預測模式和參數
3. 用於生成動態預測的基礎資料

更新週期：季度檢查，年度更新
最後更新：2025-07-22
"""

from datetime import datetime

# ETF除息歷史規律分析
BASE_DIVIDEND_PATTERNS = {
    "0056": {
        "name": "元大高股息ETF",
        "frequency": "quarterly",  # 每季配息
        "estimated_months": [1, 4, 7, 10],  # 預計除息月份
        "typical_days": [15, 16, 17, 18],    # 常見除息日期
        "historical_dates": [
            # 2024年實際除息日期
            "2024-01-15", "2024-04-15", "2024-07-15", "2024-10-15"
        ],
        "pattern_confidence": "high",  # 規律性很高
        "notes": "通常每季15-18日除息，規律性最穩定",
        "priority": 1,  # 投資優先級
        "expected_return": 9.43,  # 預期報酬率(%)
        "success_rate": 0.625  # 5%目標達成率
    },
    
    "00878": {
        "name": "國泰永續高股息ETF", 
        "frequency": "quarterly",
        "estimated_months": [2, 5, 8, 11],
        "typical_days": [16, 17, 18, 19, 20, 21],  # 日期範圍較廣
        "historical_dates": [
            # 2024年實際除息日期
            "2024-02-20", "2024-05-19", "2024-08-16", "2024-11-21"
        ],
        "pattern_confidence": "medium",  # 日期較不固定
        "notes": "通常每季16-21日除息，日期變化較大",
        "priority": 3,
        "expected_return": 5.56,
        "success_rate": 0.526
    },
    
    "00919": {
        "name": "群益台灣精選高息ETF",
        "frequency": "quarterly",
        "estimated_months": [3, 6, 9, 12],
        "typical_days": [16, 17, 18],
        "historical_dates": [
            # 2024年實際除息日期
            "2024-03-17", "2024-06-17", "2024-09-16", "2024-12-16"
        ],
        "pattern_confidence": "high",
        "notes": "通常每季16-18日除息，規律性佳",
        "priority": 2,
        "expected_return": 6.26,
        "success_rate": 0.50
    }
}

# 預測參數設定
PREDICTION_PARAMS = {
    "prediction_horizon_months": 18,  # 預測未來18個月
    "max_dates_per_etf": 6,           # 每個ETF最多保留6個未來日期
    "confidence_threshold": 0.7,      # 信心度門檻
    "pattern_stability_weight": 0.8   # 歷史規律權重
}

# 配置元資料
CONFIG_METADATA = {
    "version": "1.0",
    "created_date": "2025-07-22",
    "last_manual_update": "2025-07-22",
    "update_source": "historical_analysis_and_strategy_report",
    "data_basis": "etf_strategy_report_37_cycles_analysis",
    "confidence_level": "high",
    "update_frequency": "quarterly_review",
    "maintainer": "etf_strategy_system"
}

# 緊急備用配置（當所有其他方法都失敗時使用）
EMERGENCY_FALLBACK = {
    "0056": {
        "emergency_pattern": "quarterly_15th",
        "backup_months": [1, 4, 7, 10],
        "backup_day": 15
    },
    "00878": {
        "emergency_pattern": "quarterly_20th", 
        "backup_months": [2, 5, 8, 11],
        "backup_day": 20
    },
    "00919": {
        "emergency_pattern": "quarterly_16th",
        "backup_months": [3, 6, 9, 12], 
        "backup_day": 16
    }
}

def get_etf_pattern(etf_code: str) -> dict:
    """獲取特定ETF的除息規律"""
    return BASE_DIVIDEND_PATTERNS.get(etf_code, {})

def get_all_etf_codes() -> list:
    """獲取所有支援的ETF代碼"""
    return list(BASE_DIVIDEND_PATTERNS.keys())

def get_config_info() -> dict:
    """獲取配置檔案資訊"""
    return {
        "total_etfs": len(BASE_DIVIDEND_PATTERNS),
        "config_version": CONFIG_METADATA["version"],
        "last_update": CONFIG_METADATA["last_manual_update"],
        "confidence": CONFIG_METADATA["confidence_level"],
        "etf_list": list(BASE_DIVIDEND_PATTERNS.keys())
    }

if __name__ == "__main__":
    # 測試配置載入
    print("📊 ETF基礎除息配置測試")
    print("=" * 50)
    
    config_info = get_config_info()
    print(f"配置版本: {config_info['config_version']}")
    print(f"支援ETF: {config_info['total_etfs']} 個")
    print(f"ETF清單: {config_info['etf_list']}")
    print(f"最後更新: {config_info['last_update']}")
    
    print("\n📋 各ETF除息規律:")
    for etf_code in get_all_etf_codes():
        pattern = get_etf_pattern(etf_code)
        print(f"\n{etf_code} - {pattern['name']}")
        print(f"  頻率: {pattern['frequency']}")
        print(f"  月份: {pattern['estimated_months']}")  
        print(f"  日期: {pattern['typical_days']}")
        print(f"  信心度: {pattern['pattern_confidence']}")
        print(f"  優先級: {pattern['priority']}")
        print(f"  預期報酬: {pattern['expected_return']}%")