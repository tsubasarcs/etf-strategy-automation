"""
除息配置管理器
負責管理靜態基礎配置和動態更新配置的合併與更新

主要功能：
1. 載入並合併多層配置
2. 動態更新確認的除息日期  
3. 管理配置版本和歷史記錄
4. 提供便利的查詢介面

使用方式：
    from core.config_manager import get_dividend_schedule
    schedule = get_dividend_schedule()
"""

import json
import os
import sys
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import importlib

class DividendConfigManager:
    """除息配置管理器"""
    
    def __init__(self):
        # 設定檔案路徑
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(os.path.dirname(self.current_dir), "config")
        self.dynamic_config_path = os.path.join(self.config_dir, "dynamic_dividend.json")
        
        # 確保配置目錄存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        print(f"📁 配置管理器初始化:")
        print(f"   配置目錄: {self.config_dir}")
        print(f"   動態配置: {self.dynamic_config_path}")
    
    def get_current_schedule(self) -> Dict[str, List[str]]:
        """獲取當前有效的除息日程表
        
        Returns:
            Dict[str, List[str]]: {ETF代碼: [除息日期列表]}
        """
        try:
            print("🔄 開始載入除息配置...")
            
            # 1. 載入基礎預測
            base_schedule = self._generate_base_predictions()
            print(f"   📋 基礎預測: {len(base_schedule)} 個ETF")
            
            # 2. 載入動態更新
            dynamic_config = self._load_dynamic_config()
            print(f"   🔄 動態配置載入: {'成功' if dynamic_config else '失敗'}")
            
            # 3. 合併配置
            final_schedule = self._merge_configurations(base_schedule, dynamic_config)
            print(f"   ✅ 最終配置: {len(final_schedule)} 個ETF")
            
            # 4. 驗證結果
            total_dates = sum(len(dates) for dates in final_schedule.values())
            print(f"   📊 總計日期: {total_dates} 個")
            
            return final_schedule
            
        except Exception as e:
            print(f"❌ 載入配置失敗: {e}")
            return self._get_emergency_config()
    
    def _generate_base_predictions(self) -> Dict[str, List[str]]:
        """基於歷史規律生成預測日程"""
        try:
            # 動態導入基礎配置
            config_module_path = os.path.join(self.config_dir, "base_dividend.py")
            if not os.path.exists(config_module_path):
                print("⚠️ 基礎配置檔案不存在，使用緊急配置")
                return self._get_emergency_config()
            
            # 將配置目錄加入Python路徑
            if self.config_dir not in sys.path:
                sys.path.insert(0, self.config_dir)
            
            try:
                import base_dividend
                # 強制重新載入模組以獲取最新配置
                importlib.reload(base_dividend)
                BASE_DIVIDEND_PATTERNS = base_dividend.BASE_DIVIDEND_PATTERNS
                print("   ✅ 成功載入基礎配置模組")
            except ImportError as e:
                print(f"   ❌ 導入基礎配置失敗: {e}")
                return self._get_emergency_config()
            
        except Exception as e:
            print(f"❌ 載入基礎配置失敗: {e}")
            return self._get_emergency_config()
        
        # 基於配置生成預測
        schedule = {}
        today = date.today()
        current_year = today.year
        
        for etf_code, pattern in BASE_DIVIDEND_PATTERNS.items():
            dates = []
            
            # 預測未來18個月的除息日期
            for year_offset in [0, 1]:
                target_year = current_year + year_offset
                for month in pattern['estimated_months']:
                    # 嘗試預測的日期範圍
                    for day in pattern['typical_days']:
                        try:
                            predicted_date = date(target_year, month, day)
                            if predicted_date > today:
                                dates.append(predicted_date.strftime('%Y-%m-%d'))
                                break  # 每月只取第一個有效日期
                        except ValueError:
                            continue
            
            # 保持日期排序並限制數量
            schedule[etf_code] = sorted(dates)[:6]  # 最多6個未來日期
            print(f"   📅 {etf_code}: 預測 {len(schedule[etf_code])} 個日期")
        
        return schedule
    
    def _load_dynamic_config(self) -> Dict:
        """載入動態配置檔案"""
        try:
            if os.path.exists(self.dynamic_config_path):
                with open(self.dynamic_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"   📄 動態配置版本: {config.get('config_version', 'Unknown')}")
                    print(f"   ⏰ 最後更新: {config.get('last_updated', 'Unknown')}")
                    return config
            else:
                print("   ⚠️ 動態配置檔案不存在，創建預設配置")
                return self._create_default_dynamic_config()
        except Exception as e:
            print(f"   ❌ 載入動態配置失敗: {e}")
            return self._create_default_dynamic_config()
    
    def _merge_configurations(self, base: Dict[str, List[str]], dynamic: Dict) -> Dict[str, List[str]]:
        """合併基礎預測和動態更新"""
        final_schedule = base.copy()
        
        # 1. 應用確認的日期覆蓋（最高優先級）
        overrides_applied = 0
        for etf_code, override_data in dynamic.get('overrides', {}).items():
            if isinstance(override_data, dict) and 'confirmed_dates' in override_data:
                confirmed_dates = override_data['confirmed_dates']
                # 只保留未來日期
                future_dates = [
                    d for d in confirmed_dates 
                    if datetime.strptime(d, '%Y-%m-%d').date() > date.today()
                ]
                if future_dates:
                    final_schedule[etf_code] = sorted(future_dates)
                    overrides_applied += 1
                    print(f"   🔄 {etf_code}: 應用確認日期 {len(future_dates)} 個")
        
        # 2. 應用動態預測（如果沒有確認日期）
        predictions_applied = 0
        for etf_code, prediction_data in dynamic.get('predictions', {}).items():
            if etf_code not in dynamic.get('overrides', {}) and isinstance(prediction_data, dict):
                if 'estimated_dates' in prediction_data:
                    estimated_dates = prediction_data['estimated_dates']
                    future_dates = [
                        d for d in estimated_dates 
                        if datetime.strptime(d, '%Y-%m-%d').date() > date.today()
                    ]
                    if future_dates:
                        final_schedule[etf_code] = sorted(future_dates)
                        predictions_applied += 1
                        print(f"   📊 {etf_code}: 應用預測日期 {len(future_dates)} 個")
        
        print(f"   ✅ 配置合併完成: {overrides_applied} 個確認, {predictions_applied} 個預測")
        return final_schedule
    
    def update_confirmed_dates(self, etf_code: str, new_dates: List[str], 
                              source: str = "manual_update") -> bool:
        """更新確認的除息日期
        
        Args:
            etf_code: ETF代碼
            new_dates: 新的除息日期列表
            source: 更新來源 (manual_update, api_verified, official_announcement)
        
        Returns:
            bool: 更新是否成功
        """
        try:
            print(f"🔄 更新 {etf_code} 除息日期...")
            print(f"   新日期: {new_dates}")
            print(f"   來源: {source}")
            
            # 載入現有配置
            dynamic_config = self._load_dynamic_config()
            
            # 更新確認日期
            if 'overrides' not in dynamic_config:
                dynamic_config['overrides'] = {}
            
            dynamic_config['overrides'][etf_code] = {
                'confirmed_dates': new_dates,
                'source': source,
                'updated_at': datetime.now().isoformat(),
                'confidence': 'high' if source in ['official_announcement', 'api_verified'] else 'medium'
            }
            
            # 記錄更新日誌
            if 'manual_updates_log' not in dynamic_config:
                dynamic_config['manual_updates_log'] = []
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'update_confirmed_dates',
                'etf_code': etf_code,
                'new_dates': new_dates,
                'source': source,
                'user': 'config_manager'
            }
            dynamic_config['manual_updates_log'].append(log_entry)
            
            # 更新元資料
            dynamic_config['last_updated'] = datetime.now().isoformat()
            dynamic_config['metadata']['last_manual_update'] = datetime.now().isoformat()
            
            # 儲存配置
            with open(self.dynamic_config_path, 'w', encoding='utf-8') as f:
                json.dump(dynamic_config, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ {etf_code} 除息日期更新成功")
            
            # 備份到Firebase（如果可用）
            self._backup_to_firebase(dynamic_config)
            
            return True
            
        except Exception as e:
            print(f"   ❌ 更新失敗 {etf_code}: {e}")
            return False
    
    def get_config_status(self) -> Dict[str, Any]:
        """獲取配置狀態資訊"""
        dynamic_config = self._load_dynamic_config()
        current_schedule = self.get_current_schedule()
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'config_version': dynamic_config.get('config_version', 'Unknown'),
            'last_updated': dynamic_config.get('last_updated', 'Unknown'),
            'total_etfs': len(current_schedule),
            'total_future_dates': sum(len(dates) for dates in current_schedule.values()),
            'confirmed_etfs': len(dynamic_config.get('overrides', {})),
            'predicted_etfs': len(dynamic_config.get('predictions', {})),
            'update_log_entries': len(dynamic_config.get('manual_updates_log', [])),
            'system_status': dynamic_config.get('system_status', 'unknown'),
            'api_status': dynamic_config.get('api_status', {}),
            'validation_status': dynamic_config.get('validation', {}).get('validation_status', 'unknown')
        }
        
        return status
    
    def print_schedule_summary(self):
        """顯示配置摘要資訊"""
        print("\n" + "="*60)
        print("📊 ETF除息配置系統狀態")
        print("="*60)
        
        # 載入狀態資訊
        status = self.get_config_status()
        schedule = self.get_current_schedule()
        
        print(f"🔧 系統版本: {status['config_version']}")
        print(f"⏰ 最後更新: {status['last_updated']}")
        print(f"📊 ETF總數: {status['total_etfs']}")
        print(f"📅 未來日期: {status['total_future_dates']} 個")
        print(f"✅ 確認日期: {status['confirmed_etfs']} 個ETF")
        print(f"📈 預測日期: {status['predicted_etfs']} 個ETF")
        print(f"📝 更新記錄: {status['update_log_entries']} 筆")
        
        print(f"\n📅 當前除息日程:")
        for etf_code, dates in schedule.items():
            next_dates = dates[:3]  # 顯示前3個日期
            remaining = len(dates) - 3
            dates_str = ", ".join(next_dates)
            if remaining > 0:
                dates_str += f" (還有{remaining}個)"
            print(f"   {etf_code}: {dates_str}")
        
        print("="*60)
    
    def _create_default_dynamic_config(self) -> Dict:
        """創建預設動態配置檔案"""
        default_config = {
            "config_version": "1.0",
            "created_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "update_source": "auto_generated_default",
            "confidence_level": "medium",
            "system_status": "initializing",
            "metadata": {
                "total_etfs": 3,
                "prediction_horizon_months": 18,
                "last_api_success": None,
                "last_manual_update": None
            },
            "overrides": {},
            "predictions": {},
            "api_status": {
                "last_api_attempt": None,
                "api_failures": 0,
                "fallback_mode": True
            },
            "manual_updates_log": [{
                "timestamp": datetime.now().isoformat(),
                "action": "create_default_config",
                "description": "自動創建預設動態配置檔案",
                "user": "system"
            }],
            "validation": {
                "last_validation": datetime.now().isoformat(),
                "validation_status": "warning",
                "warnings": ["使用預設配置，建議手動驗證日期"]
            }
        }
        
        # 嘗試儲存預設配置
        try:
            os.makedirs(os.path.dirname(self.dynamic_config_path), exist_ok=True)
            with open(self.dynamic_config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print("   ✅ 預設動態配置已創建")
        except Exception as e:
            print(f"   ❌ 創建預設配置失敗: {e}")
        
        return default_config
    
    def _get_emergency_config(self) -> Dict[str, List[str]]:
        """緊急備用配置（所有其他方法都失敗時使用）"""
        print("🚨 使用緊急備用配置")
        
        today = date.today()
        current_year = today.year
        
        emergency_config = {
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
        
        # 過濾出未來日期
        filtered_config = {}
        for etf_code, dates in emergency_config.items():
            future_dates = [
                d for d in dates 
                if datetime.strptime(d, '%Y-%m-%d').date() > today
            ]
            filtered_config[etf_code] = future_dates
            print(f"   🆘 {etf_code}: {len(future_dates)} 個緊急日期")
        
        return filtered_config
    
    def _backup_to_firebase(self, config_data: Dict):
        """備份配置到Firebase（可選）"""
        try:
            # 嘗試導入Firebase客戶端
            firebase_path = os.path.join(os.path.dirname(self.current_dir), "core", "firebase_client.py")
            if os.path.exists(firebase_path):
                sys.path.insert(0, os.path.dirname(firebase_path))
                from firebase_client import FirebaseClient
                
                firebase_client = FirebaseClient()
                success = firebase_client.save("dividend_config/latest", config_data)
                
                if success:
                    print("   ☁️ 配置已備份到Firebase")
                else:
                    print("   ⚠️ Firebase備份失敗")
            else:
                print("   ℹ️ Firebase客戶端不可用，跳過備份")
        except Exception as e:
            print(f"   ⚠️ Firebase備份失敗: {e}")

# 便利函數，提供簡單的介面
_manager_instance = None

def get_dividend_schedule() -> Dict[str, List[str]]:
    """快速獲取當前除息日程表"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = DividendConfigManager()
    return _manager_instance.get_current_schedule()

def update_dividend_dates(etf_code: str, dates: List[str], source: str = "manual") -> bool:
    """快速更新除息日期"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = DividendConfigManager()
    return _manager_instance.update_confirmed_dates(etf_code, dates, source)

def get_config_info():
    """顯示配置資訊"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = DividendConfigManager()
    _manager_instance.print_schedule_summary()

def reset_config_manager():
    """重置配置管理器（強制重新載入）"""
    global _manager_instance
    _manager_instance = None

# 測試和除錯功能
if __name__ == "__main__":
    print("🧪 ETF配置管理器測試")
    print("="*50)
    
    try:
        # 測試配置管理器
        manager = DividendConfigManager()
        
        # 測試載入配置
        print("\n🔄 測試配置載入...")
        schedule = manager.get_current_schedule()
        
        if schedule:
            print("✅ 配置載入成功！")
            
            # 顯示配置摘要
            manager.print_schedule_summary()
            
            # 測試更新功能
            print("\n🧪 測試配置更新...")
            test_success = manager.update_confirmed_dates(
                "0056", 
                ["2025-10-16", "2026-01-16"], 
                "test_update"
            )
            
            if test_success:
                print("✅ 配置更新測試成功！")
                
                # 顯示更新後的配置
                updated_schedule = manager.get_current_schedule()
                print(f"📅 0056更新後日期: {updated_schedule.get('0056', [])}")
            else:
                print("❌ 配置更新測試失敗")
        else:
            print("❌ 配置載入失敗")
            
    except Exception as e:
        print(f"💥 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50)
    print("🧪 測試完成")